"""Base command interface for shell commands.

This module defines the abstract base class for all shell commands, providing
a consistent interface for command execution, help text, and aliases.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from supertape.cli.shell import TapeShell


class ShellCommand(ABC):
    """Abstract base class for shell commands.

    All shell commands must implement this interface, providing command
    metadata and execution logic. Commands are registered with the command
    registry and dispatched based on name or aliases.

    Example:
        >>> class GreetCommand(ShellCommand):
        ...     @property
        ...     def name(self) -> str:
        ...         return "greet"
        ...
        ...     @property
        ...     def description(self) -> str:
        ...         return "Greet the user"
        ...
        ...     def execute(self, shell: TapeShell, args: list[str]) -> None:
        ...         shell.ui.show_info("Hello!")
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Primary command name.

        Returns:
            The main name for this command (lowercase, no spaces)
        """
        pass

    @property
    def aliases(self) -> list[str]:
        """Command aliases.

        Returns:
            List of alternative names for this command (default: empty)
        """
        return []

    @property
    @abstractmethod
    def description(self) -> str:
        """Short description for help listing.

        Returns:
            One-line description of what the command does
        """
        pass

    @property
    def usage(self) -> str:
        """Usage string showing command syntax.

        Returns:
            Usage syntax (default: command name only)
        """
        return self.name

    @property
    def help_text(self) -> str:
        """Detailed help text.

        Returns:
            Multi-line help text with examples (default: description)
        """
        return self.description

    @abstractmethod
    def execute(self, shell: TapeShell, args: list[str]) -> None:
        """Execute the command.

        Args:
            shell: The TapeShell instance (provides access to repository, UI, etc.)
            args: Command arguments (not including command name itself)

        Raises:
            Exception: Commands may raise exceptions which will be caught by the shell
        """
        pass
