"""
Services base module.

Provides base class for all controllable components.
Uses BusClient for sidecar communication (no direct bus access).
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict

from ..bus.client import BusClient
from ..bus.envelopes import Announce, StateEvent
from ..seams.store import SeamStore


class BaseService(ABC):
    """Base service class for all Procaaso controllable components.

    Provides common functionality for:
    - Announcing service via BusClient
    - Emitting StateEvents via BusClient
    - Lifecycle management (start/stop)

    Does not subscribe directly to bus topics (sidecar handles routing).
    """

    def __init__(
        self,
        component_id: str,
        bus: BusClient,
        store: SeamStore,
        log: Any,
        contract: str,
        contract_version: str = "1.0.0",
    ):
        """Initialize base service.

        Args:
            component_id: Unique identifier for this component
            bus: BusClient for sidecar communication
            store: SeamStore for reading/writing state
            log: Logger instance
            contract: Contract type (e.g., 'Actuator', 'Sensor')
            contract_version: Version of the contract
        """
        self.component_id = component_id
        self.bus = bus
        self.store = store
        self.log = log
        self.contract = contract
        self.contract_version = contract_version
        self._running = False
        self._seq = 0

    async def announce(
        self,
        service_role: str,
        capabilities: list,
        config_hash: str,
        health: str = "OK",
    ) -> None:
        """Publish Announce message via attributeStates.

        Writes to bus_announce attribute instead of publishing directly to bus.
        Sidecar reads this attribute and forwards to event bus.

        Args:
            service_role: Role of this service (e.g., 'controller', 'actuator')
            capabilities: List of supported capabilities
            config_hash: Configuration hash for this component
            health: Health status ('OK', 'Degraded', 'Faulted')
        """
        # Map contract to instrument name
        instrument = self.contract.lower()

        announce_payload = {
            "service_id": self.component_id,
            "service_role": service_role,
            "contract": self.contract,
            "contract_version": self.contract_version,
            "capabilities": capabilities,
            "config_hash": config_hash,
            "health": health,
            "ts": datetime.utcnow().isoformat() + "Z",
            "msg_type": "Announce",
        }

        # Write to bus_announce attribute
        await self.store.set(self.component_id, instrument, "bus_announce", announce_payload)

        if self.log:
            self.log.info(
                f"Announced {self.component_id} "
                f"contract={self.contract} v{self.contract_version} "
                f"health={health}"
            )

    async def emit_state_event(self, payload: Dict[str, Any] = None) -> None:
        """Emit state event by updating state attribute.

        State events are now implicit - sidecar detects state changes and
        publishes StateEvent envelopes automatically. This method is kept
        for backwards compatibility but now just ensures state is written.

        Args:
            payload: Optional explicit payload (ignored - state is read from attributes)
        """
        # Increment sequence for tracking
        self._seq += 1

        if self.log:
            self.log.debug(
                f"State update for {self.component_id} seq={self._seq} "
                "(sidecar will publish StateEvent from attribute changes)"
            )

        # Note: No explicit publish needed. Sidecar monitors state attribute
        # and publishes StateEvent when it changes.

    @abstractmethod
    async def start(self) -> None:
        """Start the service.

        Subclasses must implement to:
        - Initialize seams in store (write defaults if missing)
        - Announce service
        - Emit initial StateEvent
        - Register handlers (actuators register with BusRouter)
        """
        pass

    async def stop(self) -> None:
        """Stop the service and cleanup resources."""
        self._running = False

        if self.log:
            self.log.info(f"Service {self.component_id} stopped")
