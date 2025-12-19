"""
Services actuator module.

Implements ActuatorService for sidecar ENS architecture.
Registers with BusRouter to receive commands from sidecar stream.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from ..bus.client import BusClient
from ..bus.envelopes import CommandReply, CommandRequest
from ..bus.router import BusRouter
from ..logging.errors import CommandRejectedError, SchemaValidationError
from ..seams.models import ActuatorCapabilities, ActuatorCmd, ActuatorState, load_defaults
from ..seams.store import SeamStore
from ..seams.validators import validate_actuator_command, validate_contract_version
from .base import BaseService


class ActuatorService(BaseService):
    """Actuator service implementing full Actuator Contract.

    Responsibilities:
    1. On start():
       - Ensure actuator seams exist in Store (write defaults if missing)
       - Publish Announce + initial StateEvent via BusClient
    2. Register with BusRouter so CommandRequests are received from sidecar stream
    3. Validate requests vs capabilities seam + spec behavioral rules
    4. If accepted:
       - Write actuator.cmd seam via SeamStore (remote-first)
       - Update actuator.state/op_mode/feedback via SeamStore
    5. Always emit CommandReply via bus.publish_reply()
    6. After any command: emit StateEvent

    Uses SeamStore for all reads/writes (remote-first via sidecar).
    BusRouter handles idempotency; service focuses on validation and execution.
    """

    def __init__(
        self,
        component_id: str,
        bus: BusClient,
        store: SeamStore,
        router: BusRouter,
        log: Any,
        contract_version: str = "1.0.0",
    ):
        """Initialize actuator service.

        Args:
            component_id: Unique actuator identifier
            bus: BusClient for sidecar communication
            store: SeamStore for reading/writing seams
            router: BusRouter for command dispatching
            log: Logger instance
            contract_version: Actuator contract version
        """
        super().__init__(
            component_id=component_id,
            bus=bus,
            store=store,
            log=log,
            contract="Actuator",
            contract_version=contract_version,
        )
        self.router = router

    async def start(self) -> None:
        """Start the actuator service.

        1. Ensure actuator seams exist (write defaults if missing)
        2. Publish Announce
        3. Emit initial StateEvent
        4. Register with BusRouter
        """
        self._running = True

        # Ensure all actuator seams exist with defaults
        await self._ensure_seams_exist()

        # Read capabilities for announce
        capabilities_dict = await self.store.get(self.component_id, "actuator", "capabilities")
        # Filter out stateSchemaId before passing to Pydantic model
        caps_data = {k: v for k, v in capabilities_dict.items() if k != "stateSchemaId"}
        capabilities = ActuatorCapabilities(**caps_data)

        # Announce on start
        await self.announce(
            service_role="actuator",
            capabilities=capabilities.supported_commands,
            config_hash="",  # TODO: Calculate from config
            health="OK",
        )

        # Emit initial StateEvent
        await self.emit_state_event()

        # Register with BusRouter to receive commands from sidecar stream
        self.router.register_handler(
            component_id=self.component_id,
            handler=self._handle_command_request,
            instrument="actuator",
        )

        # Start the router (for PollingBusRouter, this starts polling tasks)
        if hasattr(self.router, "start"):
            await self.router.start()

        if self.log:
            self.log.info(f"ActuatorService {self.component_id} started")

    async def _ensure_seams_exist(self) -> None:
        """Ensure all actuator seams exist with defaults."""
        attributes = [
            "meta",
            "state",
            "capabilities",
            "feedback",
            "intent",
            "invariants",
            "cmd",
        ]

        for attribute in attributes:
            try:
                # Try to read existing seam
                await self.store.get(self.component_id, "actuator", attribute)
            except (KeyError, Exception):
                # Seam doesn't exist, write defaults
                defaults = load_defaults(attribute)
                await self.store.set(
                    self.component_id,
                    "actuator",
                    attribute,
                    defaults,
                )
                if self.log:
                    self.log.info(
                        f"Initialized {self.component_id}.actuator.{attribute} with defaults"
                    )

    async def _handle_command_request(self, request: CommandRequest) -> None:
        """Handle incoming CommandRequest from BusRouter.

        BusRouter handles:
        - Idempotency checking
        - Error handling

        This handler focuses on:
        - Version validation
        - Capability validation
        - Behavioral rule validation
        - Command execution
        - Seam updates
        - Reply publishing (via bus_command_reply attribute)

        Args:
            request: CommandRequest envelope (already decoded by BusRouter)
        """
        # Validate contract version
        try:
            major_version = int(self.contract_version.split(".")[0])
            validate_contract_version(major_version, request.expected_version)
        except SchemaValidationError as e:
            if self.log:
                self.log.warning(
                    f"Version mismatch for command {request.command_id}: {e.validation_error}"
                )
            await self._create_reply(
                request,
                accepted=False,
                reason=f"Version mismatch: {e.validation_error}",
            )
            await self.emit_state_event()
            return

        # Read capabilities and current state
        try:
            capabilities_dict = await self.store.get(self.component_id, "actuator", "capabilities")
            # Filter out stateSchemaId before passing to Pydantic model
            caps_data = {k: v for k, v in capabilities_dict.items() if k != "stateSchemaId"}
            capabilities = ActuatorCapabilities(**caps_data)

            state_dict = await self.store.get(self.component_id, "actuator", "state")
            # Filter out stateSchemaId before passing to Pydantic model
            state_data = {k: v for k, v in state_dict.items() if k != "stateSchemaId"}
            current_state = ActuatorState(**state_data)
        except Exception as e:
            if self.log:
                self.log.error(f"Failed to read seams: {e}")
            await self._create_reply(
                request,
                accepted=False,
                reason=f"Internal error reading seams: {str(e)}",
            )
            await self.emit_state_event()
            return

        # Validate command against capabilities and behavioral rules
        try:
            validate_actuator_command(request, capabilities, current_state)
        except CommandRejectedError as e:
            if self.log:
                self.log.warning(f"Command {request.command_id} rejected: {e.reason}")
            await self._create_reply(
                request,
                accepted=False,
                reason=e.reason,
            )
            await self.emit_state_event()
            return

        # Update cmd seam with request details
        await self._update_cmd_seam(request)

        # Execute the command
        try:
            await self.handle_command(request)

            await self._create_reply(
                request,
                accepted=True,
                reason="Command accepted and executed",
            )
        except Exception as e:
            if self.log:
                self.log.error(
                    f"Command execution failed for {request.command_id}: {e}",
                    exc_info=True,
                )
            await self._create_reply(
                request,
                accepted=False,
                reason=f"Execution error: {str(e)}",
            )

        # Emit StateEvent after command processing
        await self.emit_state_event()

    async def _update_cmd_seam(self, request: CommandRequest) -> None:
        """Update actuator.cmd seam with command request details.

        Args:
            request: CommandRequest envelope
        """
        cmd_data = {
            "stateSchemaId": "procaaso.io/seams/actuator/cmd/v1",
            "command_id": request.command_id,
            "command": request.command,
            "args": request.args,
            "expected_version": request.expected_version,
            "source": request.source,
        }
        await self.store.set(self.component_id, "actuator", "cmd", cmd_data)

        if self.log:
            self.log.debug(f"Updated cmd seam: {request.command} ({request.command_id})")

    async def _create_reply(
        self,
        request: CommandRequest,
        accepted: bool,
        reason: str,
    ) -> None:
        """Create and publish CommandReply via bus_command_reply attribute.

        Writes the CommandReply envelope to the bus_command_reply attribute,
        where the sidecar will read it and forward to the control bus.

        Args:
            request: CommandRequest
            accepted: Whether command was accepted
            reason: Reason for acceptance/rejection
        """
        # Read current state for resulting_state field
        try:
            state_dict = await self.store.get(self.component_id, "actuator", "state")
            lifecycle_state = state_dict.get("lifecycle_state", "Unknown")
        except Exception:
            lifecycle_state = "Unknown"

        reply = CommandReply(
            command_id=request.command_id,
            target_id=self.component_id,
            accepted=accepted,
            reason=reason,
            resulting_state=lifecycle_state,
            ts=datetime.utcnow().isoformat() + "Z",
        )

        # Write reply to bus_command_reply attribute for sidecar forwarding
        await self.store.set(self.component_id, "actuator", "bus_command_reply", reply.to_dict())

    async def handle_command(self, request: CommandRequest) -> None:
        """Execute command logic - override in subclasses for hardware control.

        Default implementation logs command. Subclasses should:
        - Implement hardware-specific control logic
        - Update feedback seam via update_feedback()
        - Update state seam via update_state() as needed

        Args:
            request: CommandRequest envelope
        """
        if self.log:
            self.log.info(f"Executing command: {request.command} with args: {request.args}")

        # Example subclass implementation:
        # if request.command == "Setpoint":
        #     percent = request.args[0].get("percent", 0)
        #     await self.hw.set_speed(percent)
        #     await self.update_feedback(sp=percent, percent=percent)
        # elif request.command == "Start":
        #     await self.hw.start()
        #     await self.update_state(lifecycle_state="Running")

    async def update_feedback(self, **kwargs) -> None:
        """Update actuator.feedback seam fields.

        Args:
            **kwargs: Feedback fields to update (pv, sp, percent, quality, status_flags)
        """
        updated = await self.store.update_fields(
            self.component_id,
            "actuator",
            "feedback",
            **kwargs,
        )

        if self.log:
            self.log.debug(f"Updated feedback: {kwargs}")

    async def update_state(self, **kwargs) -> None:
        """Update actuator.state seam fields.

        Args:
            **kwargs: State fields to update (lifecycle_state, op_mode, faulted, etc.)
        """
        updated = await self.store.update_fields(
            self.component_id,
            "actuator",
            "state",
            **kwargs,
        )

        if self.log:
            self.log.debug(f"Updated state: {kwargs}")
