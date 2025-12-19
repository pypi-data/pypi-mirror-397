"""
SEAMS store module.

Provides remote-first seam state storage backed by sidecar ENS gateway.
"""

import asyncio
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, Dict, Optional

from ..bus.client import BusClient
from ..logging.errors import SchemaValidationError
from .validators import validate_schema_id


class SeamStore(ABC):
    """Abstract base class for seam storage.

    Paths follow spec: component.instrument.attribute
    """

    @abstractmethod
    async def get(
        self,
        component_id: str,
        instrument: str,
        attribute: str,
    ) -> Dict[str, Any]:
        """Get seam attribute value.

        Args:
            component_id: Component identifier
            instrument: Instrument name (e.g., 'actuator', 'sensor')
            attribute: Attribute name (e.g., 'meta', 'state', 'capabilities')

        Returns:
            Dictionary containing attribute value
        """
        pass

    @abstractmethod
    async def set(
        self,
        component_id: str,
        instrument: str,
        attribute: str,
        new_value: Dict[str, Any],
    ) -> None:
        """Set entire seam attribute value.

        Args:
            component_id: Component identifier
            instrument: Instrument name
            attribute: Attribute name
            new_value: New attribute value dictionary
        """
        pass

    @abstractmethod
    async def update_fields(
        self,
        component_id: str,
        instrument: str,
        attribute: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """Update specific fields within a seam attribute.

        Args:
            component_id: Component identifier
            instrument: Instrument name
            attribute: Attribute name
            **kwargs: Field updates

        Returns:
            Updated attribute value
        """
        pass

    @abstractmethod
    async def snapshot(self, component_id: str, instrument: str = "actuator") -> Dict[str, Any]:
        """Get snapshot of all component seams for StateEvent payload.

        Args:
            component_id: Component identifier
            instrument: Instrument type ('actuator', 'sensor', 'unit', 'driver')

        Returns:
            Dictionary with all component state (nested by instrument and attribute)
        """
        pass


class RemoteSeamStore(SeamStore):
    """Remote-first seam store backed by BusClient sidecar API.

    Uses BusClient methods get_seam() and put_seam() for remote seam access.
    May keep small per-attribute in-memory cache for reads.
    Validates via Pydantic seam models before writing.
    """

    def __init__(self, bus: BusClient, log: Any = None, cache_ttl: float = 1.0):
        """Initialize remote seam store.

        Args:
            bus: BusClient for sidecar communication
            log: Logger instance
            cache_ttl: Cache TTL in seconds (0 = no cache)
        """
        self.bus = bus
        self.log = log
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_times: Dict[str, float] = {}
        self._lock = asyncio.Lock()

    def _make_path(self, component_id: str, instrument: str, attribute: str) -> str:
        """Build seam path."""
        return f"{component_id}.{instrument}.{attribute}"

    async def get(
        self,
        component_id: str,
        instrument: str,
        attribute: str,
    ) -> Dict[str, Any]:
        """Get seam attribute from sidecar (with optional caching)."""
        path = self._make_path(component_id, instrument, attribute)

        # Check cache if enabled
        if self.cache_ttl > 0:
            async with self._lock:
                if path in self._cache:
                    import time

                    if time.time() - self._cache_times.get(path, 0) < self.cache_ttl:
                        if self.log:
                            self.log.debug(f"Cache hit: {path}")
                        return deepcopy(self._cache[path])

        # Fetch from sidecar
        value = await self.bus.get_seam(path)

        # Update cache
        if self.cache_ttl > 0:
            async with self._lock:
                import time

                self._cache[path] = deepcopy(value)
                self._cache_times[path] = time.time()

        return value

    async def set(
        self,
        component_id: str,
        instrument: str,
        attribute: str,
        new_value: Dict[str, Any],
    ) -> None:
        """Set seam attribute via sidecar.

        Validates before writing (basic schema_id check).
        Invalidates cache.
        """
        path = self._make_path(component_id, instrument, attribute)

        # TODO: Add Pydantic model validation here
        # For now, basic validation
        if "stateSchemaId" in new_value:
            expected_schema = f"procaaso.io/seams/{instrument}/{attribute}/v1"
            validate_schema_id(expected_schema, new_value["stateSchemaId"])

        # Write to sidecar
        await self.bus.put_seam(path, new_value)

        # Invalidate cache
        async with self._lock:
            self._cache.pop(path, None)
            self._cache_times.pop(path, None)

        if self.log:
            self.log.debug(f"Set seam {path}")

    async def update_fields(
        self,
        component_id: str,
        instrument: str,
        attribute: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """Update specific fields within seam attribute.

        Read current value, merge updates, write back.
        """
        # Read current
        current = await self.get(component_id, instrument, attribute)

        # Merge updates
        updated = {**current, **kwargs}

        # Write back
        await self.set(component_id, instrument, attribute, updated)

        return updated

    async def snapshot(self, component_id: str, instrument: str = "actuator") -> Dict[str, Any]:
        """Get snapshot of all component seams.

        Returns all attributes for the specified instrument type.
        """
        # Define attributes per instrument type
        if instrument == "actuator":
            attributes = [
                "meta",
                "state",
                "capabilities",
                "feedback",
                "intent",
                "invariants",
                "cmd",
            ]
        elif instrument == "sensor":
            attributes = ["meta", "state", "capabilities", "value", "scaling", "cmd"]
        elif instrument == "unit":
            attributes = ["meta", "state", "intent", "waiting_on", "cmd"]
        elif instrument == "driver":
            attributes = ["meta", "state", "capabilities", "inventory", "intent", "cmd"]
        elif instrument == "app":
            attributes = ["meta", "state", "cmd"]
        else:
            attributes = []

        result = {}
        result[instrument] = {}
        for attribute in attributes:
            try:
                value = await self.get(component_id, instrument, attribute)
                result[instrument][attribute] = value
            except Exception as e:
                if self.log:
                    self.log.warning(
                        f"Failed to snapshot {component_id}.{instrument}.{attribute}: {e}"
                    )

        return result


class InMemorySeamStore(SeamStore):
    """In-memory seam store for tests and simulation.

    Stores all seams in a nested dictionary structure.
    Asyncio-safe with locking.
    """

    def __init__(self, log: Any = None):
        """Initialize in-memory store."""
        self.log = log
        self._store: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]] = {}
        self._lock = asyncio.Lock()

    async def get(
        self,
        component_id: str,
        instrument: str,
        attribute: str,
    ) -> Dict[str, Any]:
        """Get seam attribute from memory."""
        async with self._lock:
            if component_id not in self._store:
                raise KeyError(f"Component not found: {component_id}")
            if instrument not in self._store[component_id]:
                raise KeyError(f"Instrument not found: {component_id}.{instrument}")
            if attribute not in self._store[component_id][instrument]:
                raise KeyError(f"Attribute not found: {component_id}.{instrument}.{attribute}")

            return deepcopy(self._store[component_id][instrument][attribute])

    async def set(
        self,
        component_id: str,
        instrument: str,
        attribute: str,
        new_value: Dict[str, Any],
    ) -> None:
        """Set seam attribute in memory."""
        async with self._lock:
            if component_id not in self._store:
                self._store[component_id] = {}
            if instrument not in self._store[component_id]:
                self._store[component_id][instrument] = {}

            self._store[component_id][instrument][attribute] = deepcopy(new_value)

            if self.log:
                self.log.debug(f"Set {component_id}.{instrument}.{attribute}")

    async def update_fields(
        self,
        component_id: str,
        instrument: str,
        attribute: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """Update specific fields in seam attribute."""
        current = await self.get(component_id, instrument, attribute)
        updated = {**current, **kwargs}
        await self.set(component_id, instrument, attribute, updated)
        return updated

    async def snapshot(self, component_id: str, instrument: str = "actuator") -> Dict[str, Any]:
        """Get snapshot of all component seams."""
        async with self._lock:
            if component_id not in self._store:
                return {}

            # If instrument specified, filter to just that instrument
            full_snapshot = deepcopy(self._store[component_id])
            if instrument and instrument in full_snapshot:
                return {instrument: full_snapshot[instrument]}
            return full_snapshot
