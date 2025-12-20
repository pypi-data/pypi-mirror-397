"""
Theme and color handling for crawl2md TUI.

Provides configurable color themes that can be loaded from TOML config.
Defaults to 16-color palette to respect terminal themes (Solarized, Dracula, etc.).
Supports optional 256-color mode for advanced customization.
"""

import curses
import sys
from dataclasses import dataclass
from typing import Union


# Map color names to terminal palette indices
# Uses 16-color palette (0-15) to respect terminal themes
# These are palette indices, not absolute colors
COLOR_MAP = {
    # Base 8 colors (0-7)
    "black": curses.COLOR_BLACK,      # 0
    "red": curses.COLOR_RED,          # 1
    "green": curses.COLOR_GREEN,      # 2
    "yellow": curses.COLOR_YELLOW,    # 3
    "blue": curses.COLOR_BLUE,        # 4
    "magenta": curses.COLOR_MAGENTA,  # 5
    "cyan": curses.COLOR_CYAN,        # 6
    "white": curses.COLOR_WHITE,      # 7
    # Bright variants (8-15)
    "bright_black": 8,
    "bright_red": 9,
    "bright_green": 10,
    "bright_yellow": 11,
    "bright_blue": 12,
    "bright_magenta": 13,
    "bright_cyan": 14,
    "bright_white": 15,
    # Terminal default
    "default": -1,
}


def parse_color(value: Union[str, int]) -> int:
    """
    Parse a color value into a curses color index.

    Supports:
    - Named colors from COLOR_MAP (e.g., "cyan", "bright_black")
    - "colorN" format where N is 0-255 (e.g., "color102")
    - Raw integers 0-255

    Args:
        value: Color specification (name, "colorN", or int)

    Returns:
        Integer color index suitable for curses.init_pair()

    Examples:
        >>> parse_color("cyan")
        6
        >>> parse_color("bright_black")
        8
        >>> parse_color("color102")
        102
        >>> parse_color(240)
        240
        >>> parse_color("invalid")  # Falls back to default
        -1
    """
    # If it's already an int, validate range
    if isinstance(value, int):
        if 0 <= value <= 255 or value == -1:
            return value
        print(f"Warning: Color value {value} out of range (0-255), using default", file=sys.stderr)
        return -1

    # If it's a string, check COLOR_MAP first
    if isinstance(value, str):
        # Check named colors
        if value in COLOR_MAP:
            return COLOR_MAP[value]

        # Check "colorN" format
        if value.startswith("color"):
            try:
                color_num = int(value[5:])
                if 0 <= color_num <= 255:
                    return color_num
                print(f"Warning: Color value '{value}' out of range (0-255), using default", file=sys.stderr)
                return -1
            except (ValueError, IndexError):
                pass

        # Unknown color name
        print(f"Warning: Unknown color name '{value}', using default", file=sys.stderr)
        return -1

    # Unsupported type
    print(f"Warning: Invalid color type {type(value)}, using default", file=sys.stderr)
    return -1


@dataclass
class Theme:
    """
    Color theme configuration for the TUI.

    Attributes:
        name: Theme name (for identification)
        primary: Main UI elements, borders, labels
        accent: Highlights, selected items
        dim: Muted/inactive text
        success: Success states, help text (green by default)
        warning: Warning messages (yellow by default)
        error: Error messages (red by default)
        text: Default text color
        extended_colors: Enable 256-color mode (may not respect terminal themes)
    """

    name: str = "default"
    primary: str = "cyan"
    accent: str = "white"
    dim: str = "bright_black"
    success: str = "green"
    warning: str = "yellow"
    error: str = "red"
    text: str = "default"
    extended_colors: bool = False


# Default theme matching current hardcoded colors
DEFAULT_THEME = Theme(
    name="default",
    primary="cyan",        # Labels, borders
    accent="white",        # Highlights
    dim="bright_black",    # Muted text (grey)
    success="green",       # Help text, success
    warning="yellow",      # Warnings
    error="red",           # Errors
    text="default",        # Normal text
    extended_colors=False, # Use 16-color palette
)

# Preset themes for common use cases

FORGE_DARK = Theme(
    name="forge-dark",
    primary="bright_blue",     # Light blue for headers, improved contrast
    accent="white",            # Highlights
    dim="bright_black",        # Blue-grey for stronger separation
    success="green",           # Bright green (use bold in rendering)
    warning="bright_yellow",   # Gold for warnings, queue processing
    error="bright_red",        # Brightened red
    text="default",            # Normal text
    extended_colors=False,
)

SOLARIZED_TUI = Theme(
    name="solarized-tui",
    primary="cyan",            # Calm cyan for headers
    accent="bright_blue",      # Blue accents
    dim="bright_black",        # Base00 (deep neutral)
    success="green",           # Aurora green
    warning="bright_red",      # Orange-like (using bright_red/9 for orange)
    error="red",               # Standard red
    text="default",            # Base0 grey-blue
    extended_colors=False,
)

MONOKAI_TERMINAL = Theme(
    name="monokai-terminal",
    primary="bright_magenta",  # Magenta headers for modern look
    accent="bright_cyan",      # Bright cyan for status
    dim="bright_black",        # Dim grey
    success="green",           # Monokai green
    warning="yellow",          # Monokai yellow
    error="red",               # Monokai red
    text="bright_white",       # Generic bright text
    extended_colors=False,
)

NORD_FROST = Theme(
    name="nord-frost",
    primary="bright_blue",     # Frost blue for headers
    accent="cyan",             # Frost cyan for running status
    dim="bright_black",        # Blue-grey placeholders
    success="green",           # Aurora green
    warning="bright_yellow",   # Warm yellow (contrasts cold palette)
    error="red",               # Aurora red
    text="default",            # Snow white
    extended_colors=False,
)

AMBER_TERMINAL = Theme(
    name="amber-terminal",
    primary="yellow",          # Amber for headers, main UI
    accent="bright_yellow",    # Bright amber for highlights
    dim="bright_black",        # Dark grey separators
    success="green",           # Green for success (only non-amber)
    warning="bright_yellow",   # Bright amber for warnings
    error="red",               # Red for errors (only other non-amber)
    text="bright_white",       # Warm white text
    extended_colors=False,
)

# Map of all available preset themes
PRESET_THEMES = {
    "default": DEFAULT_THEME,
    "forge-dark": FORGE_DARK,
    "solarized-tui": SOLARIZED_TUI,
    "monokai-terminal": MONOKAI_TERMINAL,
    "nord-frost": NORD_FROST,
    "amber-terminal": AMBER_TERMINAL,
}
