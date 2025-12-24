"""Save TapeFile objects to .k7 binary files."""

from __future__ import annotations

from supertape.core.file.api import ByteListener, TapeFile
from supertape.core.file.block import BlockSerializer
from supertape.core.file.container import ALK7Header, K7Container, K7Format
from supertape.core.file.tapefile import TapeFileSerializer


class _ByteCollector(ByteListener):
    """Collects bytes from serialization pipeline."""

    def __init__(self) -> None:
        self.bytes: list[int] = []

    def process_byte(self, value: int) -> None:
        """Process a byte from the serialization pipeline.

        Args:
            value: Byte value to process (must be 0-255)
        """
        self.bytes.append(value)

    def process_silence(self) -> None:
        """Process silence marker (no-op for file storage)."""
        pass


def _serialize_tape_file(tape: TapeFile) -> bytes:
    """Serialize a TapeFile to bytes.

    This is an internal helper function used by both file_save() and
    container_save() to convert a TapeFile to its binary representation.

    Args:
        tape: TapeFile object to serialize

    Returns:
        Bytes representing the serialized tape file
    """
    collector = _ByteCollector()
    serializer = BlockSerializer([collector])
    file_serializer = TapeFileSerializer([serializer])
    file_serializer.process_file(tape)
    return bytes(collector.bytes)


def file_save(filename: str, tape: TapeFile) -> None:
    """Save a TapeFile to a .k7 binary file.

    This function is the inverse of file_load(). It serializes a TapeFile
    object to the .k7 binary format used by emulators and cassette storage.

    The serialization pipeline:
    TapeFile → TapeFileSerializer → BlockSerializer → _ByteCollector → bytes → file

    Args:
        filename: Path to the .k7 file to create
        tape: TapeFile object to save

    Raises:
        OSError: If file cannot be written
        IOError: If file I/O operation fails
    """
    tape_bytes = _serialize_tape_file(tape)

    # Write bytes to disk
    with open(filename, "wb") as f:
        f.write(tape_bytes)


def container_save(filename: str, container: K7Container) -> None:
    """Save a K7Container to a .k7 binary file.

    Supports both standard (concatenated) and ALK7 (header-prefixed) formats.
    The format is determined by the container's format attribute.

    For standard format:
        Files are concatenated sequentially without additional headers.

    For ALK7 format:
        Each file is prefixed with a 16-byte ALK7 header containing metadata.

    Args:
        filename: Path to .k7 file to create
        container: K7Container with files to save

    Raises:
        ValueError: If container is empty
        OSError: If file cannot be written
        IOError: If file I/O operation fails

    Example:
        >>> from supertape.core.file.container import K7Container, K7Format
        >>> container = K7Container([file1, file2, file3], K7Format.STANDARD)
        >>> container_save("output.k7", container)
    """
    if len(container) == 0:
        raise ValueError("Cannot save empty container")

    with open(filename, "wb") as f:
        for tape_file in container:
            # Serialize tape file to bytes first
            tape_bytes = _serialize_tape_file(tape_file)

            # Write ALK7 header if needed
            if container.format == K7Format.ALK7:
                header = ALK7Header.create(file_size=len(tape_bytes))
                f.write(header.to_bytes())

            # Write tape data
            f.write(tape_bytes)
