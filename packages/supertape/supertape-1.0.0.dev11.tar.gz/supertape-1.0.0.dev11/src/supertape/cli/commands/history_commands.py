"""History command for the tape shell.

This module contains the command for viewing version history of tape files.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from rich.table import Table

from supertape.cli.commands.base import ShellCommand

if TYPE_CHECKING:
    from supertape.cli.shell import TapeShell


class HistoryCommand(ShellCommand):
    """Show version history for a tape file."""

    @property
    def name(self) -> str:
        return "history"

    @property
    def description(self) -> str:
        return "Show version history for a file"

    @property
    def usage(self) -> str:
        return "history <filename>"

    @property
    def help_text(self) -> str:
        return """Show version history for a tape file

Usage: history <filename>

Displays:
  • All versions of the file
  • Timestamps of each version
  • Commit messages
  • Version IDs (hashes)
  • Deletion markers for removed versions

Example:
  history GAME.BAS

Note: Only shows history for files that have been committed"""

    def execute(self, shell: TapeShell, args: list[str]) -> None:
        """Execute history command."""
        # Validate argument
        if not args:
            shell.ui.show_error("Usage: history <filename>")
            return

        filename = args[0]

        # Retrieve version history
        try:
            versions = shell.repository.get_tape_file_versions(filename)
        except Exception as e:
            shell.ui.show_error(f"Failed to retrieve history: {e}")
            return

        # Handle empty history
        if not versions:
            shell.ui.show_info(f"No version history found for '{filename}'")
            shell.ui.show_info("This file has not been committed to the repository yet.")
            return

        # Create Rich table
        table = Table(
            title=f"[bold bright_white]Version History: {filename}[/bold bright_white]",
            show_header=True,
            header_style="bold red",
            show_lines=True,
            expand=False,
        )

        table.add_column("Timestamp", style="bright_magenta", width=20)
        table.add_column("Version", style="bright_magenta", width=10)
        table.add_column("Status", style="bright_white", width=15)
        table.add_column("Message", style="bright_white", width=50)

        # Populate rows
        for i, version in enumerate(versions):
            timestamp_str = datetime.fromtimestamp(version.timestamp).strftime("%Y-%m-%d %H:%M:%S")
            short_version = version.version_id[:8]

            # Status with deletion marker
            if version.is_deleted:
                status = "[red dim]🗑️  Deleted[/red dim]"
            else:
                status = "[bright_white]Active[/bright_white]"

            # Truncate message if too long
            message = version.commit_message
            if len(message) > 50:
                message = message[:47] + "..."

            # Bold newest version
            if i == 0:
                table.add_row(
                    f"[bold]{timestamp_str}[/bold]",
                    f"[bold]{short_version}[/bold]",
                    status,
                    f"[bold]{message}[/bold]",
                )
            else:
                table.add_row(timestamp_str, short_version, status, message)

        # Display with paging support
        estimated_lines = 3 + len(versions) + 2

        if shell._should_use_pager(estimated_lines):
            with shell.ui.console.pager(styles=True):
                shell.ui.console.print(table)
                shell.ui.console.print(f"\n[dim]Total: {len(versions)} version(s)[/dim]")
        else:
            shell.ui.print(table)
            shell.ui.print(f"\n[dim]Total: {len(versions)} version(s)[/dim]")
