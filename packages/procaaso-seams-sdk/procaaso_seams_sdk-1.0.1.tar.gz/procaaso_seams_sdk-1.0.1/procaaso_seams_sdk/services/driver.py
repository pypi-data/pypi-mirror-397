"""
Services driver module.

Implements DriverService for I/O hardware drivers (spec §7).
A driver fronts a single piece of I/O hardware and hosts multiple Sensor/Actuator channels.
"""

from datetime import datetime
from typing import Any, Dict, Literal, Optional

from ..bus.client import BusClient
from ..bus.envelopes import CommandReply, CommandRequest
from ..bus.router import BusRouter
from ..logging.errors import CommandRejectedError, SchemaValidationError
from ..seams.models import DriverCapabilities, DriverCmd, DriverState, load_defaults
from ..seams.store import SeamStore
from ..seams.validators import validate_contract_version, validate_driver_command
from .base import BaseService


class DriverService(BaseService):
    """Driver service implementing full Driver Contract (spec §7).

    A driver is a containerized service that fronts a single piece of I/O hardware
    (8-channel, 16-channel, etc.) and hosts multiple Sensor and/or Actuator Contract
    instances. The driver provides driver-level health, inventory, and rescan/reset
    behaviors without leaking raw hardware details.

    Responsibilities:
    1. On start():
       - Ensure driver seams exist in Store (write defaults if missing)
       - Publish Announce + initial StateEvent via BusClient
    2. Register with BusRouter so CommandRequests are received from sidecar stream
    3. Maintain channel registry (_channels) and mirror to inventory seam
    4. Validate requests against capabilities and spec behavioral rules (spec §7.5)
    5. If accepted:
       - Write driver.cmd seam via SeamStore (remote-first)
       - Update driver.state and driver.inventory as needed
       - Call orchestration hook handle_driver_command()
    6. Always emit CommandReply via bus.publish_reply()
    7. After accepted/refused commands, emit StateEvent

    Standard Driver Commands (spec §7.4):
    - ResetDriver: Reset driver to initial state
    - RescanChannels: Refresh channel inventory
    - ResetFault: Clear fault condition

    Uses SeamStore for all reads/writes (remote-first via sidecar).
    BusRouter handles idempotency; service focuses on validation and channel management.

    Integration assumptions:
    - Never expose raw I/O tags publicly
    - Publish per-channel Sensor/Actuator contracts instead
    - Keep IO backend abstract/injectable
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
        """Initialize driver service.

        Args:
            component_id: Unique driver identifier (driver_id)
            bus: BusClient for sidecar communication
            store: SeamStore for reading/writing seams
            router: BusRouter for command dispatching
            log: Logger instance
            contract_version: Driver contract version
        """
        super().__init__(
            component_id=component_id,
            bus=bus,
            store=store,
            log=log,
            contract="Driver",
            contract_version=contract_version,
        )
        self.router = router

        # Internal channel registry: dict[channel_id, channel_info]
        # This is the authoritative source, mirrored to inventory.channels seam
        self._channels: Dict[str, Dict[str, Any]] = {}

    async def start(self) -> None:
        """Start the driver service.

        1. Ensure driver seams exist (write defaults if missing)
        2. Publish Announce
        3. Emit initial StateEvent
        4. Register with BusRouter
        """
        self._running = True

        # Ensure all driver seams exist with defaults
        await self._ensure_seams_exist()

        # Load capabilities for announce
        capabilities_dict = await self.store.get(self.component_id, "driver", "capabilities")
        caps_data = {k: v for k, v in capabilities_dict.items() if k != "stateSchemaId"}
        capabilities = DriverCapabilities(**caps_data)

        # Announce on start
        await self.announce(
            service_role="driver",
            capabilities=[],  # Driver capabilities are in driver.capabilities seam
            config_hash="",  # TODO: Calculate from config
            health="OK",
        )

        # Emit initial StateEvent
        await self.emit_state_event()

        # Register with BusRouter to receive commands from sidecar stream
        self.router.register_handler(
            component_id=self.component_id,
            handler=self._handle_command_request,
            instrument="driver",
        )

        # Start the router (for PollingBusRouter, this starts polling tasks)
        if hasattr(self.router, "start"):
            await self.router.start()

        if self.log:
            self.log.info(f"DriverService {self.component_id} started")

    async def _ensure_seams_exist(self) -> None:
        """Ensure all driver seams exist with defaults."""
        attributes = [
            "meta",
            "state",
            "capabilities",
            "inventory",
            "intent",  # Optional but standardized
            "cmd",
        ]

        for attribute in attributes:
            try:
                # Try to read existing seam
                await self.store.get(self.component_id, "driver", attribute)
            except (KeyError, Exception):
                # Seam doesn't exist, write defaults
                defaults = load_defaults(attribute)
                await self.store.set(
                    self.component_id,
                    "driver",
                    attribute,
                    defaults,
                )
                if self.log:
                    self.log.info(
                        f"Initialized {self.component_id}.driver.{attribute} with defaults"
                    )

    async def _handle_command_request(self, request: CommandRequest) -> CommandReply:
        """Handle incoming CommandRequest from BusRouter.

        BusRouter handles:
        - Idempotency checking
        - Reply publishing
        - Error handling

        This handler focuses on:
        - Version validation
        - Behavioral rule validation (spec §7.5)
        - Command execution
        - Seam updates

        Args:
            request: CommandRequest envelope (already decoded by BusRouter)

        Returns:
            CommandReply envelope
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
            reply = await self._create_reply(
                request,
                accepted=False,
                reason=f"Version mismatch: {e.validation_error}",
            )
            await self.emit_state_event()
            return reply

        # Read capabilities and current state
        try:
            capabilities_dict = await self.store.get(self.component_id, "driver", "capabilities")
            caps_data = {k: v for k, v in capabilities_dict.items() if k != "stateSchemaId"}
            capabilities = DriverCapabilities(**caps_data)

            state_dict = await self.store.get(self.component_id, "driver", "state")
            state_data = {k: v for k, v in state_dict.items() if k != "stateSchemaId"}
            current_state = DriverState(**state_data)
        except Exception as e:
            if self.log:
                self.log.error(f"Failed to read seams: {e}")
            reply = await self._create_reply(
                request,
                accepted=False,
                reason=f"Internal error reading seams: {str(e)}",
            )
            await self.emit_state_event()
            return reply

        # Validate command against capabilities and behavioral rules (spec §7.5)
        try:
            validate_driver_command(request, capabilities, current_state)
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
            await self.handle_driver_command(request)

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
        """Update driver.cmd seam with command request details.

        Args:
            request: CommandRequest envelope
        """
        cmd_data = {
            "stateSchemaId": "procaaso.io/seams/driver/cmd/v1",
            "command_id": request.command_id,
            "command": request.command,
            "args": request.args,
            "expected_version": request.expected_version,
            "source": request.source,
        }
        await self.store.set(self.component_id, "driver", "cmd", cmd_data)

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
            state_dict = await self.store.get(self.component_id, "driver", "state")
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

    async def handle_driver_command(self, request: CommandRequest) -> None:
        """Execute driver command logic - override in subclasses for hardware logic.

        Default implementation logs command. Subclasses should:
        - Implement hardware-specific driver control logic
        - Update state via update_state()
        - Update inventory via update_inventory() or channel registry helpers

        Standard Driver Commands (spec §7.4):
        - ResetDriver: Reset driver to initial state
        - RescanChannels: Refresh channel inventory from hardware
        - ResetFault: Clear fault condition

        Args:
            request: CommandRequest envelope
        """
        if self.log:
            self.log.info(f"Executing driver command: {request.command} with args: {request.args}")

        # Example subclass implementation:
        # if request.command == "ResetDriver":
        #     await self.hw.reset_driver()
        #     await self.update_state(
        #         lifecycle_state="Online",
        #         comms_ok=True,
        #         fault_code=0,
        #         fault_text=""
        #     )
        #     self._channels.clear()
        #     await self._sync_inventory_to_store()
        #
        # elif request.command == "RescanChannels":
        #     channels = await self.hw.scan_channels()
        #     for ch in channels:
        #         self.register_channel(
        #             channel_id=ch["id"],
        #             entity_type=ch["type"],
        #             status="Online"
        #         )
        #     await self._sync_inventory_to_store()
        #
        # elif request.command == "ResetFault":
        #     await self.update_state(
        #         lifecycle_state="Online",
        #         fault_code=0,
        #         fault_text=""
        #     )

    async def update_state(self, **kwargs) -> None:
        """Update driver.state seam fields.

        Args:
            **kwargs: State fields to update (lifecycle_state, comms_ok, fault_code, fault_text, scan_rate_ms)
        """
        updated = await self.store.update_fields(
            self.component_id,
            "driver",
            "state",
            **kwargs,
        )

        if self.log:
            self.log.debug(f"Updated driver state: {kwargs}")

    # -------------------------------------------------------------------
    # Channel registry management
    # -------------------------------------------------------------------

    def register_channel(
        self,
        channel_id: str,
        entity_type: Literal["Sensor", "Actuator"],
        bound_entity_id: Optional[str] = None,
        status: str = "Online",
    ) -> None:
        """Register a channel in the internal registry.

        This updates the in-memory _channels registry.
        Call _sync_inventory_to_store() after all changes to persist.

        Args:
            channel_id: Channel identifier (e.g., "ch0", "ai_0")
            entity_type: "Sensor" or "Actuator"
            bound_entity_id: Entity ID if bound (sensor_id or actuator_id)
            status: Channel status (e.g., "Online", "Offline", "Faulted")
        """
        self._channels[channel_id] = {
            "channel": channel_id,
            "entity_type": entity_type,
            "bound_entity_id": bound_entity_id or "",
            "status": status,
        }

        if self.log:
            self.log.info(
                f"Registered channel {channel_id}: type={entity_type}, "
                f"bound={bound_entity_id}, status={status}"
            )

    def bind_entity(
        self,
        channel_id: str,
        entity_type: Literal["Sensor", "Actuator"],
        entity_id: str,
    ) -> None:
        """Bind a sensor or actuator entity to a channel.

        Args:
            channel_id: Channel identifier
            entity_type: "Sensor" or "Actuator"
            entity_id: Entity ID to bind (sensor_id or actuator_id)

        Raises:
            KeyError: If channel_id not registered
        """
        if channel_id not in self._channels:
            raise KeyError(f"Channel {channel_id} not registered")

        self._channels[channel_id]["bound_entity_id"] = entity_id
        self._channels[channel_id]["entity_type"] = entity_type

        if self.log:
            self.log.info(f"Bound {entity_type} {entity_id} to channel {channel_id}")

    def unregister_channel(self, channel_id: str) -> None:
        """Unregister a channel from the registry.

        Args:
            channel_id: Channel identifier
        """
        if channel_id in self._channels:
            del self._channels[channel_id]

            if self.log:
                self.log.info(f"Unregistered channel {channel_id}")

    def list_channels(self) -> list:
        """Get list of all registered channels.

        Returns:
            List of channel dicts (runtime list, not YAML format)
        """
        return list(self._channels.values())

    async def _sync_inventory_to_store(self) -> None:
        """Sync internal _channels registry to driver.inventory seam.

        Call this after any channel registry changes to persist to store.
        """
        inventory_data = {
            "stateSchemaId": "procaaso.io/seams/driver/inventory.v1",
            "channels": list(self._channels.values()),
        }

        await self.store.set(self.component_id, "driver", "inventory", inventory_data)

        if self.log:
            self.log.debug(f"Synced inventory: {len(self._channels)} channels to driver.inventory")

    # -------------------------------------------------------------------
    # Optional child hosting hooks (for future expansion)
    # -------------------------------------------------------------------

    async def spawn_children(self) -> None:
        """Spawn per-channel SensorService/ActuatorService instances.

        TODO: Implement in future version to create child services
        for each channel in inventory based on entity_type.

        Each child would:
        - Create SensorService or ActuatorService
        - Bind to channel's bound_entity_id
        - Register with bus router
        - Maintain per-channel seams
        """
        # Future implementation
        pass

    async def stop_children(self) -> None:
        """Stop all child SensorService/ActuatorService instances.

        TODO: Implement in future version to gracefully shutdown
        child services when driver stops.
        """
        # Future implementation
        pass
