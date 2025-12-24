"""UI constants shared across interface implementations.

This module defines constants used for consistent display across different
Supertape user interfaces (CLI, shell, GUI).
"""

from supertape.core.file.api import FILE_TYPE_ASMSRC, FILE_TYPE_BASIC, FILE_TYPE_DATA, FILE_TYPE_MACHINE

# File type colors for Rich formatting
# These colors are used to visually distinguish different tape file types
FILE_TYPE_COLORS = {
    FILE_TYPE_BASIC: "bright_green",
    FILE_TYPE_DATA: "bright_magenta",
    FILE_TYPE_MACHINE: "bright_red",
    FILE_TYPE_ASMSRC: "bright_yellow",
}

# File type icons for enhanced display
FILE_TYPE_ICONS = {
    FILE_TYPE_BASIC: "📝",
    FILE_TYPE_DATA: "📦",
    FILE_TYPE_MACHINE: "⚙️",
    FILE_TYPE_ASMSRC: "🔧",
}

# File type descriptions
FILE_TYPE_DESCRIPTIONS = {
    FILE_TYPE_BASIC: "BASIC program",
    FILE_TYPE_DATA: "Binary data",
    FILE_TYPE_MACHINE: "Machine code",
    FILE_TYPE_ASMSRC: "Assembly source",
}
