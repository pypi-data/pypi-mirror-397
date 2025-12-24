"""Import command for the tape shell.

This module contains the command for importing external files into the database.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from supertape.cli.commands.base import ShellCommand
from supertape.core.assembly.encode import create_assembly_file
from supertape.core.audio.file_in import FileInput
from supertape.core.audio.modulation import AudioDemodulator
from supertape.core.basic.encode import BasicEncoder, BasicFileCompiler
from supertape.core.basic.minification import minify_basic
from supertape.core.basic.preprocess import preprocess_basic
from supertape.core.c.errors import CCompilerError, FCCNotFoundError
from supertape.core.file.api import TapeFile, TapeFileListener
from supertape.core.file.block import BlockParser
from supertape.core.file.bytes import ByteDecoder
from supertape.core.file.load import container_load, file_load
from supertape.core.file.operations import compile_c_source
from supertape.core.file.tapefile import TapeFileLoader

if TYPE_CHECKING:
    from supertape.cli.shell import TapeShell


class ImportCommand(ShellCommand):
    """Import external files into the tape database."""

    @property
    def name(self) -> str:
        return "import"

    @property
    def description(self) -> str:
        return "Import files into database"

    @property
    def usage(self) -> str:
        return "import <file> [file2] [file3] ..."

    @property
    def help_text(self) -> str:
        return """Import external files into the tape database

Usage: import <file1> [file2] [file3] ...

Supported formats:
  • .k7    - Binary tape files (supports multi-file containers)
  • .wav   - Audio recordings
  • .bas   - BASIC source (preprocessed and compiled)
  • .asm   - Assembly source (stored as ASMSRC)
  • .c     - C source (compiled to MACHINE code, generates .asm)

Files are added to the current database and can be:
  • Played with 'play <filename>'
  • Listed with 'list <filename>'
  • Removed with 'remove <filename>'

Examples:
  import game.bas
  import program.c           (generates program.asm)
  import tape.k7             (imports all files in container)
  import file1.bas file2.asm (import multiple files)

Note: If a file with the same name exists, a new version will be created"""

    def execute(self, shell: TapeShell, args: list[str]) -> None:
        """Execute import command."""
        if not args:
            shell.ui.show_error("Usage: import <file> [file2] [file3] ...")
            shell.ui.show_info("Supported formats: .k7, .wav, .bas, .asm, .c")
            return

        # Process each file
        success_count = 0
        error_count = 0

        for file_arg in args:
            try:
                file_path = Path(file_arg).expanduser().resolve()

                # Check file existence
                if not file_path.exists():
                    shell.ui.show_error(f"File not found: {file_arg}")
                    error_count += 1
                    continue

                if not file_path.is_file():
                    shell.ui.show_error(f"Not a file: {file_arg}")
                    error_count += 1
                    continue

                # Special handling for .k7 files to support multi-file containers
                if file_path.suffix.lower() == ".k7":
                    container = container_load(str(file_path))

                    # Show container info
                    if len(container) > 1:
                        shell.ui.show_info(f"Importing {len(container)} files from {file_path.name}")

                    # Import each file in the container
                    for i, tape_file in enumerate(container):
                        shell.repository.add_tape_file(tape_file)
                        file_type = shell.ui.file_type_names.get(tape_file.ftype, f"0x{tape_file.ftype:02X}")

                        if len(container) > 1:
                            shell.ui.show_success(
                                f"  [{i+1}/{len(container)}] {tape_file.fname} ({file_type})"
                            )
                        else:
                            shell.ui.show_success(
                                f"Imported {file_path.name} as {tape_file.fname} ({file_type})"
                            )

                        success_count += 1
                else:
                    # Process other file types (wav, bas, asm, c)
                    tape_file = self._import_file(shell, file_path)

                    # Add to repository (overwrites if exists)
                    shell.repository.add_tape_file(tape_file)

                    # Show success
                    file_type = shell.ui.file_type_names.get(tape_file.ftype, f"0x{tape_file.ftype:02X}")
                    shell.ui.show_success(f"Imported {file_path.name} as {tape_file.fname} ({file_type})")
                    success_count += 1

            except ValueError as e:
                shell.ui.show_error(f"{file_arg}: {e}")
                error_count += 1
            except FCCNotFoundError:
                shell.ui.show_error(f"{file_arg}: C compiler not available")
                shell.ui.show_info("Install FCC compiler to import C files")
                error_count += 1
            except CCompilerError as e:
                shell.ui.show_error(f"{file_arg}: Compilation failed: {e}")
                error_count += 1
            except Exception as e:
                shell.ui.show_error(f"{file_arg}: Import failed: {e}")
                error_count += 1

        # Summary
        if success_count > 0 or error_count > 0:
            shell.ui.print()
            if success_count > 0:
                shell.ui.show_info(f"Successfully imported {success_count} file(s)")
            if error_count > 0:
                shell.ui.show_warning(f"Failed to import {error_count} file(s)")

    def _detect_file_type(self, file_path: Path) -> str:
        """Detect file type from file extension.

        Args:
            file_path: Path to the file

        Returns:
            File type string: 'k7', 'wav', 'bas', 'asm', 'c'

        Raises:
            ValueError: If file type is unsupported
        """
        suffix = file_path.suffix.lower()
        type_map = {
            ".k7": "k7",
            ".wav": "wav",
            ".bas": "bas",
            ".asm": "asm",
            ".c": "c",
        }

        if suffix not in type_map:
            raise ValueError(f"Unsupported file type: {suffix}")

        return type_map[suffix]

    def _import_k7(self, file_path: Path) -> TapeFile:
        """Import .k7 binary file.

        Args:
            file_path: Path to .k7 file

        Returns:
            TapeFile object
        """
        return file_load(str(file_path))

    def _import_wav(self, file_path: Path) -> TapeFile:
        """Import .wav audio file.

        Args:
            file_path: Path to .wav file

        Returns:
            TapeFile object

        Raises:
            ValueError: If no tape file found in WAV
        """

        # Listener to capture TapeFile
        class _ImportListener(TapeFileListener):
            def __init__(self) -> None:
                self.file: TapeFile | None = None

            def process_file(self, file: TapeFile) -> None:
                self.file = file

        # Build processing pipeline
        listener = _ImportListener()
        file_loader = TapeFileLoader([listener])
        block_parser = BlockParser([file_loader])
        byte_decoder = ByteDecoder([block_parser])
        demodulator = AudioDemodulator([byte_decoder], rate=44100)

        # Process file
        file_input = FileInput(filename=str(file_path), listeners=[demodulator])
        file_input.run()

        if listener.file is None:
            raise ValueError("No tape file found in WAV file")

        return listener.file

    def _import_basic(self, file_path: Path) -> TapeFile:
        """Import .bas BASIC source file.

        Args:
            file_path: Path to .bas file

        Returns:
            TapeFile object
        """
        # Read and process BASIC code
        with open(file_path) as f:
            basic_code = f.read()

        basic_code = preprocess_basic(basic_code)
        basic_code = minify_basic(basic_code)

        # Compile to TapeFile
        encoder = BasicEncoder()
        compiler = BasicFileCompiler()
        instructions = [encoder.encode(line) for line in basic_code.splitlines()]

        return compiler.compile_instructions(str(file_path.name), instructions)

    def _import_assembly(self, file_path: Path) -> TapeFile:
        """Import .asm assembly source file as ASMSRC.

        Args:
            file_path: Path to .asm file

        Returns:
            TapeFile object
        """
        # Read assembly code
        with open(file_path) as f:
            asm_code = f.read()

        # Create ASMSRC TapeFile
        return create_assembly_file(str(file_path.name), asm_code)

    def _import_c(self, shell: TapeShell, file_path: Path) -> TapeFile:
        """Import .c C source file (compiles to MACHINE code).

        Args:
            shell: TapeShell instance
            file_path: Path to .c file

        Returns:
            TapeFile object

        Raises:
            FCCNotFoundError: If FCC compiler not available
            CCompilerError: If compilation fails
        """
        # Compile C to machine code (also generates .asm)
        tape_file, asm_path = compile_c_source(str(file_path), cpu="6803")

        shell.ui.show_info(f"Generated assembly: {asm_path}")

        return tape_file

    def _import_file(self, shell: TapeShell, file_path: Path) -> TapeFile:
        """Import a single file and convert to TapeFile.

        Args:
            shell: TapeShell instance
            file_path: Path to file to import

        Returns:
            TapeFile object ready for repository

        Raises:
            ValueError: If file type unsupported or processing fails
            FCCNotFoundError: If C file requires unavailable compiler
            CCompilerError: If C compilation fails
        """
        file_type = self._detect_file_type(file_path)

        if file_type == "k7":
            return self._import_k7(file_path)
        elif file_type == "wav":
            return self._import_wav(file_path)
        elif file_type == "bas":
            return self._import_basic(file_path)
        elif file_type == "asm":
            return self._import_assembly(file_path)
        elif file_type == "c":
            return self._import_c(shell, file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
