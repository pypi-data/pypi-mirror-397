"""Shell commands package.

This package contains all shell command implementations organized by
functional area (file operations, audio control, system utilities, etc.).
"""

from supertape.cli.commands.base import ShellCommand
from supertape.cli.commands.registry import CommandRegistry

__all__ = ["ShellCommand", "CommandRegistry"]
