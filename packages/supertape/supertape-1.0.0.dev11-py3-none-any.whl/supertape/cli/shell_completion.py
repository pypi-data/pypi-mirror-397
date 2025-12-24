"""Command completion providers for the enhanced supertape shell."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from prompt_toolkit.completion import Completer, Completion, PathCompleter
from prompt_toolkit.document import Document

from supertape.core.repository.api import TapeFileRepository

if TYPE_CHECKING:
    from supertape.cli.commands.registry import CommandRegistry


class ImportPathCompleter(PathCompleter):
    """PathCompleter for import command with file-type metadata."""

    def __init__(self) -> None:
        """Initialize with file filter for supported import formats."""

        def file_filter(path: str) -> bool:
            """Filter to show directories and supported file extensions."""
            import os

            if os.path.isdir(path):
                return True
            return path.endswith((".k7", ".wav", ".bas", ".asm", ".c"))

        super().__init__(file_filter=file_filter, expanduser=True, min_input_len=0)

    def get_completions(self, document: Document, complete_event: Any) -> Iterable[Completion]:
        """Generate path completions with metadata for file types."""
        try:
            for comp in super().get_completions(document, complete_event):
                # Extract display text to determine file type
                # comp.display can be str or FormattedText - convert to str for file type detection
                display_str = str(comp.display)

                # Map file extensions to metadata
                if display_str.endswith("/"):
                    meta = "Directory"
                elif display_str.endswith(".k7"):
                    meta = "K7 Binary"
                elif display_str.endswith(".wav"):
                    meta = "WAV Audio"
                elif display_str.endswith(".bas"):
                    meta = "BASIC Source"
                elif display_str.endswith(".asm"):
                    meta = "Assembly Source"
                elif display_str.endswith(".c"):
                    meta = "C Source"
                else:
                    meta = ""

                # Yield enriched completion
                yield Completion(
                    text=comp.text,
                    start_position=comp.start_position,
                    display=comp.display,
                    display_meta=meta,
                )
        except (OSError, PermissionError):
            pass  # Silently ignore filesystem errors


class TapeShellCompleter(Completer):
    """Auto-completion provider for the tape shell."""

    def __init__(self, repository: TapeFileRepository, registry: CommandRegistry) -> None:
        """Initialize the completer with a tape repository and command registry."""
        self.repository = repository
        self.registry = registry

        # Build command dictionary from registry
        self.commands: dict[str, str] = {}
        for command in registry.all_commands():
            self.commands[command.name] = command.description
            for alias in command.aliases:
                self.commands[alias] = f"{command.description} (alias)"

        # Create import path completer once for reuse
        self.import_completer = ImportPathCompleter()

    def get_completions(self, document: Document, complete_event: Any) -> Iterable[Completion]:
        """Generate completions for the current input."""
        text = document.text_before_cursor
        words = text.split()

        if not words:
            # Complete commands when no input
            for command in self.commands:
                yield Completion(command, start_position=0, display_meta=self.commands[command])
        elif len(words) == 1 and not text.endswith(" "):
            # Complete commands when typing first word (but not if there's a trailing space)
            word = words[0].lower()
            for command in self.commands:
                if command.startswith(word):
                    yield Completion(command, start_position=-len(word), display_meta=self.commands[command])
        else:
            # Complete file names for commands that take file arguments
            command = words[0].lower()
            if command in ["play", "info", "remove", "rm", "list", "history"]:
                # If text ends with space, we're starting a new argument
                # If len(words) >= 2, we're completing an existing argument
                if text.endswith(" ") or len(words) >= 2:
                    # Complete tape file names
                    current_word = "" if text.endswith(" ") else words[-1]
                    tape_files = self.repository.get_tape_files()

                    for tape_file in tape_files:
                        if tape_file.fname.lower().startswith(current_word.lower()):
                            yield Completion(
                                tape_file.fname,
                                start_position=-len(current_word),
                                display_meta=f"Type: {self._get_file_type_name(tape_file.ftype)}, Size: {len(tape_file.fbody)} bytes",
                            )
            elif command in ["search", "find"]:
                # For search commands, we could provide suggestions based on existing file names
                if text.endswith(" ") or len(words) >= 2:
                    current_word = "" if text.endswith(" ") else words[-1]
                    tape_files = self.repository.get_tape_files()

                    # Suggest unique words from file names
                    unique_words = set()
                    for tape_file in tape_files:
                        for word in tape_file.fname.split():
                            if len(word) > 1:  # Only suggest words longer than 1 character
                                unique_words.add(word.lower())

                    for word in sorted(unique_words):
                        if word.startswith(current_word.lower()):
                            yield Completion(
                                word, start_position=-len(current_word), display_meta="Search term"
                            )
            elif command == "import":
                # Complete filesystem paths for import command
                if text.endswith(" ") or len(words) >= 2:
                    current_word = "" if text.endswith(" ") else words[-1]

                    # Create a new document with just the path part for PathCompleter
                    # PathCompleter expects the document to contain only the path being completed
                    path_document = Document(current_word, cursor_position=len(current_word))

                    # Delegate to ImportPathCompleter
                    yield from self.import_completer.get_completions(path_document, complete_event)

    def _get_file_type_name(self, ftype: int) -> str:
        """Get human-readable file type name."""
        file_type_names = {
            0x00: "BASIC",
            0x01: "DATA",
            0x02: "MACHINE",
            0x05: "ASMSRC",
        }
        return file_type_names.get(ftype, f"0x{ftype:02X}")


class CommandCompleter(Completer):
    """Simple command name completer."""

    def __init__(self, commands: dict[str, str]) -> None:
        """Initialize with a dictionary of commands and their descriptions."""
        self.commands = commands

    def get_completions(self, document: Document, complete_event: Any) -> Iterable[Completion]:
        """Generate command completions."""
        text = document.text_before_cursor.lower()

        for command, description in self.commands.items():
            if command.startswith(text):
                yield Completion(command, start_position=-len(text), display_meta=description)


class FileNameCompleter(Completer):
    """File name completer for tape files."""

    def __init__(self, repository: TapeFileRepository) -> None:
        """Initialize with a tape repository."""
        self.repository = repository

    def get_completions(self, document: Document, complete_event: Any) -> Iterable[Completion]:
        """Generate file name completions."""
        text = document.text_before_cursor.lower()
        tape_files = self.repository.get_tape_files()

        for tape_file in tape_files:
            if tape_file.fname.lower().startswith(text):
                file_type_name = self._get_file_type_name(tape_file.ftype)
                yield Completion(
                    tape_file.fname,
                    start_position=-len(text),
                    display_meta=f"Type: {file_type_name}, Size: {len(tape_file.fbody)} bytes",
                )

    def _get_file_type_name(self, ftype: int) -> str:
        """Get human-readable file type name."""
        file_type_names = {
            0x00: "BASIC",
            0x01: "DATA",
            0x02: "MACHINE",
            0x05: "ASMSRC",
        }
        return file_type_names.get(ftype, f"0x{ftype:02X}")
