"""
Bus idempotency module.

Ensures idempotent processing of messages.
"""

import asyncio
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from ..bus.envelopes import CommandReply, CommandRequest


class IdempotencyCache:
    """In-memory cache for command idempotency.

    Caches CommandReply by command_id to ensure idempotent processing.
    Duplicate commands return the cached reply without re-execution.

    Command IDs are permanently cached (no TTL) - commands must use unique IDs (UUIDs recommended).
    """

    def __init__(self):
        """Initialize idempotency cache.

        Command IDs are cached permanently to prevent re-execution.
        Use UUID-based command_ids to ensure uniqueness.
        """
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, command_id: str) -> Optional[Dict[str, Any]]:
        """Get cached reply for a command_id.

        Args:
            command_id: Unique command identifier

        Returns:
            Cached reply dict or None if not found
        """
        entry = self._cache.get(command_id)
        if not entry:
            return None

        return entry["reply"]

    def set(self, command_id: str, reply: Dict[str, Any]) -> None:
        """Cache a reply for a command_id.

        Args:
            command_id: Unique command identifier
            reply: CommandReply dictionary to cache
        """
        self._cache[command_id] = {"reply": reply}

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()


class IdempotencyStore:
    """Asyncio-safe in-memory idempotency tracker for CommandRequest handling.

    Tracks CommandRequest/CommandReply pairs by command_id permanently to prevent re-execution.
    Command IDs must be unique (UUIDs recommended) as they are never expired.

    Thread-safe using asyncio.Lock for concurrent access.
    """

    def __init__(self):
        """Initialize idempotency store.

        Command IDs are tracked permanently to prevent duplicate execution.
        Use UUID-based command_ids to ensure uniqueness.
        """
        self._store: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def seen(self, command_id: str) -> bool:
        """Check if a command_id has been seen before.

        Args:
            command_id: Unique command identifier

        Returns:
            True if command_id exists
        """
        async with self._lock:
            return command_id in self._store

    async def get(self, command_id: str) -> Optional["CommandReply"]:
        """Get cached CommandReply for a command_id.

        Args:
            command_id: Unique command identifier

        Returns:
            CommandReply instance or None if not found
        """
        from ..bus.envelopes import CommandReply

        async with self._lock:
            entry = self._store.get(command_id)
            if not entry:
                return None

            # Return CommandReply from stored dict
            return CommandReply.from_dict(entry["reply"])

    async def record(
        self,
        request: "CommandRequest",
        reply: Optional["CommandReply"] = None,
    ) -> None:
        """Record a CommandRequest (and optionally CommandReply).

        With attributeStates architecture, replies are written directly to
        bus_command_reply attribute by handlers, so reply parameter is optional.

        Args:
            request: CommandRequest that was processed
            reply: CommandReply that was generated (optional, may be None)

        Raises:
            IdempotencyConflictError: If same command_id exists with different
                command details (command, args, target_id, contract)
        """
        from ..bus.envelopes import CommandReply, CommandRequest
        from ..logging.errors import IdempotencyConflictError

        async with self._lock:
            command_id = request.command_id
            existing = self._store.get(command_id)

            if existing:
                # Command ID already exists - check for conflicts
                cached_req = existing["request"]

                # Compare critical fields that must match for same command_id
                if (
                    cached_req["command"] != request.command
                    or cached_req["target_id"] != request.target_id
                    or cached_req["contract"] != request.contract
                    or cached_req["args"] != request.args
                ):
                    # Conflict detected!
                    raise IdempotencyConflictError(
                        command_id=command_id,
                        cached_payload={
                            "command": cached_req["command"],
                            "target_id": cached_req["target_id"],
                            "contract": cached_req["contract"],
                            "args": cached_req["args"],
                        },
                        new_payload={
                            "command": request.command,
                            "target_id": request.target_id,
                            "contract": request.contract,
                            "args": request.args,
                        },
                    )

                # Same command details, this is a valid retry
                if reply:
                    self._store[command_id]["reply"] = reply.to_dict()
                return

            # New entry - store permanently
            self._store[command_id] = {
                "request": {
                    "command_id": request.command_id,
                    "command": request.command,
                    "target_id": request.target_id,
                    "contract": request.contract,
                    "args": request.args,
                    "expected_version": request.expected_version,
                    "source": request.source,
                },
                "reply": reply.to_dict() if reply else None,
            }

    async def clear(self) -> None:
        """Clear all stored entries."""
        async with self._lock:
            self._store.clear()
