"""
Sidecar bus adapter.

Maps SDK BusClient API to sidecar /attributeStates REST endpoints.
"""

from typing import TYPE_CHECKING, Any, Dict, Optional

from pydantic import BaseModel

if TYPE_CHECKING:
    from procaaso_client.asynchronous.client import AsyncHarnessClient

try:
    from procaaso_client.asynchronous.client import AsyncHarnessClient as _AsyncHarnessClient

    PROCAASO_CLIENT_AVAILABLE = True
except ImportError:
    PROCAASO_CLIENT_AVAILABLE = False
    _AsyncHarnessClient = None  # type: ignore

from ..bus.envelopes import Announce, CommandReply, StateEvent
from ..seams.models import (
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
)


class SidecarBusAdapter:
    """
    Adapter for polling-based sidecar communication.

    Maps SDK API to sidecar /attributeStates endpoints with polling pattern.
    """

    def __init__(self, sidecar_client: "AsyncHarnessClient", system_name: str, log=None):
        """
        Initialize sidecar bus adapter.

        Args:
            sidecar_client: AsyncHarnessClient instance
            system_name: System name in sidecar
            log: Optional logger
        """
        if not PROCAASO_CLIENT_AVAILABLE:
            raise ImportError(
                "procaaso_client is required for sidecar integration. "
                "Install it with: pip install procaaso-client"
            )

        self.client = sidecar_client
        self.system_name = system_name
        self.log = log

    def _parse_seam_path(self, path: str):
        """Parse component.instrument.attribute path."""
        parts = path.split(".")
        if len(parts) != 3:
            raise ValueError(
                f"Invalid seam path: {path}. Expected format: component.instrument.attribute"
            )
        return parts[0], parts[1], parts[2]

    async def get_seam(self, path: str) -> Dict[str, Any]:
        """
        Get attribute value from sidecar cache.

        Maps: "pump-101.actuator.cmd" ->
              GET /attributeStates?system=...&component=pump-101&instrument=actuator&attribute=cmd

        Args:
            path: Seam path in format "component.instrument.attribute"

        Returns:
            Dictionary containing attribute value
        """
        component, instrument, attribute = self._parse_seam_path(path)

        if self.log:
            self.log.debug(f"GET seam: {path}")

        # Map attribute names to SDK models for type safety based on instrument type
        from ..seams.models import (
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
        )

        if instrument == "actuator":
            model_map = {
                "meta": ActuatorMeta,
                "state": ActuatorState,
                "capabilities": ActuatorCapabilities,
                "feedback": ActuatorFeedback,
                "intent": ActuatorIntent,
                "invariants": ActuatorInvariants,
                "cmd": ActuatorCmd,
            }
        elif instrument == "sensor":
            model_map = {
                "meta": SensorMeta,
                "state": SensorState,
                "capabilities": SensorCapabilities,
                "value": SensorValue,
                "scaling": SensorScaling,
                "cmd": SensorCmd,
            }
        elif instrument == "unit":
            model_map = {
                "meta": UnitMeta,
                "state": UnitState,
                "intent": UnitIntent,
                "waiting_on": UnitWaitingOn,
                "cmd": UnitCmd,
                "outcome": UnitOutcome,
            }
        elif instrument == "app":
            model_map = {
                "meta": AppMeta,
                "state": AppState,
                "cmd": AppCmd,
            }
        else:
            model_map = {}

        value_model = model_map.get(attribute, BaseModel)

        try:
            # Get from sidecar cache
            result = await self.client.get_attribute_state(
                system_name=self.system_name,
                component_name=component,
                connector_name="",
                instrument_name=instrument,
                attribute_name=attribute,
                value_model=value_model,
            )

            # Convert Pydantic model to dict
            if hasattr(result, "dict"):
                return result.dict()
            elif hasattr(result, "__dict__"):
                return result.__dict__
            else:
                return {}

        except Exception as e:
            if self.log:
                self.log.warning(f"Failed to get seam {path}: {e}")
            # Return empty dict for missing attributes
            return {}

    async def put_seam(self, path: str, payload: Dict[str, Any]) -> None:
        """
        Write attribute value to sidecar cache.

        Maps: "pump-101.actuator.state" + {"lifecycle_state": "Running"} ->
              POST /attributeStates?...&attribute=state with body

        Args:
            path: Seam path in format "component.instrument.attribute"
            payload: Dictionary to write
        """
        component, instrument, attribute = self._parse_seam_path(path)

        if self.log:
            self.log.debug(f"PUT seam: {path}")

        try:
            # Create dynamic Pydantic model from payload
            from typing import get_type_hints

            from pydantic import create_model

            # Build field definitions for create_model
            # Format: field_name: (type, default_value)
            field_definitions: Dict[str, Any] = {}
            for k, v in payload.items():
                # Use Any type with the value as default to avoid type inference issues
                field_definitions[k] = (Any, v)

            PayloadModel = create_model("PayloadModel", **field_definitions)  # type: ignore
            value_model = PayloadModel()

            await self.client.post_attribute_state(
                value=value_model,
                system_name=self.system_name,
                component_name=component,
                connector_name="",
                instrument_name=instrument,
                attribute_name=attribute,
            )

        except Exception as e:
            if self.log:
                self.log.error(f"Failed to put seam {path}: {e}")
            raise

    async def announce(self, msg: Announce) -> None:
        """
        Publish Announce message.

        In polling architecture, this could write to bus_announce attribute.
        For now, log locally.
        """
        if self.log:
            self.log.info(
                f"Announced {msg.service_id} contract={msg.contract} v{msg.contract_version} health={msg.health}"
            )

    async def publish_state(self, msg: StateEvent) -> None:
        """Publish StateEvent message - log locally for now."""
        if self.log:
            self.log.debug(f"STATE EVENT: {msg.entity_id} (seq={msg.seq})")

    async def publish_reply(self, msg: CommandReply) -> None:
        """Publish CommandReply message - log locally for now."""
        if self.log:
            status = "ACCEPTED" if msg.accepted else "REJECTED"
            self.log.info(f"REPLY: {msg.command_id} - {status}: {msg.reason}")

    async def close(self) -> None:
        """Close sidecar client."""
        await self.client.close()
