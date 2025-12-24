"""Centralized exception hierarchy for Supertape.

This module defines all exceptions used throughout the Supertape codebase,
organized in a clear hierarchy that reflects the architecture.
"""


class SupertapeException(Exception):
    """Base exception for all Supertape errors."""

    pass


class StreamProcessingError(SupertapeException):
    """Base for all stream processing errors (audio and file)."""

    pass


#####################################################################
# Audio Stream Exceptions
#####################################################################


class AudioStreamError(StreamProcessingError):
    """Audio stream processing errors."""

    pass


class AudioStreamInterruption(AudioStreamError):
    """Audio stream was interrupted."""

    def __init__(self, reason: str) -> None:
        super().__init__("Audio stream interrupted: " + reason)


#####################################################################
# File Processing Exceptions
#####################################################################


class FileProcessingError(StreamProcessingError):
    """File processing errors."""

    pass


class InvalidCRCError(FileProcessingError):
    """Invalid CRC checksum in data block."""

    pass


class InvalidBlockType(FileProcessingError):
    """Unknown or invalid block type encountered."""

    def __init__(self, type: int) -> None:
        super().__init__("Unknown type for Alice block: " + hex(type))
        self.type: int = type


class UnexpectedBlockType(FileProcessingError):
    """Received unexpected block type in sequence."""

    def __init__(self, received_type: int, expected_type: int) -> None:
        super().__init__(
            "Received block type " + hex(received_type) + " while expecting type " + hex(expected_type)
        )
        self.received_type: int = received_type
        self.expected_type: int = expected_type


#####################################################################
# Repository Exceptions
#####################################################################


class RepositoryError(SupertapeException):
    """Repository operation errors."""

    pass


#####################################################################
# Compilation Exceptions
#####################################################################


class CompilationError(SupertapeException):
    """Compilation and assembly errors."""

    pass
