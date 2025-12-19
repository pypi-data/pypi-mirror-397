"""
SEAMS validators module.

Provides validation functionality for SEAMS data per:
- specs/Procaaso_Seam_Interface_Spec_v1.0.md
- specs/seams_models_v1.yaml

All validators are pure functions (no IO).
"""

from typing import Optional

from ..bus.envelopes import CommandRequest
from ..logging.errors import (
    CommandRejectedError,
    PreconditionFailed,
    SchemaValidationError,
    UnsupportedCommand,
)
from .models import (
    ActuatorCapabilities,
    ActuatorState,
    DriverCapabilities,
    DriverState,
    SensorCapabilities,
    SensorState,
    UnitIntent,
    UnitState,
    UnitWaitingOn,
)


def validate_actuator_command(
    request: CommandRequest,
    capabilities: ActuatorCapabilities,
    current_state: ActuatorState,
) -> None:
    """Validate actuator command against capabilities and behavioral rules.

    Enforces spec §4.4 behavioral rules:
    - If lifecycle_state == Faulted, only ResetFault is accepted
    - Setpoint valid only when op_mode in {Fixed, Ramp, PID_Control}
    - Commands must be in supported_commands
    - SetMode only to supported_modes

    Args:
        request: CommandRequest to validate
        capabilities: Actuator capabilities seam
        current_state: Current actuator state seam

    Raises:
        UnsupportedCommand: If command not in supported_commands
        PreconditionFailed: If behavioral rules violated

    This is a pure function with no IO.
    """
    command = request.command
    target_id = request.target_id
    command_id = request.command_id

    # Rule 1: Command must be in supported_commands (spec §4.4)
    if command not in capabilities.supported_commands:
        raise UnsupportedCommand(
            command=command,
            target_id=target_id,
            supported_commands=capabilities.supported_commands,
            command_id=command_id,
        )

    # Rule 2: If Faulted, only ResetFault accepted (spec §4.4)
    if current_state.lifecycle_state == "Faulted" and command != "ResetFault":
        raise PreconditionFailed(
            command=command,
            target_id=target_id,
            precondition=f"lifecycle_state is Faulted, only ResetFault allowed",
            current_state={
                "lifecycle_state": current_state.lifecycle_state,
                "faulted": current_state.faulted,
                "fault_code": current_state.fault_code,
                "fault_text": current_state.fault_text,
            },
            command_id=command_id,
        )

    # Rule 3: Setpoint valid only when op_mode in {Fixed, Ramp, PID_Control} (spec §4.4)
    if command == "Setpoint":
        valid_modes = {"Fixed", "Ramp", "PID_Control"}
        if current_state.op_mode not in valid_modes:
            raise PreconditionFailed(
                command=command,
                target_id=target_id,
                precondition=f"Setpoint requires op_mode in {valid_modes}, current: {current_state.op_mode}",
                current_state={"op_mode": current_state.op_mode},
                command_id=command_id,
            )

    # Rule 4: SetMode must specify a mode in supported_modes
    if command == "SetMode":
        # Extract requested mode from args
        if not request.args or len(request.args) == 0:
            raise PreconditionFailed(
                command=command,
                target_id=target_id,
                precondition="SetMode requires args with 'mode' field",
                command_id=command_id,
            )

        requested_mode = request.args[0].get("mode")
        if not requested_mode:
            raise PreconditionFailed(
                command=command,
                target_id=target_id,
                precondition="SetMode requires 'mode' in args[0]",
                command_id=command_id,
            )

        # Mode must be in supported_modes
        if requested_mode not in capabilities.supported_modes:
            raise PreconditionFailed(
                command=command,
                target_id=target_id,
                precondition=f"Requested mode '{requested_mode}' not in supported_modes: {capabilities.supported_modes}",
                command_id=command_id,
            )


def validate_sensor_command(
    request: CommandRequest,
    capabilities: SensorCapabilities,
    current_state: SensorState,
) -> None:
    """Validate sensor command against capabilities and behavioral rules.

    Enforces spec behavioral rules:
    - If faulted == True, only ResetFault/Reset accepted
    - Commands must be in supported_commands

    Args:
        request: CommandRequest to validate
        capabilities: Sensor capabilities seam
        current_state: Current sensor state seam

    Raises:
        UnsupportedCommand: If command not in supported_commands
        PreconditionFailed: If behavioral rules violated

    This is a pure function with no IO.
    """
    command = request.command
    target_id = request.target_id
    command_id = request.command_id

    # Rule 1: Command must be in supported_commands
    if command not in capabilities.supported_commands:
        raise UnsupportedCommand(
            command=command,
            target_id=target_id,
            supported_commands=capabilities.supported_commands,
            command_id=command_id,
        )

    # Rule 2: If Faulted, only ResetFault/Reset accepted
    if current_state.faulted and command not in ["ResetFault", "Reset"]:
        raise PreconditionFailed(
            command=command,
            target_id=target_id,
            precondition=f"Sensor is faulted, only ResetFault or Reset allowed",
            current_state={
                "faulted": current_state.faulted,
                "fault_code": current_state.fault_code,
                "fault_text": current_state.fault_text,
            },
            command_id=command_id,
        )


def validate_unit_command(
    request: CommandRequest,
    current_state: UnitState,
    current_intent: UnitIntent,
    current_waiting_on: UnitWaitingOn,
) -> None:
    """Validate unit command against S88 state machine rules.

    Enforces S88-aligned behavioral rules:
    - Start: Only from Idle, requires recipe_id in intent
    - Pause: Only from Running
    - Resume: Only from Paused
    - Hold: Only from Running
    - Restart: Only from Held
    - Stop: From Running, Paused, or Held
    - Abort: From any active state
    - Reset: Only from Faulted or terminal states (Complete, Stopped, Aborted)

    Args:
        request: CommandRequest to validate
        current_state: Current unit state seam
        current_intent: Current unit intent seam
        current_waiting_on: Current unit waiting_on seam

    Raises:
        PreconditionFailed: If S88 state transition rules violated

    This is a pure function with no IO.
    """
    command = request.command
    target_id = request.target_id
    command_id = request.command_id
    state = current_state.lifecycle_state

    # S88 State Transition Rules
    if command == "Start":
        # Start only from Idle
        if state != "Idle":
            raise PreconditionFailed(
                command=command,
                target_id=target_id,
                precondition=f"Start only allowed from Idle, current state: {state}",
                current_state={"lifecycle_state": state},
                command_id=command_id,
            )
        # Requires recipe_id in command parameters
        params = request.args[0] if request.args else {}
        if not params.get("recipe_id"):
            raise PreconditionFailed(
                command=command,
                target_id=target_id,
                precondition="Start requires recipe_id in command parameters",
                current_state={"command_args": params},
                command_id=command_id,
            )

    elif command == "Pause":
        # Pause only from Running
        if state != "Running":
            raise PreconditionFailed(
                command=command,
                target_id=target_id,
                precondition=f"Pause only allowed from Running, current state: {state}",
                current_state={"lifecycle_state": state},
                command_id=command_id,
            )

    elif command == "Resume":
        # Resume only from Paused
        if state != "Paused":
            raise PreconditionFailed(
                command=command,
                target_id=target_id,
                precondition=f"Resume only allowed from Paused, current state: {state}",
                current_state={"lifecycle_state": state},
                command_id=command_id,
            )

    elif command == "Hold":
        # Hold only from Running
        if state != "Running":
            raise PreconditionFailed(
                command=command,
                target_id=target_id,
                precondition=f"Hold only allowed from Running, current state: {state}",
                current_state={"lifecycle_state": state},
                command_id=command_id,
            )

    elif command == "Restart":
        # Restart only from Held
        if state != "Held":
            raise PreconditionFailed(
                command=command,
                target_id=target_id,
                precondition=f"Restart only allowed from Held, current state: {state}",
                current_state={"lifecycle_state": state},
                command_id=command_id,
            )

    elif command == "Stop":
        # Stop from active states
        if state not in ["Running", "Paused", "Held", "Holding", "Pausing"]:
            raise PreconditionFailed(
                command=command,
                target_id=target_id,
                precondition=f"Stop only allowed from active states, current state: {state}",
                current_state={"lifecycle_state": state},
                command_id=command_id,
            )

    elif command == "Abort":
        # Abort allowed from any non-terminal state
        if state in ["Idle", "Complete", "Stopped", "Aborted"]:
            raise PreconditionFailed(
                command=command,
                target_id=target_id,
                precondition=f"Abort not applicable in state: {state}",
                current_state={"lifecycle_state": state},
                command_id=command_id,
            )

    elif command == "Reset":
        # Reset only from Faulted or terminal states
        if state not in ["Faulted", "Complete", "Stopped", "Aborted"]:
            raise PreconditionFailed(
                command=command,
                target_id=target_id,
                precondition=f"Reset only allowed from Faulted/Complete/Stopped/Aborted, current: {state}",
                current_state={"lifecycle_state": state},
                command_id=command_id,
            )

    # Consistency check: If Held, waiting_on.reasons should be non-empty
    if state == "Held" and not current_waiting_on.reasons:
        # This is a consistency warning, not a command validation failure
        pass


def validate_state_schema_id(expected: str, actual: str) -> None:
    """Validate that stateSchemaId values match.

    Args:
        expected: Expected stateSchemaId (e.g., "procaaso.io/seams/actuator/meta/v1")
        actual: Actual stateSchemaId from data

    Raises:
        SchemaValidationError: If stateSchemaIds don't match

    This is a pure function with no IO.
    """
    if expected != actual:
        raise SchemaValidationError(
            path="<stateSchemaId>",
            expected_schema=expected,
            actual_value=actual,
            validation_error=f"stateSchemaId mismatch: expected '{expected}', got '{actual}'",
        )


# Backward compatibility alias
validate_schema_id = validate_state_schema_id


def validate_contract_version(expected_major: int, provided: str) -> None:
    """Validate contract version compatibility.

    Per spec §3.3: Reject MAJOR mismatch, allow MINOR/PATCH differences.

    Args:
        expected_major: Expected MAJOR version number
        provided: Provided version string (e.g., "1.2.3")

    Raises:
        SchemaValidationError: If version format invalid or MAJOR mismatch

    This is a pure function with no IO.
    """
    try:
        # Parse provided version
        parts = provided.split(".")
        if len(parts) < 1:
            raise SchemaValidationError(
                path="<contract_version>",
                validation_error=f"Invalid version format: '{provided}', expected 'MAJOR.MINOR.PATCH'",
            )

        provided_major = int(parts[0])

        # Check MAJOR version match (spec §3.3)
        if provided_major != expected_major:
            raise SchemaValidationError(
                path="<contract_version>",
                expected_schema=f"MAJOR version {expected_major}",
                actual_value=provided,
                validation_error=f"MAJOR version mismatch: expected {expected_major}, got {provided_major} (from '{provided}')",
            )

        # MINOR and PATCH differences are allowed per spec

    except ValueError as e:
        raise SchemaValidationError(
            path="<contract_version>",
            validation_error=f"Invalid version format: '{provided}', error: {e}",
        ) from e


def validate_driver_command(
    request: CommandRequest,
    capabilities: DriverCapabilities,
    current_state: DriverState,
) -> None:
    """Validate driver command against capabilities and behavioral rules.

    Enforces spec §7.5 behavioral rules:
    - If lifecycle_state == Faulted, only ResetFault (and optionally ResetDriver) accepted
    - Standard commands: ResetDriver, RescanChannels, ResetFault

    Args:
        request: CommandRequest to validate
        capabilities: Driver capabilities seam
        current_state: Current driver state seam

    Raises:
        PreconditionFailed: If behavioral rules violated

    This is a pure function with no IO.
    """
    command = request.command
    target_id = request.target_id
    command_id = request.command_id

    # Rule 1: If Faulted, only ResetFault (and optionally ResetDriver) accepted (spec §7.5)
    if current_state.lifecycle_state == "Faulted":
        if command not in ["ResetFault", "ResetDriver"]:
            raise PreconditionFailed(
                command=command,
                target_id=target_id,
                precondition=f"Driver is Faulted, only ResetFault or ResetDriver allowed",
                current_state={
                    "lifecycle_state": current_state.lifecycle_state,
                    "fault_code": current_state.fault_code,
                    "fault_text": current_state.fault_text,
                },
                command_id=command_id,
            )

    # Rule 2: RescanChannels only if supported
    if command == "RescanChannels":
        if not capabilities.supports_rescan:
            raise PreconditionFailed(
                command=command,
                target_id=target_id,
                precondition="RescanChannels not supported by this driver",
                current_state={"supports_rescan": capabilities.supports_rescan},
                command_id=command_id,
            )
