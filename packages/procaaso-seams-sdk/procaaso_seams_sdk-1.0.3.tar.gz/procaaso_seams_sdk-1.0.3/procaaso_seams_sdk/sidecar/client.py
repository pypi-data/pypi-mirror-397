"""
High-level client for APP containers.

Provides simplified API for control applications to interact with
actuator services via sidecar ENS.
"""

import logging
from typing import Any, Dict, Optional

from .adapter import SidecarBusAdapter


class ActuatorClient:
    """
    Simplified client for APP containers to control actuators.

    Hides all the seam path construction and model mapping complexity.
    Just poll state/feedback and send commands.
    """

    def __init__(
        self,
        sidecar_url: str,
        system_name: str,
        component_id: str,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Create actuator client.

        Args:
            sidecar_url: Sidecar HTTP endpoint (e.g., "http://localhost:8080")
            system_name: System name in sidecar attribute tree
            component_id: Component ID (e.g., "pump01")
            logger: Optional logger instance

        Example:
            pump = ActuatorClient("http://localhost:8080", "batch_system", "pump01")
            state = await pump.get_state()
            await pump.send_command("Start", {})
        """
        try:
            from procaaso_client.asynchronous.client import AsyncHarnessClient, AsyncHttpClient
        except ImportError:
            raise ImportError(
                "procaaso_client is required. Install it with: pip install procaaso-client"
            )

        self.component_id = component_id
        self.log = logger or logging.getLogger(__name__)

        # Create sidecar client and adapter
        http_client = AsyncHttpClient(base_url=sidecar_url)
        sidecar_client = AsyncHarnessClient(http_client=http_client)
        self.bus = SidecarBusAdapter(sidecar_client, system_name, log=self.log)

    def _make_path(self, attribute: str) -> str:
        """Build seam path for this component."""
        return f"{self.component_id}.actuator.{attribute}"

    async def get_meta(self) -> Dict[str, Any]:
        """Get actuator meta (component info, schema)."""
        return await self.bus.get_seam(self._make_path("meta"))

    async def get_state(self) -> Dict[str, Any]:
        """Get current actuator state (mode, health, etc)."""
        return await self.bus.get_seam(self._make_path("state"))

    async def get_capabilities(self) -> Dict[str, Any]:
        """Get actuator capabilities (available modes, health values, etc)."""
        return await self.bus.get_seam(self._make_path("capabilities"))

    async def get_feedback(self) -> Dict[str, Any]:
        """Get actuator feedback (sensor readings, status info)."""
        return await self.bus.get_seam(self._make_path("feedback"))

    async def get_intent(self) -> Dict[str, Any]:
        """Get actuator intent (target state, mode)."""
        return await self.bus.get_seam(self._make_path("intent"))

    async def get_invariants(self) -> Dict[str, Any]:
        """Get actuator invariants (constraints, limits)."""
        return await self.bus.get_seam(self._make_path("invariants"))

    async def send_command(
        self,
        command_type: str,
        parameters: Optional[Dict[str, Any]] = None,
        command_id: Optional[str] = None,
    ) -> str:
        """
        Send command to actuator.

        Args:
            command_type: Command type (e.g., "Start", "Stop", "Setpoint")
            parameters: Command parameters (optional)
            command_id: Custom command ID (auto-generated if not provided)

        Returns:
            The command_id (for tracking replies)

        Example:
            cmd_id = await pump.send_command("Setpoint", {"value": 50.0})
        """
        import uuid
        from datetime import datetime, timezone

        cmd_id = command_id or str(uuid.uuid4())
        cmd_payload = {
            "command_id": cmd_id,
            "command": command_type,
            "args": [parameters] if parameters else [],
            "source": "control_app",
            "expected_version": "1.0.0",
        }

        await self.bus.put_seam(self._make_path("cmd"), cmd_payload)
        self.log.debug(f"Sent command {command_type} with ID {cmd_id}")
        return cmd_id

    async def wait_for_reply(
        self, command_id: str, timeout: float = 5.0
    ) -> Optional[Dict[str, Any]]:
        """
        Poll for command reply (not implemented yet).

        In future, this could poll state/feedback for changes
        or use a reply queue mechanism.

        Args:
            command_id: Command ID to wait for
            timeout: Max wait time in seconds

        Returns:
            Reply payload if found, None if timeout
        """
        # TODO: Implement reply polling mechanism
        self.log.warning("wait_for_reply not yet implemented")
        return None

    async def close(self):
        """Close client and cleanup resources."""
        await self.bus.close()


class SensorClient:
    """
    Simplified client for APP containers to monitor sensors.

    Hides all the seam path construction and model mapping complexity.
    Just poll state/value and send commands.
    """

    def __init__(
        self,
        sidecar_url: str,
        system_name: str,
        component_id: str,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Create sensor client.

        Args:
            sidecar_url: Sidecar HTTP endpoint (e.g., "http://localhost:8080")
            system_name: System name in sidecar attribute tree
            component_id: Component ID (e.g., "temp01")
            logger: Optional logger instance

        Example:
            temp = SensorClient("http://localhost:8080", "batch_system", "temp01")
            value = await temp.get_value()
            await temp.send_command("Zero", {})
        """
        try:
            from procaaso_client.asynchronous.client import AsyncHarnessClient, AsyncHttpClient
        except ImportError:
            raise ImportError(
                "procaaso_client is required. Install it with: pip install procaaso-client"
            )

        self.component_id = component_id
        self.log = logger or logging.getLogger(__name__)

        # Create sidecar client and adapter
        http_client = AsyncHttpClient(base_url=sidecar_url)
        sidecar_client = AsyncHarnessClient(http_client=http_client)
        self.bus = SidecarBusAdapter(sidecar_client, system_name, log=self.log)

    def _make_path(self, attribute: str) -> str:
        """Build seam path for this component."""
        return f"{self.component_id}.sensor.{attribute}"

    async def get_meta(self) -> Dict[str, Any]:
        """Get sensor meta (component info, schema)."""
        return await self.bus.get_seam(self._make_path("meta"))

    async def get_state(self) -> Dict[str, Any]:
        """Get current sensor state (health, faulted, etc)."""
        return await self.bus.get_seam(self._make_path("state"))

    async def get_capabilities(self) -> Dict[str, Any]:
        """Get sensor capabilities (available commands)."""
        return await self.bus.get_seam(self._make_path("capabilities"))

    async def get_value(self) -> Dict[str, Any]:
        """Get sensor value (pv, raw, quality, timestamp)."""
        return await self.bus.get_seam(self._make_path("value"))

    async def get_scaling(self) -> Dict[str, Any]:
        """Get sensor scaling (engineering units, ranges)."""
        return await self.bus.get_seam(self._make_path("scaling"))

    async def send_command(
        self,
        command_type: str,
        parameters: Optional[Dict[str, Any]] = None,
        command_id: Optional[str] = None,
    ) -> str:
        """
        Send command to sensor.

        Args:
            command_type: Command type (e.g., "Zero", "Tare", "ResetFault")
            parameters: Command parameters (optional)
            command_id: Custom command ID (auto-generated if not provided)

        Returns:
            The command_id (for tracking replies)

        Example:
            cmd_id = await temp.send_command("Zero")
        """
        import uuid

        cmd_id = command_id or str(uuid.uuid4())
        cmd_payload = {
            "command_id": cmd_id,
            "command": command_type,
            "args": [parameters] if parameters else [],
            "source": "control_app",
            "expected_version": "1.0.0",
        }

        await self.bus.put_seam(self._make_path("cmd"), cmd_payload)
        self.log.debug(f"Sent command {command_type} with ID {cmd_id}")
        return cmd_id

    async def wait_for_reply(
        self, command_id: str, timeout: float = 5.0
    ) -> Optional[Dict[str, Any]]:
        """
        Poll for command reply (not implemented yet).

        In future, this could poll state/value for changes
        or use a reply queue mechanism.

        Args:
            command_id: Command ID to wait for
            timeout: Max wait time in seconds

        Returns:
            Reply payload if found, None if timeout
        """
        # TODO: Implement reply polling mechanism
        self.log.warning("wait_for_reply not yet implemented")
        return None

    async def close(self):
        """Close client and cleanup resources."""
        await self.bus.close()


class UnitClient:
    """
    Simplified client for APP containers to interact with Unit services.

    Provides access to S88 state machine for batch execution tracking.
    """

    def __init__(
        self,
        sidecar_url: str,
        system_name: str,
        component_id: str,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Create unit client.

        Args:
            sidecar_url: Sidecar HTTP endpoint (e.g., "http://localhost:8080")
            system_name: System name in sidecar attribute tree
            component_id: Component ID (e.g., "unit01")
            logger: Optional logger instance

        Example:
            unit = UnitClient("http://localhost:8080", "batch_system", "unit01")
            state = await unit.get_state()
            await unit.send_command("Start", {"recipe_id": "BATCH-001"})
        """
        try:
            from procaaso_client.asynchronous.client import AsyncHarnessClient, AsyncHttpClient
        except ImportError:
            raise ImportError(
                "procaaso_client is required. Install it with: pip install procaaso-client"
            )

        self.component_id = component_id
        self.log = logger or logging.getLogger(__name__)

        # Create sidecar client and adapter
        http_client = AsyncHttpClient(base_url=sidecar_url)
        sidecar_client = AsyncHarnessClient(http_client=http_client)
        self.bus = SidecarBusAdapter(sidecar_client, system_name, log=self.log)

    def _make_path(self, attribute: str) -> str:
        """Build seam path for this component."""
        return f"{self.component_id}.unit.{attribute}"

    async def get_meta(self) -> Dict[str, Any]:
        """Get unit meta (component info, schema)."""
        return await self.bus.get_seam(self._make_path("meta"))

    async def get_state(self) -> Dict[str, Any]:
        """Get current unit state (S88 state, equipment assignments)."""
        return await self.bus.get_seam(self._make_path("state"))

    async def get_intent(self) -> Dict[str, Any]:
        """Get unit intent (target recipe, procedure, operation, phase)."""
        return await self.bus.get_seam(self._make_path("intent"))

    async def get_waiting_on(self) -> Dict[str, Any]:
        """Get unit waiting reasons (for Holding/Held states)."""
        return await self.bus.get_seam(self._make_path("waiting_on"))

    async def send_command(
        self,
        command_type: str,
        parameters: Optional[Dict[str, Any]] = None,
        command_id: Optional[str] = None,
    ) -> str:
        """
        Send S88 command to unit.

        Args:
            command_type: Command type (e.g., "Start", "Pause", "Resume", "Stop", "Abort", "Reset", "Complete")
            parameters: Command parameters (optional, e.g., {"recipe_id": "BATCH-001"})
            command_id: Custom command ID (auto-generated if not provided)

        Returns:
            The command_id (for tracking replies)

        Example:
            cmd_id = await unit.send_command("Start", {"recipe_id": "BATCH-001", "procedure": "Concentration"})
        """
        import uuid

        cmd_id = command_id or str(uuid.uuid4())
        cmd_payload = {
            "command_id": cmd_id,
            "command": command_type,
            "args": [parameters] if parameters else [],
            "source": "recipe_controller",
            "expected_version": "1.0.0",
        }

        await self.bus.put_seam(self._make_path("cmd"), cmd_payload)
        self.log.debug(f"Sent S88 command {command_type} with ID {cmd_id}")
        return cmd_id

    async def update_phase(self, phase_id: str):
        """
        Update current phase_id in unit.intent seam.

        Args:
            phase_id: Phase identifier (e.g., "Prime", "Feed", "Concentrate")

        Example:
            await unit.update_phase("Prime")
        """
        intent = await self.get_intent()
        intent["phase_id"] = phase_id
        await self.bus.put_seam(self._make_path("intent"), intent)
        self.log.debug(f"Updated phase to: {phase_id}")

    async def close(self):
        """Close client and cleanup resources."""
        await self.bus.close()
