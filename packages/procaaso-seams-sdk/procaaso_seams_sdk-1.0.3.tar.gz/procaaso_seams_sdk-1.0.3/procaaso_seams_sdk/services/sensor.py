"""
Services sensor module.

Implements SensorService for sidecar ENS architecture.
Registers with BusRouter to receive commands from sidecar stream.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from ..bus.client import BusClient
from ..bus.envelopes import CommandReply, CommandRequest
from ..bus.router import BusRouter
from ..logging.errors import CommandRejectedError, SchemaValidationError
from ..seams.models import SensorCapabilities, SensorCmd, SensorState, load_defaults
from ..seams.store import SeamStore
from ..seams.validators import validate_contract_version, validate_sensor_command
from .base import BaseService


class SensorService(BaseService):
    """Sensor service implementing full Sensor Contract.

    Responsibilities:
    1. On start():
       - Ensure sensor seams exist in Store (write defaults if missing)
       - Publish Announce + initial StateEvent via BusClient
    2. Register with BusRouter so CommandRequests are received from sidecar stream
    3. Validate requests vs capabilities seam + spec behavioral rules
    4. If accepted:
       - Write sensor.cmd seam via SeamStore (remote-first)
       - Update sensor.state/value via SeamStore
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
        """Initialize sensor service.

        Args:
            component_id: Sensor ID
            bus: BusClient for publishing announcements, state events, replies
            store: SeamStore for reading/writing sensor seams
            router: BusRouter to register for CommandRequest handling
            log: Logger instance
            contract_version: Sensor contract version (default: 1.0.0)
        """
        super().__init__(
            component_id=component_id,
            bus=bus,
            store=store,
            log=log,
            contract="Sensor",
            contract_version=contract_version,
        )
        self.router = router

    async def start(self) -> None:
        """Start the sensor service.

        1. Ensure sensor seams exist (write defaults if missing)
        2. Publish Announce
        3. Emit initial StateEvent
        4. Register with BusRouter
        """
        self._running = True

        # Ensure all sensor seams exist with defaults
        await self._ensure_seams_exist()

        # Read capabilities for announce
        capabilities_dict = await self.store.get(self.component_id, "sensor", "capabilities")
        # Filter out stateSchemaId before passing to Pydantic model
        caps_data = {k: v for k, v in capabilities_dict.items() if k != "stateSchemaId"}
        capabilities = SensorCapabilities(**caps_data)

        # Announce on start
        await self.announce(
            service_role="sensor",
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
            instrument="sensor",
        )

        # Start the router (for PollingBusRouter, this starts polling tasks)
        if hasattr(self.router, "start"):
            await self.router.start()

        if self.log:
            self.log.info(f"SensorService {self.component_id} started")

    async def _ensure_seams_exist(self) -> None:
        """Ensure all sensor seams exist with defaults."""
        attributes = [
            "meta",
            "state",
            "value",
            "scaling",
            "capabilities",
            "cmd",
        ]

        for attribute in attributes:
            try:
                # Try to read existing seam
                await self.store.get(self.component_id, "sensor", attribute)
            except (KeyError, Exception):
                # Seam doesn't exist, write defaults
                defaults = load_defaults(attribute)
                await self.store.set(
                    self.component_id,
                    "sensor",
                    attribute,
                    defaults,
                )

                if self.log:
                    self.log.debug(f"Created default sensor.{attribute} seam")

    async def _handle_command_request(self, request: CommandRequest) -> CommandReply:
        """Handle CommandRequest envelope from BusRouter.

        This is the entry point after idempotency checks.
        Validates contract version, capabilities, and behavioral rules.

        Args:
            request: CommandRequest envelope

        Returns:
            CommandReply envelope (accepted or rejected)
        """
        # Validate contract version
        try:
            # Parse expected major version from self.contract_version
            expected_major = int(self.contract_version.split(".")[0])
            validate_contract_version(
                expected_major=expected_major,
                provided=request.expected_version,
            )
        except SchemaValidationError as e:
            if self.log:
                self.log.warning(f"Contract mismatch for {request.command_id}: {e}")
            reply = await self._create_reply(
                request,
                accepted=False,
                reason=str(e),
            )
            await self.emit_state_event()
            return reply

        # Read current capabilities and state for validation
        try:
            capabilities_dict = await self.store.get(self.component_id, "sensor", "capabilities")
            # Filter out stateSchemaId before passing to Pydantic model
            caps_data = {k: v for k, v in capabilities_dict.items() if k != "stateSchemaId"}
            capabilities = SensorCapabilities(**caps_data)

            state_dict = await self.store.get(self.component_id, "sensor", "state")
            # Filter out stateSchemaId before passing to Pydantic model
            state_data = {k: v for k, v in state_dict.items() if k != "stateSchemaId"}
            state = SensorState(**state_data)
        except Exception as e:
            if self.log:
                self.log.error(f"Failed to read sensor seams: {e}")
            reply = await self._create_reply(
                request,
                accepted=False,
                reason=f"Internal error reading seams: {str(e)}",
            )
            await self.emit_state_event()
            return reply

        # Validate command against capabilities and behavioral rules
        try:
            validate_sensor_command(request, capabilities, state)
        except CommandRejectedError as e:
            if self.log:
                self.log.warning(f"Command {request.command_id} rejected: {e.reason}")
            reply = await self._create_reply(
                request,
                accepted=False,
                reason=e.reason,
            )
            await self.emit_state_event()
            return reply

        # Update cmd seam with request details
        await self._update_cmd_seam(request)

        # Execute the command
        try:
            await self.handle_command(request)

            reply = await self._create_reply(
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
            reply = await self._create_reply(
                request,
                accepted=False,
                reason=f"Execution error: {str(e)}",
            )

        # Emit StateEvent after command processing
        await self.emit_state_event()

        return reply

    async def _update_cmd_seam(self, request: CommandRequest) -> None:
        """Update sensor.cmd seam with command request details.

        Args:
            request: CommandRequest envelope
        """
        cmd_data = {
            "stateSchemaId": "procaaso.io/seams/sensor/cmd/v1",
            "command_id": request.command_id,
            "command": request.command,
            "args": request.args,
            "expected_version": request.expected_version,
            "source": request.source,
        }
        await self.store.set(self.component_id, "sensor", "cmd", cmd_data)

        if self.log:
            self.log.debug(f"Updated cmd seam: {request.command} ({request.command_id})")

    async def _create_reply(
        self,
        request: CommandRequest,
        accepted: bool,
        reason: str,
    ) -> CommandReply:
        """Create CommandReply envelope.

        Args:
            request: CommandRequest
            accepted: Whether command was accepted
            reason: Reason for acceptance/rejection

        Returns:
            CommandReply envelope
        """
        # Read current state for resulting_state field
        try:
            state_dict = await self.store.get(self.component_id, "sensor", "state")
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

        return reply

    async def handle_command(self, request: CommandRequest) -> None:
        """Execute command logic - override in subclasses for hardware control.

        Default implementation logs command. Subclasses should:
        - Implement hardware-specific control logic
        - Update value seam via update_value()
        - Update state seam via update_state() as needed

        Args:
            request: CommandRequest envelope
        """
        if self.log:
            self.log.info(f"Executing command: {request.command} with args: {request.args}")

        # Example subclass implementation:
        # if request.command == "Zero":
        #     await self.hw.zero_sensor()
        #     await self.update_state(faulted=False, fault_code=0, fault_text="")
        # elif request.command == "Tare":
        #     offset = request.args[0].get("offset", 0.0) if request.args else 0.0
        #     await self.hw.tare(offset)
        # elif request.command == "ResetFault":
        #     await self.update_state(faulted=False, fault_code=0, fault_text="", lifecycle_state="Online")

    async def update_value(self, **kwargs) -> None:
        """Update sensor.value seam fields.

        Args:
            **kwargs: Value fields to update (pv, raw, percent, quality, ts)
        """
        updated = await self.store.update_fields(
            self.component_id,
            "sensor",
            "value",
            **kwargs,
        )

        if self.log:
            self.log.debug(f"Updated value: {kwargs}")

    async def update_state(self, **kwargs) -> None:
        """Update sensor.state seam fields.

        Args:
            **kwargs: State fields to update (lifecycle_state, faulted, etc.)
        """
        updated = await self.store.update_fields(
            self.component_id,
            "sensor",
            "state",
            **kwargs,
        )

        if self.log:
            self.log.debug(f"Updated state: {kwargs}")
