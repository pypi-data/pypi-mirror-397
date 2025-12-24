"""Enhanced interactive tape shell with rich UI and audio management."""

from __future__ import annotations

import argparse
import shlex
import sys
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from rich.progress import Progress

from supertape.cli.audio_manager import AudioManager
from supertape.cli.commands.audio_commands import ListenCommand, PlayCommand, RecordCommand, StopCommand
from supertape.cli.commands.file_commands import (
    InfoCommand,
    ListCommand,
    LsCommand,
    RemoveCommand,
    SearchCommand,
)
from supertape.cli.commands.history_commands import HistoryCommand
from supertape.cli.commands.import_commands import ImportCommand
from supertape.cli.commands.registry import CommandRegistry
from supertape.cli.commands.system_commands import ClearCommand, ExitCommand, HelpCommand, StatusCommand
from supertape.cli.shell_completion import TapeShellCompleter
from supertape.cli.shell_ui import ShellUI
from supertape.core.audio.device import get_device
from supertape.core.audio.progress import RichProgressObserver
from supertape.core.file.api import TapeFile, TapeFileListener
from supertape.core.file.container import K7Container
from supertape.core.file.play import play_file
from supertape.core.output.streams import PromptToolkitOutputStream
from supertape.core.repository.api import TapeFileRepository
from supertape.core.repository.dulwich_repo import DulwichRepository


class TapeFileHandler(TapeFileListener):
    """Handles tape files from audio input by adding them to the repository."""

    def __init__(self, repository: TapeFileRepository) -> None:
        """Initialize the tape file handler."""
        self.repository = repository

    def process_file(self, file: TapeFile) -> None:
        """Process a received tape file by adding it to the repository."""
        self.repository.add_tape_file(file)


class TapeShell:
    """Enhanced interactive tape shell with rich UI and audio management."""

    def __init__(self, repository: TapeFileRepository, audio_device: int | None = None) -> None:
        """Initialize the tape shell."""
        self.repository = repository
        self.audio_manager = AudioManager(repository, audio_device)
        self.ui = ShellUI()
        self.output_stream = PromptToolkitOutputStream()

        # Setup history file
        history_file = Path.home() / ".supertape" / "shell_history"
        history_file.parent.mkdir(parents=True, exist_ok=True)

        # Setup prompt style
        self.prompt_style = Style.from_dict(
            {
                "prompt": "#00aa00 bold",
                "path": "#884444 italic",
                "command": "#aa6600 bold",
            }
        )

        # Initialize command registry
        self.registry = CommandRegistry()
        self._register_commands()

        # Setup prompt session with completion and history
        # Use reserve_space_for_menu=4 to enable auto-scrolling when completions appear
        # This allows the prompt to scroll up when at the bottom of the terminal,
        # making room for 3-4 completion suggestions
        self.session: PromptSession[str] = PromptSession(
            history=FileHistory(str(history_file)),
            completer=TapeShellCompleter(repository, self.registry),
            style=self.prompt_style,
            complete_while_typing=True,
            auto_suggest=None,
            reserve_space_for_menu=4,
        )

        self.running = True

    def _register_commands(self) -> None:
        """Register all available commands."""
        # File commands
        self.registry.register(LsCommand())
        self.registry.register(ListCommand())
        self.registry.register(InfoCommand())
        self.registry.register(RemoveCommand())
        self.registry.register(SearchCommand())

        # Audio commands
        self.registry.register(PlayCommand())
        self.registry.register(ListenCommand())
        self.registry.register(RecordCommand())
        self.registry.register(StopCommand())

        # System commands
        self.registry.register(HelpCommand())
        self.registry.register(ExitCommand())
        self.registry.register(ClearCommand())
        self.registry.register(StatusCommand())

        # Import/history
        self.registry.register(ImportCommand())
        self.registry.register(HistoryCommand())

    def start(self) -> None:
        """Start the interactive shell."""
        self.ui.show_banner()
        self._show_welcome_message()

        try:
            while self.running:
                try:
                    # Create rich prompt with audio status indicator
                    repo_info = self.repository.get_repository_info()
                    database_name = Path(repo_info.path).name
                    audio_indicator = "🔴" if self.audio_manager.is_listening else "⚫"
                    prompt_text = HTML(
                        f"<prompt>tape</prompt><path>:{database_name}</path> {audio_indicator} <prompt>></prompt> "
                    )

                    # Get user input
                    user_input = self.session.prompt(prompt_text)

                    if user_input.strip():
                        self._execute_command(user_input.strip())

                except KeyboardInterrupt:
                    self.ui.show_info("Use 'exit' or 'quit' to leave the shell")
                    continue
                except EOFError:
                    # Ctrl+D pressed
                    break
        finally:
            # Cleanup audio resources
            self.audio_manager.stop_audio()

        self.ui.show_info("Goodbye! 👋")

    def _show_welcome_message(self) -> None:
        """Show welcome message with basic instructions."""
        repo_info = self.repository.get_repository_info()
        terminal_height = self.ui.console.height

        if terminal_height < 15:
            # Tiny terminal: Single-line compact message
            self.ui.show_success(f"{repo_info.file_count} files • Type 'help' for commands")
        else:
            # Normal terminal: Full welcome message
            device = get_device()
            if self.audio_manager.device is not None:
                device_info = device.p.get_device_info_by_host_api_device_index(0, self.audio_manager.device)
                device_str = f"Device {self.audio_manager.device}: {device_info['name']}"
            else:
                default_device = device.get_default_device()
                device_info = device.p.get_device_info_by_host_api_device_index(0, default_device)
                device_str = f"Default (Device {default_device}: {device_info['name']})"

            # Show status information
            self.ui.show_success(f"Audio device: {device_str}")
            self.ui.show_success(f"Tape database: {repo_info.file_count} files loaded from {repo_info.path}")
            self.ui.show_info("Type 'help' for commands • 'exit' to quit • 🔴 = listening active")

        self.ui.print()

    def _execute_command(self, command_line: str) -> None:
        """Parse and execute a command."""
        try:
            # Parse command line using shlex for proper quote handling
            parts = shlex.split(command_line)
            if not parts:
                return

            command_name = parts[0].lower()
            args = parts[1:]

            command = self.registry.get(command_name)
            if command:
                command.execute(self, args)
            else:
                self.ui.show_error(f"Unknown command: {command_name}")
                self.ui.show_info("Type 'help' for available commands")

        except ValueError as e:
            self.ui.show_error(f"Invalid command syntax: {e}")
        except Exception as e:
            self.ui.show_error(f"Command failed: {e}")

    def _should_use_pager(self, estimated_lines: int) -> bool:
        """
        Determine if pager should be used based on terminal height.

        Uses adaptive margin: smaller terminals get smaller margins to maximize
        visible content, while larger terminals use more comfortable margins.

        Args:
            estimated_lines: Estimated number of output lines

        Returns:
            True if pager should be used, False otherwise
        """
        terminal_height = self.ui.console.height

        # Adaptive margin based on terminal size
        if terminal_height < 15:
            # Tiny terminal: minimal margin (pager footer + 1 line)
            reserved_lines = 2
        elif terminal_height < 25:
            # Small terminal: small margin
            reserved_lines = 3
        else:
            # Larger terminal: comfortable margin
            reserved_lines = 5

        available_lines = terminal_height - reserved_lines
        return estimated_lines > available_lines

    def _display_k7_file_list(self, container: K7Container, current_index: int) -> None:
        """Display a list of files in a K7 container with a cursor indicator.

        Args:
            container: K7Container with multiple tape files
            current_index: Index of the currently playing file (0-based)
        """
        from rich.console import Group
        from rich.panel import Panel
        from rich.text import Text

        # Create a list of file information with colors
        file_entries = []
        for i, tape_file in enumerate(container):
            file_type = self.ui.file_type_names.get(tape_file.ftype, f"0x{tape_file.ftype:02X}")

            # Current file gets special highlighting
            if i == current_index:
                entry = Text(f"  > {tape_file.fname} ({file_type})", style="bold bright_white on blue")
            else:
                entry = Text(f"    {tape_file.fname} ({file_type})", style="bright_white")
            file_entries.append(entry)

        # Create the panel with cursor
        panel = Panel(
            Group(*file_entries),
            title=f"[bold bright_magenta]K7 Container: {len(container)} file(s)[/bold bright_magenta]",
            border_style="bright_magenta",
            padding=(1, 1),
        )

        self.ui.print(panel)

    def _play_k7_container(self, container: K7Container) -> None:
        """Play all files in a K7 container with interactive prompts.

        Args:
            container: K7Container with multiple tape files
        """
        # Display the file list initially
        self._display_k7_file_list(container, -1)

        # Play each file with pause in between
        for i, tape_file in enumerate(container):
            # Display current file with cursor
            self._display_k7_file_list(container, i)
            self.ui.print()

            # Play the current file
            try:
                with Progress() as progress:
                    task_id = progress.add_task(f"[magenta]Playing {tape_file.fname}...", total=100)
                    observer = RichProgressObserver(progress, task_id, post_delay=0.5)
                    play_file(file=tape_file, observer=observer, device=self.audio_manager.device)
                    observer.wait_for_completion()

                self.ui.show_success(f"Playback complete: {tape_file.fname}")
            except Exception as e:
                self.ui.show_error(f"Playback failed: {e}")
                return

            # Check if there are more files
            if i < len(container) - 1:
                self.ui.print()
                self.ui.show_info(f"File {i+1}/{len(container)} completed.")

                # Ask user if they want to continue
                while True:
                    try:
                        response = (
                            input(f"Continue with next file {i+2}/{len(container)}? (Y/n): ").strip().lower()
                        )
                        if response in ["y", "yes", ""]:
                            self.ui.show_info("Continuing with next file...")
                            break
                        elif response in ["n", "no"]:
                            self.ui.show_info(f"Stopped after file {i+1}/{len(container)}.")
                            return
                        else:
                            self.ui.show_error("Please enter 'y' or 'n'.")
                    except KeyboardInterrupt:
                        self.ui.print("\nPlayback interrupted by user.")
                        return

    def _suggest_similar_files(self, filename: str, tape_files: list[TapeFile]) -> None:
        """Suggest similar file names when a file is not found."""
        filename_lower = filename.lower()
        suggestions = []

        for tape_file in tape_files:
            tape_name_lower = tape_file.fname.lower()

            # Simple similarity check - contains substring or starts with same letter
            if (
                filename_lower in tape_name_lower
                or tape_name_lower in filename_lower
                or (
                    len(filename_lower) > 0
                    and len(tape_name_lower) > 0
                    and filename_lower[0] == tape_name_lower[0]
                )
            ):
                suggestions.append(tape_file.fname)

        if suggestions:
            self.ui.show_info("Did you mean one of these?")
            for suggestion in suggestions[:5]:  # Limit to 5 suggestions
                self.ui.print(f"  • [bright_magenta]{suggestion}[/bright_magenta]")


def main() -> None:
    """Main entry point for the tape shell."""
    parser = argparse.ArgumentParser(description="Run an interactive tape shell session with rich UI.")
    parser.add_argument("--device", help="Select a device by index or name substring.")
    parser.add_argument("dbname", nargs="?", type=str, help="Name of the tape database to use.")
    args = parser.parse_args()

    # Use config default device if --device not specified
    if args.device is None:
        from supertape.core.config import get_config

        device = get_config().audio.default_device
    else:
        device = args.device

    # Resolve device spec to actual device index
    from supertape.core.audio.device import resolve_device

    try:
        device_index = resolve_device(device)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Create repository
    repository = DulwichRepository(args.dbname, observers=[])

    # Start the enhanced shell
    shell = TapeShell(repository, device_index)
    shell.start()


if __name__ == "__main__":
    main()
