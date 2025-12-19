"""
Remote seam store backed by sidecar.

Implements SeamStore interface using sidecar /attributeStates API.
"""

from typing import Any, Dict

from ..seams.store import SeamStore
from .adapter import SidecarBusAdapter


class RemoteSeamStore(SeamStore):
    """Seam store backed by sidecar /attributeStates API."""

    def __init__(self, bus_adapter: SidecarBusAdapter, log=None):
        """
        Initialize remote seam store.

        Args:
            bus_adapter: SidecarBusAdapter instance
            log: Optional logger
        """
        self.bus = bus_adapter
        self.log = log

    def _make_path(self, component_id: str, instrument: str, attribute: str) -> str:
        """Build seam path."""
        return f"{component_id}.{instrument}.{attribute}"

    async def get(self, component_id: str, instrument: str, attribute: str) -> Dict[str, Any]:
        """Get seam attribute from sidecar."""
        path = self._make_path(component_id, instrument, attribute)
        return await self.bus.get_seam(path)

    async def set(
        self, component_id: str, instrument: str, attribute: str, new_value: Dict[str, Any]
    ) -> None:
        """Set seam attribute via sidecar."""
        path = self._make_path(component_id, instrument, attribute)
        await self.bus.put_seam(path, new_value)

    async def update_fields(
        self, component_id: str, instrument: str, attribute: str, **updates
    ) -> Dict[str, Any]:
        """Update specific fields in seam attribute."""
        current = await self.get(component_id, instrument, attribute)
        current.update(updates)
        await self.set(component_id, instrument, attribute, current)
        return current

    async def snapshot(self, component_id: str, instrument: str = "actuator") -> Dict[str, Any]:
        """Get snapshot of all component seams.

        Args:
            component_id: Component identifier
            instrument: Instrument type ('actuator', 'sensor', 'unit', 'driver')

        Returns:
            Dictionary with instrument seams
        """
        # Define seam structure per instrument type
        if instrument == "actuator":
            seam_keys = [
                ("actuator", "meta"),
                ("actuator", "state"),
                ("actuator", "capabilities"),
                ("actuator", "feedback"),
                ("actuator", "intent"),
                ("actuator", "invariants"),
                ("actuator", "cmd"),
                ("actuator", "bus_announce"),
                ("actuator", "bus_command_reply"),
                ("actuator", "bus_command_request"),
            ]
        elif instrument == "sensor":
            seam_keys = [
                ("sensor", "meta"),
                ("sensor", "state"),
                ("sensor", "capabilities"),
                ("sensor", "value"),
                ("sensor", "scaling"),
                ("sensor", "cmd"),
            ]
        elif instrument == "unit":
            seam_keys = [
                ("unit", "meta"),
                ("unit", "state"),
                ("unit", "intent"),
                ("unit", "waiting_on"),
                ("unit", "cmd"),
            ]
        elif instrument == "driver":
            seam_keys = [
                ("driver", "meta"),
                ("driver", "state"),
                ("driver", "capabilities"),
                ("driver", "inventory"),
                ("driver", "intent"),
                ("driver", "cmd"),
                ("driver", "bus_announce"),
                ("driver", "bus_command_reply"),
                ("driver", "bus_command_request"),
            ]
        else:
            # Unknown instrument type
            seam_keys = []

        snapshot = {}
        for inst, attribute in seam_keys:
            try:
                value = await self.get(component_id, inst, attribute)
                if inst not in snapshot:
                    snapshot[inst] = {}
                snapshot[inst][attribute] = value
            except Exception as e:
                if self.log:
                    self.log.debug(f"Failed to snapshot {inst}.{attribute}: {e}")
        return snapshot
