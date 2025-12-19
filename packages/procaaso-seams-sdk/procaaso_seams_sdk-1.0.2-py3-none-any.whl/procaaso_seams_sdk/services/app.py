"""
Services app module.

Implements APPService for recipe controllers and orchestration containers.
Receives commands from MES/HMI and coordinates Unit execution.

APP State Machine:
==================

    Idle ──LoadRecipe──> RecipeLoaded ──StartRecipe──> Running ──Complete──> Complete
                                                          │   │                   │
                                                          │   └──Stop──> Stopped  │
                                                          │                       │
                                                          ├──PauseRecipe──> Paused ──ResumeRecipe──┐
                                                          │                                         │
                                                          └──AbortRecipe──> Aborted                │
                                                                                                    │
    Faulted ──Reset──> Idle                                               Running <───────────────┘

Terminal States: Complete, Stopped, Aborted (require Reset to return to Idle)

APP Commands:
- LoadRecipe: Load and validate recipe (Idle → RecipeLoaded)
- StartRecipe: Begin recipe execution (RecipeLoaded → Running)
- PauseRecipe: Pause execution (Running → Paused)
- ResumeRecipe: Resume execution (Paused → Running)
- StopRecipe: Controlled termination (Running/Paused → Stopped)
- AbortRecipe: Emergency termination (Any → Aborted)
- Reset: Clear state and return to Idle (Faulted/Complete/Stopped/Aborted → Idle)
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from ..bus.client import BusClient
from ..bus.envelopes import CommandReply, CommandRequest
from ..bus.router import BusRouter
from ..logging.errors import CommandRejectedError, PreconditionFailed
from ..seams.store import SeamStore
from .base import BaseService

# APP lifecycle states
APPLifecycleState = Literal[
    "Idle", "RecipeLoaded", "Running", "Paused", "Complete", "Stopped", "Aborted", "Faulted"
]


class APPService(BaseService):
    """APP service for recipe orchestration and external command handling.

    Responsibilities:
    1. On start():
       - Ensure app seams exist (meta, state, cmd)
       - Publish Announce + initial StateEvent
    2. Register with BusRouter to receive CommandRequests from app.cmd seam
    3. Handle MES/HMI commands:
       - LoadRecipe: Validate recipe, check equipment availability
       - StartRecipe: Coordinate Unit(s) to execute recipe
       - PauseRecipe/ResumeRecipe: Pause/resume execution
       - StopRecipe: Controlled shutdown
       - AbortRecipe: Emergency stop
       - Reset: Return to Idle
    4. Coordinate with Unit services through unit.cmd seams
    5. Emit StateEvent on lifecycle transitions

    Integration with Units:
    - APP sends high-level commands to Unit (Start, ExecutePhase, Stop)
    - APP monitors Unit state through unit.state seam
    - APP orchestrates multiple Units if needed
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
        """Initialize APP service.

        Args:
            component_id: Unique APP identifier (e.g., "tff_recipe_controller")
            bus: BusClient for sidecar communication
            store: SeamStore for reading/writing seams
            router: BusRouter for command dispatching
            log: Logger instance
            contract_version: APP contract version
        """
        super().__init__(
            component_id=component_id,
            bus=bus,
            store=store,
            log=log,
            contract="APP",
            contract_version=contract_version,
        )
        self.router = router

        # APP state tracking
        self.current_state: APPLifecycleState = "Idle"
        self.loaded_recipe_id: str = ""
        self.loaded_batch_id: str = ""
        self.current_phase: str = ""

    async def start(self) -> None:
        """Start the APP service.

        1. Ensure app seams exist
        2. Publish Announce
        3. Emit initial StateEvent
        4. Register with BusRouter
        """
        self._running = True

        # Ensure all app seams exist with defaults
        await self._ensure_seams_exist()

        # Announce on start
        await self.announce(
            service_role="app",
            capabilities=["recipe_orchestration", "unit_coordination"],
            config_hash="",  # TODO: Calculate from config
            health="OK",
        )

        # Emit initial StateEvent
        await self.emit_state_event()

        # Register with BusRouter to receive commands from app.cmd seam
        self.router.register_handler(
            component_id=self.component_id,
            handler=self._handle_command_request,
            instrument="app",  # Poll app.cmd instead of actuator.cmd
        )

        # Start the router (for PollingBusRouter, starts polling tasks)
        if hasattr(self.router, "start"):
            await self.router.start()

    async def _ensure_seams_exist(self) -> None:
        """Ensure all app seams exist with proper defaults."""
        # Check if meta seam exists
        existing_meta = await self.store.get(self.component_id, "app", "meta")
        if not existing_meta:
            meta = {
                "app_id": self.component_id,
                "contract_version": self.contract_version,
                "name": "",
                "description": "",
            }
            await self.store.set(self.component_id, "app", "meta", meta)

        # Check if state seam exists
        existing_state = await self.store.get(self.component_id, "app", "state")
        if not existing_state:
            state = {
                "lifecycle_state": "Idle",
                "loaded_recipe_id": "",
                "loaded_batch_id": "",
                "current_phase": "",
                "faulted": False,
                "fault_text": "",
            }
            await self.store.set(self.component_id, "app", "state", state)

        # Check if cmd seam exists
        existing_cmd = await self.store.get(self.component_id, "app", "cmd")
        if not existing_cmd:
            cmd = {
                "command_id": "",
                "command": "",
                "args": [],
                "expected_version": self.contract_version,
                "source": "",
            }
            await self.store.set(self.component_id, "app", "cmd", cmd)

        if self.log:
            self.log.info(f"APP {self.component_id} seams initialized")

    async def _handle_command_request(self, request: CommandRequest) -> CommandReply:
        """Handle incoming command request from MES/HMI.

        Args:
            request: CommandRequest from app.cmd seam

        Returns:
            CommandReply envelope
        """
        # Validate command
        try:
            await self._validate_command(request)
        except (CommandRejectedError, PreconditionFailed) as e:
            if self.log:
                self.log.warning(f"Command rejected: {request.command} - {e}")
            reply = await self._create_reply(
                request,
                accepted=False,
                reason=str(e),
            )
            await self.emit_state_event()
            return reply

        # Execute command (subclass implements handle_command)
        try:
            await self.handle_command(request)

            if self.log:
                self.log.info(f"Command accepted: {request.command}")

            reply = await self._create_reply(
                request,
                accepted=True,
                reason="Command accepted and executed",
            )
        except Exception as e:
            if self.log:
                self.log.error(f"Command execution failed: {e}")

            # Transition to Faulted state
            await self.update_state(lifecycle_state="Faulted", fault_text=str(e))

            reply = await self._create_reply(
                request,
                accepted=False,
                reason=f"Execution error: {str(e)}",
            )

        # Emit state event
        await self.emit_state_event()

        return reply

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
            state_dict = await self.store.get(self.component_id, "app", "state")
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

    async def _validate_command(self, request: CommandRequest) -> None:
        """Validate APP command preconditions.

        Args:
            request: CommandRequest to validate

        Raises:
            CommandRejectedError: If command is invalid
            PreconditionFailed: If preconditions not met
        """
        cmd_type = request.command
        current_state = self.current_state

        # State transition rules
        valid_transitions = {
            "LoadRecipe": ["Idle"],
            "StartRecipe": ["RecipeLoaded"],
            "PauseRecipe": ["Running"],
            "ResumeRecipe": ["Paused"],
            "StopRecipe": ["Running", "Paused"],
            "AbortRecipe": ["Running", "Paused", "RecipeLoaded"],
            "Reset": ["Faulted", "Complete", "Stopped", "Aborted"],
        }

        if cmd_type in valid_transitions:
            if current_state not in valid_transitions[cmd_type]:
                raise PreconditionFailed(
                    command=cmd_type,
                    target_id=self.component_id,
                    precondition=f"{cmd_type} requires state in {valid_transitions[cmd_type]}, "
                    f"but current state is {current_state}",
                )

        # Command-specific validation
        if cmd_type == "LoadRecipe":
            params = request.args[0] if request.args else {}
            if not params.get("recipe_id"):
                raise CommandRejectedError(
                    command=cmd_type,
                    target_id=self.component_id,
                    reason="LoadRecipe requires recipe_id parameter",
                )

        elif cmd_type == "StartRecipe":
            if not self.loaded_recipe_id:
                raise PreconditionFailed(
                    command=cmd_type,
                    target_id=self.component_id,
                    precondition="StartRecipe requires a loaded recipe",
                )

    async def handle_command(self, request: CommandRequest) -> None:
        """Handle validated APP command.

        Subclasses should override this to implement specific command logic.

        Args:
            request: Validated CommandRequest
        """
        cmd_type = request.command
        params = request.args[0] if request.args else {}

        if cmd_type == "LoadRecipe":
            recipe_id = params.get("recipe_id", "")
            batch_id = params.get("batch_id", "")

            # Update state
            await self.update_state(
                lifecycle_state="RecipeLoaded",
                loaded_recipe_id=recipe_id,
                loaded_batch_id=batch_id,
            )

            if self.log:
                self.log.info(f"Recipe loaded: {recipe_id} for batch {batch_id}")

        elif cmd_type == "StartRecipe":
            # Update state
            await self.update_state(lifecycle_state="Running")

            if self.log:
                self.log.info(f"Starting recipe: {self.loaded_recipe_id}")

        elif cmd_type == "PauseRecipe":
            await self.update_state(lifecycle_state="Paused")

            if self.log:
                self.log.info("Recipe paused")

        elif cmd_type == "ResumeRecipe":
            await self.update_state(lifecycle_state="Running")

            if self.log:
                self.log.info("Recipe resumed")

        elif cmd_type == "StopRecipe":
            await self.update_state(lifecycle_state="Stopped")

            if self.log:
                self.log.info("Recipe stopped")

        elif cmd_type == "AbortRecipe":
            await self.update_state(lifecycle_state="Aborted")

            if self.log:
                self.log.warning("Recipe ABORTED")

        elif cmd_type == "Reset":
            await self.update_state(
                lifecycle_state="Idle",
                loaded_recipe_id="",
                loaded_batch_id="",
                current_phase="",
                faulted=False,
                fault_text="",
            )

            if self.log:
                self.log.info("APP reset to Idle")

    async def update_state(self, **kwargs) -> None:
        """Update APP state seam.

        Args:
            **kwargs: State fields to update (lifecycle_state, loaded_recipe_id, etc.)
        """
        # Read current state
        state = await self.store.get(self.component_id, "app", "state")

        # Update fields
        for key, value in kwargs.items():
            state[key] = value
            # Also update internal tracking
            if key == "lifecycle_state":
                self.current_state = value
            elif key == "loaded_recipe_id":
                self.loaded_recipe_id = value
            elif key == "loaded_batch_id":
                self.loaded_batch_id = value
            elif key == "current_phase":
                self.current_phase = value

        # Write back
        await self.store.set(self.component_id, "app", "state", state)

        # Emit state event
        await self.emit_state_event()

    async def emit_state_event(self) -> None:
        """Emit APP StateEvent to bus."""
        state = await self.store.get(self.component_id, "app", "state")

        # TODO: Implement StateEvent emission through bus
        # For now, just log
        if self.log:
            self.log.debug(f"APP state: {state.get('lifecycle_state', 'Unknown')}")
