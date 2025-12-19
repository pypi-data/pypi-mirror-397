"""
Bus router module.

Polls bus_command_request attribute and dispatches to registered handlers.
Handlers write replies directly to bus_command_request attribute for sidecar forwarding.
"""

import asyncio
from typing import Any, Awaitable, Callable, Dict

from ..logging.errors import CommandRejectedError
from ..sidecar.store import RemoteSeamStore
from .envelopes import CommandRequest
from .idempotency import IdempotencyStore


class BusRouter:
    """Routes CommandRequests from bus_command_request attribute to registered component handlers.

    - Polls bus_command_request attribute every 100ms for each registered component
    - Decodes CommandRequest envelopes
    - Enforces idempotency via IdempotencyStore
    - Invokes handler(request) which writes reply to bus_command_reply attribute
    - Sidecar forwards reply from bus_command_reply to control bus

    Router does not manage topics directly; sidecar handles pub/sub filtering.
    """

    def __init__(
        self,
        store: RemoteSeamStore,
        idempotency_store: IdempotencyStore,
        log: Any = None,
    ):
        """Initialize router.

        Args:
            store: RemoteSeamStore for reading bus_command_request attribute
            idempotency_store: IdempotencyStore for deduplication
            log: Logger instance
        """
        self.store = store
        self.idempotency_store = idempotency_store
        self.log = log
        self._handlers: Dict[str, Callable[[CommandRequest], Awaitable[None]]] = {}
        self._instruments: Dict[str, str] = {}  # Track instrument type per component
        self._tasks: Dict[str, asyncio.Task] = {}
        self._running = False
        self._last_command_ids: Dict[str, str] = {}  # Track last processed command_id per component

    def register_handler(
        self,
        component_id: str,
        handler: Callable[[CommandRequest], Awaitable[None]],
        instrument: str = "actuator",
    ) -> None:
        """Register a component command handler.

        When router starts, it will poll bus_command_request attribute for this component.

        Args:
            component_id: Component ID
            handler: Async handler that processes CommandRequest (writes reply to bus_command_reply)
            instrument: Instrument type (e.g., 'actuator', 'sensor', 'unit', 'driver', 'app')
        """
        self._handlers[component_id] = handler
        self._instruments[component_id] = instrument
        if self.log:
            self.log.info(f"Registered {instrument} handler: {component_id}")

        # If already running, start polling immediately
        if self._running and component_id not in self._tasks:
            task = asyncio.create_task(self._poll_and_dispatch(component_id, handler))
            self._tasks[component_id] = task

    def register_actuator(
        self,
        actuator_id: str,
        handler: Callable[[CommandRequest], Awaitable[None]],
        instrument: str = "actuator",
    ) -> None:
        """Register an actuator command handler (deprecated, use register_handler).

        Provided for backward compatibility. Use register_handler instead.

        Args:
            actuator_id: Actuator component ID
            handler: Async handler that processes CommandRequest (writes reply to bus_command_reply)
            instrument: Instrument type (defaults to 'actuator')
        """
        self.register_handler(actuator_id, handler, instrument)

    async def start(self) -> None:
        """Start router - begin polling commands for all registered components."""
        self._running = True

        # Start polling task for each registered component
        for component_id, handler in self._handlers.items():
            if component_id not in self._tasks:
                task = asyncio.create_task(self._poll_and_dispatch(component_id, handler))
                self._tasks[component_id] = task

        if self.log:
            self.log.info(f"BusRouter started for {len(self._handlers)} components")

    async def stop(self) -> None:
        """Stop router - cancel all polling tasks."""
        self._running = False

        # Cancel all tasks
        for task in self._tasks.values():
            task.cancel()

        if self._tasks:
            await asyncio.gather(*self._tasks.values(), return_exceptions=True)

        self._tasks.clear()

        if self.log:
            self.log.info("BusRouter stopped")

    async def _poll_and_dispatch(
        self,
        component_id: str,
        handler: Callable[[CommandRequest], Awaitable[None]],
    ) -> None:
        """Poll bus_command_request attribute and dispatch to handler.

        Polls every 100ms. Tracks last_command_id to detect new commands.

        Args:
            component_id: Component ID
            handler: Command handler function
        """
        try:
            if self.log:
                self.log.info(f"Starting command polling for component: {component_id}")

            # Get instrument type
            instrument = self._instruments.get(component_id, "actuator")

            while self._running:
                try:
                    # Read bus_command_request attribute
                    command_data = await self.store.get(
                        component_id, instrument, "bus_command_request"
                    )

                    # Check if command_data is valid and has a command_id
                    if command_data and isinstance(command_data, dict):
                        command_id = command_data.get("command_id")

                        # Check if this is a new command (different from last processed)
                        if command_id and command_id != self._last_command_ids.get(component_id):
                            # Parse CommandRequest
                            try:
                                request = CommandRequest(**command_data)

                                # Update last_command_id
                                self._last_command_ids[component_id] = command_id

                                # Process command in background
                                asyncio.create_task(self._process_command(request, handler))

                            except Exception as parse_error:
                                if self.log:
                                    self.log.error(
                                        f"Failed to parse CommandRequest for {component_id}: {parse_error}",
                                        exc_info=True,
                                    )

                except Exception as read_error:
                    # Attribute may not exist yet or sidecar may be down
                    if self.log:
                        self.log.debug(
                            f"Failed to read bus_command_request for {component_id}: {read_error}"
                        )

                # Poll every 100ms
                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            if self.log:
                self.log.info(f"Command polling cancelled for component: {component_id}")
            raise

        except Exception as e:
            if self.log:
                self.log.error(
                    f"Command polling error for component {component_id}: {e}",
                    exc_info=True,
                )

    async def _process_command(
        self,
        request: CommandRequest,
        handler: Callable[[CommandRequest], Awaitable[None]],
    ) -> None:
        """Process a single command request with idempotency check.

        Handler writes reply directly to bus_command_reply attribute.
        Idempotency is enforced to avoid re-executing commands.

        Args:
            request: CommandRequest envelope
            handler: Command handler function (writes to bus_command_reply)
        """
        command_id = request.command_id

        try:
            # Check idempotency
            if await self.idempotency_store.seen(command_id):
                if self.log:
                    self.log.info(f"Idempotent command {command_id}: already processed, skipping")
                # Note: Original reply already written to bus_command_reply attribute
                # No need to re-publish
                return

            # Invoke handler (writes reply to bus_command_reply attribute)
            await handler(request)

            # Record in idempotency store (reply not needed since handler writes directly)
            await self.idempotency_store.record(request, None)

            if self.log:
                self.log.debug(f"Processed command {command_id}")

        except Exception as e:
            # Handler failed - log error
            # Note: Handler should catch exceptions and write error replies
            # But if handler itself crashes, we log here
            if self.log:
                self.log.error(
                    f"Error processing command {command_id}: {e}",
                    exc_info=True,
                )
