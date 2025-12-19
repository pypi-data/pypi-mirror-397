"""
Bus client module.

Provides async gateway to Procaaso ENS sidecar.
Containers never speak to event bus directly; all communication flows through the sidecar.
"""

import asyncio
from datetime import datetime
from typing import Any, AsyncIterator, Dict, Optional

import aiohttp

from ..logging.errors import BusConnectionError, BusDecodeError
from .envelopes import Announce, CommandReply, CommandRequest, StateEvent


class BusClient:
    """Async gateway to Procaaso ENS sidecar.

    The sidecar exposes HTTP endpoints for:
    - Getting current seam values (cached)
    - Setting seam values
    - Publishing Announce / StateEvent / CommandReply
    - Streaming CommandRequest messages

    Containers never speak directly to the event bus.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        session: Optional[aiohttp.ClientSession] = None,
        log: Any = None,
    ):
        """Initialize BusClient.

        Args:
            base_url: Sidecar HTTP endpoint base URL
            session: Optional aiohttp session (will create if None)
            log: Logger instance
        """
        self.base_url = base_url.rstrip("/")
        self._session = session
        self._owns_session = session is None
        self.log = log
        self._streaming_tasks: Dict[str, asyncio.Task] = {}

    async def __aenter__(self):
        """Async context manager entry."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self):
        """Close client and clean up resources."""
        # Cancel streaming tasks
        for task in self._streaming_tasks.values():
            task.cancel()
        if self._streaming_tasks:
            await asyncio.gather(*self._streaming_tasks.values(), return_exceptions=True)
        self._streaming_tasks.clear()

        # Close session if we own it
        if self._owns_session and self._session:
            await self._session.close()
            self._session = None

    async def get_seam(self, path: str) -> Dict[str, Any]:
        """Get current seam value from sidecar cache.

        Args:
            path: Seam path in format 'component.instrument.attribute'

        Returns:
            Dictionary containing seam value

        Raises:
            BusConnectionError: If sidecar unreachable
            BusDecodeError: If response payload invalid
        """
        if self._session is None:
            raise BusConnectionError("BusClient not initialized (session is None)")

        url = f"{self.base_url}/seams/{path}"
        try:
            async with self._session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                if self.log:
                    self.log.debug(f"get_seam({path}): {data}")
                return data
        except aiohttp.ClientError as e:
            raise BusConnectionError(f"Failed to get seam {path}: {e}")
        except Exception as e:
            raise BusDecodeError(f"Invalid response for seam {path}: {e}")

    async def put_seam(self, path: str, payload: Dict[str, Any]) -> None:
        """Set seam value via sidecar.

        Args:
            path: Seam path in format 'component.instrument.attribute'
            payload: Dictionary containing new seam value

        Raises:
            BusConnectionError: If sidecar unreachable
        """
        if self._session is None:
            raise BusConnectionError("BusClient not initialized (session is None)")

        url = f"{self.base_url}/seams/{path}"
        try:
            async with self._session.put(url, json=payload) as response:
                response.raise_for_status()
                if self.log:
                    self.log.debug(f"put_seam({path}): {payload}")
        except aiohttp.ClientError as e:
            raise BusConnectionError(f"Failed to put seam {path}: {e}")

    async def announce(self, msg: Announce) -> None:
        """Publish Announce message via sidecar.

        Args:
            msg: Announce envelope

        Raises:
            BusConnectionError: If sidecar unreachable
        """
        if self._session is None:
            raise BusConnectionError("BusClient not initialized (session is None)")

        url = f"{self.base_url}/messages/announce"
        try:
            payload = msg.to_dict()
            async with self._session.post(url, json=payload) as response:
                response.raise_for_status()
                if self.log:
                    self.log.info(f"Published Announce: {msg.service_id}")
        except aiohttp.ClientError as e:
            raise BusConnectionError(f"Failed to publish Announce: {e}")

    async def publish_state(self, msg: StateEvent) -> None:
        """Publish StateEvent message via sidecar.

        Args:
            msg: StateEvent envelope

        Raises:
            BusConnectionError: If sidecar unreachable
        """
        if self._session is None:
            raise BusConnectionError("BusClient not initialized (session is None)")

        url = f"{self.base_url}/messages/state"
        try:
            payload = msg.to_dict()
            async with self._session.post(url, json=payload) as response:
                response.raise_for_status()
                if self.log:
                    self.log.debug(f"Published StateEvent: {msg.entity_id} seq={msg.seq}")
        except aiohttp.ClientError as e:
            raise BusConnectionError(f"Failed to publish StateEvent: {e}")

    async def publish_reply(self, msg: CommandReply) -> None:
        """Publish CommandReply message via sidecar.

        Args:
            msg: CommandReply envelope

        Raises:
            BusConnectionError: If sidecar unreachable
        """
        if self._session is None:
            raise BusConnectionError("BusClient not initialized (session is None)")

        url = f"{self.base_url}/messages/reply"
        try:
            payload = msg.to_dict()
            async with self._session.post(url, json=payload) as response:
                response.raise_for_status()
                if self.log:
                    self.log.debug(
                        f"Published CommandReply: {msg.command_id} accepted={msg.accepted}"
                    )
        except aiohttp.ClientError as e:
            raise BusConnectionError(f"Failed to publish CommandReply: {e}")

    async def stream_commands(
        self,
        contract: str,
        target_id: str,
    ) -> AsyncIterator[CommandRequest]:
        """Stream CommandRequest messages from sidecar for a specific target.

        The sidecar handles filtering and routing based on contract + target_id.

        Args:
            contract: Contract type (e.g., 'Actuator')
            target_id: Target component ID

        Yields:
            CommandRequest envelopes

        Raises:
            BusConnectionError: If sidecar unreachable
            BusDecodeError: If message payload invalid
        """
        if self._session is None:
            raise BusConnectionError("BusClient not initialized (session is None)")

        url = f"{self.base_url}/messages/commands/stream"
        params = {
            "contract": contract,
            "target_id": target_id,
        }

        try:
            async with self._session.get(url, params=params) as response:
                response.raise_for_status()

                # Server-sent events or line-delimited JSON stream
                async for line in response.content:
                    if not line:
                        continue

                    try:
                        # Decode line as JSON
                        data = line.decode("utf-8").strip()
                        if not data:
                            continue

                        import json

                        payload = json.loads(data)

                        # Decode to CommandRequest envelope
                        request = CommandRequest.from_dict(payload)

                        if self.log:
                            self.log.debug(
                                f"Received command: {request.command_id} "
                                f"cmd={request.command} target={request.target_id}"
                            )

                        yield request

                    except (json.JSONDecodeError, BusDecodeError) as e:
                        if self.log:
                            self.log.error(f"Failed to decode command message: {e}")
                        # Continue streaming despite decode errors
                        continue

        except aiohttp.ClientError as e:
            raise BusConnectionError(f"Failed to stream commands for {target_id}: {e}")
