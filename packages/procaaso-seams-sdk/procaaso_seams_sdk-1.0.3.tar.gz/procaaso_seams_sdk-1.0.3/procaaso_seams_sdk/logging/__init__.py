"""
Logging module.

Provides SDK exception and error types.
"""

from .errors import (
    ProcaasoSeamsError,
    SchemaValidationError,
    CommandRejectedError,
    IdempotencyConflictError,
    BusConnectionError,
    BusDecodeError,
    InvalidCommand,
    UnsupportedCommand,
    VersionMismatch,
    PreconditionFailed,
    HardwareFault,
)

__all__ = [
    "ProcaasoSeamsError",
    "SchemaValidationError",
    "CommandRejectedError",
    "IdempotencyConflictError",
    "BusConnectionError",
    "BusDecodeError",
    "InvalidCommand",
    "UnsupportedCommand",
    "VersionMismatch",
    "PreconditionFailed",
    "HardwareFault",
]
