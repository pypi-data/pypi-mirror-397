"""
Polling-based router for sidecar architecture.

Instead of streaming commands, this router polls the cmd attribute
at regular intervals to detect new commands.
"""

import asyncio
import time
from typing import Any, Callable, Dict, Optional, Tuple

from .envelopes import CommandReply, CommandRequest
from .idempotency import IdempotencyStore


class PollingBusRouter:
    """
    Poll-based command router for sidecar architecture.

    Instead of streaming commands from the sidecar, this router:
    1. Polls the component's cmd attribute at regular intervals
    2. Detects new commands by comparing command_id with last processed
    3. Invokes registered handlers
    4. Enforces idempotency to prevent duplicate execution
    5. Publishes replies back through bus

    Architecture:
    - External system writes CommandRequest to: component.instrument.cmd
    - Router polls and reads cmd attribute
    - Handler processes command and returns CommandReply
    - Router publishes reply via bus
    """

    def __init__(
        self,
        bus: Any,
        idempotency_store: IdempotencyStore,
        log: Any = None,
        poll_interval: float = 0.5,
        dedup_window: float = 10.0,
    ):
        """Initialize polling router.

        Args:
            bus: Bus client for reading cmd and publishing replies
            idempotency_store: Store for tracking processed commands
            log: Logger instance
            poll_interval: Seconds between polls (default 0.5s = 500ms)
            dedup_window: Seconds to track command_ids for deduplication (default 10s)
        """
        self.bus = bus
        self.idempotency_store = idempotency_store
        self.log = log
        self.poll_interval = poll_interval
        self.dedup_window = dedup_window

        self._handlers: Dict[str, Callable] = {}
        self._polling_tasks: Dict[str, asyncio.Task] = {}
        self._running = False
        self._last_command_ids: Dict[str, Tuple[str, float]] = (
            {}
        )  # Track (command_id, timestamp) per component
        self._instrument_types: Dict[str, str] = {}  # Track instrument type per component

    def register_handler(
        self,
        component_id: str,
        handler: Callable[[CommandRequest], CommandReply],
        instrument: str = "actuator",
    ) -> None:
        """Register component command handler.

        Args:
            component_id: Component ID to poll for commands
            handler: Async function that processes CommandRequest and returns CommandReply
            instrument: Instrument type (e.g., 'actuator', 'sensor', 'unit', 'driver')
        """
        self._handlers[component_id] = handler
        self._last_command_ids[component_id] = ""
        self._instrument_types[component_id] = instrument

        if self.log:
            self.log.info(f"Registered handler for {component_id}")

    def register_actuator(
        self,
        actuator_id: str,
        handler: Callable[[CommandRequest], CommandReply],
        instrument: str = "actuator",
    ) -> None:
        """Backward compatibility alias for register_handler.

        Deprecated: Use register_handler() instead.
        """
        return self.register_handler(actuator_id, handler, instrument)

    async def start(self) -> None:
        """Start polling for all registered components."""
        if self._running:
            return

        self._running = True

        for component_id in self._handlers.keys():
            task = asyncio.create_task(self._poll_for_commands(component_id))
            self._polling_tasks[component_id] = task

            if self.log:
                self.log.info(
                    f"Started polling for {component_id} (interval={self.poll_interval}s)"
                )

    async def stop(self) -> None:
        """Stop all polling tasks."""
        self._running = False

        # Cancel all polling tasks
        for task in self._polling_tasks.values():
            task.cancel()

        if self._polling_tasks:
            await asyncio.gather(*self._polling_tasks.values(), return_exceptions=True)

        self._polling_tasks.clear()

        if self.log:
            self.log.info("Stopped all polling tasks")

    async def _poll_for_commands(self, component_id: str) -> None:
        """Poll cmd attribute for new commands.

        Args:
            component_id: Component ID to poll
        """
        handler = self._handlers[component_id]
        instrument = self._instrument_types.get(component_id, "actuator")

        if self.log:
            self.log.info(f"Starting poll loop for {component_id}.{instrument}.cmd")

        while self._running:
            try:
                # Read current cmd attribute from sidecar cache
                path = f"{component_id}.{instrument}.cmd"

                cmd_data = await self.bus.get_seam(path)

                command_id = cmd_data.get("command_id", "")
                command_name = cmd_data.get("command", "")

                if not command_id:
                    # No command present
                    await asyncio.sleep(self.poll_interval)
                    continue

                # Check if this command_id has been seen before (permanent tracking)
                last_cmd_id = self._last_command_ids.get(component_id, "")

                if command_id == last_cmd_id:
                    # Same command_id as last poll, skip
                    await asyncio.sleep(self.poll_interval)
                    continue

                # New command detected! Read intent and waiting_on for context (if applicable)
                intent_context = ""
                waiting_context = ""

                # intent exists on: actuator, unit, app (optional on sensor per spec)
                if instrument in ["actuator", "unit", "app"]:
                    intent_context = await self._get_intent_context(component_id, instrument)

                # waiting_on exists on: unit, app only
                if instrument in ["unit", "app"]:
                    waiting_context = await self._get_waiting_context(component_id, instrument)

                if self.log:
                    context_parts = [f"command={command_name}"]
                    if intent_context:
                        context_parts.append(intent_context)
                    if waiting_context:
                        context_parts.append(waiting_context)
                    self.log.info(f"New command for {component_id}: {', '.join(context_parts)}")

                # Build CommandRequest from cmd data
                request = CommandRequest(
                    command_id=command_id,
                    contract=cmd_data.get("contract", "Actuator"),
                    expected_version=cmd_data.get("expected_version", "1.0.0"),
                    target_id=component_id,
                    command=cmd_data.get("command", ""),
                    args=cmd_data.get("args", []),
                    source=cmd_data.get("source", "unknown"),
                    ts=cmd_data.get("ts", ""),
                )

                # Process the command
                await self._process_command(component_id, request, handler)

                # Update last processed command_id (tracked permanently)
                self._last_command_ids[component_id] = command_id

            except asyncio.CancelledError:
                # Task cancelled during shutdown
                break
            except Exception as e:
                if self.log:
                    self.log.error(f"Error polling {component_id}: {e}", exc_info=True)
                await asyncio.sleep(self.poll_interval)

    async def _get_intent_context(self, component_id: str, instrument: str) -> str:
        """Extract intent context for logging.

        Only call for instruments that have intent attribute (actuator, unit, app).

        Args:
            component_id: Component ID
            instrument: Instrument type

        Returns:
            Formatted intent context string or empty string
        """
        try:
            intent_path = f"{component_id}.{instrument}.intent"
            intent_data = await self.bus.get_seam(intent_path)
            parts = []
            if intent_data.get("owner"):
                parts.append(f"owner={intent_data['owner']}")
            if intent_data.get("batch_id"):
                parts.append(f"batch={intent_data['batch_id']}")
            if intent_data.get("recipe_id"):
                parts.append(f"recipe={intent_data['recipe_id']}")
            if intent_data.get("phase_id"):
                parts.append(f"phase={intent_data['phase_id']}")
            return f"intent({', '.join(parts)})" if parts else ""
        except Exception:
            return ""

    async def _get_waiting_context(self, component_id: str, instrument: str) -> str:
        """Extract waiting_on context for logging.

        Only call for instruments that have waiting_on attribute (unit, app).

        Args:
            component_id: Component ID
            instrument: Instrument type

        Returns:
            Formatted waiting_on context string or empty string
        """
        try:
            waiting_path = f"{component_id}.{instrument}.waiting_on"
            waiting_data = await self.bus.get_seam(waiting_path)
            reasons = waiting_data.get("reasons", [])
            if reasons:
                # Show first 3 reasons to keep logs concise
                return f"waiting_on({', '.join(reasons[:3])})"
            return ""
        except Exception:
            return ""

    async def _process_command(
        self,
        component_id: str,
        request: CommandRequest,
        handler: Callable,
    ) -> None:
        """Process a command request.

        Handler writes reply directly to bus_command_reply attribute.
        Idempotency is enforced to avoid re-executing commands.

        Args:
            component_id: Component ID
            request: CommandRequest to process
            handler: Handler function (writes reply to bus_command_reply)
        """
        try:
            # Check idempotency
            if await self.idempotency_store.seen(request.command_id):
                if self.log:
                    self.log.info(
                        f"Command {request.command_id} already processed (idempotent), skipping"
                    )
                # Note: Original reply already written to bus_command_reply attribute
                return

            # Invoke handler (writes reply to bus_command_reply attribute)
            await handler(request)

            # Record in idempotency store (reply not needed since handler writes directly)
            await self.idempotency_store.record(request, None)

            if self.log:
                self.log.info(f"Processed command {request.command_id} for {component_id}")

        except Exception as e:
            # Handler failed - log error
            # Note: Handler should catch exceptions and write error replies
            # But if handler itself crashes, we log here
            if self.log:
                self.log.error(
                    f"Error processing command {request.command_id} for {component_id}: {e}",
                    exc_info=True,
                )
