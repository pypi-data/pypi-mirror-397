"""File management commands for the tape shell.

This module contains commands for listing, viewing, searching, and removing
tape files from the database.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from supertape.cli.commands.base import ShellCommand
from supertape.cli.list import decode_assembly_source
from supertape.core.basic.decode import BasicDecoder, BasicFileParser
from supertape.core.disasm.m6803 import disassemble
from supertape.core.file.api import (
    FILE_TYPE_ASMSRC,
    FILE_TYPE_BASIC,
    FILE_TYPE_DATA,
    FILE_TYPE_MACHINE,
    TapeFile,
)
from supertape.core.log.dump import dump

if TYPE_CHECKING:
    from supertape.cli.shell import TapeShell


class LsCommand(ShellCommand):
    """List all tape files in database."""

    @property
    def name(self) -> str:
        return "ls"

    @property
    def description(self) -> str:
        return "List all tape files in database"

    @property
    def help_text(self) -> str:
        return """List all tape files in the current database

Usage: ls

Displays a table of all files with:
  • Filename
  • File type (BASIC, MACHINE, ASMSRC, DATA)
  • Size in bytes
  • Last modified date

Tip: Use 'list <filename>' to see file contents"""

    def execute(self, shell: TapeShell, args: list[str]) -> None:
        """Execute ls command."""
        tape_files = shell.repository.get_tape_files()
        table = shell.ui.create_file_table(tape_files)

        # Estimate table height: header (3) + files (1 per file) + footer (2)
        estimated_lines = 3 + len(tape_files) + 2

        if shell._should_use_pager(estimated_lines):
            with shell.ui.console.pager(styles=True):
                shell.ui.console.print(table)
                if tape_files:
                    shell.ui.console.print(f"\n[dim]Total: {len(tape_files)} file(s)[/dim]")
        else:
            shell.ui.print(table)
            if tape_files:
                shell.ui.print(f"\n[dim]Total: {len(tape_files)} file(s)[/dim]")


class ListCommand(ShellCommand):
    """List all files OR show specific file contents."""

    @property
    def name(self) -> str:
        return "list"

    @property
    def description(self) -> str:
        return "List all tape files or show file contents"

    @property
    def usage(self) -> str:
        return "list [filename]"

    @property
    def help_text(self) -> str:
        return """List all files OR show specific file contents

Usage:
  list              List all files (same as 'ls')
  list <filename>   Display file contents

When listing a file, displays:
  • BASIC: Decoded program listing
  • ASMSRC: Assembly source code
  • MACHINE: Disassembled M6803 assembly with addresses
  • DATA: Hex dump with ASCII

Examples:
  list                Show all files
  list GAME.BAS       Show BASIC program listing
  list DEMO.ASM       Show assembly source"""

    def execute(self, shell: TapeShell, args: list[str]) -> None:
        """Execute list command."""
        # If no parameters, behave like ls
        if not args:
            ls_cmd = shell.registry.get("ls")
            if ls_cmd:
                ls_cmd.execute(shell, args)
            return

        filename = args[0]
        tape_files = shell.repository.get_tape_files()

        # Find the file
        target_file = None
        for tape_file in tape_files:
            if tape_file.fname.lower() == filename.lower():
                target_file = tape_file
                break

        if target_file is None:
            shell.ui.show_error(f"File not found: {filename}")
            shell._suggest_similar_files(filename, tape_files)
            return

        # Estimate content lines based on file type
        estimated_lines = 0
        if target_file.ftype == FILE_TYPE_BASIC:
            parser = BasicFileParser()
            estimated_lines = sum(1 for _ in parser.get_binary_instructions(target_file))
        elif target_file.ftype == FILE_TYPE_ASMSRC:
            lines = decode_assembly_source(target_file)
            estimated_lines = len(lines)
        elif target_file.ftype == FILE_TYPE_MACHINE:
            # Estimate disassembly line count (roughly body_size / 2 bytes per instruction)
            # Add 4 for address header lines
            estimated_lines = len(target_file.fbody) // 2 + 4
        elif target_file.ftype == FILE_TYPE_DATA:
            # Each dump line shows 16 bytes
            estimated_lines = len(target_file.fbody) // 16

        # Add header lines (file info: ~4 lines)
        estimated_lines += 4

        # Use terminal-aware paging
        use_pager = shell._should_use_pager(estimated_lines)

        # Display file header
        file_type = shell.ui.file_type_names.get(target_file.ftype, f"Unknown (0x{target_file.ftype:02X})")
        file_type_color = shell.ui.file_type_colors.get(target_file.ftype, "white")

        if use_pager:
            with shell.ui.console.pager(styles=True):
                shell.ui.console.print(f"[bold bright_white]File:[/bold bright_white] {target_file.fname}")
                shell.ui.console.print(
                    f"[bold bright_white]Type:[/bold bright_white] [{file_type_color}]{file_type}[/{file_type_color}]"
                )
                shell.ui.console.print("[dim]" + "-" * 60 + "[/dim]")
                shell.ui.console.print()

                # Route to appropriate handler based on file type
                if target_file.ftype == FILE_TYPE_BASIC:
                    self._display_basic(shell, target_file, use_pager=True)
                elif target_file.ftype == FILE_TYPE_ASMSRC:
                    self._display_assembly(shell, target_file, use_pager=True)
                elif target_file.ftype == FILE_TYPE_MACHINE:
                    self._display_machine(shell, target_file, use_pager=True)
                elif target_file.ftype == FILE_TYPE_DATA:
                    self._display_data(shell, target_file, use_pager=True)
                else:
                    # Unknown file type - default to hex dump
                    shell.ui.console.print(
                        f"[bold yellow]⚠️  Warning:[/bold yellow] Unknown file type 0x{target_file.ftype:02X}, displaying as hex dump"
                    )
                    shell.ui.console.print()
                    self._display_data(shell, target_file, use_pager=True)
        else:
            shell.ui.print(f"[bold bright_white]File:[/bold bright_white] {target_file.fname}")
            shell.ui.print(
                f"[bold bright_white]Type:[/bold bright_white] [{file_type_color}]{file_type}[/{file_type_color}]"
            )
            shell.ui.print("[dim]" + "-" * 60 + "[/dim]")
            shell.ui.print()

            # Route to appropriate handler based on file type
            if target_file.ftype == FILE_TYPE_BASIC:
                self._display_basic(shell, target_file)
            elif target_file.ftype == FILE_TYPE_ASMSRC:
                self._display_assembly(shell, target_file)
            elif target_file.ftype == FILE_TYPE_MACHINE:
                self._display_machine(shell, target_file)
            elif target_file.ftype == FILE_TYPE_DATA:
                self._display_data(shell, target_file)
            else:
                # Unknown file type - default to hex dump
                shell.ui.show_warning(f"Unknown file type 0x{target_file.ftype:02X}, displaying as hex dump")
                shell.ui.print()
                self._display_data(shell, target_file)

    def _display_basic(self, shell: TapeShell, file: TapeFile, use_pager: bool = False) -> None:
        """Display BASIC program listing with syntax highlighting."""
        parser = BasicFileParser()
        decoder = BasicDecoder()
        console = shell.ui.console if use_pager else shell.ui

        for basic_line in parser.get_binary_instructions(file):
            decoded = decoder.decode(instruction=basic_line.instruction)
            # Simple syntax highlighting for BASIC
            # Line numbers in cyan, rest in white
            parts = decoded.split(" ", 1)
            if len(parts) == 2:
                line_num, code = parts
                console.print(f"    [bright_magenta]{line_num}[/bright_magenta] {code}")
            else:
                console.print(f"    {decoded}")

    def _display_assembly(self, shell: TapeShell, file: TapeFile, use_pager: bool = False) -> None:
        """Display assembly source listing."""
        lines = decode_assembly_source(file)
        console = shell.ui.console if use_pager else shell.ui

        for line in lines:
            # Simple syntax highlighting for assembly
            # Labels in yellow, opcodes in cyan
            stripped = line.lstrip()
            if stripped and not stripped.startswith(";"):
                # Check if line has a label (starts at column 0)
                if line and line[0] not in (" ", "\t"):
                    # Likely a label
                    console.print(f"[bright_yellow]{line}[/bright_yellow]")
                else:
                    # Regular instruction
                    console.print(f"[bright_magenta]{line}[/bright_magenta]")
            else:
                # Comment or empty line
                console.print(f"[dim]{line}[/dim]")

    def _display_machine(self, shell: TapeShell, file: TapeFile, use_pager: bool = False) -> None:
        """Display machine code as disassembled 6803 assembly."""
        console = shell.ui.console if use_pager else shell.ui

        # Display address information
        if file.fstartaddress is not None:
            console.print(
                f"[bold]Start Address:[/bold] [bright_magenta]${file.fstartaddress:04X}[/bright_magenta]"
            )
        if file.floadaddress is not None:
            console.print(
                f"[bold]Load Address:[/bold]  [bright_magenta]${file.floadaddress:04X}[/bright_magenta]"
            )

        console.print("[dim]" + "-" * 60 + "[/dim]")
        console.print()

        # Use load address if available, otherwise use start address
        base_address = file.floadaddress if file.floadaddress is not None else file.fstartaddress

        # Disassemble the machine code
        disasm_lines = disassemble(file.fbody, base_address)
        for line in disasm_lines:
            # Syntax highlighting for disassembly
            # Address in magenta, hex bytes in dim, instruction in cyan
            parts = line.split(None, 2)
            if len(parts) >= 3:
                addr, hex_bytes, instruction = parts[0], parts[1], " ".join(parts[2:])
                console.print(
                    f"[bright_magenta]{addr}[/bright_magenta] [dim]{hex_bytes:12}[/dim] [bright_magenta]{instruction}[/bright_magenta]"
                )
            elif len(parts) == 2:
                addr, hex_bytes = parts
                console.print(f"[bright_magenta]{addr}[/bright_magenta] [dim]{hex_bytes}[/dim]")
            else:
                console.print(f"[dim]{line}[/dim]")

    def _display_data(self, shell: TapeShell, file: TapeFile, use_pager: bool = False) -> None:
        """Display data file as hex dump with ASCII."""
        dump_lines = dump(file.fbody)
        console = shell.ui.console if use_pager else shell.ui

        for line in dump_lines:
            # Syntax highlighting for hex dump
            # Address in magenta, hex in dim, ASCII in white
            if ":" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    addr, rest = parts
                    # Further split hex and ASCII parts
                    if "|" in rest:
                        hex_part, ascii_part = rest.split("|", 1)
                        console.print(
                            f"[bright_magenta]{addr}:[/bright_magenta][dim]{hex_part}[/dim]|[bright_white]{ascii_part}[/bright_white]"
                        )
                    else:
                        console.print(f"[bright_magenta]{addr}:[/bright_magenta][dim]{rest}[/dim]")
                else:
                    console.print(f"[dim]{line}[/dim]")
            else:
                console.print(f"[dim]{line}[/dim]")


class InfoCommand(ShellCommand):
    """Show detailed information about a tape file."""

    @property
    def name(self) -> str:
        return "info"

    @property
    def description(self) -> str:
        return "Show detailed file information"

    @property
    def usage(self) -> str:
        return "info <filename>"

    @property
    def help_text(self) -> str:
        return """Show detailed information about a tape file

Usage: info <filename>

Displays:
  • File metadata (name, type, size)
  • Addresses (load/start for MACHINE files)
  • Hex preview of file data
  • Creation/modification dates

Example:
  info PROGRAM.BAS"""

    def execute(self, shell: TapeShell, args: list[str]) -> None:
        """Execute info command."""
        if not args:
            shell.ui.show_error("Usage: info <filename>")
            return

        filename = args[0]
        tape_files = shell.repository.get_tape_files()

        # Find the file
        target_file = None
        for tape_file in tape_files:
            if tape_file.fname.lower() == filename.lower():
                target_file = tape_file
                break

        if target_file is None:
            shell.ui.show_error(f"File not found: {filename}")
            shell._suggest_similar_files(filename, tape_files)
            return

        shell.ui.show_file_info(target_file)


class RemoveCommand(ShellCommand):
    """Remove a tape file from the database."""

    @property
    def name(self) -> str:
        return "remove"

    @property
    def aliases(self) -> list[str]:
        return ["rm"]

    @property
    def description(self) -> str:
        return "Remove a tape file"

    @property
    def usage(self) -> str:
        return "remove <filename>"

    @property
    def help_text(self) -> str:
        return """Remove a tape file from the database

Usage: remove <filename>
Alias: rm

Permanently removes the file from the database.

Example:
  remove OLD.BAS
  rm TEMP.BAS"""

    def execute(self, shell: TapeShell, args: list[str]) -> None:
        """Execute remove command."""
        if not args:
            shell.ui.show_error("Usage: remove <filename>")
            return

        filename = args[0]
        tape_files = shell.repository.get_tape_files()

        # Find the file
        target_file = None
        for tape_file in tape_files:
            if tape_file.fname.lower() == filename.lower():
                target_file = tape_file
                break

        if target_file is None:
            shell.ui.show_error(f"File not found: {filename}")
            shell._suggest_similar_files(filename, tape_files)
            return

        try:
            shell.repository.remove_tape_file(target_file)
            shell.ui.show_success(f"Removed file: {target_file.fname}")
        except Exception as e:
            shell.ui.show_error(f"Failed to remove file: {e}")


class SearchCommand(ShellCommand):
    """Search for tape files by name pattern."""

    @property
    def name(self) -> str:
        return "search"

    @property
    def aliases(self) -> list[str]:
        return ["find"]

    @property
    def description(self) -> str:
        return "Search for files by name"

    @property
    def usage(self) -> str:
        return "search <pattern>"

    @property
    def help_text(self) -> str:
        return """Search for tape files by name pattern

Usage: search <pattern>
Alias: find

Searches for files containing the pattern (case-insensitive).
Displays matching files in a table.

Examples:
  search GAME          Find files with 'GAME' in name
  search .BAS          Find all BASIC files
  search TEST          Find test programs"""

    def execute(self, shell: TapeShell, args: list[str]) -> None:
        """Execute search command."""
        if not args:
            shell.ui.show_error("Usage: search <pattern>")
            return

        pattern = args[0].lower()
        tape_files = shell.repository.get_tape_files()

        # Find matching files
        matching_files = []
        for tape_file in tape_files:
            if pattern in tape_file.fname.lower():
                matching_files.append(tape_file)

        if matching_files:
            shell.ui.print(f"[bold bright_white]Search Results for '{pattern}':[/bold bright_white]")
            table = shell.ui.create_file_table(matching_files)
            shell.ui.print(table)
            shell.ui.print(f"\n[dim]Found {len(matching_files)} matching file(s)[/dim]")
        else:
            shell.ui.show_warning(f"No files found matching pattern: {pattern}")
