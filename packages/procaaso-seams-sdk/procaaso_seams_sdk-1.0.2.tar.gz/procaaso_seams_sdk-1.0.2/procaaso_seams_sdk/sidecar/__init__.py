"""
Sidecar integration module.

Provides high-level convenience functions for connecting to Procaaso sidecar.
"""

from .adapter import SidecarBusAdapter
from .client import ActuatorClient, SensorClient
from .factory import connect_actuator, connect_sensor
from .store import RemoteSeamStore

__all__ = [
    "SidecarBusAdapter",
    "RemoteSeamStore",
    "connect_actuator",
    "connect_sensor",
    "ActuatorClient",
    "SensorClient",
]
