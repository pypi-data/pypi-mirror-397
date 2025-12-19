"""
SEAMS models module.

Defines data models for SEAMS functionality per:
- specs/Procaaso_Seam_Interface_Spec_v1.0.md
- specs/seams_models_v1.yaml
"""

import copy
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

# Import bus envelopes - do not redefine them
from ..bus.envelopes import Announce, CommandReply, CommandRequest

# -------------------------------------------------------------------
# Enums from spec
# -------------------------------------------------------------------

# Actuator lifecycle states (spec §4.3)
ActuatorLifecycleState = Literal[
    "Idle", "Starting", "Running", "Holding", "Stopping", "Faulted", "Manual"
]

# Actuator operating modes (spec §4.3)
ActuatorOpMode = Literal["Off", "OnOff", "Fixed", "Ramp", "PID_Control", "Jog"]

# Quality enum (spec §4.3, §5.3)
Quality = Literal["GOOD", "BAD", "UNCERTAIN"]

# Sensor lifecycle states (spec §5.3)
SensorLifecycleState = Literal["Online", "Offline", "Faulted", "Calibrating"]

# Unit lifecycle states (ISA-88 Unit Procedure States, spec §6.3)
UnitLifecycleState = Literal[
    "Idle",  # No procedure active
    "Running",  # Procedure executing
    "Complete",  # Procedure completed successfully
    "Pausing",  # Transitioning to Paused
    "Paused",  # Procedure paused, can resume
    "Holding",  # Waiting for condition (equipment, material, etc.)
    "Held",  # In held state
    "Restarting",  # Restarting from held/paused
    "Stopping",  # Transitioning to controlled stop
    "Stopped",  # Procedure stopped (normal termination)
    "Aborting",  # Transitioning to emergency stop
    "Aborted",  # Procedure aborted (abnormal termination)
    "Faulted",  # Equipment fault condition
]


# -------------------------------------------------------------------
# Actuator Models (spec §4)
# -------------------------------------------------------------------


class ActuatorMeta(BaseModel):
    """Actuator meta attribute (spec §4.3).

    Schema ID: procaaso.io/seams/actuator/meta.v1
    """

    actuator_id: str = ""
    contract_version: str = "1.0.0"
    actuator_type: str = ""

    class Config:
        extra = "allow"  # Allow extra fields like component_id, description, manufacturer, model


class ActuatorState(BaseModel):
    """Actuator state attribute (spec §4.3).

    Schema ID: procaaso.io/seams/actuator/state.v1
    """

    lifecycle_state: ActuatorLifecycleState = "Idle"
    op_mode: ActuatorOpMode = "Off"
    comms_ok: bool = True
    faulted: bool = False
    fault_code: int = 0
    fault_text: str = ""

    class Config:
        extra = "ignore"


class ActuatorCapabilities(BaseModel):
    """Actuator capabilities attribute (spec §4.3).

    Schema ID: procaaso.io/seams/actuator/capabilities.v1
    """

    supported_modes: List[str] = Field(default_factory=list)
    supported_commands: List[str] = Field(default_factory=list)

    class Config:
        extra = "ignore"


class ActuatorFeedback(BaseModel):
    """Actuator feedback attribute (spec §4.3).

    Schema ID: procaaso.io/seams/actuator/feedback.v1
    """

    pv: float = 0.0
    sp: float = 0.0
    percent: float = 0.0
    quality: Quality = "GOOD"
    status_flags: List[str] = Field(default_factory=list)

    class Config:
        extra = "ignore"


class ActuatorIntent(BaseModel):
    """Actuator intent attribute (spec §4.3).

    Schema ID: procaaso.io/seams/actuator/intent.v1
    """

    owner: str = ""
    batch_id: str = ""
    recipe_id: str = ""
    phase_id: str = ""
    target: str = ""

    class Config:
        extra = "allow"  # Allow extra fields like target_state, target_mode


class ActuatorInvariants(BaseModel):
    """Actuator invariants attribute (spec §4.3).

    Schema ID: procaaso.io/seams/actuator/invariants.v1

    Guards are stored as list of dicts per spec.
    """

    guards: List[Dict[str, Any]] = Field(default_factory=list)

    class Config:
        extra = "ignore"


class ActuatorCmd(BaseModel):
    """Actuator cmd attribute (spec §4.3).

    Schema ID: procaaso.io/seams/actuator/cmd.v1

    Command mailbox write surface.
    """

    command_id: str = ""
    command: str = ""
    args: List[Dict[str, Any]] = Field(default_factory=list)
    expected_version: str = "1.0.0"
    source: str = ""

    class Config:
        extra = "allow"  # Allow extra fields like contract, ts for full command envelope


# -------------------------------------------------------------------
# Sensor Models (spec §5)
# -------------------------------------------------------------------


class SensorMeta(BaseModel):
    """Sensor meta attribute (spec §5.3).

    Schema ID: procaaso.io/seams/sensor/meta.v1
    """

    sensor_id: str = ""
    contract_version: str = "1.0.0"
    sensor_type: str = ""

    class Config:
        extra = "ignore"


class SensorState(BaseModel):
    """Sensor state attribute (spec §5.3).

    Schema ID: procaaso.io/seams/sensor/state.v1
    """

    lifecycle_state: SensorLifecycleState = "Online"
    comms_ok: bool = True
    faulted: bool = False
    fault_code: int = 0
    fault_text: str = ""

    class Config:
        extra = "ignore"


class SensorValue(BaseModel):
    """Sensor value attribute (spec §5.3).

    Schema ID: procaaso.io/seams/sensor/value.v1
    """

    pv: float = 0.0
    raw: int = 0
    percent: float = 0.0
    quality: Quality = "GOOD"
    ts: str = ""

    class Config:
        extra = "ignore"


class SensorScaling(BaseModel):
    """Sensor scaling attribute (spec §5.3).

    Schema ID: procaaso.io/seams/sensor/scaling.v1
    """

    eu: str = ""
    eu_min: float = 0.0
    eu_max: float = 0.0
    raw_min: int = 0
    raw_max: int = 0

    class Config:
        extra = "ignore"


class SensorCapabilities(BaseModel):
    """Sensor capabilities attribute (spec §5.3).

    Schema ID: procaaso.io/seams/sensor/capabilities.v1
    """

    supported_commands: List[str] = Field(default_factory=list)

    class Config:
        extra = "ignore"


class SensorCmd(BaseModel):
    """Sensor cmd attribute (spec §5.3).

    Schema ID: procaaso.io/seams/sensor/cmd.v1
    """

    command_id: str = ""
    command: str = ""
    args: List[Dict[str, Any]] = Field(default_factory=list)
    expected_version: str = "1.0.0"
    source: str = ""

    class Config:
        extra = "allow"  # Allow extra fields like contract, ts for full command envelope


# -------------------------------------------------------------------
# Unit Models (spec §6)
# -------------------------------------------------------------------


class UnitMeta(BaseModel):
    """Unit meta attribute (spec §6.3).

    Schema ID: procaaso.seams.unit.meta.v1
    """

    unit_id: str = ""
    contract_version: str = "1.0.0"

    class Config:
        extra = "ignore"


class UnitState(BaseModel):
    """Unit state attribute (S88-aligned, spec §6.3).

    Schema ID: procaaso.seams.unit.state.v1
    """

    lifecycle_state: UnitLifecycleState = "Idle"
    procedure_status: str = ""  # S88: current procedure name
    current_step: str = ""  # S88: current operation/phase step
    step_index: int = 0  # Current step number in sequence
    faulted: bool = False
    fault_code: int = 0
    fault_text: str = ""

    class Config:
        extra = "ignore"


class UnitIntent(BaseModel):
    """Unit intent attribute (ISA-88 hierarchy, spec §6.3).

    ISA-88 Hierarchy: Recipe → Unit Procedure → Operation → Phase

    Schema ID: procaaso.seams.unit.intent.v1
    """

    owner: str = ""
    batch_id: str = ""
    recipe_id: str = ""  # ISA-88: Recipe
    procedure_id: str = ""  # ISA-88: Unit Procedure
    operation_id: str = ""  # ISA-88: Operation
    phase_id: str = ""  # ISA-88: Phase (smallest executable unit)
    targets: List[Dict[str, Any]] = Field(default_factory=list)  # Setpoints, parameters

    class Config:
        extra = "allow"  # Allow additional intent fields


class UnitWaitingOn(BaseModel):
    """Unit waiting_on attribute (spec §6.3).

    Schema ID: procaaso.seams.unit.waiting_on.v1
    """

    reasons: List[Any] = Field(default_factory=list)  # str or object

    class Config:
        extra = "ignore"


class UnitCmd(BaseModel):
    """Unit cmd attribute (ISA-88 commands, spec §6.3).

    ISA-88 Standard Commands:
    - Start: Begin procedure execution (Idle → Running)
    - Pause: Pause at safe point (Running → Pausing → Paused)
    - Resume: Resume from paused (Paused → Restarting → Running)
    - Hold: Hold for external condition (Running → Holding → Held)
    - Restart: Restart from held (Held → Restarting → Running)
    - Stop: Controlled termination (Running/Paused/Held → Stopping → Stopped)
    - Abort: Emergency termination (Any → Aborting → Aborted)
    - Reset: Clear faults and return to Idle (Faulted/Complete/Stopped/Aborted → Idle)

    Phase Execution Commands (from APP to Unit):
    - ExecutePhase: Execute a specific phase with parameters
      args[0]: {
        "phase_name": "Prime" | "Feed" | "Concentrate" | "Flush",
        "parameters": {...}  # Phase-specific parameters
      }

    Schema ID: procaaso.seams.unit.cmd.v1
    """

    command_id: str = ""
    command: str = ""
    args: List[Dict[str, Any]] = Field(default_factory=list)
    expected_version: str = "1.0.0"
    source: str = ""

    class Config:
        extra = "allow"  # Allow extra fields


class UnitOutcome(BaseModel):
    """Unit outcome attribute (spec §6.3, optional).

    Schema ID: procaaso.seams.unit.outcome.v1
    """

    success: bool = False
    completion_ts: str = ""
    metrics: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "allow"


# -------------------------------------------------------------------
# Driver Models (spec §7)
# -------------------------------------------------------------------

# Driver lifecycle states (spec §7.3)
DriverLifecycleState = Literal["Online", "Offline", "Faulted", "Degraded"]


class DriverMeta(BaseModel):
    """Driver meta attribute (spec §7.3).

    Schema ID: procaaso.seams.driver.meta.v1
    """

    driver_id: str = ""
    contract_version: str = "1.0.0"
    driver_type: str = ""
    vendor: str = ""
    model: str = ""
    fw_version: str = ""

    class Config:
        extra = "ignore"


class DriverState(BaseModel):
    """Driver state attribute (spec §7.3).

    Schema ID: procaaso.seams.driver.state.v1
    """

    lifecycle_state: DriverLifecycleState = "Online"
    comms_ok: bool = True
    fault_code: int = 0
    fault_text: str = ""
    scan_rate_ms: float = 0.0

    class Config:
        extra = "ignore"


class DriverCapabilities(BaseModel):
    """Driver capabilities attribute (spec §7.3).

    Schema ID: procaaso.seams.driver.capabilities.v1
    """

    supports_hot_swap: bool = False
    supports_rescan: bool = False
    max_channels: int = 0

    class Config:
        extra = "ignore"


class DriverInventory(BaseModel):
    """Driver inventory attribute (spec §7.3).

    Schema ID: procaaso.seams.driver.inventory.v1

    channels: list of channel dicts, each containing:
    - channel: str (channel identifier)
    - bound_entity_id: str (sensor_id or actuator_id)
    - entity_type: str ("Sensor" or "Actuator")
    - status: str (e.g., "Online", "Offline", "Faulted")
    """

    channels: List[Dict[str, Any]] = Field(default_factory=list)

    class Config:
        extra = "ignore"


class DriverIntent(BaseModel):
    """Driver intent attribute (spec §7.3, optional).

    Schema ID: procaaso.seams.driver.intent.v1
    """

    owner: str = ""
    context: str = ""

    class Config:
        extra = "allow"  # Allow additional intent fields


class DriverCmd(BaseModel):
    """Driver cmd attribute (spec §7.3).

    Standard Driver Commands (spec §7.4):
    - ResetDriver
    - RescanChannels
    - ResetFault

    Schema ID: procaaso.seams.driver.cmd.v1
    """

    command_id: str = ""
    command: str = ""
    args: List[Dict[str, Any]] = Field(default_factory=list)
    expected_version: str = "1.0.0"
    source: str = ""

    class Config:
        extra = "allow"  # Allow extra fields


# -------------------------------------------------------------------
# APP Models (Recipe Controllers / Orchestration Containers)
# -------------------------------------------------------------------

# APP lifecycle states
AppLifecycleState = Literal[
    "Idle", "RecipeLoaded", "Running", "Paused", "Complete", "Stopped", "Aborted", "Faulted"
]


class AppMeta(BaseModel):
    """APP meta attribute.

    Schema ID: procaaso.seams.app.meta.v1
    """

    app_id: str = ""
    contract_version: str = "1.0.0"
    name: str = ""
    description: str = ""

    class Config:
        extra = "allow"


class AppState(BaseModel):
    """APP state attribute.

    Schema ID: procaaso.seams.app.state.v1
    """

    lifecycle_state: AppLifecycleState = "Idle"
    loaded_recipe_id: str = ""
    loaded_batch_id: str = ""
    current_phase: str = ""
    faulted: bool = False
    fault_text: str = ""

    class Config:
        extra = "ignore"


class AppCmd(BaseModel):
    """APP cmd attribute.

    Standard APP Commands:
    - LoadRecipe: Load and validate recipe
    - StartRecipe: Begin recipe execution
    - PauseRecipe: Pause execution
    - ResumeRecipe: Resume execution
    - StopRecipe: Controlled termination
    - AbortRecipe: Emergency termination
    - Reset: Return to Idle

    Schema ID: procaaso.seams.app.cmd.v1
    """

    command_id: str = ""
    command: str = ""
    args: List[Dict[str, Any]] = Field(default_factory=list)
    expected_version: str = "1.0.0"
    source: str = ""

    class Config:
        extra = "allow"  # Allow extra fields


# -------------------------------------------------------------------
# Default values from seams_models_v1.yaml
# -------------------------------------------------------------------

# Actuator defaults
ACTUATOR_DEFAULTS = {
    "meta": {
        "stateSchemaId": "procaaso.io/seams/actuator/meta.v1",
        "actuator_id": "",
        "contract_version": "1.0.0",
        "actuator_type": "",
    },
    "state": {
        "stateSchemaId": "procaaso.io/seams/actuator/state.v1",
        "lifecycle_state": "Idle",
        "op_mode": "Off",
        "comms_ok": True,
        "faulted": False,
        "fault_code": 0,
        "fault_text": "",
    },
    "capabilities": {
        "stateSchemaId": "procaaso.io/seams/actuator/capabilities.v1",
        "supported_modes": [],
        "supported_commands": [],
    },
    "feedback": {
        "stateSchemaId": "procaaso.io/seams/actuator/feedback.v1",
        "pv": 0.0,
        "sp": 0.0,
        "percent": 0.0,
        "quality": "GOOD",
        "status_flags": [],
    },
    "intent": {
        "stateSchemaId": "procaaso.io/seams/actuator/intent.v1",
        "owner": "",
        "batch_id": "",
        "recipe_id": "",
        "phase_id": "",
        "target": "",
    },
    "invariants": {
        "stateSchemaId": "procaaso.io/seams/actuator/invariants.v1",
        "guards": [],
    },
    "cmd": {
        "stateSchemaId": "procaaso.io/seams/actuator/cmd.v1",
        "command_id": "",
        "command": "",
        "args": [],
        "expected_version": "1.0.0",
        "source": "",
    },
}

# Sensor defaults
SENSOR_DEFAULTS = {
    "meta": {
        "stateSchemaId": "procaaso.io/seams/sensor/meta.v1",
        "sensor_id": "",
        "contract_version": "1.0.0",
        "sensor_type": "",
    },
    "state": {
        "stateSchemaId": "procaaso.io/seams/sensor/state.v1",
        "lifecycle_state": "Online",
        "comms_ok": True,
        "faulted": False,
        "fault_code": 0,
        "fault_text": "",
    },
    "value": {
        "stateSchemaId": "procaaso.io/seams/sensor/value.v1",
        "pv": 0.0,
        "raw": 0,
        "percent": 0.0,
        "quality": "GOOD",
        "ts": "",
    },
    "scaling": {
        "stateSchemaId": "procaaso.io/seams/sensor/scaling.v1",
        "eu": "",
        "eu_min": 0.0,
        "eu_max": 0.0,
        "raw_min": 0,
        "raw_max": 0,
    },
    "capabilities": {
        "stateSchemaId": "procaaso.io/seams/sensor/capabilities.v1",
        "supported_commands": [],
    },
    "cmd": {
        "stateSchemaId": "procaaso.io/seams/sensor/cmd.v1",
        "command_id": "",
        "command": "",
        "args": [],
        "expected_version": "1.0.0",
        "source": "",
    },
}

# Unit defaults (S88-aligned, spec §6.3)
UNIT_DEFAULTS = {
    "meta": {
        "stateSchemaId": "procaaso.io/seams/unit/meta.v1",
        "unit_id": "",
        "contract_version": "1.0.0",
    },
    "state": {
        "stateSchemaId": "procaaso.io/seams/unit/state.v1",
        "lifecycle_state": "Idle",
        "procedure_status": "",
        "current_step": "",
        "step_index": 0,
        "faulted": False,
        "fault_code": 0,
        "fault_text": "",
    },
    "intent": {
        "stateSchemaId": "procaaso.io/seams/unit/intent.v1",
        "owner": "",
        "batch_id": "",
        "recipe_id": "",
        "procedure_id": "",
        "operation_id": "",
        "phase_id": "",
        "targets": [],
    },
    "waiting_on": {
        "stateSchemaId": "procaaso.io/seams/unit/waiting_on.v1",
        "reasons": [],
    },
    "cmd": {
        "stateSchemaId": "procaaso.io/seams/unit/cmd.v1",
        "command_id": "",
        "command": "",
        "args": [],
        "expected_version": "1.0.0",
        "source": "",
    },
    "outcome": {
        "success": False,
        "completion_ts": "",
        "metrics": {},
    },
}

# Pump-specific overlays (from seams_models_v1.yaml)
PUMP_OVERLAY = {
    "meta": {
        "actuator_type": "pump",
    },
    "capabilities": {
        "supported_modes": ["OnOff", "Fixed", "Ramp", "PID_Control"],
        "supported_commands": ["Start", "Stop", "SetMode", "Setpoint", "ResetFault"],
    },
}

# Valve-specific overlays
VALVE_OVERLAY = {
    "meta": {
        "actuator_type": "valve",
    },
    "capabilities": {
        "supported_modes": ["OnOff"],
        "supported_commands": ["Start", "Stop", "SetMode", "ResetFault"],
    },
}

# Driver defaults (spec §7.3)
DRIVER_DEFAULTS = {
    "meta": {
        "stateSchemaId": "procaaso.io/seams/driver/meta.v1",
        "driver_id": "",
        "contract_version": "1.0.0",
        "driver_type": "",
        "vendor": "",
        "model": "",
        "fw_version": "",
    },
    "state": {
        "stateSchemaId": "procaaso.io/seams/driver/state.v1",
        "lifecycle_state": "Online",
        "comms_ok": True,
        "fault_code": 0,
        "fault_text": "",
        "scan_rate_ms": 0.0,
    },
    "capabilities": {
        "stateSchemaId": "procaaso.io/seams/driver/capabilities.v1",
        "supports_hot_swap": False,
        "supports_rescan": False,
        "max_channels": 0,
    },
    "inventory": {
        "stateSchemaId": "procaaso.io/seams/driver/inventory.v1",
        "channels": [],
    },
    "intent": {
        "stateSchemaId": "procaaso.io/seams/driver/intent.v1",
        "owner": "",
        "context": "",
    },
    "cmd": {
        "stateSchemaId": "procaaso.io/seams/driver/cmd.v1",
        "command_id": "",
        "command": "",
        "args": [],
        "expected_version": "1.0.0",
        "source": "",
    },
}

# APP defaults
APP_DEFAULTS = {
    "meta": {
        "stateSchemaId": "procaaso.io/seams/app/meta.v1",
        "app_id": "",
        "contract_version": "1.0.0",
        "name": "",
        "description": "",
    },
    "state": {
        "stateSchemaId": "procaaso.io/seams/app/state.v1",
        "lifecycle_state": "Idle",
        "loaded_recipe_id": "",
        "loaded_batch_id": "",
        "current_phase": "",
        "faulted": False,
        "fault_text": "",
    },
    "cmd": {
        "stateSchemaId": "procaaso.io/seams/app/cmd.v1",
        "command_id": "",
        "command": "",
        "args": [],
        "expected_version": "1.0.0",
        "source": "",
    },
}


# -------------------------------------------------------------------
# Helper function
# -------------------------------------------------------------------


def load_defaults(attr_name: str, overlay: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Load default values for a seam attribute with optional overlay.

    Merges generic seam defaults + overlay defaults from seams_models_v1.yaml.

    Args:
        attr_name: Attribute name (e.g., "meta", "state", "capabilities")
        overlay: Optional overlay dict to merge (e.g., pump_defaults, valve_defaults)

    Returns:
        Merged dictionary with defaults

    Example:
        # Get generic actuator meta defaults
        meta = load_defaults("meta")

        # Get pump-specific capabilities
        caps = load_defaults("capabilities", PUMP_OVERLAY)
    """
    # Determine which default set to use based on common attribute names
    # Check UNIT_DEFAULTS first as it's more specific than ACTUATOR_DEFAULTS
    if attr_name in UNIT_DEFAULTS:
        base = copy.deepcopy(UNIT_DEFAULTS[attr_name])
    elif attr_name in ACTUATOR_DEFAULTS:
        base = copy.deepcopy(ACTUATOR_DEFAULTS[attr_name])
    elif attr_name in SENSOR_DEFAULTS:
        base = copy.deepcopy(SENSOR_DEFAULTS[attr_name])
    elif attr_name in DRIVER_DEFAULTS:
        base = copy.deepcopy(DRIVER_DEFAULTS[attr_name])
    elif attr_name in APP_DEFAULTS:
        base = copy.deepcopy(APP_DEFAULTS[attr_name])
    else:
        # Unknown attribute, return empty dict
        # TODO: Consider raising SchemaValidationError here
        return {}

    # Apply overlay if provided
    if overlay and attr_name in overlay:
        overlay_data = overlay[attr_name]
        if isinstance(overlay_data, dict) and "default" in overlay_data:
            # Handle seams_models_v1.yaml structure with nested "default"
            _deep_merge(base, overlay_data["default"])
        else:
            # Direct overlay
            _deep_merge(base, overlay_data)

    return base


def _deep_merge(base: Dict[str, Any], overlay: Dict[str, Any]) -> None:
    """Deep merge overlay into base dict (in-place).

    Args:
        base: Base dictionary to merge into
        overlay: Overlay dictionary with values to merge
    """
    for key, value in overlay.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            # Recursively merge nested dicts
            _deep_merge(base[key], value)
        else:
            # Overwrite or add new key
            base[key] = value
