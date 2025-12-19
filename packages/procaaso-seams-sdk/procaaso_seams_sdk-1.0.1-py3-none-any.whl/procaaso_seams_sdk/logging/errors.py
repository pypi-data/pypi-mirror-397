"""
Logging errors module.

Defines error handling and logging functionality.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


class ProcaasoSeamsError(Exception):
    """Base exception for all Procaaso Seams SDK errors.

    All SDK exceptions inherit from this to allow easy catching
    and differentiation from other exceptions.
    """

    def __init__(self, message: str, **context):
        """Initialize error with message and optional context.

        Args:
            message: Error message
            **context: Additional context for observability (e.g., command_id, target_id)
        """
        super().__init__(message)
        self.message = message
        self.context = context

    def __str__(self) -> str:
        """String representation with context."""
        if self.context:
            ctx_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} [{ctx_str}]"
        return self.message


@dataclass
class SchemaValidationError(ProcaasoSeamsError):
    """Raised when seam data fails schema validation.

    Examples:
    - Missing required attribute
    - Invalid field type
    - Schema ID mismatch
    - Bad seam shape
    """

    path: str
    expected_schema: Optional[str] = None
    actual_value: Optional[Any] = None
    validation_error: Optional[str] = None

    def __init__(
        self,
        path: str,
        expected_schema: Optional[str] = None,
        actual_value: Optional[Any] = None,
        validation_error: Optional[str] = None,
    ):
        """Initialize schema validation error.

        Args:
            path: Seam path that failed validation
            expected_schema: Expected schema ID
            actual_value: Actual value that failed
            validation_error: Specific validation failure message
        """
        self.path = path
        self.expected_schema = expected_schema
        self.actual_value = actual_value
        self.validation_error = validation_error

        msg = f"Schema validation failed for '{path}'"
        if validation_error:
            msg += f": {validation_error}"
        if expected_schema:
            msg += f" (expected schema: {expected_schema})"

        super().__init__(msg, path=path)

    def __str__(self) -> str:
        """Detailed string representation for debugging."""
        parts = [f"SchemaValidationError: {self.message}"]
        if self.actual_value is not None:
            parts.append(f"  Actual value: {self.actual_value}")
        return "\n".join(parts)


@dataclass
class CommandRejectedError(ProcaasoSeamsError):
    """Raised when a command is rejected by validation or preconditions.

    This maps to a CommandReply with accepted=False.
    """

    command: str
    target_id: str
    reason: str
    command_id: Optional[str] = None

    def __init__(
        self,
        command: str,
        target_id: str,
        reason: str,
        command_id: Optional[str] = None,
    ):
        """Initialize command rejected error.

        Args:
            command: Command that was rejected
            target_id: Target entity ID
            reason: Reason for rejection
            command_id: Optional command identifier
        """
        self.command = command
        self.target_id = target_id
        self.reason = reason
        self.command_id = command_id

        msg = f"Command '{command}' rejected for {target_id}: {reason}"

        context = {"command": command, "target_id": target_id}
        if command_id:
            context["command_id"] = command_id

        super().__init__(msg, **context)


@dataclass
class IdempotencyConflictError(ProcaasoSeamsError):
    """Raised when duplicate command_id arrives with different payload.

    This indicates a potential bug in the caller - same command_id
    should always have the same command/args/target.
    """

    command_id: str
    cached_payload: Dict[str, Any]
    new_payload: Dict[str, Any]

    def __init__(
        self,
        command_id: str,
        cached_payload: Dict[str, Any],
        new_payload: Dict[str, Any],
    ):
        """Initialize idempotency conflict error.

        Args:
            command_id: Conflicting command identifier
            cached_payload: Previously cached command payload
            new_payload: New command payload that differs
        """
        self.command_id = command_id
        self.cached_payload = cached_payload
        self.new_payload = new_payload

        msg = f"Idempotency conflict: command_id '{command_id}' reused with different payload"

        super().__init__(msg, command_id=command_id)

    def __str__(self) -> str:
        """Detailed string representation showing payload differences."""
        parts = [f"IdempotencyConflictError: {self.message}"]
        parts.append(f"  Cached: {self.cached_payload}")
        parts.append(f"  New: {self.new_payload}")
        return "\n".join(parts)


class BusConnectionError(ProcaasoSeamsError):
    """Raised when bus connection fails or is lost.

    Examples:
    - Failed to connect to message broker
    - Connection lost during operation
    - Timeout waiting for connection
    """

    def __init__(self, message: str, endpoint: Optional[str] = None, **context):
        """Initialize bus connection error.

        Args:
            message: Error message
            endpoint: Optional bus endpoint that failed
            **context: Additional context
        """
        if endpoint:
            context["endpoint"] = endpoint
        super().__init__(message, **context)


class BusDecodeError(ProcaasoSeamsError):
    """Raised when bus message cannot be decoded.

    Examples:
    - Invalid JSON payload
    - Missing required envelope fields
    - Unexpected message format
    - Pydantic validation failure
    """

    def __init__(
        self,
        message: str,
        raw_payload: Optional[Any] = None,
        msg_type: Optional[str] = None,
        **context,
    ):
        """Initialize bus decode error.

        Args:
            message: Error message
            raw_payload: Raw payload that failed to decode
            msg_type: Expected message type
            **context: Additional context
        """
        if msg_type:
            context["msg_type"] = msg_type
        if raw_payload is not None:
            context["raw_payload"] = str(raw_payload)[:200]  # Truncate for logging
        super().__init__(message, **context)


# Additional errors from SDK spec for completeness
class InvalidCommand(CommandRejectedError):
    """Command is structurally invalid or malformed."""

    pass


class UnsupportedCommand(CommandRejectedError):
    """Command is not in supported_commands list."""

    def __init__(
        self,
        command: str,
        target_id: str,
        supported_commands: list,
        command_id: Optional[str] = None,
    ):
        """Initialize unsupported command error.

        Args:
            command: Command that is unsupported
            target_id: Target entity ID
            supported_commands: List of supported commands
            command_id: Optional command identifier
        """
        reason = f"Command not in supported_commands: {supported_commands}"
        super().__init__(command, target_id, reason, command_id)
        self.supported_commands = supported_commands


class VersionMismatch(CommandRejectedError):
    """Contract version mismatch (MAJOR version incompatible)."""

    def __init__(
        self,
        expected_version: str,
        actual_version: str,
        target_id: str,
        command_id: Optional[str] = None,
    ):
        """Initialize version mismatch error.

        Args:
            expected_version: Version expected by caller
            actual_version: Actual contract version
            target_id: Target entity ID
            command_id: Optional command identifier
        """
        reason = (
            f"Version mismatch: expected {expected_version}, actual {actual_version}"
        )
        super().__init__("(version check)", target_id, reason, command_id)
        self.expected_version = expected_version
        self.actual_version = actual_version


class PreconditionFailed(CommandRejectedError):
    """Command precondition not met (e.g., wrong state, mode, or faulted)."""

    def __init__(
        self,
        command: str,
        target_id: str,
        precondition: str,
        current_state: Optional[Dict[str, Any]] = None,
        command_id: Optional[str] = None,
    ):
        """Initialize precondition failed error.

        Args:
            command: Command that failed precondition
            target_id: Target entity ID
            precondition: Description of failed precondition
            current_state: Optional current state for context
            command_id: Optional command identifier
        """
        reason = f"Precondition failed: {precondition}"
        super().__init__(command, target_id, reason, command_id)
        self.precondition = precondition
        self.current_state = current_state


class HardwareFault(ProcaasoSeamsError):
    """Hardware or device fault detected.

    Should trigger state.faulted=True and publish StateEvent.
    """

    def __init__(
        self,
        target_id: str,
        fault_code: int,
        fault_text: str,
        **context,
    ):
        """Initialize hardware fault error.

        Args:
            target_id: Faulted entity ID
            fault_code: Numeric fault code
            fault_text: Human-readable fault description
            **context: Additional context
        """
        msg = f"Hardware fault on {target_id}: [{fault_code}] {fault_text}"
        context.update({"target_id": target_id, "fault_code": fault_code})
        super().__init__(msg, **context)
        self.target_id = target_id
        self.fault_code = fault_code
        self.fault_text = fault_text
