"""
Bus envelopes module.

Defines message envelope structures for event-based communication.
"""

from typing import Any, Dict, List, Literal
from pydantic import BaseModel, Field, validator


class Announce(BaseModel):
    """Announce message for service discovery and heartbeat.

    Sent on startup and as periodic heartbeat.

    Fields per spec §8.1:
    - msg_type="Announce"
    - service_id
    - service_role
    - contract
    - contract_version
    - capabilities[]
    - config_hash
    - health
    - ts
    """

    msg_type: Literal["Announce"] = Field(default="Announce")
    service_id: str
    service_role: str
    contract: str
    contract_version: str
    capabilities: List[str]
    config_hash: str
    health: str
    ts: str

    class Config:
        extra = "forbid"  # Forbid unknown keys

    @validator("msg_type")
    def validate_msg_type(cls, v):
        """Validate msg_type is exactly 'Announce'."""
        if v != "Announce":
            from ..logging.errors import BusDecodeError

            raise BusDecodeError(
                f"Invalid msg_type for Announce: expected 'Announce', got '{v}'"
            )
        return v

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for bus transmission."""
        return self.dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Announce":
        """Create from dictionary received from bus.

        Args:
            data: Dictionary containing message fields

        Returns:
            Announce instance

        Raises:
            BusDecodeError: If validation fails
        """
        from ..logging.errors import BusDecodeError

        try:
            return cls(**data)
        except Exception as e:
            raise BusDecodeError(
                f"Failed to decode Announce message: {e}",
                raw_payload=data,
                msg_type="Announce",
            ) from e


class StateEvent(BaseModel):
    """StateEvent message for publishing state changes.

    Published after state-relevant commands (accepted or refused).

    Fields per spec §8.2:
    - msg_type="StateEvent"
    - contract
    - contract_version
    - entity_id
    - seq (monotonic per entity)
    - payload[] (list-of-dicts; payload[0] mirrors seam fields)
    - ts
    """

    msg_type: Literal["StateEvent"] = Field(default="StateEvent")
    contract: str
    contract_version: str
    entity_id: str
    seq: int
    payload: List[Dict[str, Any]]
    ts: str

    class Config:
        extra = "forbid"  # Forbid unknown keys

    @validator("msg_type")
    def validate_msg_type(cls, v):
        """Validate msg_type is exactly 'StateEvent'."""
        if v != "StateEvent":
            from ..logging.errors import BusDecodeError

            raise BusDecodeError(
                f"Invalid msg_type for StateEvent: expected 'StateEvent', got '{v}'"
            )
        return v

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for bus transmission."""
        return self.dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StateEvent":
        """Create from dictionary received from bus.

        Args:
            data: Dictionary containing message fields

        Returns:
            StateEvent instance

        Raises:
            BusDecodeError: If validation fails
        """
        from ..logging.errors import BusDecodeError

        try:
            return cls(**data)
        except Exception as e:
            raise BusDecodeError(
                f"Failed to decode StateEvent message: {e}",
                raw_payload=data,
                msg_type="StateEvent",
            ) from e


class CommandRequest(BaseModel):
    """CommandRequest message for sending commands to entities.

    Must be idempotent via command_id.

    Fields per spec §8.3:
    - msg_type="CommandRequest"
    - command_id
    - contract (Actuator | Sensor | Unit | Driver)
    - expected_version
    - target_id
    - command
    - args[]
    - source
    - ts
    """

    msg_type: Literal["CommandRequest"] = Field(default="CommandRequest")
    command_id: str
    contract: str
    expected_version: str
    target_id: str
    command: str
    args: List[Dict[str, Any]]
    source: str
    ts: str

    class Config:
        extra = "forbid"  # Forbid unknown keys

    @validator("msg_type")
    def validate_msg_type(cls, v):
        """Validate msg_type is exactly 'CommandRequest'."""
        if v != "CommandRequest":
            from ..logging.errors import BusDecodeError

            raise BusDecodeError(
                f"Invalid msg_type for CommandRequest: expected 'CommandRequest', got '{v}'"
            )
        return v

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for bus transmission."""
        return self.dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CommandRequest":
        """Create from dictionary received from bus.

        Args:
            data: Dictionary containing message fields

        Returns:
            CommandRequest instance

        Raises:
            BusDecodeError: If validation fails
        """
        from ..logging.errors import BusDecodeError

        try:
            return cls(**data)
        except Exception as e:
            raise BusDecodeError(
                f"Failed to decode CommandRequest message: {e}",
                raw_payload=data,
                msg_type="CommandRequest",
            ) from e

    def validate_version(self, actual_version: str) -> None:
        """Validate MAJOR version compatibility.

        Args:
            actual_version: The actual contract version to compare against

        Raises:
            VersionMismatch: If MAJOR versions don't match
        """
        from ..logging.errors import VersionMismatch

        try:
            expected_major = int(self.expected_version.split(".")[0])
            actual_major = int(actual_version.split(".")[0])

            if expected_major != actual_major:
                raise VersionMismatch(
                    expected_version=self.expected_version,
                    actual_version=actual_version,
                    target_id=self.target_id,
                    command_id=self.command_id,
                )
        except (ValueError, IndexError) as e:
            from ..logging.errors import BusDecodeError

            raise BusDecodeError(
                f"Invalid version format: expected_version='{self.expected_version}', actual_version='{actual_version}'",
                command_id=self.command_id,
            ) from e


class CommandReply(BaseModel):
    """CommandReply message responding to CommandRequest.

    Every CommandRequest must receive a CommandReply.

    Fields per spec §8.3:
    - msg_type="CommandReply"
    - command_id
    - target_id
    - accepted: bool
    - reason: string
    - resulting_state: string
    - ts
    """

    msg_type: Literal["CommandReply"] = Field(default="CommandReply")
    command_id: str
    target_id: str
    accepted: bool
    reason: str
    resulting_state: str
    ts: str

    class Config:
        extra = "forbid"  # Forbid unknown keys

    @validator("msg_type")
    def validate_msg_type(cls, v):
        """Validate msg_type is exactly 'CommandReply'."""
        if v != "CommandReply":
            from ..logging.errors import BusDecodeError

            raise BusDecodeError(
                f"Invalid msg_type for CommandReply: expected 'CommandReply', got '{v}'"
            )
        return v

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for bus transmission."""
        return self.dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CommandReply":
        """Create from dictionary received from bus.

        Args:
            data: Dictionary containing message fields

        Returns:
            CommandReply instance

        Raises:
            BusDecodeError: If validation fails
        """
        from ..logging.errors import BusDecodeError

        try:
            return cls(**data)
        except Exception as e:
            raise BusDecodeError(
                f"Failed to decode CommandReply message: {e}",
                raw_payload=data,
                msg_type="CommandReply",
            ) from e
