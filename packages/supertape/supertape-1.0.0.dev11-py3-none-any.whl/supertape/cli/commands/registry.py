"""Command registry for managing shell commands.

This module provides the CommandRegistry class which manages registration,
lookup, and discovery of shell commands.
"""

from __future__ import annotations

from supertape.cli.commands.base import ShellCommand


class CommandRegistry:
    """Registry for shell commands.

    The registry maintains a mapping of command names and aliases to command
    instances, enabling command dispatch and discovery.

    Example:
        >>> registry = CommandRegistry()
        >>> registry.register(HelpCommand())
        >>> cmd = registry.get("help")
        >>> cmd.execute(shell, [])
    """

    def __init__(self) -> None:
        """Initialize an empty command registry."""
        self._commands: dict[str, ShellCommand] = {}
        self._name_to_command: dict[str, ShellCommand] = {}

    def register(self, command: ShellCommand) -> None:
        """Register a command and its aliases.

        Registers the command under its primary name and all aliases,
        enabling lookup by any of these names.

        Args:
            command: The command to register

        Example:
            >>> registry.register(ListCommand())  # Registers "list"
            >>> registry.register(RemoveCommand())  # Registers "remove" and "rm"
        """
        # Store by primary name
        self._commands[command.name] = command
        self._name_to_command[command.name.lower()] = command

        # Store all aliases
        for alias in command.aliases:
            self._name_to_command[alias.lower()] = command

    def get(self, name: str) -> ShellCommand | None:
        """Get command by name or alias (case-insensitive).

        Args:
            name: Command name or alias to lookup

        Returns:
            ShellCommand instance or None if not found

        Example:
            >>> cmd = registry.get("ls")
            >>> cmd = registry.get("LS")  # Case insensitive
            >>> cmd = registry.get("rm")  # Works with aliases too
        """
        return self._name_to_command.get(name.lower())

    def all_commands(self) -> list[ShellCommand]:
        """Get all registered commands.

        Returns only unique commands (excludes aliases pointing to same command).

        Returns:
            List of all ShellCommand instances

        Example:
            >>> for cmd in registry.all_commands():
            ...     print(f"{cmd.name}: {cmd.description}")
        """
        return list(self._commands.values())

    def get_names_and_aliases(self) -> list[str]:
        """Get all command names and aliases.

        Useful for tab completion and command listing.

        Returns:
            List of all valid command names and aliases

        Example:
            >>> names = registry.get_names_and_aliases()
            >>> print(sorted(names))
            ['clear', 'exit', 'help', 'list', 'ls', 'quit', 'rm', 'remove']
        """
        return list(self._name_to_command.keys())

    def get_command_count(self) -> int:
        """Get number of registered commands (excluding aliases).

        Returns:
            Number of unique commands
        """
        return len(self._commands)
