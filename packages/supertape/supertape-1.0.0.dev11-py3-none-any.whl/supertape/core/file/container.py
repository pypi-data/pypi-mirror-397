"""K7 container support for multi-file tape archives.

This module provides data structures and utilities for working with k7 files
that contain multiple tape files. Two format variants are supported:

1. Standard K7: Files are concatenated sequentially without container headers
2. ALK7 K7: DCAlice emulator format with 16-byte headers before each file

Example usage:
    >>> from supertape.core.file.container import K7Container, K7Format
    >>> from supertape.core.file.load import container_load
    >>>
    >>> # Load all files from a multi-file k7
    >>> container = container_load("tapes.k7")
    >>> print(f"Container has {len(container)} files")
    >>> for tape_file in container:
    ...     print(tape_file.fname)
"""

from __future__ import annotations

from collections.abc import Iterator
from enum import Enum

from supertape.core.file.api import TapeFile


class K7Format(Enum):
    """K7 container format variant.

    Attributes:
        STANDARD: Standard MC-10/Alice format with concatenated files
        ALK7: DCAlice emulator format with 16-byte container headers
    """

    STANDARD = "standard"
    ALK7 = "alk7"


class ALK7Header:
    """ALK7 container header (16 bytes).

    The ALK7 format is used by the DCAlice emulator to store multiple
    tape files in a single .k7 file. Each file is prefixed with a 16-byte
    header containing metadata.

    Header structure:
        Bytes 0-3:   Signature "ALK7" (0x41 0x4C 0x4B 0x37)
        Bytes 4-7:   Reserved (typically 0x00 0x00 0x00 0x00)
        Bytes 8-11:  File size in bytes (little-endian uint32)
        Bytes 12-15: Flags (typically 0x7F 0x00 0x00 0x00)

    Attributes:
        signature: 4-byte signature (must be b"ALK7")
        metadata: 12-byte metadata section (reserved, size, flags)
    """

    def __init__(self, signature: bytes, metadata: bytes) -> None:
        """Initialize ALK7 header.

        Args:
            signature: 4-byte signature (must be b"ALK7")
            metadata: 12-byte metadata section

        Raises:
            ValueError: If signature is not b"ALK7" or lengths are invalid
        """
        if len(signature) != 4:
            raise ValueError(f"Signature must be 4 bytes, got {len(signature)}")
        if signature != b"ALK7":
            raise ValueError(f"Invalid ALK7 signature: {signature!r}")
        if len(metadata) != 12:
            raise ValueError(f"Metadata must be 12 bytes, got {len(metadata)}")

        self.signature: bytes = signature
        self.metadata: bytes = metadata

    @classmethod
    def from_bytes(cls, data: bytes) -> ALK7Header:
        """Parse ALK7 header from 16 bytes.

        Args:
            data: 16-byte header data

        Returns:
            Parsed ALK7Header object

        Raises:
            ValueError: If data is not exactly 16 bytes or signature is invalid
        """
        if len(data) != 16:
            raise ValueError(f"ALK7 header must be exactly 16 bytes, got {len(data)}")

        signature = data[0:4]
        if signature != b"ALK7":
            raise ValueError(f"Invalid ALK7 signature: {signature!r} (expected b'ALK7')")

        metadata = data[4:16]
        return cls(signature, metadata)

    def to_bytes(self) -> bytes:
        """Serialize header to 16 bytes.

        Returns:
            16-byte header data
        """
        return self.signature + self.metadata

    @classmethod
    def create(cls, file_size: int) -> ALK7Header:
        """Create ALK7 header for a file of given size.

        This is a convenience method for generating headers when creating
        new ALK7 format k7 files.

        Args:
            file_size: Size of the tape file in bytes

        Returns:
            ALK7Header with appropriate metadata

        Raises:
            ValueError: If file_size is negative or exceeds 32-bit uint max
        """
        if file_size < 0:
            raise ValueError(f"File size cannot be negative: {file_size}")
        if file_size > 0xFFFFFFFF:
            raise ValueError(f"File size exceeds 32-bit maximum: {file_size}")

        # Metadata layout:
        # Bytes 0-3:  Reserved (0x00 0x00 0x00 0x00)
        # Bytes 4-7:  File size (little-endian uint32)
        # Bytes 8-11: Flags (0x7F 0x00 0x00 0x00 is standard)
        metadata = b"\x00\x00\x00\x00"  # Reserved
        metadata += file_size.to_bytes(4, "little")  # File size
        metadata += b"\x7f\x00\x00\x00"  # Standard flags

        return cls(signature=b"ALK7", metadata=metadata)

    def get_file_size(self) -> int:
        """Extract file size from metadata.

        Returns:
            File size in bytes (from metadata bytes 4-7)
        """
        return int.from_bytes(self.metadata[4:8], "little")

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        size = self.get_file_size()
        return f"ALK7Header(size={size})"

    def __eq__(self, other: object) -> bool:
        """Compare headers for equality."""
        if not isinstance(other, ALK7Header):
            return False
        return self.signature == other.signature and self.metadata == other.metadata


class K7Container:
    """Container for multiple tape files in k7 format.

    A K7Container represents a collection of tape files stored in either
    standard (concatenated) or ALK7 (header-prefixed) format. It provides
    a unified interface for working with multi-file k7 archives.

    Attributes:
        files: List of TapeFile objects in the container
        format: K7Format indicating the container variant (STANDARD or ALK7)

    Example:
        >>> container = K7Container([file1, file2, file3], K7Format.STANDARD)
        >>> print(f"Container has {len(container)} files")
        >>> for i, tape_file in enumerate(container):
        ...     print(f"File {i}: {tape_file.fname}")
    """

    def __init__(self, files: list[TapeFile], format: K7Format = K7Format.STANDARD) -> None:
        """Initialize K7Container.

        Args:
            files: List of TapeFile objects
            format: Container format (default: K7Format.STANDARD)
        """
        self.files: list[TapeFile] = files
        self.format: K7Format = format

    def __len__(self) -> int:
        """Return number of files in container.

        Returns:
            Number of tape files
        """
        return len(self.files)

    def __getitem__(self, index: int) -> TapeFile:
        """Get file by index.

        Args:
            index: Zero-based file index

        Returns:
            TapeFile at the specified index

        Raises:
            IndexError: If index is out of range
        """
        return self.files[index]

    def __iter__(self) -> Iterator[TapeFile]:
        """Iterate over files in container.

        Yields:
            TapeFile objects in order
        """
        return iter(self.files)

    def __repr__(self) -> str:
        """Return string representation for debugging."""
        file_names = [f.fname for f in self.files]
        return f"K7Container(format={self.format.value}, files={file_names})"

    def __eq__(self, other: object) -> bool:
        """Compare containers for equality."""
        if not isinstance(other, K7Container):
            return False
        return self.files == other.files and self.format == other.format
