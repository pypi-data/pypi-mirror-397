from __future__ import annotations

from typing import BinaryIO

from supertape.core.file.api import TapeFile, TapeFileListener
from supertape.core.file.block import BlockParser
from supertape.core.file.container import ALK7Header, K7Container, K7Format
from supertape.core.file.tapefile import TapeFileLoader


class _filelistener(TapeFileListener):
    """Single-file listener that keeps only the last file processed."""

    def __init__(self) -> None:
        self.file: TapeFile | None = None

    def process_file(self, file: TapeFile) -> None:
        self.file = file


class _MultiFileListener(TapeFileListener):
    """Multi-file listener that accumulates all files processed."""

    def __init__(self) -> None:
        self.files: list[TapeFile] = []

    def process_file(self, file: TapeFile) -> None:
        self.files.append(file)


def _load_from_stream(stream: BinaryIO) -> TapeFile:
    """Load a TapeFile from a binary stream.

    Args:
        stream: Binary stream to read .k7 file data from

    Returns:
        TapeFile object loaded from the stream

    Raises:
        ValueError: If no tape file was loaded from the stream
    """
    file_listener = _filelistener()
    tape_file_loader = TapeFileLoader([file_listener])
    block_parser = BlockParser([tape_file_loader])

    while True:
        byte: bytes = stream.read(1)

        if len(byte) == 0:
            break

        block_parser.process_byte(byte[0])

    if file_listener.file is None:
        raise ValueError("No tape file was loaded")
    return file_listener.file


def detect_k7_format(file_path: str | BinaryIO) -> K7Format:
    """Detect k7 format by reading first 4 bytes.

    Checks if the file starts with "ALK7" signature (ALK7 format) or
    standard leader bytes (standard format).

    Args:
        file_path: Path to k7 file or binary stream

    Returns:
        K7Format.ALK7 if starts with "ALK7", else K7Format.STANDARD

    Example:
        >>> format = detect_k7_format("myfile.k7")
        >>> if format == K7Format.ALK7:
        ...     print("DCAlice ALK7 format detected")
    """

    def _detect_from_stream(stream: BinaryIO) -> K7Format:
        pos = stream.tell()
        magic = stream.read(4)
        stream.seek(pos)  # Reset position

        if magic == b"ALK7":
            return K7Format.ALK7
        else:
            return K7Format.STANDARD

    if isinstance(file_path, str):
        with open(file_path, "rb") as f:
            return _detect_from_stream(f)
    else:
        return _detect_from_stream(file_path)


def _load_container_from_stream(stream: BinaryIO, format: K7Format) -> K7Container:
    """Load all files from a binary stream.

    This internal function handles the actual loading of multi-file k7
    containers. It supports both standard (concatenated) and ALK7
    (header-prefixed) formats.

    Args:
        stream: Binary stream to read from
        format: K7 format variant (STANDARD or ALK7)

    Returns:
        K7Container with all loaded tape files

    Raises:
        ValueError: If no files were loaded or ALK7 headers are invalid
    """
    file_listener = _MultiFileListener()
    tape_file_loader = TapeFileLoader([file_listener])
    block_parser = BlockParser([tape_file_loader])

    while True:
        # For ALK7: skip 16-byte headers before each file
        if format == K7Format.ALK7:
            header_bytes = stream.read(16)
            if len(header_bytes) == 0:
                break  # End of file
            if len(header_bytes) < 16:
                # Incomplete header at end of file - stop processing
                break

            # Validate ALK7 header
            try:
                ALK7Header.from_bytes(header_bytes)
                # Successfully parsed header, continue to tape data
            except ValueError:
                # Not a valid ALK7 header - could be end of files or corruption
                break

        # Read tape data byte-by-byte until EOF or next ALK7 header
        while True:
            # Peek ahead for ALK7 signature if in ALK7 mode
            if format == K7Format.ALK7:
                pos = stream.tell()
                peek = stream.read(4)
                if len(peek) == 0:
                    break  # End of stream
                stream.seek(pos)  # Reset position
                if peek == b"ALK7":
                    break  # Next file's ALK7 header

            byte = stream.read(1)
            if len(byte) == 0:
                break  # End of stream

            block_parser.process_byte(byte[0])

        # If we reached end of stream, exit outer loop
        if len(byte) == 0 and format == K7Format.STANDARD:
            break
        if format == K7Format.ALK7:
            # Check if there are more files
            pos = stream.tell()
            peek = stream.read(4)
            if len(peek) < 4 or peek != b"ALK7":
                break  # No more files
            stream.seek(pos)  # Reset for next iteration

    return K7Container(file_listener.files, format)


def container_load(file_name: str | BinaryIO) -> K7Container:
    """Load all files from a k7 container.

    This function loads multi-file k7 containers in both standard
    (concatenated) and ALK7 (header-prefixed) formats. The format is
    automatically detected.

    Args:
        file_name: Path to k7 file or binary stream

    Returns:
        K7Container with all tape files

    Raises:
        ValueError: If no files were loaded
        OSError: If file cannot be opened

    Example:
        >>> container = container_load("multi.k7")
        >>> print(f"Found {len(container)} files")
        >>> for i, tape_file in enumerate(container):
        ...     print(f"File {i}: {tape_file.fname}")
    """
    if isinstance(file_name, str):
        format = detect_k7_format(file_name)
        with open(file_name, "rb") as tape_file:
            container = _load_container_from_stream(tape_file, format)
    else:
        format = detect_k7_format(file_name)
        container = _load_container_from_stream(file_name, format)

    if len(container) == 0:
        raise ValueError("No tape file was loaded")

    return container


def file_load(file_name: str | BinaryIO, index: int = 0) -> TapeFile:
    """Load a TapeFile from a file path or binary stream.

    This function now supports loading specific files from multi-file k7
    containers using the index parameter. For backward compatibility, it
    defaults to returning the first file (index 0).

    Args:
        file_name: Either a file path (str) or a binary stream (BinaryIO)
        index: File index to load (default: 0 for first file)

    Returns:
        TapeFile object at the specified index

    Raises:
        ValueError: If no tape file was loaded
        IndexError: If index is out of range

    Example:
        >>> # Load first file (backward compatible)
        >>> file = file_load("myfile.k7")
        >>>
        >>> # Load third file from multi-file k7
        >>> file = file_load("myfile.k7", index=2)
    """
    container = container_load(file_name)
    if index < 0 or index >= len(container):
        raise IndexError(f"File index {index} out of range (container has {len(container)} files)")
    return container[index]
