"""
Procaaso SEAMS SDK

Interface Wrapper to allow event-based communication between containers via sidecar ENS.
"""

__version__ = "1.0.0"

# Bus communication
from .bus import (
    Announce,
    BusClient,
    BusRouter,
    CommandReply,
    CommandRequest,
    IdempotencyStore,
    PollingBusRouter,
    StateEvent,
)

# Errors
from .logging.errors import (
    BusConnectionError,
    BusDecodeError,
    CommandRejectedError,
    HardwareFault,
    IdempotencyConflictError,
    InvalidCommand,
    PreconditionFailed,
    ProcaasoSeamsError,
    SchemaValidationError,
    UnsupportedCommand,
    VersionMismatch,
)

# Seam models
from .seams.models import (
    ActuatorCapabilities,
    ActuatorCmd,
    ActuatorFeedback,
    ActuatorIntent,
    ActuatorInvariants,
    ActuatorMeta,
    ActuatorState,
    AppCmd,
    AppMeta,
    AppState,
    DriverCapabilities,
    DriverCmd,
    DriverIntent,
    DriverInventory,
    DriverMeta,
    DriverState,
    SensorCapabilities,
    SensorCmd,
    SensorMeta,
    SensorScaling,
    SensorState,
    SensorValue,
    UnitCmd,
    UnitIntent,
    UnitMeta,
    UnitOutcome,
    UnitState,
    UnitWaitingOn,
    load_defaults,
)

# Seam storage
from .seams.store import InMemorySeamStore, RemoteSeamStore, SeamStore

# Seam validators
from .seams.validators import (
    validate_actuator_command,
    validate_contract_version,
    validate_driver_command,
    validate_schema_id,
    validate_sensor_command,
    validate_state_schema_id,
    validate_unit_command,
)

# Services
from .services.actuator import ActuatorService
from .services.app import APPService
from .services.base import BaseService
from .services.driver import DriverService
from .services.sensor import SensorService
from .services.unit import UnitService

# Sidecar convenience layer
from .sidecar import ActuatorClient, connect_actuator

__all__ = [
    # Version
    "__version__",
    # Bus
    "BusClient",
    "BusRouter",
    "PollingBusRouter",
    "Announce",
    "CommandRequest",
    "CommandReply",
    "StateEvent",
    "IdempotencyStore",
    # Seam storage
    "SeamStore",
    "RemoteSeamStore",
    "InMemorySeamStore",
    # Seam models
    "ActuatorMeta",
    "ActuatorState",
    "ActuatorCapabilities",
    "ActuatorFeedback",
    "ActuatorIntent",
    "ActuatorInvariants",
    "ActuatorCmd",
    "AppMeta",
    "AppState",
    "AppCmd",
    "DriverMeta",
    "DriverState",
    "DriverCapabilities",
    "DriverInventory",
    "DriverIntent",
    "DriverCmd",
    "SensorMeta",
    "SensorState",
    "SensorValue",
    "SensorScaling",
    "SensorCapabilities",
    "SensorCmd",
    "UnitMeta",
    "UnitState",
    "UnitIntent",
    "UnitWaitingOn",
    "UnitCmd",
    "UnitOutcome",
    "load_defaults",
    # Seam validators
    "validate_actuator_command",
    "validate_driver_command",
    "validate_sensor_command",
    "validate_unit_command",
    "validate_state_schema_id",
    "validate_schema_id",  # Backward compatibility alias
    "validate_contract_version",
    # Services
    "BaseService",
    "ActuatorService",
    "APPService",
    "DriverService",
    "SensorService",
    "UnitService",
    # Sidecar convenience layer
    "connect_actuator",
    "ActuatorClient",
    # Errors
    "ProcaasoSeamsError",
    "SchemaValidationError",
    "CommandRejectedError",
    "IdempotencyConflictError",
    "BusConnectionError",
    "BusDecodeError",
    "InvalidCommand",
    "UnsupportedCommand",
    "VersionMismatch",
    "PreconditionFailed",
    "HardwareFault",
]
