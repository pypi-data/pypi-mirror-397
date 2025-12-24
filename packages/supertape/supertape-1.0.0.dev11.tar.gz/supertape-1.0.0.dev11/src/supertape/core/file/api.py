#####################################################################
# Data models
#####################################################################

from __future__ import annotations

from abc import ABC, abstractmethod

FILE_TYPE_BASIC = 0x00
FILE_TYPE_DATA = 0x01
FILE_TYPE_MACHINE = 0x02
FILE_TYPE_ASMSRC = 0x05

FILE_TYPE_NAMES = {0x00: "BASIC", 0x01: "DATA", 0x02: "MACHINE", 0x05: "ASMSRC"}

FILE_DATA_TYPE_BIN = 0x00
FILE_DATA_TYPE_ASC = 0xFF

FILE_GAP_NONE = 0x00
FILE_GAP_GAPS = 0xFF


class DataBlock:
    def __init__(self, type: int, body: list[int]) -> None:
        self.type: int = type
        self.body: list[int] = body
        self.checksum: int = (type + len(body) + sum(body)) % 256

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return "Block-" + hex(self.type) + "-" + str([hex(x) for x in self.body])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DataBlock):
            return False
        return self.type == other.type and self.body == other.body


class TapeFile:
    def __init__(self, blocks: list[DataBlock]) -> None:
        self.blocks: list[DataBlock] = blocks

        self.fname: str = self._get_name()
        self.fbody: list[int] = self._get_body()
        # Per official MC-10/Alice tape format spec (see TAPE_FORMAT.md:55-68)
        self.ftype: int = self.blocks[0].body[8]  # Byte 8: file type
        self.fdatatype: int = self.blocks[0].body[9]  # Byte 9: ASCII flag
        self.fgap: int = self.blocks[0].body[10]  # Byte 10: gap flag
        # Bytes 11-12: start address (little-endian)
        self.fstartaddress: int = self.blocks[0].body[11] + self.blocks[0].body[12] * 256
        # Bytes 13-14: load address (little-endian)
        self.floadaddress: int | None = (
            self.blocks[0].body[13] + self.blocks[0].body[14] * 256 if len(self.blocks[0].body) > 14 else None
        )

    def _get_name(self) -> str:
        fname = ""

        for b in self.blocks[0].body[0:8]:
            fname += chr(b)

        return fname.rstrip().rstrip("\x00").upper()  # Normalize to uppercase per CSAVEM format

    def _get_body(self) -> list[int]:
        body: list[int] = []

        for block in self.blocks[1:-1]:
            body += block.body

        return body

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TapeFile):
            return False
        return self.blocks == other.blocks

    def __str__(self) -> str:
        return "TapeFile{" + self.fname + "}"

    def calculate_duration(self, sample_rate: int = 44100) -> float:
        """Calculate the duration of this tape file in seconds.

        Calculates the playback duration by running the tape through the
        audio modulation pipeline and counting samples. This ensures
        perfect accuracy by using the same timing logic as actual playback.

        Args:
            sample_rate: Audio sample rate in Hz (default: 44100)

        Returns:
            Duration in seconds

        Example:
            >>> tape_file = TapeFile(blocks)
            >>> duration = tape_file.calculate_duration()
            >>> print(f"Duration: {duration:.1f}s")
            Duration: 45.3s
        """
        from supertape.core.audio.duration import calculate_duration

        return calculate_duration(self, sample_rate)

    def get_type_name(self) -> str:
        """Get human-readable file type name.

        Returns:
            String name of file type (e.g., "BASIC", "MACHINE", "DATA")
        """
        return FILE_TYPE_NAMES.get(self.ftype, "UNKNOWN")

    def is_basic_program(self) -> bool:
        """Check if this is a BASIC program.

        Returns:
            True if file type is BASIC
        """
        return self.ftype == FILE_TYPE_BASIC

    def is_machine_code(self) -> bool:
        """Check if this is machine code.

        Returns:
            True if file type is MACHINE
        """
        return self.ftype == FILE_TYPE_MACHINE

    def is_assembly_source(self) -> bool:
        """Check if this is assembly source.

        Returns:
            True if file type is ASMSRC
        """
        return self.ftype == FILE_TYPE_ASMSRC

    def is_data(self) -> bool:
        """Check if this is data.

        Returns:
            True if file type is DATA
        """
        return self.ftype == FILE_TYPE_DATA

    def get_size_bytes(self) -> int:
        """Get total size of file body in bytes.

        Returns:
            Number of bytes in file body
        """
        return len(self.fbody)

    def validate(self) -> list[str]:
        """Validate file structure and return any issues found.

        Checks for common problems like:
        - Empty filename
        - Invalid file type
        - Invalid address values

        Returns:
            List of issue descriptions (empty if valid)

        Example:
            >>> tape_file = TapeFile(blocks)
            >>> issues = tape_file.validate()
            >>> if issues:
            ...     print("Validation errors:", issues)
        """
        issues: list[str] = []

        if not self.fname.strip():
            issues.append("Empty filename")

        if self.ftype not in FILE_TYPE_NAMES:
            issues.append(f"Invalid file type: 0x{self.ftype:02X}")

        if self.fstartaddress > 0xFFFF:
            issues.append(f"Invalid start address: 0x{self.fstartaddress:04X}")

        if self.floadaddress is not None and self.floadaddress > 0xFFFF:
            issues.append(f"Invalid load address: 0x{self.floadaddress:04X}")

        return issues


#####################################################################
# Event management interfaces
#####################################################################


class BlockListener(ABC):
    """Abstract base class for block event listeners."""

    @abstractmethod
    def process_block(self, block: DataBlock) -> None:
        """Process a data block.

        Args:
            block: The data block to process
        """
        pass


class ByteListener(ABC):
    """Abstract base class for byte event listeners."""

    @abstractmethod
    def process_byte(self, value: int) -> None:
        """Process a byte value.

        Args:
            value: The byte value to process
        """
        pass

    @abstractmethod
    def process_silence(self) -> None:
        """Process a silence event."""
        pass


class TapeFileListener(ABC):
    """Abstract base class for tape file event listeners."""

    @abstractmethod
    def process_file(self, file: TapeFile) -> None:
        """Process a tape file.

        Args:
            file: The tape file to process
        """
        pass
