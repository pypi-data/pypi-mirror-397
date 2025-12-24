"""System commands for the tape shell.

This module contains commands for help, exit, clear, and status.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from supertape.cli.commands.base import ShellCommand

if TYPE_CHECKING:
    from supertape.cli.shell import TapeShell


class HelpCommand(ShellCommand):
    """Show help information."""

    @property
    def name(self) -> str:
        return "help"

    @property
    def aliases(self) -> list[str]:
        return ["?"]

    @property
    def description(self) -> str:
        return "Show help information"

    @property
    def usage(self) -> str:
        return "help [command]"

    @property
    def help_text(self) -> str:
        return """Show help information

Usage:
  help              Show all available commands
  help <command>    Show detailed help for a command
Alias: ?

Examples:
  help              General help
  help play         Help for 'play' command
  ? import          Help for 'import' command"""

    def execute(self, shell: TapeShell, args: list[str]) -> None:
        """Execute help command."""
        if args:
            # Show help for specific command
            command_name = args[0].lower()
            command = shell.registry.get(command_name)
            if command:
                self._show_command_help(shell, command)
            else:
                shell.ui.show_error(f"No help available for unknown command: {command_name}")
        else:
            # Show general help
            self._show_general_help(shell)

    def _show_general_help(self, shell: TapeShell) -> None:
        """Show general help with all commands."""
        help_text = """
[bold bright_white]Available Commands:[/bold bright_white]

[bright_green]File Management:[/bright_green]
  [bright_magenta]ls, list[/bright_magenta]           List all tape files in database
  [bright_magenta]list <file>[/bright_magenta]        Display contents of a specific file
  [bright_magenta]info <file>[/bright_magenta]        Show detailed file information
  [bright_magenta]import <file> [...][/bright_magenta] Import files into database (.k7, .wav, .bas, .asm, .c)
  [bright_magenta]remove <file>[/bright_magenta]      Remove a tape file (alias: rm)
  [bright_magenta]search <pattern>[/bright_magenta]   Search for files by name (alias: find)
  [bright_magenta]history <file>[/bright_magenta]     Show version history for a file

[bright_green]Audio Operations:[/bright_green]
  [bright_magenta]listen[/bright_magenta]             Start listening to audio (passive monitoring)
  [bright_magenta]record[/bright_magenta]             Start recording to database (saves received files)
  [bright_magenta]stop[/bright_magenta]               Stop all audio operations

[bright_green]Playback:[/bright_green]
  [bright_magenta]play <file>[/bright_magenta]        Play a tape file or K7 container to audio output

[bright_green]System:[/bright_green]
  [bright_magenta]status[/bright_magenta]             Show system and audio status
  [bright_magenta]clear[/bright_magenta]              Clear the screen
  [bright_magenta]help [command][/bright_magenta]     Show help (alias: ?)
  [bright_magenta]exit[/bright_magenta]               Exit the shell (alias: quit)

[bright_yellow]Tips:[/bright_yellow]
  • Use Tab for auto-completion of commands and filenames
  • Use arrow keys to navigate command history
  • 🔴 in prompt = audio actively listening
  • ⚫ in prompt = audio inactive
  • Use quotes for file names with spaces: play "my file.bas"
  • Type 'help <command>' for detailed help on a specific command
        """
        # Estimate lines: ~33 lines of content
        estimated_lines = 33

        if shell._should_use_pager(estimated_lines):
            with shell.ui.console.pager(styles=True):
                shell.ui.console.print(help_text)
        else:
            shell.ui.print(help_text)

    def _show_command_help(self, shell: TapeShell, command: ShellCommand) -> None:
        """Show help for a specific command."""
        help_content = command.help_text
        # Count lines in help text (header + content + footer)
        estimated_lines = help_content.count("\n") + 3  # +3 for header and footer

        help_output = f"\n[bold bright_white]{command.name.upper()}[/bold bright_white]\n\n{help_content}\n"

        if shell._should_use_pager(estimated_lines):
            with shell.ui.console.pager(styles=True):
                shell.ui.console.print(help_output)
        else:
            shell.ui.print(help_output)


class ExitCommand(ShellCommand):
    """Exit the tape shell."""

    @property
    def name(self) -> str:
        return "exit"

    @property
    def aliases(self) -> list[str]:
        return ["quit"]

    @property
    def description(self) -> str:
        return "Exit the shell"

    @property
    def help_text(self) -> str:
        return """Exit the tape shell

Usage: exit
Alias: quit

Exits the shell and cleans up audio resources"""

    def execute(self, shell: TapeShell, args: list[str]) -> None:
        """Execute exit command."""
        shell.running = False


class ClearCommand(ShellCommand):
    """Clear the terminal screen."""

    @property
    def name(self) -> str:
        return "clear"

    @property
    def description(self) -> str:
        return "Clear the screen"

    @property
    def help_text(self) -> str:
        return """Clear the terminal screen

Usage: clear

Clears the screen and redisplays the banner"""

    def execute(self, shell: TapeShell, args: list[str]) -> None:
        """Execute clear command."""
        shell.ui.clear_screen()
        shell.ui.show_banner()


class StatusCommand(ShellCommand):
    """Show system status."""

    @property
    def name(self) -> str:
        return "status"

    @property
    def description(self) -> str:
        return "Show system status"

    @property
    def help_text(self) -> str:
        return """Show system status

Usage: status

Displays:
  • Database name and path
  • Number of tape files in database
  • Audio device information
  • Audio status (listening/recording state)"""

    def execute(self, shell: TapeShell, args: list[str]) -> None:
        """Execute status command."""
        repo_info = shell.repository.get_repository_info()
        database_path = Path(repo_info.path)
        db_name = database_path.name

        audio_status = shell.audio_manager.get_status()

        # Show regular status
        shell.ui.show_status(
            database_name=db_name,
            database_path=database_path,
            audio_device=audio_status["device"],
            tape_count=repo_info.file_count,
        )

        # Show audio status
        shell.ui.print("\n[bold bright_white]Audio Status:[/bold bright_white]")
        listening_status = "🔴 Active" if audio_status["listening"] else "⚫ Inactive"
        recording_status = "📼 Recording" if audio_status["recording"] else "📻 Monitoring"

        shell.ui.print(f"  Listening: {listening_status}")
        if audio_status["listening"]:
            shell.ui.print(f"  Mode: {recording_status}")
