"""
Services unit module.

Implements UnitService for APP/brain containers (ISA-88 aligned).
Orchestrates actuators and sensors ONLY through seam contracts.

ISA-88 Unit Procedure State Machine (spec §6.3):
=================================================

    Idle ──Start──> Running ──Complete──> Complete
                      │   │                   │
                      │   └──Stop──> Stopped  │
                      │                       │
                      ├──Pause──> Pausing ──> Paused ──Resume──> Restarting ──┐
                      │                                                        │
                      ├──Hold──> Holding ──> Held ──Restart──> Restarting ────┤
                      │                                                        │
                      └──Abort──> Aborting ──> Aborted                        │
                                                                               │
    Faulted ──Reset──> Idle                                         Running <─┘

Terminal States: Complete, Stopped, Aborted (require Reset to return to Idle)
Fault: Any state can transition to Faulted on equipment fault

ISA-88 Standard Commands (spec §6.3):
- Start: Begin procedure execution (Idle → Running)
- Pause: Pause at safe point (Running → Pausing → Paused)
- Resume: Resume from paused (Paused → Restarting → Running)
- Hold: Hold for external condition (Running → Holding → Held)
- Restart: Restart from held (Held → Restarting → Running)
- Stop: Controlled termination (Running/Paused/Held → Stopping → Stopped)
- Abort: Emergency termination (Any → Aborting → Aborted)
- Reset: Clear faults and return to Idle (Faulted/Complete/Stopped/Aborted → Idle)
"""

from datetime import datetime
from typing import Any, Dict, Optional

from ..bus.client import BusClient
from ..bus.envelopes import CommandReply, CommandRequest
from ..bus.router import BusRouter
from ..logging.errors import CommandRejectedError, SchemaValidationError
from ..seams.models import UnitCmd, UnitIntent, UnitState, UnitWaitingOn, load_defaults
from ..seams.store import SeamStore
from ..seams.validators import validate_contract_version, validate_unit_command
from .base import BaseService


class UnitService(BaseService):
    """Unit service implementing ISA-88 Unit Contract (spec §6.3).

    ISA-88 State Model:
    - Idle → Running → Complete/Stopped/Aborted
    - Running ⇔ Pausing ⇔ Paused ⇔ Restarting → Running
    - Running ⇔ Holding ⇔ Held ⇔ Restarting → Running
    - Any → Stopping → Stopped
    - Any → Aborting → Aborted
    - Faulted/Complete/Stopped/Aborted → Reset → Idle

    Responsibilities:
    1. On start():
       - Ensure unit seams exist in Store (write defaults if missing)
       - Publish Announce + initial StateEvent via BusClient
    2. Register with BusRouter so CommandRequests are received from sidecar stream
    3. Validate requests against S88 state machine rules
    4. If accepted:
       - Write unit.cmd seam via SeamStore (remote-first)
       - Update unit.state (lifecycle_state, procedure_status, current_step)
       - Update unit.intent (recipe_id, procedure_id, operation_id, phase_id)
       - Update unit.waiting_on (reasons for Holding/Held states)
       - Call orchestration hooks that interact ONLY through seams:
         * Read sensors via SeamStore.get(...)
         * Issue actuator commands by writing actuator.cmd seam or BusClient.request(...)
    5. Always emit CommandReply via bus.publish_reply()
    6. After accepted/refused commands and lifecycle transitions, emit StateEvent

    Uses SeamStore for all reads/writes (remote-first via sidecar).
    BusRouter handles idempotency; service focuses on validation and orchestration.

    Integration assumptions:
    - Never call hardware directly
    - Never invent seams/fields
    - Async everywhere bus/seam IO is involved
    - Leave TODO hooks for recipe/phase engines
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
        """Initialize unit service.

        Args:
            component_id: Unique unit identifier
            bus: BusClient for sidecar communication
            store: SeamStore for reading/writing seams
            router: BusRouter for command dispatching
            log: Logger instance
            contract_version: Unit contract version
        """
        super().__init__(
            component_id=component_id,
            bus=bus,
            store=store,
            log=log,
            contract="Unit",
            contract_version=contract_version,
        )
        self.router = router

    async def start(self) -> None:
        """Start the unit service.

        1. Ensure unit seams exist (write defaults if missing)
        2. Publish Announce
        3. Emit initial StateEvent
        4. Register with BusRouter
        """
        self._running = True

        # Ensure all unit seams exist with defaults
        await self._ensure_seams_exist()

        # Announce on start (no capabilities for units per spec)
        await self.announce(
            service_role="unit",
            capabilities=[],  # Units don't expose capabilities in same way
            config_hash="",  # TODO: Calculate from config
            health="OK",
        )

        # Emit initial StateEvent
        await self.emit_state_event()

        # Register with BusRouter to receive commands from sidecar stream
        self.router.register_handler(
            component_id=self.component_id,
            handler=self._handle_command_request,
            instrument="unit",  # Poll unit.cmd instead of actuator.cmd
        )

        # Start the router (for PollingBusRouter, this starts polling tasks)
        if hasattr(self.router, "start"):
            await self.router.start()

        if self.log:
            self.log.info(f"UnitService {self.component_id} started")

    async def _ensure_seams_exist(self) -> None:
        """Ensure all unit seams exist with defaults."""
        attributes = [
            "meta",
            "state",
            "intent",
            "waiting_on",
            "cmd",
            "outcome",  # Optional but standardized
        ]

        for attribute in attributes:
            # Try to read existing seam
            existing = await self.store.get(self.component_id, "unit", attribute)

            # Check if seam exists (get_seam returns {} for 404)
            if existing:
                if self.log:
                    self.log.debug(f"Seam {self.component_id}.unit.{attribute} already exists")
                continue

            # Seam doesn't exist, write defaults
            if self.log:
                self.log.debug(
                    f"Seam {self.component_id}.unit.{attribute} not found, initializing..."
                )

            defaults = load_defaults(attribute)
            if self.log:
                self.log.debug(f"Loaded defaults for {attribute}: {defaults}")

            if not defaults:
                if self.log:
                    self.log.error(f"No defaults found for {attribute}! Skipping...")
                continue

            try:
                await self.store.set(
                    self.component_id,
                    "unit",
                    attribute,
                    defaults,
                )
                if self.log:
                    self.log.info(
                        f"✓ Initialized {self.component_id}.unit.{attribute} with defaults"
                    )
            except Exception as set_error:
                if self.log:
                    self.log.error(f"Failed to set {attribute}: {set_error}")

    async def _handle_command_request(self, request: CommandRequest) -> CommandReply:
        """Handle incoming CommandRequest from BusRouter.

        BusRouter handles:
        - Idempotency checking
        - Reply publishing
        - Error handling

        This handler focuses on:
        - Version validation
        - Behavioral rule validation (spec §6.4)
        - Command execution
        - Seam updates
        - Orchestration hooks

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

        # Read current state, intent, and waiting_on
        try:
            state_dict = await self.store.get(self.component_id, "unit", "state")
            state_data = {k: v for k, v in state_dict.items() if k != "stateSchemaId"}
            state = UnitState(**state_data)

            intent_dict = await self.store.get(self.component_id, "unit", "intent")
            intent_data = {k: v for k, v in intent_dict.items() if k != "stateSchemaId"}
            intent = UnitIntent(**intent_data)

            waiting_dict = await self.store.get(self.component_id, "unit", "waiting_on")
            waiting_data = {k: v for k, v in waiting_dict.items() if k != "stateSchemaId"}
            current_waiting_on = UnitWaitingOn(**waiting_data)
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

        # Validate command against behavioral rules (spec §6.4)
        try:
            validate_unit_command(request, state, intent, current_waiting_on)
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
        """Update unit.cmd seam with command request details.

        Args:
            request: CommandRequest envelope
        """
        cmd_data = {
            "stateSchemaId": "procaaso.io/seams/unit/cmd/v1",
            "command_id": request.command_id,
            "command": request.command,
            "args": request.args,
            "expected_version": request.expected_version,
            "source": request.source,
        }
        await self.store.set(self.component_id, "unit", "cmd", cmd_data)

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
            state_dict = await self.store.get(self.component_id, "unit", "state")
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
        """Execute command logic - override in subclasses for orchestration logic.

        Default implementation logs command. Subclasses should:
        - Implement recipe/phase orchestration logic
        - Read sensors via self.store.get(sensor_id, "sensor", "value")
        - Issue actuator commands via self.store.set(actuator_id, "actuator", "cmd", ...)
          or via self.bus.request(...)
        - Update intent via update_intent()
        - Update state via update_state()
        - Update waiting_on via update_waiting_on()

        ISA-88 Commands (spec §6.3):
        - Start: Begin procedure execution (Idle → Running)
        - Pause: Pause at safe point (Running → Pausing → Paused)
        - Resume: Resume from paused (Paused → Restarting → Running)
        - Hold: Hold for condition (Running → Holding → Held)
        - Restart: Restart from held (Held → Restarting → Running)
        - Stop: Controlled stop (Running/Paused/Held → Stopping → Stopped)
        - Abort: Emergency stop (Any → Aborting → Aborted)
        - Reset: Clear and return to Idle (Faulted/Complete/Stopped/Aborted → Idle)

        Args:
            request: CommandRequest envelope
        """
        if self.log:
            self.log.info(f"Executing ISA-88 command: {request.command} with args: {request.args}")

        # Subclasses should implement this method to handle Unit-specific commands.
        #
        # ISA-88 Standard Commands (required):
        # - Start: Transition from Idle to Running, load recipe context
        # - Pause/Resume: Pause execution at safe point, resume
        # - Hold/Restart: Hold for external condition, restart when ready
        # - Stop: Controlled shutdown (Running → Stopped)
        # - Abort: Emergency shutdown (Any → Aborted)
        # - Reset: Clear state and return to Idle
        #
        # Phase Execution Command (APP-to-Unit coordination):
        # - ExecutePhase: Execute a specific phase with parameters
        #   Example: {"phase_name": "Prime", "parameters": {"duration": 30}}
        #
        # Example subclass implementation:
        #
        # if request.command == "Start":
        #     # Update intent with recipe hierarchy
        #     await self.update_intent(
        #         batch_id=params.get("batch_id"),
        #         recipe_id=params.get("recipe_id"),
        #         procedure_id=params.get("procedure_id"),
        #         operation_id=params.get("operation_id"),
        #     )
        #     # Transition to Running
        #     await self.update_state(
        #         lifecycle_state="Running",
        #         procedure_status="executing",
        #     )
        #
        # elif request.command == "ExecutePhase":
        #     # Unit owns equipment and executes phase logic
        #     phase_name = params.get("phase_name")
        #     phase_params = params.get("parameters", {})
        #
        #     # Update current phase in intent
        #     await self.update_intent(phase_id=phase_name)
        #
        #     # Execute phase with owned equipment
        #     if phase_name == "Prime":
        #         await self._execute_prime_phase(phase_params)
        #     # ... etc for other phases
        #
        # See examples/tff_unit.py for complete implementation

    async def update_state(self, **kwargs) -> None:
        """Update unit.state seam fields.

        S88 State Fields:
        - lifecycle_state: Current S88 procedure state
        - procedure_status: Procedure execution status
        - current_step: Current operation/phase being executed
        - step_index: Numeric step position in sequence
        - faulted, fault_code, fault_text: Fault information

        Args:
            **kwargs: State fields to update
        """
        updated = await self.store.update_fields(
            self.component_id,
            "unit",
            "state",
            **kwargs,
        )

        if self.log:
            self.log.debug(f"Updated S88 state: {kwargs}")

    async def update_intent(self, **kwargs) -> None:
        """Update unit.intent seam fields.

        S88 Hierarchy Fields:
        - recipe_id: Top-level recipe identifier
        - procedure_id: Unit procedure within recipe
        - operation_id: Operation within procedure
        - phase_id: Phase within operation (smallest unit)
        - targets: Setpoints and parameters for execution

        Args:
            **kwargs: Intent fields to update
        """
        updated = await self.store.update_fields(
            self.component_id,
            "unit",
            "intent",
            **kwargs,
        )

        if self.log:
            self.log.debug(f"Updated S88 intent: {kwargs}")

    async def update_waiting_on(self, **kwargs) -> None:
        """Update unit.waiting_on seam fields.

        Args:
            **kwargs: waiting_on fields to update (reasons)
        """
        updated = await self.store.update_fields(
            self.component_id,
            "unit",
            "waiting_on",
            **kwargs,
        )

        if self.log:
            self.log.debug(f"Updated waiting_on: {kwargs}")

    async def update_outcome(self, **kwargs) -> None:
        """Update unit.outcome seam fields.

        Args:
            **kwargs: Outcome fields to update (success, completion_ts, metrics)
        """
        updated = await self.store.update_fields(
            self.component_id,
            "unit",
            "outcome",
            **kwargs,
        )

        if self.log:
            self.log.debug(f"Updated outcome: {kwargs}")

    # -------------------------------------------------------------------
    # Equipment coordination helper methods (for Unit subclasses)
    # -------------------------------------------------------------------

    async def read_sensor_value(self, sensor_id: str) -> Dict[str, Any]:
        """Read sensor value seam.

        Args:
            sensor_id: Sensor component ID

        Returns:
            Sensor value dictionary
        """
        value_dict = await self.store.get(sensor_id, "sensor", "value")
        return {k: v for k, v in value_dict.items() if k != "stateSchemaId"}

    async def issue_actuator_command(
        self,
        actuator_id: str,
        command: str,
        args: Optional[list] = None,
    ) -> None:
        """Issue command to actuator by writing actuator.cmd seam.

        Args:
            actuator_id: Actuator component ID
            command: Command name (Start, Stop, Setpoint, etc.)
            args: Command arguments (list of dicts)
        """
        import uuid

        cmd_data = {
            "stateSchemaId": "procaaso.io/seams/actuator/cmd/v1",
            "command_id": str(uuid.uuid4()),
            "command": command,
            "args": args or [],
            "expected_version": "1.0.0",
            "source": self.component_id,
        }

        await self.store.set(actuator_id, "actuator", "cmd", cmd_data)

        if self.log:
            self.log.info(f"Issued {command} to {actuator_id}")

        # Note: For proper request/reply pattern, could use BusClient.request():
        # reply = await self.bus.request(
        #     target_id=actuator_id,
        #     contract="Actuator",
        #     command=command,
        #     args=args or [],
        # )

    # -------------------------------------------------------------------
    # Phase Execution Pattern (Implement in Subclasses)
    # -------------------------------------------------------------------
    #
    # Units should implement phase execution methods that:
    # 1. Own their equipment (connect to ActuatorClient/SensorClient in start())
    # 2. Execute phase logic with owned equipment
    # 3. Implement safety checks and interlocks
    # 4. Return when phase completes
    #
    # Example pattern:
    #
    # async def _execute_prime_phase(self, params: Dict[str, Any]) -> None:
    #     """Execute Prime phase: open valves, start pump at low speed."""
    #     duration = params.get("duration", 30)
    #     pump_speed = params.get("pump_speed", 20.0)
    #
    #     # Control owned equipment
    #     await self.feed_valve.send_command("Start")
    #     await self.pump.send_command("SetMode", {"mode": "Fixed"})
    #     await self.pump.send_command("Setpoint", {"value": pump_speed})
    #
    #     # Monitor with owned sensors
    #     while elapsed < duration:
    #         flow = await self.flow_sensor.get_value()
    #         # ... monitoring logic
    #
    # See examples/tff_unit.py for complete implementation of all phases.
    #
    # Architecture:
    # - APP (recipe controller) sends ExecutePhase commands
    # - Unit executes phase with its equipment
    # - Unit reports completion (or errors)
    # - APP orchestrates next phase based on recipe logic
