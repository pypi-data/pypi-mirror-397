"""
Curses-based Terminal User Interface for crawl2md crawler.

Provides real-time monitoring and control of documentation crawls through
an interactive terminal interface with adaptive layout, pause/resume,
speed control, and crash handling.
"""

import curses
import os
import select
import sys
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .config import Config, load_theme
from .crawler import CrawlStats, LogEntry, LogType, QueueEntry, QueueStatus
from .theme import Theme, COLOR_MAP, DEFAULT_THEME, parse_color


# ============================================================================
# Theme Management
# ============================================================================

# Module-level variable to store the active theme (for mid-crawl access in Phase 3)
_active_theme: Theme = DEFAULT_THEME


def init_theme_colors(theme: Theme) -> None:
    """
    Initialize curses color pairs from theme configuration.

    Maps semantic color roles to curses color pairs:
    - Pair 1: success (green by default - help text)
    - Pair 2: warning (yellow by default)
    - Pair 3: error (red by default)
    - Pair 4: primary (cyan by default - labels, borders)
    - Pair 5: dim (bright_black by default - muted text)
    - Pair 6: accent (white by default - highlights)

    Args:
        theme: Theme object with color configuration
    """
    global _active_theme
    _active_theme = theme

    # Parse theme colors to curses indices
    success_color = parse_color(theme.success)
    warning_color = parse_color(theme.warning)
    error_color = parse_color(theme.error)
    primary_color = parse_color(theme.primary)
    dim_color = parse_color(theme.dim)
    accent_color = parse_color(theme.accent)

    # Initialize color pairs (all use terminal default background)
    curses.init_pair(1, success_color, -1)  # success/help
    curses.init_pair(2, warning_color, -1)  # warnings
    curses.init_pair(3, error_color, -1)    # errors
    curses.init_pair(4, primary_color, -1)  # labels/borders
    curses.init_pair(5, dim_color, -1)      # muted text
    curses.init_pair(6, accent_color, -1)   # highlights


# ============================================================================
# Config Form State and Types
# ============================================================================


@dataclass
class FormField:
    """Definition of a form field."""
    name: str           # Internal field name (matches Config attribute)
    label: str          # Display label
    required: bool = False
    field_type: str = "text"  # "text", "bool", "number"
    placeholder: str = ""
    expandable: bool = False  # If True, field shows as toggle + sub-field when expanded
    default_value: str = ""   # Default value when toggle is No/collapsed


# Form field definitions in display order
CONFIG_FORM_FIELDS: List[FormField] = [
    # Always visible fields
    FormField("start_url", "Start URL *", required=True, placeholder="ex: https://docs.example.com"),
    FormField("output", "Output Dir", placeholder="default: docs-md", default_value="docs-md"),
    FormField("dedupe", "Dedupe", field_type="bool"),

    # Expandable fields (toggle + value)
    FormField("tags", "Tags", expandable=True, placeholder="ex: api,guide,reference", default_value=""),
    FormField("restrict_prefix", "Restrict Prefix", expandable=True, placeholder="ex: /docs", default_value=""),
    FormField("exclude_patterns", "Exclude Patterns", expandable=True, placeholder="ex: *.php,/admin/*", default_value=""),
    FormField("delay", "Delay (sec)", field_type="number", expandable=True, placeholder="default: 0.3", default_value="0.3"),
    FormField("max_pages", "Max Pages", field_type="number", expandable=True, placeholder="empty = unlimited", default_value=""),
    FormField("user_agent", "User Agent", expandable=True, placeholder="default: crawl2md/0.1.0", default_value=""),
]


@dataclass
class ConfigFormState:
    """State for the config form UI."""
    field_index: int = 0                           # Currently selected field
    values: Dict[str, str] = field(default_factory=dict)  # Field values as strings
    expanded: Dict[str, bool] = field(default_factory=dict)  # Expansion state for expandable fields
    edit_mode: bool = False                        # Currently editing a field
    cursor_pos: int = 0                            # Cursor position in edit mode
    submitted: bool = False                        # User pressed submit
    cancelled: bool = False                        # User pressed cancel
    on_subfield: bool = False                      # True if cursor is on sub-field, False if on toggle
    current_profile: Optional[str] = None          # Currently selected profile name
    on_profile_selector: bool = False              # True if cursor is on profile selector
    multiselect_mode: bool = False                 # True if in multi-select mode for list fields
    multiselect_index: int = 0                     # Current selection in multi-select list
    multiselect_selected: List[str] = field(default_factory=list)  # Selected values in multi-select

    def current_field(self) -> FormField:
        """Get the currently selected field."""
        return CONFIG_FORM_FIELDS[self.field_index]

    def current_value(self) -> str:
        """Get the current field's value."""
        return self.values.get(self.current_field().name, "")

    def set_current_value(self, value: str) -> None:
        """Set the current field's value."""
        self.values[self.current_field().name] = value

    def move_up(self) -> None:
        """Move selection up, handling sub-fields and profile selector."""
        current_field = CONFIG_FORM_FIELDS[self.field_index]

        # If on sub-field, move to parent toggle
        if self.on_subfield:
            self.on_subfield = False
            return

        # If on first field, move to profile selector
        if self.field_index == 0 and not self.on_profile_selector:
            self.on_profile_selector = True
            return

        # If on profile selector, can't move up
        if self.on_profile_selector:
            return

        # Otherwise, move to previous field/sub-field
        if self.field_index > 0:
            self.field_index -= 1
            # Check if new field is expandable and expanded
            new_field = CONFIG_FORM_FIELDS[self.field_index]
            if new_field.expandable and self.expanded.get(new_field.name, False):
                # Land on sub-field when moving up to expanded field
                self.on_subfield = True
            else:
                self.on_subfield = False

    def move_down(self) -> None:
        """Move selection down, handling sub-fields and profile selector."""
        # If on profile selector, move to first field
        if self.on_profile_selector:
            self.on_profile_selector = False
            self.field_index = 0
            self.on_subfield = False
            return

        current_field = CONFIG_FORM_FIELDS[self.field_index]

        # If on toggle of expanded field, move to sub-field
        if current_field.expandable and self.expanded.get(current_field.name, False) and not self.on_subfield:
            self.on_subfield = True
            return

        # Otherwise, move to next field
        if self.field_index < len(CONFIG_FORM_FIELDS) - 1:
            self.field_index += 1
            self.on_subfield = False

    @classmethod
    def from_config(cls, config: Config) -> "ConfigFormState":
        """Initialize form state from existing config."""
        values = {
            "start_url": config.start_url or "",
            "output": config.output or "docs-md",
            "tags": ",".join(config.tags) if config.tags else "",
            "restrict_prefix": config.restrict_prefix or "",
            "exclude_patterns": ",".join(config.exclude_patterns) if config.exclude_patterns else "",
            "delay": str(config.delay),
            "max_pages": str(config.max_pages) if config.max_pages else "",
            "user_agent": config.user_agent or "",
            "dedupe": "yes" if config.dedupe else "no",
        }

        # Initialize expanded state from config values
        # If a value exists and differs from default, auto-expand
        expanded = {}
        for form_field in CONFIG_FORM_FIELDS:
            if form_field.expandable:
                val = values.get(form_field.name, "")
                # Expand if value is non-empty and different from default
                if val and val != form_field.default_value:
                    expanded[form_field.name] = True
                else:
                    expanded[form_field.name] = False

        return cls(values=values, expanded=expanded)


@dataclass
class ConfigMenuState:
    """State for mid-crawl config menu overlay."""
    current_field: int = 0                         # Currently selected field (0-2)
    editing: bool = False                          # Whether currently editing a field
    whitelist_edit: str = ""                       # Temp buffer for restrict_prefix
    blacklist_edit: List[str] = field(default_factory=list)  # Temp buffer for exclude_patterns
    autoscroll_edit: bool = True                   # Temp buffer for autoscroll
    cursor_pos: int = 0                            # Cursor position for text field editing
    blacklist_cursor: int = 0                      # Which blacklist item is selected


# ============================================================================
# Helper Functions
# ============================================================================

import re
from urllib.parse import urlparse

_PREFIX_RE = re.compile(r"^(\s*[A-Za-z]+:\s+)")

_LOG_BASE_URL: str | None = None
_LOG_HOST: str | None = None
_LOG_OUTPUT_DIR: str | None = None


def _split_log_prefix(line: str) -> tuple[str, str]:
    """Split a log line into (prefix, rest), where prefix includes the label."""
    m = _PREFIX_RE.match(line)
    if not m:
        return "", line
    prefix = m.group(1)
    rest = line[m.end() :]
    return prefix, rest


def _reformat_log_prefix(prefix: str) -> str:
    """Reformat log prefix for consistent alignment.

    Converts:
        "Fetching: " -> " Fetching  "
        "  Saved: "  -> " Saved     "
        "  Skipped: " -> " Skipped   "
        "  Queued: "  -> " Queued    "

    All prefixes are aligned to the same width for visual consistency.
    Format: 1-space padding on left, log type, padding to align to width of longest type.

    Args:
        prefix: Original prefix with optional leading spaces and trailing ": "

    Returns:
        Reformatted prefix with consistent alignment (11 chars total)
    """
    if not prefix:
        return prefix

    # Extract just the word (strip leading spaces and trailing ": ")
    word = prefix.strip().rstrip(':').strip()

    if not word:
        return prefix

    # Format with 1-space left padding and right-pad to width of "Fetching" + 2 spaces
    # " Fetching  " = 1 + 8 + 2 = 11 chars total
    return f" {word:<9}"


def _normalize_log_rest(rest: str, show_full_urls: bool = False) -> str:
    """
    Remove base URL / base output directory from the 'rest' of a log line.

    Args:
        rest: The part of the log line after the prefix
        show_full_urls: If True, keep full URLs; if False, strip base URL
    """
    global _LOG_BASE_URL, _LOG_HOST, _LOG_OUTPUT_DIR

    s = rest.strip()

    if s.startswith(("http://", "https://")):
        try:
            parsed = urlparse(s)
        except Exception:
            return s
        if parsed.scheme and parsed.netloc:
            if _LOG_BASE_URL is None:
                _LOG_BASE_URL = f"{parsed.scheme}://{parsed.netloc}"
                _LOG_HOST = parsed.netloc

            if show_full_urls:
                return s

            path = parsed.path or "/"
            if parsed.query:
                path += "?" + parsed.query
            return path or "/"

    if _LOG_OUTPUT_DIR and s.startswith(_LOG_OUTPUT_DIR):
        remainder = s[len(_LOG_OUTPUT_DIR):]
        if remainder and not remainder.startswith("/"):
            remainder = "/" + remainder
        return remainder or "/"

    if _LOG_HOST and _LOG_HOST in s:
        idx = s.index(_LOG_HOST)
        s2 = s[idx:]
        if not s2.startswith("/"):
            s2 = "/" + s2
        return s2

    if "/" in s:
        parts = [p for p in s.split("/") if p]
        if not parts:
            return s
        tail_parts = parts[-3:] if len(parts) > 3 else parts
        return "/" + "/".join(tail_parts)

    return s


def log_line_truncate_preserve_prefix(line: str, max_length: int, show_full_urls: bool = False) -> str:
    """
    Format a log line for display:

      - Keep the leading keyword prefix ("Saved: ", "Fetching: ", etc.).
      - Strip base URL / base output directory from the rest (unless show_full_urls=True).
      - Always prepend "..." when normalized to show path was stripped.
      - Left-truncate the *rest* while preserving the prefix.

    Example (max_length=30):
        "Saved: /home/me/out/site/spell/illusion.md"
            -> "Saved: .../spell/illusion.md"

    Args:
        line: The log line to format
        max_length: Maximum length of the output
        show_full_urls: If True, keep full URLs; if False, strip base URL
    """
    if max_length <= 0:
        return ""

    prefix, rest = _split_log_prefix(line)
    prefix = _reformat_log_prefix(prefix)  # Align for consistent display
    original_rest = rest
    rest = _normalize_log_rest(rest, show_full_urls)

    # If normalized (content was stripped), prepend "..." to indicate stripping
    was_normalized = rest != original_rest
    if was_normalized and not rest.startswith("..."):
        rest = "..." + rest

    base = prefix + rest

    if len(base) <= max_length:
        return base

    if max_length <= len(prefix) + 4:
        return base[:max_length]

    if rest.startswith("..."):
        remaining = max_length - len(prefix) - 3
        tail = rest[3:]
        if len(tail) > remaining:
            tail = tail[-remaining:]
        return prefix + "..." + tail
    else:
        remaining = max_length - len(prefix) - 3
        tail = rest[-remaining:] if remaining > 0 else ""
        return prefix + "..." + tail


def format_queue_url(url: str, max_length: int) -> str:
    """
    Format a queue URL/path, stripping base URL and output dir
    and left-truncating as needed.
    """
    if max_length <= 0:
        return ""
    rest = _normalize_log_rest(url)
    base = rest
    if len(base) <= max_length:
        return base
    if max_length <= 3:
        return base[-max_length:]
    return "..." + base[-(max_length - 3) :]

def strip_base_url(url: str, base: str) -> str:
    """
    Remove the base URL (scheme+domain) from a URL.
    Example:
        base = "http://dnd2024.wikidot.com"
        url  = "http://dnd2024.wikidot.com/spell/illusion"
        -> "/spell/illusion"
    """
    if url.startswith(base):
        return url[len(base):] or "/"
    return url


def contract_home_dir(path: str) -> str:
    """
    Replace home directory with ~ in a path.
    Example:
        "/home/user/scraper-output" -> "~/scraper-output"

    Args:
        path: Path to contract

    Returns:
        Path with home directory replaced by ~
    """
    from pathlib import Path
    try:
        home = str(Path.home())
        if path.startswith(home):
            return "~" + path[len(home):]
    except Exception:
        pass
    return path


def _format_meta_line(label: str, value: str) -> str:
    """Format a metadata line with aligned labels.

    Converts:
        "URL", "http://..." -> " URL      http://..."
        "Pages", "42"       -> " Pages    42"
        "Output", "~/dir"   -> " Output   ~/dir"

    All labels are aligned to the same width for visual consistency.
    Format: 1-space padding on left, label, padding to align to width of longest label.

    Args:
        label: Label text (e.g., "URL", "Pages", "Output")
        value: Value text to display after label

    Returns:
        Formatted string with consistent alignment (9 chars for label column)
    """
    # Format with 1-space left padding and right-pad to width of "Output" + 2 spaces
    # " Output   " = 1 + 6 + 2 = 9 chars total for label column
    return f" {label:<8}{value}"

def format_error_line(error_msg: str, show_full_urls: bool = False) -> str:
    """Format error message with type and normalized path.

    Args:
        error_msg: Raw error message from crawler
        show_full_urls: If True, show full URLs; if False, normalize paths

    Returns:
        Formatted error with aligned bracket prefix and normalized path
    """
    if ": " in error_msg:
        error_type, url = error_msg.split(": ", 1)
        normalized_path = _normalize_log_rest(url.strip(), show_full_urls)
        error_label = f"[{error_type.strip()}]"
        return f" {error_label:<7}{normalized_path}"
    return error_msg


def get_error_entries(stats: CrawlStats) -> List:
    """Get error log entries from pre-filtered list (O(1) access).

    Args:
        stats: CrawlStats object with error_logs list

    Returns:
        List of LogEntry objects for errors
    """
    return stats.error_logs


def get_main_log_lines(stats: CrawlStats) -> List[str]:
    """Get main log lines from pre-filtered list (O(1) access).

    Main logs include: FETCH, SAVE, SKIP, INFO
    Excludes: ERROR (in errors window), QUEUE (in queue window)

    Args:
        stats: CrawlStats object with main_logs list

    Returns:
        List of message strings for main log display
    """
    return [str(entry) for entry in stats.main_logs]


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate a string to fit within a maximum length.

    Args:
        text: String to truncate
        max_length: Maximum length (including suffix)
        suffix: Suffix to append if truncated (default: "...")

    Returns:
        Truncated string with suffix if needed, original if fits

    Examples:
        truncate_string("Hello World", 8) -> "Hello..."
        truncate_string("Hi", 10) -> "Hi"
    """
    if len(text) <= max_length:
        return text
    if max_length <= len(suffix):
        return text[:max_length]
    return text[: max_length - len(suffix)] + suffix


# ============================================================================
# Layout Geometry System
# ============================================================================


@dataclass
class Rect:
    """
    Represents a rectangular region in the terminal using inclusive coordinates.

    Attributes:
        y0: Top row (inclusive)
        x0: Left column (inclusive)
        y1: Bottom row (inclusive)
        x1: Right column (inclusive)

    Example:
        Rect(y0=0, x0=0, y1=2, x1=9) represents a 3-row by 10-column region:
        - Rows: 0, 1, 2 (3 rows total)
        - Columns: 0, 1, 2, ..., 9 (10 columns total)
    """
    y0: int
    x0: int
    y1: int
    x1: int


def rect_height(r: Rect) -> int:
    """
    Calculate the height of a rectangle (number of rows).

    Args:
        r: Rectangle to measure

    Returns:
        Height in rows (always >= 1 for valid rectangles)

    Example:
        rect_height(Rect(y0=5, x0=0, y1=9, x1=10)) -> 5
        (rows 5, 6, 7, 8, 9)
    """
    return r.y1 - r.y0 + 1


def rect_width(r: Rect) -> int:
    """
    Calculate the width of a rectangle (number of columns).

    Args:
        r: Rectangle to measure

    Returns:
        Width in columns (always >= 1 for valid rectangles)

    Example:
        rect_width(Rect(y0=0, x0=5, y1=10, x1=14)) -> 10
        (columns 5, 6, 7, 8, 9, 10, 11, 12, 13, 14)
    """
    return r.x1 - r.x0 + 1


def is_wide_layout(height: int, width: int) -> bool:
    """
    Determine if the terminal aspect ratio calls for a wide layout.

    Wide layout is used when the terminal is significantly wider than it is
    tall, allowing side-by-side panels for better space utilization.

    Args:
        height: Terminal height in rows
        width: Terminal width in columns

    Returns:
        True if wide layout should be used (width > height * 1.5),
        False for narrow/square layout

    Examples:
        is_wide_layout(40, 80) -> True (80 > 40*1.5=60)
        is_wide_layout(50, 80) -> False (80 <= 50*1.5=75)
        is_wide_layout(24, 80) -> True (80 > 24*1.5=36)
    """
    return width > height * 1.5


def draw_window_with_border(win: "curses.window", label: str, count: int | None = None) -> Tuple[int, int]:
    """
    Draw a bordered window with a top-right label.

    This function draws a box border around the window and places a label
    at the top-right corner of the border. If a count is provided, it's
    appended to the label as ": {count}".

    Args:
        win: Curses window to draw border on
        label: Label text to display (e.g., "Meta", "Errors", "Queue", "Log")
        count: Optional count to display after label (e.g., error count, queue size)

    Returns:
        Tuple of (inner_y0, inner_x0): coordinates where content should start
        (1 row down and 1 column right from the border)

    Raises:
        curses.error: When window is too small to draw border or label

    Examples:
        # Draw window with simple label
        inner_y, inner_x = draw_window_with_border(win, "Meta")

        # Draw window with count
        inner_y, inner_x = draw_window_with_border(win, "Errors", 5)
        # Label displays as " Errors: 5 "
    """
    try:
        height, width = win.getmaxyx()

        if height < 3 or width < 4:
            return (0, 0)

        win.box()

        if count is not None:
            label_text = f" {label}: {count} "
        else:
            label_text = f" {label} "

        max_label_len = width - 2
        if len(label_text) > max_label_len:
            label_text = label_text[: max_label_len - 1] + "…"

        label_x = width - len(label_text) - 1
        if label_x < 1:
            label_x = 1

        # Use cyan for window labels if colors available
        label_attr = curses.color_pair(4) | curses.A_BOLD if curses.has_colors() else curses.A_BOLD
        win.addstr(0, label_x, label_text, label_attr)

        return (1, 1)

    except curses.error:
        return (0, 0)


def compute_layout(height: int, width: int) -> Tuple[Dict[str, Rect], int, int]:
    """
    Compute window layout based on terminal dimensions.

    This function implements two adaptive layout modes:

    NARROW/SQUARE LAYOUT (width <= height * 1.2):
    ┌─────────────────────────────┐
    │ meta      │ errors          │  <- Top band (3 rows)
    ├─────────────────────────────┤
    │ queue                       │  <- Middle band (1/3 remaining)
    ├─────────────────────────────┤
    │ log                         │  <- Bottom band (2/3 remaining)
    ├─────────────────────────────┤
    │ help                        │  <- Help line (1 row)
    └─────────────────────────────┘

    WIDE LAYOUT (width > height * 1.2):
    ┌─────────────────────────────┐
    │ meta      │ errors          │  <- Top band (3 rows)
    ├──────────────┬──────────────┤
    │ queue        │ log          │  <- Lower band (remaining rows)
    ├──────────────┴──────────────┤
    │ help                        │  <- Help line (1 row)
    └─────────────────────────────┘

    Coordinate System:
    - All coordinates are inclusive: Rect(y0=0, x0=0, y1=2, x1=9) is 3×10
    - Terminal uses 0-based indexing
    - Height and width are the terminal dimensions from stdscr.getmaxyx()

    Edge Case Handling:
    - Terminals smaller than 10 rows or 20 columns get minimal layouts
    - All rectangles are guaranteed to have positive dimensions
    - Coordinates are clamped to valid ranges

    Args:
        height: Terminal height in rows
        width: Terminal width in columns

    Returns:
        Tuple of:
        - Dictionary mapping window names to Rect objects:
          - "meta": Metadata panel (top-left)
          - "errors": Error summary panel (top-right)
          - "queue": Queue status panel
          - "log": Log output panel
        - Help line y-coordinate (always height - 1)
        - Status bar y-coordinate (always 0)

    Examples:
        # Narrow terminal (40 rows × 80 cols)
        rects, help_y = compute_layout(40, 80)
        # meta: Rect(0, 0, 2, 39)  - 3 rows × 40 cols
        # errors: Rect(0, 40, 2, 79) - 3 rows × 40 cols
        # queue: Rect(3, 0, 14, 79) - 12 rows × 80 cols
        # log: Rect(15, 0, 38, 79) - 24 rows × 80 cols
        # help_y: 39

        # Wide terminal (30 rows × 120 cols)
        rects, help_y = compute_layout(30, 120)
        # meta: Rect(0, 0, 2, 59)  - 3 rows × 60 cols
        # errors: Rect(0, 60, 2, 119) - 3 rows × 60 cols
        # queue: Rect(3, 0, 28, 59) - 26 rows × 60 cols
        # log: Rect(3, 60, 28, 119) - 26 rows × 60 cols
        # help_y: 29
    """
    # Handle minimum terminal size gracefully
    height = max(10, height)
    width = max(20, width)

    # Reserve row 0 for status bar, bottom line for help
    status_y = 0
    help_y = height - 1
    available_height = height - 2  # Exclude status bar (top) and help line (bottom)
    content_start_y = 1  # Windows start at row 1

    # Calculate mid points for layout
    mid_y = available_height // 2
    mid_x = width // 2

    if is_wide_layout(height, width):
        # Wide layout:
        # ┌─────────┬─────────┐
        # │  Queue  │  Meta   │  Top half
        # │         ├─────────┤
        # │         │ Errors  │
        # ├─────────┴─────────┤
        # │    Log (full)     │  Bottom half
        # └───────────────────┘

        # Top left: Queue (occupies left half of top)
        queue_rect = Rect(
            y0=content_start_y,
            x0=0,
            y1=content_start_y + mid_y - 1,
            x1=mid_x - 1
        )

        # Top right top: Meta (needs ~9 rows: 7 content + 2 borders)
        meta_height = min(10, mid_y)  # At most 10 rows or half of top section
        meta_rect = Rect(
            y0=content_start_y,
            x0=mid_x,
            y1=content_start_y + meta_height - 1,
            x1=width - 1
        )

        # Top right bottom: Errors (rest of top right)
        errors_rect = Rect(
            y0=content_start_y + meta_height,
            x0=mid_x,
            y1=content_start_y + mid_y - 1,
            x1=width - 1
        )

        # Bottom: Log (full width)
        log_rect = Rect(
            y0=content_start_y + mid_y,
            x0=0,
            y1=content_start_y + available_height - 1,
            x1=width - 1
        )
    else:
        # Narrow layout: everything stacked vertically
        # Top band for meta and errors side-by-side
        top_band_height = min(max(10, available_height // 4), available_height // 3)
        top_band_y1 = content_start_y + top_band_height - 1

        meta_rect = Rect(
            y0=content_start_y,
            x0=0,
            y1=top_band_y1,
            x1=mid_x - 1
        )

        errors_rect = Rect(
            y0=content_start_y,
            x0=mid_x,
            y1=top_band_y1,
            x1=width - 1
        )

        # Remaining rows for queue and log stacked
        remaining_y0 = top_band_y1 + 1
        remaining_y1 = content_start_y + available_height - 1
        remaining_height = remaining_y1 - remaining_y0 + 1

        queue_height = max(1, remaining_height // 3)
        queue_y1 = remaining_y0 + queue_height - 1

        queue_rect = Rect(
            y0=remaining_y0,
            x0=0,
            y1=queue_y1,
            x1=width - 1
        )

        log_rect = Rect(
            y0=queue_y1 + 1,
            x0=0,
            y1=remaining_y1,
            x1=width - 1
        )

    # Ensure all rectangles have positive dimensions
    rects = {
        "meta": meta_rect,
        "errors": errors_rect,
        "queue": queue_rect,
        "log": log_rect,
    }

    # Validate all rectangles (for debugging/safety)
    for name, rect in rects.items():
        assert rect_height(rect) >= 1, f"{name} has non-positive height"
        assert rect_width(rect) >= 1, f"{name} has non-positive width"
        assert 0 <= rect.y0 <= rect.y1 < height, f"{name} has invalid y coords"
        assert 0 <= rect.x0 <= rect.x1 < width, f"{name} has invalid x coords"

    return rects, help_y, status_y


# ============================================================================
# Window Drawing Functions
# ============================================================================


def draw_help_overlay(stdscr: "curses.window", height: int, width: int) -> None:
    """
    Draw a centered help overlay showing all keyboard controls.

    Args:
        stdscr: Curses window to draw in
        height: Terminal height in rows
        width: Terminal width in columns
    """
    # Define help content
    help_lines = [
        "Keyboard Controls",
        "",
        "Navigation:",
        "  \u2191/\u2193        Scroll log up/down by one line",
        "  PgUp/PgDn  Scroll log up/down by half page",
        "  Home       Jump to oldest logs",
        "  End        Jump to newest logs",
        "",
        "Mouse:",
        "  Wheel      Scroll log window",
        "",
        "Controls:",
        "  p          Pause/resume crawl",
        "  c          Re-center queue on current item",
        "  u          Toggle URL display (paths/full)",
        "  m          Open configuration menu",
        "  q          Quit (exit TUI)",
        "",
        "Help:",
        "  h          Toggle this help screen",
        "  Esc        Close this help screen",
        "",
        "After crawl finishes, press 'q' to exit",
    ]

    # Calculate box dimensions (centered)
    box_height = min(len(help_lines) + 4, height - 4)  # +4 for borders and padding
    box_width = min(62, width - 4)  # Leave margins

    # Calculate position (centered)
    start_y = max(0, (height - box_height) // 2)
    start_x = max(0, (width - box_width) // 2)

    try:
        # Draw box background (filled with spaces)
        for i in range(box_height):
            y_pos = start_y + i
            if 0 <= y_pos < height:
                try:
                    stdscr.addstr(y_pos, start_x, " " * box_width, curses.A_REVERSE)
                except curses.error:
                    pass

        # Draw border
        for i in range(box_height):
            y_pos = start_y + i
            if 0 <= y_pos < height:
                if i == 0 or i == box_height - 1:
                    # Top and bottom border
                    border = "+" + "-" * (box_width - 2) + "+"
                    try:
                        stdscr.addstr(y_pos, start_x, border, curses.A_REVERSE | curses.A_BOLD)
                    except curses.error:
                        pass
                else:
                    # Side borders
                    try:
                        stdscr.addstr(y_pos, start_x, "|", curses.A_REVERSE | curses.A_BOLD)
                        stdscr.addstr(y_pos, start_x + box_width - 1, "|", curses.A_REVERSE | curses.A_BOLD)
                    except curses.error:
                        pass

        # Draw help content
        content_start_y = start_y + 2
        content_width = box_width - 4  # Leave padding
        available_content_lines = box_height - 4

        for i, line in enumerate(help_lines[:available_content_lines]):
            y_pos = content_start_y + i
            if 0 <= y_pos < height:
                # Center title, left-align others
                if i == 0:  # Title
                    line_x = start_x + (box_width - len(line)) // 2
                    try:
                        stdscr.addstr(y_pos, line_x, line, curses.A_REVERSE | curses.A_BOLD)
                    except curses.error:
                        pass
                else:
                    # Truncate if needed
                    display_line = line[:content_width] if len(line) > content_width else line
                    line_x = start_x + 2
                    try:
                        stdscr.addstr(y_pos, line_x, display_line, curses.A_REVERSE)
                    except curses.error:
                        pass

    except curses.error:
        pass  # Terminal too small or other error


def draw_config_menu_overlay(
    stdscr: "curses.window",
    height: int,
    width: int,
    config: Config,
    stats: "CrawlStats",
    state: ConfigMenuState,
) -> None:
    """
    Draw a centered config menu overlay for mid-crawl configuration changes.

    Args:
        stdscr: Curses window to draw in
        height: Terminal height in rows
        width: Terminal width in columns
        config: Current configuration object
        stats: Crawl stats (for auto_scroll state)
        state: Current menu state
    """
    # Return early if terminal too small
    if height < 20 or width < 40:
        return

    # Define menu content - field names and labels
    # Use state edit buffers to show edited (but not yet saved) values
    fields = [
        ("Whitelist (restrict_prefix)", state.whitelist_edit),
        ("Blacklist (exclude_patterns)", ", ".join(state.blacklist_edit) if state.blacklist_edit else ""),
        ("Auto-scroll logs", "Enabled" if state.autoscroll_edit else "Disabled"),
    ]

    # Calculate box dimensions (60% width, auto height)
    box_width = min(int(width * 0.6), 80)
    # Height: title + blank + fields*2 (label+value) + blank + help line + borders
    box_height = min(3 + len(fields) * 2 + 2 + 2, height - 4)

    # Calculate position (centered)
    start_y = max(0, (height - box_height) // 2)
    start_x = max(0, (width - box_width) // 2)

    try:
        # Draw box background (filled with spaces)
        for i in range(box_height):
            y_pos = start_y + i
            if 0 <= y_pos < height:
                try:
                    stdscr.addstr(y_pos, start_x, " " * box_width, curses.A_REVERSE)
                except curses.error:
                    pass

        # Draw border
        for i in range(box_height):
            y_pos = start_y + i
            if 0 <= y_pos < height:
                if i == 0 or i == box_height - 1:
                    # Top and bottom border
                    border = "+" + "-" * (box_width - 2) + "+"
                    try:
                        if curses.has_colors():
                            stdscr.addstr(y_pos, start_x, border, curses.color_pair(4) | curses.A_BOLD | curses.A_REVERSE)
                        else:
                            stdscr.addstr(y_pos, start_x, border, curses.A_REVERSE | curses.A_BOLD)
                    except curses.error:
                        pass
                else:
                    # Side borders
                    try:
                        if curses.has_colors():
                            stdscr.addstr(y_pos, start_x, "|", curses.color_pair(4) | curses.A_BOLD | curses.A_REVERSE)
                            stdscr.addstr(y_pos, start_x + box_width - 1, "|", curses.color_pair(4) | curses.A_BOLD | curses.A_REVERSE)
                        else:
                            stdscr.addstr(y_pos, start_x, "|", curses.A_REVERSE | curses.A_BOLD)
                            stdscr.addstr(y_pos, start_x + box_width - 1, "|", curses.A_REVERSE | curses.A_BOLD)
                    except curses.error:
                        pass

        # Draw title (centered)
        title = "Mid-Crawl Configuration"
        title_y = start_y + 1
        title_x = start_x + (box_width - len(title)) // 2
        try:
            if curses.has_colors():
                stdscr.addstr(title_y, title_x, title, curses.color_pair(1) | curses.A_BOLD | curses.A_REVERSE)
            else:
                stdscr.addstr(title_y, title_x, title, curses.A_REVERSE | curses.A_BOLD)
        except curses.error:
            pass

        # Draw fields
        content_y = start_y + 3
        content_width = box_width - 4  # Leave padding

        for idx, (label, value) in enumerate(fields):
            field_y = content_y + idx * 2
            if field_y >= start_y + box_height - 3:
                break  # Don't overflow box

            # Determine if this field is selected and if we're editing it
            is_selected = (idx == state.current_field)
            is_editing = (is_selected and state.editing)

            # Show cursor/indicator for selected field
            indicator = "> " if is_selected else "  "

            try:
                # Draw label with indicator
                label_text = f"{indicator}{label}:"
                if len(label_text) > content_width:
                    label_text = label_text[:content_width - 3] + "..."

                label_x = start_x + 2
                if curses.has_colors():
                    label_attr = curses.color_pair(6) | curses.A_BOLD | curses.A_REVERSE if is_selected else curses.color_pair(1) | curses.A_REVERSE
                else:
                    label_attr = curses.A_BOLD | curses.A_REVERSE if is_selected else curses.A_REVERSE
                stdscr.addstr(field_y, label_x, label_text, label_attr)

                # Draw value (with edit indicator if editing)
                value_y = field_y + 1

                # Get current edit value if editing this field
                if is_editing:
                    if idx == 0:  # Whitelist
                        display_value = state.whitelist_edit
                    elif idx == 1:  # Blacklist
                        display_value = ", ".join(state.blacklist_edit) if state.blacklist_edit else ""
                    elif idx == 2:  # Auto-scroll
                        display_value = "Enabled" if state.autoscroll_edit else "Disabled"
                    else:
                        display_value = value
                else:
                    display_value = value

                # For bool fields in edit mode, show toggle indicator
                if is_editing and idx == 2:  # Auto-scroll bool field
                    display_value = f"[{'X' if state.autoscroll_edit else ' '}] {display_value}"

                value_text = f"    {display_value}"
                if len(value_text) > content_width:
                    value_text = value_text[:content_width - 3] + "..."

                value_x = start_x + 2
                if curses.has_colors():
                    value_attr = curses.color_pair(1) | curses.A_REVERSE
                    if is_editing:
                        value_attr = curses.color_pair(2) | curses.A_REVERSE  # Yellow for editing
                else:
                    value_attr = curses.A_REVERSE
                    if is_editing:
                        value_attr = curses.A_REVERSE | curses.A_BOLD
                stdscr.addstr(value_y, value_x, value_text, value_attr)

                # Show cursor in edit mode for text fields
                if is_editing and idx < 2:  # Text fields (whitelist, blacklist)
                    cursor_x = value_x + 4 + state.cursor_pos
                    if cursor_x < start_x + box_width - 2:
                        try:
                            stdscr.addstr(value_y, cursor_x, "_", curses.A_REVERSE | curses.A_BLINK)
                        except curses.error:
                            pass

            except curses.error:
                pass

        # Draw help line at bottom
        help_y = start_y + box_height - 2
        help_x = start_x + 2

        if state.editing:
            # Show editing help
            if state.current_field == 2:  # Bool field
                help_text = "Space: toggle | Enter: done | Esc: cancel"
            else:  # Text fields
                help_text = "Type to edit | Enter: done | Esc: cancel"
        else:
            # Show navigation help
            help_text = "↑/↓ or j/k: navigate | Enter: edit | s: save | m/Esc: cancel"

        if len(help_text) > content_width:
            help_text = help_text[:content_width - 3] + "..."

        try:
            if curses.has_colors():
                stdscr.addstr(help_y, help_x, help_text, curses.color_pair(5) | curses.A_REVERSE)
            else:
                stdscr.addstr(help_y, help_x, help_text, curses.A_REVERSE | curses.A_DIM)
        except curses.error:
            pass

    except curses.error:
        pass  # Terminal too small or other error


def draw_config_form(
    stdscr: "curses.window",
    height: int,
    width: int,
    state: ConfigFormState,
) -> None:
    """
    Draw the configuration form for pre-crawl setup.

    Renders a centered form with labeled fields, visual selection indicator,
    and help line showing available keybinds. Expandable fields show as toggles
    with indented sub-fields when expanded.

    Args:
        stdscr: Curses window to draw in
        height: Terminal height in rows
        width: Terminal width in columns
        state: Current form state
    """
    # Form layout constants
    LABEL_WIDTH = 18  # Width for field labels
    MIN_VALUE_WIDTH = 30  # Minimum width for value field
    FORM_PADDING = 4  # Padding from edges
    SUBFIELD_INDENT = 2  # Indentation for sub-fields

    # Calculate form dimensions
    form_width = min(width - FORM_PADDING * 2, LABEL_WIDTH + MIN_VALUE_WIDTH + 10)

    # Count expanded sub-fields for height calculation
    expanded_count = sum(1 for f in CONFIG_FORM_FIELDS if f.expandable and state.expanded.get(f.name, False))
    form_height = len(CONFIG_FORM_FIELDS) + expanded_count + 7  # Fields + sub-fields + profile + title + help + borders

    # Center the form
    start_x = max(FORM_PADDING, (width - form_width) // 2)
    start_y = max(2, (height - form_height) // 2)

    value_width = form_width - LABEL_WIDTH - 6  # Space for value display

    try:
        # Clear screen
        stdscr.erase()

        # Draw title
        title = "crawl2md Configuration"
        title_x = start_x + (form_width - len(title)) // 2
        try:
            stdscr.addstr(start_y, title_x, title, curses.A_BOLD)
        except curses.error:
            pass

        # Draw separator line
        try:
            stdscr.addstr(start_y + 1, start_x, "─" * form_width)
        except curses.error:
            pass

        # Draw profile selector
        from .config import load_profiles
        profiles = load_profiles()
        profile_names = ["default"] + list(profiles.keys()) + ["+"]

        profile_y = start_y + 2
        profile_label = f"{'Profile':>{LABEL_WIDTH}}: "

        try:
            # Draw profile label
            profile_label_attr = curses.A_BOLD if state.on_profile_selector else curses.A_NORMAL
            stdscr.addstr(profile_y, start_x, profile_label, profile_label_attr)

            # Draw profile options in compact dropdown style
            value_x = start_x + len(profile_label)
            current_profile = state.current_profile or "default"

            # Get current position in list
            try:
                current_idx = profile_names.index(current_profile)
            except ValueError:
                current_idx = 0

            # Build compact dropdown display
            # Show: < profile_name >  (X/Y)
            left_arrow = "◀" if current_idx > 0 else " "
            right_arrow = "▶" if current_idx < len(profile_names) - 1 else " "

            # Special handling for "+" indicator
            if current_profile == "+":
                profile_display = f"{left_arrow} [+ new profile] {right_arrow}  ({current_idx + 1}/{len(profile_names)})"
            else:
                profile_display = f"{left_arrow} {current_profile} {right_arrow}  ({current_idx + 1}/{len(profile_names)})"

            if state.on_profile_selector:
                # Highlight when selected
                padded_profile = profile_display.ljust(value_width)[:value_width]
                stdscr.addstr(profile_y, value_x, padded_profile, curses.A_REVERSE)
            else:
                stdscr.addstr(profile_y, value_x, profile_display)
        except curses.error:
            pass

        # Draw each field
        field_start_y = start_y + 4
        y_pos = field_start_y

        for i, form_field in enumerate(CONFIG_FORM_FIELDS):
            is_selected = (i == state.field_index) and not state.on_profile_selector
            is_expanded = state.expanded.get(form_field.name, False)

            # Get field value
            value = state.values.get(form_field.name, "")

            # Format label (right-aligned)
            label = f"{form_field.label:>{LABEL_WIDTH}}: "

            # Handle expandable fields (toggle + sub-field)
            if form_field.expandable:
                # Draw toggle line
                toggle_value = "Yes" if is_expanded else "No"
                if is_expanded:
                    display_value = "[Yes]  No "
                else:
                    display_value = " Yes  [No]"

                try:
                    # Draw label
                    label_attr = curses.A_BOLD if is_selected and not state.on_subfield else curses.A_NORMAL
                    stdscr.addstr(y_pos, start_x, label, label_attr)

                    # Draw toggle value
                    value_x = start_x + len(label)
                    if is_selected and not state.on_subfield:
                        # Highlight toggle when selected
                        padded_value = display_value.ljust(value_width)[:value_width]
                        stdscr.addstr(y_pos, value_x, padded_value, curses.A_REVERSE)
                    else:
                        stdscr.addstr(y_pos, value_x, display_value)
                except curses.error:
                    pass

                y_pos += 1

                # Draw sub-field if expanded
                if is_expanded:
                    # Check if this field supports multi-select (has saved values)
                    from .config import load_saved_values
                    saved_values = load_saved_values()

                    # Map field names to saved value lists
                    field_saved_map = {
                        "tags": saved_values.tags,
                        "restrict_prefix": saved_values.restrict_prefixes,
                        "exclude_patterns": saved_values.exclude_patterns,
                        "user_agent": saved_values.user_agents,
                    }

                    has_saved = form_field.name in field_saved_map and len(field_saved_map[form_field.name]) > 0

                    if has_saved and is_selected and state.on_subfield and state.multiselect_mode:
                        # Draw multi-select UI
                        saved_list = field_saved_map[form_field.name]
                        options = saved_list + ["+ custom..."]

                        for opt_idx, option in enumerate(options):
                            opt_y = y_pos + opt_idx
                            opt_x = start_x + SUBFIELD_INDENT + 2

                            try:
                                # Determine if this option is selected
                                is_checked = option in state.multiselect_selected
                                checkbox = "[x]" if is_checked else "[ ]"

                                # Highlight current selection
                                if opt_idx == state.multiselect_index:
                                    display_text = f"{checkbox} {option}"
                                    stdscr.addstr(opt_y, opt_x, display_text, curses.A_REVERSE)
                                else:
                                    stdscr.addstr(opt_y, opt_x, f"{checkbox} {option}")
                            except curses.error:
                                pass

                        y_pos += len(options)
                    else:
                        # Draw regular text input sub-field
                        subfield_label = f"{'':>{LABEL_WIDTH-SUBFIELD_INDENT}}  ↳ "
                        subfield_value_x = start_x + SUBFIELD_INDENT + len(subfield_label)

                        # Format sub-field display
                        if value:
                            display_subvalue = value
                        else:
                            display_subvalue = form_field.placeholder

                        # Truncate if needed
                        avail_width = value_width - SUBFIELD_INDENT
                        if len(display_subvalue) > avail_width:
                            display_subvalue = display_subvalue[:avail_width - 3] + "..."

                        try:
                            # Draw sub-field label
                            dim_attr = curses.color_pair(5) if curses.has_colors() else curses.A_DIM
                            subfield_label_attr = curses.A_BOLD if is_selected and state.on_subfield else dim_attr
                            stdscr.addstr(y_pos, start_x + SUBFIELD_INDENT, subfield_label, subfield_label_attr)

                            # Draw sub-field value
                            if is_selected and state.on_subfield:
                                if state.edit_mode:
                                    # Edit mode: show value with cursor
                                    edit_value = value if value else ""
                                    cursor_pos = min(state.cursor_pos, len(edit_value))

                                    # Draw text before cursor
                                    if cursor_pos > 0:
                                        stdscr.addstr(y_pos, subfield_value_x, edit_value[:cursor_pos])

                                    # Draw cursor position (highlighted)
                                    cursor_char = edit_value[cursor_pos] if cursor_pos < len(edit_value) else " "
                                    stdscr.addstr(y_pos, subfield_value_x + cursor_pos, cursor_char, curses.A_REVERSE)

                                    # Draw text after cursor
                                    if cursor_pos < len(edit_value) - 1:
                                        stdscr.addstr(y_pos, subfield_value_x + cursor_pos + 1, edit_value[cursor_pos + 1:])
                                else:
                                    # Selected but not editing: highlight the whole value area
                                    # Show hint if saved values available
                                    if has_saved:
                                        display_subvalue = "(Press Enter for multi-select)"
                                    padded_subvalue = display_subvalue.ljust(avail_width)[:avail_width]
                                    stdscr.addstr(y_pos, subfield_value_x, padded_subvalue, curses.A_REVERSE)
                            else:
                                # Not selected
                                if value:
                                    stdscr.addstr(y_pos, subfield_value_x, display_subvalue)
                                else:
                                    # Show placeholder in muted grey
                                    stdscr.addstr(y_pos, subfield_value_x, display_subvalue, dim_attr)
                        except curses.error:
                            pass

                        y_pos += 1

            # Handle non-expandable fields
            else:
                # Format value display
                if form_field.field_type == "bool":
                    # Boolean: show [Yes] / [No] toggle
                    if value.lower() in ("yes", "true", "1"):
                        display_value = "[Yes]  No "
                    else:
                        display_value = " Yes  [No]"
                else:
                    # Text/number: show value or placeholder
                    if value:
                        display_value = value
                    else:
                        display_value = form_field.placeholder

                    # Truncate if needed
                    if len(display_value) > value_width:
                        display_value = display_value[:value_width - 3] + "..."

                try:
                    # Draw label
                    label_attr = curses.A_BOLD if is_selected else curses.A_NORMAL
                    stdscr.addstr(y_pos, start_x, label, label_attr)

                    # Draw value
                    value_x = start_x + len(label)
                    if is_selected:
                        if state.edit_mode:
                            # Edit mode: show value with cursor
                            if form_field.field_type != "bool":
                                # Draw the value
                                edit_value = value if value else ""
                                # Ensure cursor is within bounds
                                cursor_pos = min(state.cursor_pos, len(edit_value))

                                # Draw text before cursor
                                if cursor_pos > 0:
                                    stdscr.addstr(y_pos, value_x, edit_value[:cursor_pos])

                                # Draw cursor position (highlighted)
                                cursor_char = edit_value[cursor_pos] if cursor_pos < len(edit_value) else " "
                                stdscr.addstr(y_pos, value_x + cursor_pos, cursor_char, curses.A_REVERSE)

                                # Draw text after cursor
                                if cursor_pos < len(edit_value) - 1:
                                    stdscr.addstr(y_pos, value_x + cursor_pos + 1, edit_value[cursor_pos + 1:])
                            else:
                                stdscr.addstr(y_pos, value_x, display_value, curses.A_REVERSE)
                        else:
                            # Selected but not editing: highlight the whole value area
                            padded_value = display_value.ljust(value_width)[:value_width]
                            stdscr.addstr(y_pos, value_x, padded_value, curses.A_REVERSE)
                    else:
                        # Not selected
                        if value:
                            stdscr.addstr(y_pos, value_x, display_value)
                        else:
                            # Show placeholder in muted grey (A_DIM unreliable)
                            dim_attr = curses.color_pair(5) if curses.has_colors() else curses.A_DIM
                            stdscr.addstr(y_pos, value_x, display_value, dim_attr)

                except curses.error:
                    pass

                y_pos += 1

        # Draw separator before help
        help_y = y_pos + 1
        try:
            stdscr.addstr(help_y, start_x, "─" * form_width)
        except curses.error:
            pass

        # Draw help line
        if state.edit_mode:
            help_text = "Type to edit │ Enter:confirm │ Esc:cancel"
        else:
            help_text = "↑/↓:select │ Enter:edit │ Tab:next │ q:quit │ F10:start crawl"

        help_x = start_x + (form_width - len(help_text)) // 2
        try:
            if curses.has_colors():
                stdscr.addstr(help_y + 1, help_x, help_text, curses.color_pair(1))
            else:
                stdscr.addstr(help_y + 1, help_x, help_text)
        except curses.error:
            pass

        # Draw bottom status with validation
        status_y = height - 1
        validation_error = _validate_form_state(state)
        if validation_error:
            status = validation_error
            status_attr = curses.color_pair(3) if curses.has_colors() else curses.A_BOLD
        else:
            status = "Ready to start (F10)"
            status_attr = curses.color_pair(5) if curses.has_colors() else curses.A_DIM

        try:
            status_x = (width - len(status)) // 2
            stdscr.addstr(status_y, status_x, status, status_attr)
        except curses.error:
            pass

    except curses.error:
        pass


def draw_metadata_window(
    win: "curses.window",
    inner_y: int,
    inner_x: int,
    stats: CrawlStats,
    config: Config,
) -> None:
    """
    Draw the metadata window with crawl statistics.

    Displays high-level information about the crawl:
    - Root URL (truncated if needed)
    - Output directory
    - Pages crawled
    - Files saved
    - Errors count
    - Queue size
    - Elapsed time
    - Pages per second rate

    Args:
        win: Curses window to draw in
        inner_y: Y coordinate for first line of content
        inner_x: X coordinate for content start
        stats: CrawlStats object with current statistics
        config: Config object
    """
    try:
        height, width = win.getmaxyx()
        max_line_width = width - inner_x - 1  # Leave room for right border

        if max_line_width < 10:
            return  # Window too narrow

        current_y = inner_y
        available_lines = height - inner_y - 1  # Leave room for bottom border

        # Calculate elapsed time (pause-aware)
        elapsed = stats.get_elapsed_time()

        # Calculate rate (pages per second)
        if elapsed > 0:
            rate = stats.pages_processed / elapsed
        else:
            rate = 0.0

        # Build lines to display with aligned labels (9-char column)
        # Order: URL, Output, Pages, Saved, Errors, Queue, Time, Rate
        output_path = contract_home_dir(config.output or 'docs-md')
        lines = [
            _format_meta_line("URL", truncate_string(config.start_url or '(none)', max_line_width - 9)),
            _format_meta_line("Output", truncate_string(output_path, max_line_width - 9)),
            _format_meta_line("Pages", str(stats.pages_processed)),
            _format_meta_line("Saved", str(stats.files_saved)),
            _format_meta_line("Errors", str(stats.error_count)),
            _format_meta_line("Queue", str(stats.queue_size)),
            _format_meta_line("Time", f"{elapsed:.1f}s"),
            _format_meta_line("Rate", f"{rate:.2f} p/s"),
        ]

        # Draw lines
        for i, line in enumerate(lines):
            if i >= available_lines:
                break  # No more room
            try:
                truncated_line = truncate_string(line, max_line_width)
                win.addstr(current_y + i, inner_x, truncated_line)
            except curses.error:
                pass  # Line doesn't fit, skip

    except curses.error:
        pass  # Window too small


def draw_errors_window(
    win: "curses.window",
    inner_y: int,
    inner_x: int,
    stats: CrawlStats,
    scroll_offset: int = 0,
    show_full_urls: bool = False,
) -> int:
    """
    Draw the errors window with scrollable error messages.

    Displays a scrolling view of error log entries, with most recent
    errors at the bottom (like a log tail). Each error shows the error
    type and URL, followed by a source line if available.

    Args:
        win: Curses window to draw in
        inner_y: Y coordinate for first line of content
        inner_x: X coordinate for content start
        stats: CrawlStats object with log_entries
        scroll_offset: Scroll offset from bottom (0 = newest, >0 = scrolled up)
        show_full_urls: If True, show full URLs; if False, show normalized paths

    Returns:
        Total number of error lines available (including source lines)
    """
    try:
        height, width = win.getmaxyx()
        max_line_width = width - inner_x - 1  # Leave room for right border

        if max_line_width < 10:
            return 0  # Window too narrow

        available_lines = height - inner_y - 1  # Leave room for bottom border

        if available_lines <= 0:
            return 0  # No room for content

        # Get warning and error entries
        warn_entries = stats.warn_logs  # Already limited to 3 most recent
        error_entries = get_error_entries(stats)

        if not warn_entries and not error_entries:
            try:
                win.addstr(inner_y, inner_x, "(no warnings or errors)")
            except curses.error:
                pass
            return 0

        # Build warning and error display lines
        warn_attr = curses.color_pair(2) if curses.has_colors() else curses.A_BOLD
        warn_display_lines = []
        for entry in warn_entries:
            warn_line = f"WARN: {entry.message}"
            warn_display_lines.append(warn_line)

        error_display_lines = []
        for entry in error_entries:
            error_line = format_error_line(str(entry), show_full_urls)
            error_display_lines.append(error_line)
            if entry.source_url:
                source_display = _normalize_log_rest(entry.source_url, show_full_urls)
                source_line = "         src: " + source_display
                error_display_lines.append(source_line)

        num_warnings = len(warn_display_lines)
        num_errors = len(error_display_lines)

        # Dynamic space allocation: each section gets up to half
        has_both = num_warnings > 0 and num_errors > 0
        separator_lines = 1 if has_both else 0
        usable_lines = available_lines - separator_lines
        max_per_section = usable_lines // 2

        # Calculate how many lines each section CAN display
        max_warnings_display = min(num_warnings, max_per_section) if num_warnings > 0 else 0
        max_errors_display = min(num_errors, max_per_section) if num_errors > 0 else 0

        # Distribute leftover space
        used_lines = max_warnings_display + max_errors_display
        leftover = usable_lines - used_lines

        if leftover > 0:
            if num_warnings > max_warnings_display:
                extra = min(leftover, num_warnings - max_warnings_display)
                max_warnings_display += extra
                leftover -= extra
            if leftover > 0 and num_errors > max_errors_display:
                extra = min(leftover, num_errors - max_errors_display)
                max_errors_display += extra

        current_y = inner_y

        # Warnings section: independent scrolling within its viewport
        if num_warnings > 0 and max_warnings_display > 0:
            # Each section independently clamps scroll to its valid range
            warn_max_scroll = max(0, num_warnings - max_warnings_display)
            warn_scroll = min(scroll_offset, warn_max_scroll)

            warn_start = warn_scroll
            warn_end = min(warn_start + max_warnings_display, num_warnings)
            warnings_to_show = warn_display_lines[warn_start:warn_end]

            for warn_line in warnings_to_show:
                if current_y >= inner_y + available_lines:
                    break
                try:
                    truncated = truncate_string(warn_line, max_line_width)
                    win.addnstr(current_y, inner_x, truncated, max_line_width, warn_attr)
                    current_y += 1
                except curses.error:
                    pass

        # Separator
        if has_both and current_y < inner_y + available_lines:
            try:
                separator = "-" * min(max_line_width, 20)
                sep_attr = curses.color_pair(5) if curses.has_colors() else curses.A_DIM
                win.addnstr(current_y, inner_x, separator, max_line_width, sep_attr)
                current_y += 1
            except curses.error:
                pass

        # Errors section: independent scrolling within its viewport
        if num_errors > 0 and max_errors_display > 0:
            # Each section independently clamps scroll to its valid range
            error_max_scroll = max(0, num_errors - max_errors_display)
            error_scroll = min(scroll_offset, error_max_scroll)

            error_start = error_scroll
            error_end = min(error_start + max_errors_display, num_errors)
            errors_to_show = error_display_lines[error_start:error_end]

            for error_line in errors_to_show:
                if current_y >= inner_y + available_lines:
                    break
                try:
                    sanitized = error_line.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                    truncated = truncate_string(sanitized, max_line_width)
                    win.addnstr(current_y, inner_x, truncated, max_line_width)
                    current_y += 1
                except curses.error:
                    pass

        # Return the larger of the two max scrolls for proper scroll limit calculation
        warn_max = max(0, num_warnings - max_warnings_display) if num_warnings > 0 else 0
        error_max = max(0, num_errors - max_errors_display) if num_errors > 0 else 0
        return max(warn_max, error_max)

    except curses.error:
        return 0  # Window too small


def draw_main_log_window(
    win: "curses.window",
    inner_y: int,
    inner_x: int,
    filtered_log_lines: list[str],
    scroll_offset: int,
    visible_log_height: int,
    show_full_urls: bool = False,
) -> None:
    """
    Draw the main log window with scrollable log lines.

    Args:
        win: Curses window
        inner_y: Y coordinate for first line of content
        inner_x: X coordinate for content start
        filtered_log_lines: Pre-filtered log lines for the main log
        scroll_offset: Current scroll offset from newest line (0 = bottom)
        visible_log_height: Number of visible log lines in the window
        show_full_urls: If True, show full URLs; if False, show only paths
    """
    try:
        height, width = win.getmaxyx()
        max_line_width = width - inner_x - 1

        # Very narrow window / no space
        if max_line_width < 10 or visible_log_height <= 0:
            return

        total_lines = len(filtered_log_lines)

        if total_lines == 0:
            # Nothing to show
            try:
                win.addstr(inner_y, inner_x, "(no log entries yet)")
            except curses.error:
                pass
            return

        # Clamp scroll_offset in case caller forgot
        max_scroll_offset = max(0, total_lines - visible_log_height)
        scroll_offset = max(0, min(scroll_offset, max_scroll_offset))

        # Determine slice of lines to render
        newest_index = total_lines - 1
        oldest_visible_index = max(
            0,
            newest_index - scroll_offset - visible_log_height + 1,
        )
        newest_visible_index = newest_index - scroll_offset

        lines_to_show = filtered_log_lines[
            oldest_visible_index : newest_visible_index + 1
        ]

        current_y = inner_y
        # Use red color for skip reasons, fallback to dim if no colors
        reason_attr = curses.color_pair(3) if curses.has_colors() else curses.A_DIM

        for line in lines_to_show:
            # Check bounds to prevent writing beyond content area
            if current_y >= inner_y + visible_log_height:
                break
            try:
                display = log_line_truncate_preserve_prefix(line, max_line_width, show_full_urls)
                # Sanitize
                sanitized = display.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')

                # Check for skip reason to render in red
                # Pattern: " Skipped   .../path (reason)" - note: colon removed by _reformat_log_prefix
                if " Skipped " in sanitized and sanitized.endswith(")"):
                    # Find the reason part
                    paren_start = sanitized.rfind(" (")
                    if paren_start > 0:
                        main_part = sanitized[:paren_start]
                        reason_part = sanitized[paren_start:]
                        win.addnstr(current_y, inner_x, main_part, max_line_width)
                        # Render reason in red at end
                        reason_x = inner_x + len(main_part)
                        if reason_x < inner_x + max_line_width:
                            win.addnstr(current_y, reason_x, reason_part, max_line_width - len(main_part), reason_attr)
                        current_y += 1
                        continue

                win.addnstr(current_y, inner_x, sanitized, max_line_width)
                current_y += 1
            except curses.error:
                # Skip if it doesn't fit
                continue

    except curses.error:
        # Window too small, nothing to do
        return


def draw_queue_window(
    win: "curses.window",
    inner_y: int,
    inner_x: int,
    stats: CrawlStats,
    scroll_offset: int = 0,
    auto_center: bool = True,
    prev_processing_idx: int = -1,
) -> Tuple[int, int]:
    """
    Draw the queue window with status indicators and auto-centering.

    Displays queue history with status:
    - ✓ (completed) - greyed out
    - ✗ (error) - red
    - ▶ (processing) - highlighted, auto-centered
    - · (queued) - normal

    Args:
        win: Curses window to draw in
        inner_y: Y coordinate for first line of content
        inner_x: X coordinate for content start
        stats: CrawlStats object with queue_history
        scroll_offset: Manual scroll offset (overrides auto-center)
        auto_center: If True, auto-center on processing item
        prev_processing_idx: Previous processing index for stable positioning

    Returns:
        Tuple of (total_entries, processing_index)
    """
    try:
        height, width = win.getmaxyx()
        max_line_width = width - inner_x - 1  # Leave room for right border

        if max_line_width < 10:
            return 0, -1  # Window too narrow

        available_lines = height - inner_y - 1  # Leave room for bottom border

        if available_lines <= 0:
            return 0, -1  # No room for content

        # Check if queue history is empty
        if not stats.queue_history:
            try:
                win.addstr(inner_y, inner_x, "No queue entries yet")
            except curses.error:
                pass
            return 0, -1

        total_entries = len(stats.queue_history)

        # Get processing index from cached value (O(1) instead of O(n) search)
        processing_index = stats.processing_index

        # Calculate visible range with hysteresis for stable positioning
        if auto_center:
            if processing_index >= 0:
                # Check if we should recenter (hysteresis logic)
                should_recenter = False

                if prev_processing_idx == -1:
                    # First time seeing a processing item, center it
                    should_recenter = True
                elif processing_index != prev_processing_idx:
                    # Processing index changed
                    # Calculate current visible range based on previous position
                    center_offset = available_lines // 2
                    prev_start_idx = max(0, prev_processing_idx - center_offset)
                    prev_end_idx = min(total_entries, prev_start_idx + available_lines)
                    if prev_end_idx == total_entries:
                        prev_start_idx = max(0, prev_end_idx - available_lines)

                    # Only recenter if new processing item would be out of view
                    if processing_index < prev_start_idx or processing_index >= prev_end_idx:
                        should_recenter = True

                if should_recenter:
                    # Center on processing item
                    center_offset = available_lines // 2
                    start_idx = max(0, processing_index - center_offset)
                    end_idx = min(total_entries, start_idx + available_lines)
                    if end_idx == total_entries:
                        start_idx = max(0, end_idx - available_lines)
                else:
                    # Keep stable position from previous frame
                    center_offset = available_lines // 2
                    start_idx = max(0, prev_processing_idx - center_offset)
                    end_idx = min(total_entries, start_idx + available_lines)
                    if end_idx == total_entries:
                        start_idx = max(0, end_idx - available_lines)
            else:
                # No processing item - center on first queued item (same as processing)
                first_queued = -1
                for i, entry in enumerate(stats.queue_history):
                    if entry.status == QueueStatus.QUEUED:
                        first_queued = i
                        break
                if first_queued >= 0:
                    # Center on first queued item to prevent jumping when processing completes
                    center_offset = available_lines // 2
                    start_idx = max(0, first_queued - center_offset)
                    end_idx = min(total_entries, start_idx + available_lines)
                    if end_idx == total_entries:
                        start_idx = max(0, end_idx - available_lines)
                else:
                    # No queued items, show from end (most recent)
                    start_idx = max(0, total_entries - available_lines)
                    end_idx = total_entries
        else:
            # Manual scroll mode (scroll_offset is from top, like traditional scrolling)
            start_idx = min(scroll_offset, max(0, total_entries - available_lines))
            end_idx = min(total_entries, start_idx + available_lines)

        entries_to_show = stats.queue_history[start_idx:end_idx]

        # Status symbols
        symbols = {
            QueueStatus.COMPLETED: "✓",
            QueueStatus.SKIPPED: "→",
            QueueStatus.ERROR: "✗",
            QueueStatus.PROCESSING: "▶",
            QueueStatus.QUEUED: "·",
        }

        # Draw entries
        current_y = inner_y
        for entry in entries_to_show:
            if current_y >= inner_y + available_lines:
                break

            symbol = symbols.get(entry.status, "?")
            url_display = format_queue_url(entry.url, max_line_width - 3)
            line = f"{symbol} {url_display}"
            # Sanitize to remove newlines/control chars
            line = line.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')

            try:
                # Apply color/attributes based on status - use addnstr to prevent overflow
                if entry.status == QueueStatus.COMPLETED:
                    # Muted (saved successfully) - use grey color, A_DIM unreliable
                    attr = curses.color_pair(5) if curses.has_colors() else curses.A_DIM
                    win.addnstr(current_y, inner_x, line, max_line_width, attr)
                elif entry.status == QueueStatus.SKIPPED:
                    # Muted (bypassed - non-HTML, duplicate, etc.)
                    attr = curses.color_pair(5) if curses.has_colors() else curses.A_DIM
                    win.addnstr(current_y, inner_x, line, max_line_width, attr)
                elif entry.status == QueueStatus.ERROR:
                    # Red if colors available
                    if curses.has_colors():
                        win.addnstr(current_y, inner_x, line, max_line_width, curses.color_pair(3))
                    else:
                        win.addnstr(current_y, inner_x, line, max_line_width, curses.A_BOLD)
                elif entry.status == QueueStatus.PROCESSING:
                    # Highlighted/bold
                    if curses.has_colors():
                        win.addnstr(current_y, inner_x, line, max_line_width, curses.color_pair(2) | curses.A_BOLD)
                    else:
                        win.addnstr(current_y, inner_x, line, max_line_width, curses.A_REVERSE)
                else:  # QUEUED
                    # Normal
                    win.addnstr(current_y, inner_x, line, max_line_width)

                current_y += 1
            except curses.error:
                pass

        return total_entries, processing_index

    except curses.error:
        return 0, -1  # Window too small


# ============================================================================
# Config Form TUI
# ============================================================================


def run_config_tui(config: Config) -> Optional[Config]:
    """
    Run the config form TUI for pre-crawl configuration.

    Displays an interactive form allowing the user to configure all crawl
    settings before starting. Returns a configured Config object on submit,
    or None if the user cancels.

    Args:
        config: Initial configuration with defaults

    Returns:
        Configured Config object if user submits, None if cancelled
    """
    import os

    # Load theme before entering TUI (so warnings can be displayed)
    theme, theme_warning = load_theme()
    if theme.extended_colors:
        print(
            "Note: 256-color mode enabled. Colors may not match your terminal theme.",
            file=sys.stderr
        )

    # Show theme warning before TUI if present
    if theme_warning:
        print(f"\n⚠️  Theme Warning: {theme_warning}", file=sys.stderr)
        print("Using default theme. Press Enter to continue or Ctrl+C to fix config...", file=sys.stderr)
        try:
            input()
        except (KeyboardInterrupt, EOFError):
            return None

    # Redirect stderr during TUI
    original_stderr = sys.stderr
    try:
        sys.stderr = open(os.devnull, 'w')
        result = curses.wrapper(lambda stdscr: _config_form_loop(stdscr, config, theme))
        return result
    finally:
        sys.stderr.close()
        sys.stderr = original_stderr


def _prompt_profile_name(stdscr: "curses.window") -> Optional[str]:
    """
    Prompt user for a profile name using a simple inline input.

    Args:
        stdscr: Curses window

    Returns:
        Profile name if entered, None if cancelled
    """
    try:
        height, width = stdscr.getmaxyx()
    except curses.error:
        return None

    # Create a centered prompt box
    prompt_text = "Enter profile name: "
    box_width = min(50, width - 4)
    box_height = 3
    box_y = (height - box_height) // 2
    box_x = (width - box_width) // 2

    # Draw prompt box
    stdscr.clear()
    try:
        # Draw border
        for i in range(box_height):
            stdscr.addstr(box_y + i, box_x, " " * box_width)

        # Draw prompt
        stdscr.addstr(box_y + 1, box_x + 2, prompt_text)
        stdscr.refresh()
    except curses.error:
        pass

    # Get input
    curses.echo()
    curses.curs_set(1)

    input_x = box_x + 2 + len(prompt_text)
    input_width = box_width - 4 - len(prompt_text)

    try:
        stdscr.move(box_y + 1, input_x)
        # Use getstr for simple string input
        profile_name = stdscr.getstr(box_y + 1, input_x, input_width).decode('utf-8').strip()
    except (curses.error, KeyboardInterrupt):
        profile_name = None
    finally:
        curses.noecho()
        curses.curs_set(0)

    return profile_name if profile_name else None


def _reset_state_to_config(state: ConfigFormState, config: Config) -> None:
    """
    Reset form state to match the given config (used for "default" profile).

    Args:
        state: Form state to update
        config: Configuration to load from
    """
    # Reset all values from config
    state.values["start_url"] = config.start_url or ""
    state.values["output"] = config.output or "docs-md"
    state.values["tags"] = ",".join(config.tags) if config.tags else ""
    state.values["restrict_prefix"] = config.restrict_prefix or ""
    state.values["exclude_patterns"] = ",".join(config.exclude_patterns) if config.exclude_patterns else ""
    state.values["delay"] = str(config.delay)
    state.values["max_pages"] = str(config.max_pages) if config.max_pages else ""
    state.values["user_agent"] = config.user_agent or ""
    state.values["dedupe"] = "yes" if config.dedupe else "no"

    # Reset expanded state based on whether values differ from defaults
    for form_field in CONFIG_FORM_FIELDS:
        if form_field.expandable:
            val = state.values.get(form_field.name, "")
            # Expand if value is non-empty and different from default
            if val and val != form_field.default_value:
                state.expanded[form_field.name] = True
            else:
                state.expanded[form_field.name] = False


def _load_profile_into_state(state: ConfigFormState, profile: "Profile") -> None:
    """
    Load a profile's values into the form state.

    Args:
        state: Form state to update
        profile: Profile to load from
    """
    from .config import Profile

    # Update form values from profile
    # If a profile value is None, reset to default/empty
    if profile.start_url is not None:
        state.values["start_url"] = profile.start_url
    else:
        state.values["start_url"] = ""

    if profile.output is not None:
        state.values["output"] = profile.output
    else:
        state.values["output"] = "docs-md"

    if profile.tags is not None:
        state.values["tags"] = ",".join(profile.tags)
        state.expanded["tags"] = True
    else:
        state.values["tags"] = ""
        state.expanded["tags"] = False

    if profile.restrict_prefix is not None:
        state.values["restrict_prefix"] = profile.restrict_prefix
        state.expanded["restrict_prefix"] = True
    else:
        state.values["restrict_prefix"] = ""
        state.expanded["restrict_prefix"] = False

    if profile.exclude_patterns is not None:
        state.values["exclude_patterns"] = ",".join(profile.exclude_patterns)
        state.expanded["exclude_patterns"] = True
    else:
        state.values["exclude_patterns"] = ""
        state.expanded["exclude_patterns"] = False

    if profile.delay is not None:
        state.values["delay"] = str(profile.delay)
        state.expanded["delay"] = True
    else:
        state.values["delay"] = "0.3"
        state.expanded["delay"] = False

    if profile.max_pages is not None:
        state.values["max_pages"] = str(profile.max_pages)
        state.expanded["max_pages"] = True
    else:
        state.values["max_pages"] = ""
        state.expanded["max_pages"] = False

    if profile.user_agent is not None:
        state.values["user_agent"] = profile.user_agent
        state.expanded["user_agent"] = True
    else:
        state.values["user_agent"] = ""
        state.expanded["user_agent"] = False

    if profile.dedupe is not None:
        state.values["dedupe"] = "yes" if profile.dedupe else "no"
    else:
        state.values["dedupe"] = "no"


def _validate_form_state(state: ConfigFormState) -> Optional[str]:
    """
    Validate form state before submission.

    Args:
        state: Current form state

    Returns:
        Error message string if validation fails, None if valid
    """
    start_url = state.values.get("start_url", "").strip()

    if not start_url:
        return "Start URL is required"

    # Check URL format
    if not (start_url.startswith("http://") or start_url.startswith("https://")):
        return "URL must start with http:// or https://"

    return None


def _config_form_loop(stdscr: "curses.window", config: Config, theme: Theme) -> Optional[Config]:
    """
    Main config form loop.

    Args:
        stdscr: Curses screen
        config: Initial configuration
        theme: Theme configuration for colors

    Returns:
        Configured Config object if submitted, None if cancelled
    """
    stdscr.nodelay(False)  # Blocking input for form
    curses.curs_set(0)  # Hide cursor
    stdscr.keypad(True)  # Enable special keys

    # Initialize color pairs if available (use terminal default background)
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()  # Enable -1 for terminal default
        # Initialize theme colors (theme loaded in run_config_tui)
        init_theme_colors(theme)

    # Initialize form state from config
    state = ConfigFormState.from_config(config)

    # Track pre-edit value for cancel
    pre_edit_value = ""

    while True:
        # Get terminal size
        try:
            height, width = stdscr.getmaxyx()
        except curses.error:
            time.sleep(0.1)
            continue

        # Draw the form
        draw_config_form(stdscr, height, width, state)

        # Refresh screen
        try:
            stdscr.refresh()
        except curses.error:
            pass

        # Check for exit conditions
        if state.submitted:
            return _build_config_from_state(config, state)
        if state.cancelled:
            return None

        # Get input
        try:
            key = stdscr.getch()
        except curses.error:
            continue
        except KeyboardInterrupt:
            # Ctrl+C - exit gracefully
            return None

        # Handle profile selector navigation
        if state.on_profile_selector:
            from .config import load_profiles, Profile
            profiles = load_profiles()
            profile_names = ["default"] + list(profiles.keys()) + ["+"]

            if key == ord('q') or key == ord('Q'):
                state.cancelled = True
            elif key == curses.KEY_F10 or key == 274:
                if _validate_form_state(state) is None:
                    state.submitted = True
            elif key == curses.KEY_UP or key == ord('k'):
                state.move_up()
            elif key == curses.KEY_DOWN or key == ord('j'):
                state.move_down()
            elif key == ord('\t'):
                state.move_down()
            elif key == 353:
                state.move_up()
            elif key == curses.KEY_LEFT or key == ord('h'):
                # Cycle to previous profile
                current_profile = state.current_profile or "default"
                try:
                    idx = profile_names.index(current_profile)
                    idx = (idx - 1) % len(profile_names)
                    state.current_profile = profile_names[idx]
                    # Load profile values into form
                    if state.current_profile == "default":
                        _reset_state_to_config(state, config)
                    elif state.current_profile != "+":
                        _load_profile_into_state(state, profiles[state.current_profile])
                except ValueError:
                    pass
            elif key == curses.KEY_RIGHT or key == ord('l'):
                # Cycle to next profile
                current_profile = state.current_profile or "default"
                try:
                    idx = profile_names.index(current_profile)
                    idx = (idx + 1) % len(profile_names)
                    state.current_profile = profile_names[idx]
                    # Load profile values into form
                    if state.current_profile == "default":
                        _reset_state_to_config(state, config)
                    elif state.current_profile != "+":
                        _load_profile_into_state(state, profiles[state.current_profile])
                except ValueError:
                    pass
            elif key == ord('\n') or key == curses.KEY_ENTER or key == 10:
                # Handle "+" for saving new profile
                if state.current_profile == "+":
                    # Prompt for profile name
                    profile_name = _prompt_profile_name(stdscr)
                    if profile_name:
                        # Build config from current state
                        temp_config = _build_config_from_state(config, state)
                        # Save profile
                        from .config import save_profile
                        if save_profile(profile_name, temp_config):
                            # Switch to newly saved profile
                            state.current_profile = profile_name
                        # If save failed, stay on "+"
            elif key == 27:
                state.cancelled = True
            continue

        current_field = state.current_field()

        # Handle multi-select mode input
        if state.multiselect_mode:
            from .config import load_saved_values
            saved_values = load_saved_values()

            field_saved_map = {
                "tags": saved_values.tags,
                "restrict_prefix": saved_values.restrict_prefixes,
                "exclude_patterns": saved_values.exclude_patterns,
                "user_agent": saved_values.user_agents,
            }

            saved_list = field_saved_map.get(current_field.name, [])
            options = saved_list + ["+ custom..."]

            if key == curses.KEY_UP or key == ord('k'):
                state.multiselect_index = max(0, state.multiselect_index - 1)
            elif key == curses.KEY_DOWN or key == ord('j'):
                state.multiselect_index = min(len(options) - 1, state.multiselect_index + 1)
            elif key == ord(' '):
                # Toggle selection
                current_option = options[state.multiselect_index]
                if current_option == "+ custom...":
                    # Enter edit mode to add custom value
                    state.multiselect_mode = False
                    state.edit_mode = True
                    pre_edit_value = ""
                    state.cursor_pos = 0
                elif current_option in state.multiselect_selected:
                    state.multiselect_selected.remove(current_option)
                else:
                    state.multiselect_selected.append(current_option)
            elif key == ord('\n') or key == curses.KEY_ENTER or key == 10:
                # Exit multi-select and apply selections
                if current_field.name in ["tags", "exclude_patterns"]:
                    # Join as comma-separated list
                    state.values[current_field.name] = ",".join(state.multiselect_selected)
                elif current_field.name in ["restrict_prefix", "user_agent"]:
                    # Single value fields - use first selected or empty
                    state.values[current_field.name] = state.multiselect_selected[0] if state.multiselect_selected else ""
                state.multiselect_mode = False
                state.multiselect_selected = []
                state.multiselect_index = 0
            elif key == 27:  # Escape
                # Cancel multi-select
                state.multiselect_mode = False
                state.multiselect_selected = []
                state.multiselect_index = 0
            continue

        if state.edit_mode:
            # Handle edit mode input
            _handle_edit_mode_input(state, key)
        else:
            # Handle navigation mode input
            if key == ord('q') or key == ord('Q'):
                # Quit
                state.cancelled = True
            elif key == curses.KEY_F10 or key == 274:  # F10
                # Submit form only if validation passes
                if _validate_form_state(state) is None:
                    state.submitted = True
            elif key == curses.KEY_UP or key == ord('k'):
                # Move up
                state.move_up()
            elif key == curses.KEY_DOWN or key == ord('j'):
                # Move down
                state.move_down()
            elif key == ord('\t'):  # Tab
                # Next field
                state.move_down()
            elif key == 353:  # Shift+Tab (KEY_BTAB)
                # Previous field
                state.move_up()
            elif key == ord('\n') or key == curses.KEY_ENTER or key == 10:
                # Enter: handle based on field type and position
                if current_field.expandable:
                    if state.on_subfield:
                        # Check if field has saved values for multi-select
                        from .config import load_saved_values
                        saved_values = load_saved_values()

                        field_saved_map = {
                            "tags": saved_values.tags,
                            "restrict_prefix": saved_values.restrict_prefixes,
                            "exclude_patterns": saved_values.exclude_patterns,
                            "user_agent": saved_values.user_agents,
                        }

                        has_saved = current_field.name in field_saved_map and len(field_saved_map[current_field.name]) > 0

                        if has_saved:
                            # Enter multi-select mode
                            state.multiselect_mode = True
                            state.multiselect_index = 0
                            # Pre-populate selections from current value
                            current_val = state.current_value()
                            if current_val:
                                if current_field.name in ["tags", "exclude_patterns"]:
                                    state.multiselect_selected = [v.strip() for v in current_val.split(",") if v.strip()]
                                else:
                                    state.multiselect_selected = [current_val] if current_val else []
                            else:
                                state.multiselect_selected = []
                        else:
                            # On sub-field: enter edit mode
                            state.edit_mode = True
                            pre_edit_value = state.current_value()
                            state.cursor_pos = len(pre_edit_value)
                    else:
                        # On toggle: toggle expanded state
                        is_expanded = state.expanded.get(current_field.name, False)
                        state.expanded[current_field.name] = not is_expanded
                        # If toggling to Yes, auto-expand and move to sub-field
                        if not is_expanded:
                            state.on_subfield = True
                elif current_field.field_type == "bool":
                    # Toggle boolean
                    current_val = state.values.get(current_field.name, "no")
                    if current_val.lower() in ("yes", "true", "1"):
                        state.values[current_field.name] = "no"
                    else:
                        state.values[current_field.name] = "yes"
                else:
                    # Enter edit mode for text/number fields
                    state.edit_mode = True
                    pre_edit_value = state.current_value()
                    state.cursor_pos = len(pre_edit_value)
            elif key == ord(' '):
                # Space: toggle boolean fields and expandable toggles
                if current_field.expandable and not state.on_subfield:
                    # Toggle expanded state
                    is_expanded = state.expanded.get(current_field.name, False)
                    state.expanded[current_field.name] = not is_expanded
                    # If toggling to Yes, auto-expand and move to sub-field
                    if not is_expanded:
                        state.on_subfield = True
                elif current_field.field_type == "bool":
                    # Toggle boolean
                    current_val = state.values.get(current_field.name, "no")
                    if current_val.lower() in ("yes", "true", "1"):
                        state.values[current_field.name] = "no"
                    else:
                        state.values[current_field.name] = "yes"
            elif key == 27:  # Escape
                # Exit
                state.cancelled = True


def _handle_edit_mode_input(state: ConfigFormState, key: int) -> None:
    """
    Handle keyboard input when in edit mode.

    Args:
        state: Current form state
        key: Key code pressed
    """
    current_value = state.current_value()

    if key == 27:  # Escape - cancel edit
        state.edit_mode = False
        # Value is already in state, so nothing to restore unless we track pre-edit
    elif key == ord('\n') or key == curses.KEY_ENTER or key == 10:
        # Confirm edit
        state.edit_mode = False

        # Save custom value if it's a list field with saved values support
        current_field = state.current_field()
        if current_field.name in ["tags", "restrict_prefix", "exclude_patterns", "user_agent"]:
            # Check if this is a new value worth saving
            new_value = state.current_value().strip()
            if new_value:
                # For multi-value fields, save each value separately
                if current_field.name in ["tags", "exclude_patterns"]:
                    values = [v.strip() for v in new_value.split(",") if v.strip()]
                    from .config import save_custom_value
                    for val in values:
                        # save_custom_value will check if value already exists
                        save_custom_value(current_field.name, val)
                else:
                    # For single-value fields
                    from .config import save_custom_value
                    save_custom_value(current_field.name, new_value)
    elif key == curses.KEY_LEFT:
        # Move cursor left
        if state.cursor_pos > 0:
            state.cursor_pos -= 1
    elif key == curses.KEY_RIGHT:
        # Move cursor right
        if state.cursor_pos < len(current_value):
            state.cursor_pos += 1
    elif key == curses.KEY_HOME:
        # Move to start
        state.cursor_pos = 0
    elif key == curses.KEY_END:
        # Move to end
        state.cursor_pos = len(current_value)
    elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:
        # Backspace - delete char before cursor
        if state.cursor_pos > 0:
            new_value = current_value[:state.cursor_pos - 1] + current_value[state.cursor_pos:]
            state.set_current_value(new_value)
            state.cursor_pos -= 1
    elif key == curses.KEY_DC or key == 330:
        # Delete - delete char at cursor
        if state.cursor_pos < len(current_value):
            new_value = current_value[:state.cursor_pos] + current_value[state.cursor_pos + 1:]
            state.set_current_value(new_value)
    elif 32 <= key <= 126:  # Printable ASCII
        # Insert character at cursor
        char = chr(key)
        new_value = current_value[:state.cursor_pos] + char + current_value[state.cursor_pos:]
        state.set_current_value(new_value)
        state.cursor_pos += 1


def _apply_config_changes(state: ConfigMenuState, config: Config, stats: "CrawlStats") -> None:
    """
    Apply config menu changes to the running crawler.

    Thread-safely updates the configuration and crawler instance with new values
    from the menu state.

    Args:
        state: Config menu state with edited values
        config: Configuration object to update
        stats: Crawl stats (contains crawler reference and auto_scroll)
    """
    # Update config.restrict_prefix
    new_prefix = state.whitelist_edit.strip()
    if new_prefix and not new_prefix.startswith("/"):
        new_prefix = "/" + new_prefix
    config.restrict_prefix = new_prefix if new_prefix else None

    # Update config.exclude_patterns
    config.exclude_patterns = state.blacklist_edit.copy() if state.blacklist_edit else []

    # Update crawler's cached restrict_prefix (if crawler is available)
    if hasattr(stats, 'crawler') and stats.crawler is not None:
        stats.crawler.restrict_prefix = new_prefix if new_prefix else None

    # Note: auto_scroll will be updated in _tui_loop after this function returns


def handle_config_menu_input(
    state: ConfigMenuState,
    key: int,
    config: Config,
    stats: "CrawlStats",
):
    """
    Handle keyboard input for config menu overlay.

    Args:
        state: Current menu state
        key: Key code pressed
        config: Current configuration object
        stats: Crawl stats (for auto_scroll state)

    Returns:
        False to keep menu open, True to close without saving, "save" to close with saving
    """
    # If in editing mode, handle edit-specific keys
    if state.editing:
        current_field = state.current_field

        if current_field == 0:  # Whitelist (text field)
            if key == 27:  # Escape - cancel edit
                state.editing = False
                state.whitelist_edit = config.restrict_prefix or ""
                state.cursor_pos = 0
            elif key == ord('\n') or key == curses.KEY_ENTER or key == 10:
                # Confirm edit (but don't apply yet - that's next plan)
                state.editing = False
            elif key == curses.KEY_LEFT:
                if state.cursor_pos > 0:
                    state.cursor_pos -= 1
            elif key == curses.KEY_RIGHT:
                if state.cursor_pos < len(state.whitelist_edit):
                    state.cursor_pos += 1
            elif key == curses.KEY_HOME:
                state.cursor_pos = 0
            elif key == curses.KEY_END:
                state.cursor_pos = len(state.whitelist_edit)
            elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:
                if state.cursor_pos > 0:
                    state.whitelist_edit = (
                        state.whitelist_edit[:state.cursor_pos - 1] +
                        state.whitelist_edit[state.cursor_pos:]
                    )
                    state.cursor_pos -= 1
            elif key == curses.KEY_DC or key == 330:
                if state.cursor_pos < len(state.whitelist_edit):
                    state.whitelist_edit = (
                        state.whitelist_edit[:state.cursor_pos] +
                        state.whitelist_edit[state.cursor_pos + 1:]
                    )
            elif 32 <= key <= 126:  # Printable ASCII
                char = chr(key)
                state.whitelist_edit = (
                    state.whitelist_edit[:state.cursor_pos] +
                    char +
                    state.whitelist_edit[state.cursor_pos:]
                )
                state.cursor_pos += 1

        elif current_field == 1:  # Blacklist (text field with comma-separated values)
            if key == 27:  # Escape - cancel edit
                state.editing = False
                state.blacklist_edit = config.exclude_patterns.copy() if config.exclude_patterns else []
                state.cursor_pos = 0
            elif key == ord('\n') or key == curses.KEY_ENTER or key == 10:
                # Confirm edit
                state.editing = False
            elif key == curses.KEY_LEFT:
                if state.cursor_pos > 0:
                    state.cursor_pos -= 1
            elif key == curses.KEY_RIGHT:
                current_text = ", ".join(state.blacklist_edit)
                if state.cursor_pos < len(current_text):
                    state.cursor_pos += 1
            elif key == curses.KEY_HOME:
                state.cursor_pos = 0
            elif key == curses.KEY_END:
                current_text = ", ".join(state.blacklist_edit)
                state.cursor_pos = len(current_text)
            elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:
                current_text = ", ".join(state.blacklist_edit)
                if state.cursor_pos > 0:
                    new_text = current_text[:state.cursor_pos - 1] + current_text[state.cursor_pos:]
                    state.blacklist_edit = [x.strip() for x in new_text.split(",") if x.strip()]
                    state.cursor_pos -= 1
            elif key == curses.KEY_DC or key == 330:
                current_text = ", ".join(state.blacklist_edit)
                if state.cursor_pos < len(current_text):
                    new_text = current_text[:state.cursor_pos] + current_text[state.cursor_pos + 1:]
                    state.blacklist_edit = [x.strip() for x in new_text.split(",") if x.strip()]
            elif 32 <= key <= 126:  # Printable ASCII
                char = chr(key)
                current_text = ", ".join(state.blacklist_edit)
                new_text = current_text[:state.cursor_pos] + char + current_text[state.cursor_pos:]
                state.blacklist_edit = [x.strip() for x in new_text.split(",") if x.strip()]
                state.cursor_pos += 1

        elif current_field == 2:  # Auto-scroll (bool field)
            if key == 27:  # Escape - cancel edit
                state.editing = False
                state.autoscroll_edit = getattr(stats, 'auto_scroll', True)
            elif key == ord('\n') or key == curses.KEY_ENTER or key == 10:
                # Confirm edit
                state.editing = False
            elif key == ord(' '):  # Space - toggle bool
                state.autoscroll_edit = not state.autoscroll_edit

    else:
        # Navigation mode (not editing)
        if key == ord('m') or key == ord('M') or key == 27:  # 'm' or Escape - close menu without saving
            return True
        elif key == ord('s') or key == ord('S'):  # 's' - Save & Apply changes
            # Apply configuration changes to running crawler
            _apply_config_changes(state, config, stats)
            # Signal that menu should close with a confirmation message
            return "save"
        elif key == curses.KEY_UP or key == ord('k') or key == ord('K'):
            # Move up
            if state.current_field > 0:
                state.current_field -= 1
        elif key == curses.KEY_DOWN or key == ord('j') or key == ord('J'):
            # Move down
            if state.current_field < 2:  # 3 fields total (0-2)
                state.current_field += 1
        elif key == ord('\n') or key == curses.KEY_ENTER or key == 10:
            # Enter - start editing current field
            state.editing = True
            # Initialize edit buffers with current values
            if state.current_field == 0:  # Whitelist
                state.whitelist_edit = config.restrict_prefix or ""
                state.cursor_pos = len(state.whitelist_edit)
            elif state.current_field == 1:  # Blacklist
                state.blacklist_edit = config.exclude_patterns.copy() if config.exclude_patterns else []
                current_text = ", ".join(state.blacklist_edit)
                state.cursor_pos = len(current_text)
            elif state.current_field == 2:  # Auto-scroll
                state.autoscroll_edit = getattr(stats, 'auto_scroll', True)

    return False  # Keep menu open


def _build_config_from_state(base_config: Config, state: ConfigFormState) -> Config:
    """
    Build a Config object from form state.

    For expandable fields, only use values when toggle is expanded (Yes).
    When collapsed (No), use default values.

    Args:
        base_config: Base config with defaults
        state: Form state with user values

    Returns:
        New Config object with form values applied
    """
    # Start with a copy of base config values
    values = state.values

    # Helper to get value only if field is expanded
    def get_expanded_value(field_name: str, default: str = "") -> str:
        """Get value for expandable field, or default if collapsed."""
        # Find the field
        field = next((f for f in CONFIG_FORM_FIELDS if f.name == field_name), None)
        if field and field.expandable:
            # Only use value if expanded
            if state.expanded.get(field_name, False):
                return values.get(field_name, "").strip()
            else:
                # Use field's default_value
                return field.default_value
        else:
            # Non-expandable field, always use value
            return values.get(field_name, "").strip()

    # Parse tags (comma-separated) - only if expanded
    tags_str = get_expanded_value("tags")
    tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []

    # Parse exclude patterns (comma-separated) - only if expanded
    patterns_str = get_expanded_value("exclude_patterns")
    exclude_patterns = [p.strip() for p in patterns_str.split(",") if p.strip()] if patterns_str else []

    # Parse delay - only if expanded
    delay_str = get_expanded_value("delay", "0.3")
    try:
        delay = float(delay_str) if delay_str else 0.3
        if delay < 0:
            delay = 0.3
    except ValueError:
        delay = 0.3

    # Parse max_pages - only if expanded
    max_pages_str = get_expanded_value("max_pages")
    try:
        max_pages = int(max_pages_str) if max_pages_str else None
        if max_pages is not None and max_pages <= 0:
            max_pages = None
    except ValueError:
        max_pages = None

    # Parse user_agent - only if expanded
    user_agent_str = get_expanded_value("user_agent")
    user_agent = user_agent_str if user_agent_str else base_config.user_agent

    # Parse restrict_prefix - only if expanded
    restrict_prefix_str = get_expanded_value("restrict_prefix")
    restrict_prefix = restrict_prefix_str if restrict_prefix_str else None

    # Parse dedupe (non-expandable, always use)
    dedupe_val = values.get("dedupe", "no").lower()
    dedupe = dedupe_val in ("yes", "true", "1")

    # Get start_url for variable expansion
    start_url = values.get("start_url", "").strip() or None

    # Build context for variable expansion
    from .config import extract_domain, expand_variables
    from datetime import datetime

    context = {
        "domain": extract_domain(start_url),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "profile": state.current_profile or "default",
    }

    # Get output path and expand variables, then expand user home directory
    output_raw = values.get("output", "").strip() or "docs-md"
    output_expanded = expand_variables(output_raw, context)
    output = os.path.expanduser(output_expanded)

    # Expand variables in restrict_prefix if present
    if restrict_prefix:
        restrict_prefix = expand_variables(restrict_prefix, context)

    # Expand variables in user_agent if present
    if user_agent:
        user_agent = expand_variables(user_agent, context)

    return Config(
        start_url=start_url,
        base_url=base_config.base_url,  # Keep base_url from original
        output=output,
        tags=tags,
        restrict_prefix=restrict_prefix,
        exclude_patterns=exclude_patterns,
        delay=delay,
        max_pages=max_pages,
        no_frontmatter=base_config.no_frontmatter,
        user_agent=user_agent,
        verbose=base_config.verbose,
        no_tui=False,  # Config form is TUI, so TUI is enabled
        dedupe=dedupe,
        scroll_lines=base_config.scroll_lines,
        max_log_lines=base_config.max_log_lines,
    )


def run_tui(config: Config, stats: CrawlStats, crawler_thread: threading.Thread) -> None:
    """
    Run curses TUI in main thread, monitoring crawler in background thread.

    Args:
        config: Configuration object (contains delay, which may be modified)
        stats: Shared stats object updated by crawler thread
        crawler_thread: Background thread running the crawler

    Returns:
        None (blocks until user quits or crawler finishes)
    """
    import sys
    import os

    original_delay = config.delay

    # Load theme before entering TUI (so warnings can be displayed)
    theme, theme_warning = load_theme()
    if theme.extended_colors:
        print(
            "Note: 256-color mode enabled. Colors may not match your terminal theme.",
            file=sys.stderr
        )

    # Show theme warning before TUI if present
    if theme_warning:
        print(f"\n⚠️  Theme Warning: {theme_warning}", file=sys.stderr)
        print("Using default theme. Press Enter to continue or Ctrl+C to exit...", file=sys.stderr)
        try:
            input()
        except (KeyboardInterrupt, EOFError):
            sys.exit(0)

    # Redirect stderr to /dev/null to prevent crawler print statements from corrupting TUI
    original_stderr = sys.stderr
    try:
        sys.stderr = open(os.devnull, 'w')
        curses.wrapper(lambda stdscr: _tui_loop(stdscr, config, stats, crawler_thread, theme))
    finally:
        # Restore stderr
        sys.stderr.close()
        sys.stderr = original_stderr

        # After TUI exits, check for speed persistence
        if config.delay != original_delay:
            _prompt_save_delay(config, original_delay)


def _tui_loop(
    stdscr: "curses.window",
    config: Config,
    stats: CrawlStats,
    crawler_thread: threading.Thread,
    theme: Theme,
) -> None:
    """
    Main TUI loop (runs in main thread).

    Args:
        stdscr: Curses window object
        config: Configuration object
        stats: Shared stats object
        crawler_thread: Background thread running crawler
        theme: Theme configuration for colors
    """
    stdscr.nodelay(True)  # Non-blocking input
    curses.curs_set(0)  # Hide cursor
    stdscr.keypad(True)  # Enable special keys

    # Enable mouse support for scroll wheel
    try:
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    except:
        pass  # Mouse support optional

    # Set output directory for log path normalization
    global _LOG_OUTPUT_DIR
    if config.output:
        # Expand to absolute path for reliable matching
        from pathlib import Path
        _LOG_OUTPUT_DIR = str(Path(config.output).expanduser().resolve())

    # Initialize color pairs if colors are available (use terminal default background)
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()  # Enable -1 for terminal default
        # Initialize theme colors (theme passed from run_tui)
        init_theme_colors(theme)

    # Scroll state for each window
    scroll_offset_log = 0
    scroll_offset_errors = 0
    scroll_offset_queue = 0
    auto_scroll = True  # Start with auto-scroll enabled for log window
    auto_scroll_errors = True  # Start with auto-scroll enabled for errors/warnings window
    auto_center_queue = True  # Start with auto-center enabled for queue window
    prev_processing_idx = -1  # Track previous processing index for stable auto-center
    spinner_frame = 0
    spinner_frames = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

    # Track previous terminal size for resize detection
    prev_height, prev_width = stdscr.getmaxyx()

    # Window objects (created on first iteration and on resize)
    windows = None
    rects = None

    # Track last processed log index for error filtering
    last_log_index = 0
    max_error_lines = 100  # Keep last 100 errors

    # Phase 5: Help overlay and completion state
    show_help_overlay = False
    user_requested_exit = False
    crawl_done = False

    # Config menu overlay state
    show_config_menu = False
    config_menu_state = None

    # Config save confirmation message
    config_save_message = None
    config_save_message_time = 0.0

    # URL display toggle (False = show paths only, True = show full URLs)
    show_full_urls = False

    # Track if we need to redraw (for performance)
    needs_redraw = True

    while not user_requested_exit:
        # 1. Check for new log entries to trigger redraw
        current_log_count = len(stats.log_entries)
        if current_log_count > last_log_index:
            # New logs arrived, trigger redraw
            last_log_index = current_log_count
            needs_redraw = True  # New data arrived, redraw

        # 2. Determine crawl state
        # Check if crawler has finished (thread is dead and no error)
        if not crawler_thread.is_alive() and stats.crawler_error is None:
            crawl_done = True
            stats.mark_crawl_finished()  # Freeze timer

        # Also consider finished if stop was requested and thread is dead
        if stats.stop_requested and not crawler_thread.is_alive():
            crawl_done = True
            stats.mark_crawl_finished()  # Freeze timer

        is_paused = stats.paused

        # 3. Check for crash (immediate exit)
        if stats.crawler_error is not None:
            # Crawler crashed, but stay in TUI to show error panel
            # User can press 'q' to exit
            pass

        # 4. Get terminal size
        try:
            height, width = stdscr.getmaxyx()
        except curses.error:
            # Terminal resize in progress, skip this iteration
            time.sleep(0.1)
            continue

        # 5. Detect terminal resize and recreate windows
        if windows is None or height != prev_height or width != prev_width:
            prev_height, prev_width = height, width

            # Clear screen on resize
            stdscr.clear()

            # Compute layout
            rects, help_y, status_y = compute_layout(height, width)

            # Create subwindows for each panel
            try:
                windows = {
                    "meta": stdscr.subwin(
                        rect_height(rects["meta"]),
                        rect_width(rects["meta"]),
                        rects["meta"].y0,
                        rects["meta"].x0
                    ),
                    "errors": stdscr.subwin(
                        rect_height(rects["errors"]),
                        rect_width(rects["errors"]),
                        rects["errors"].y0,
                        rects["errors"].x0
                    ),
                    "queue": stdscr.subwin(
                        rect_height(rects["queue"]),
                        rect_width(rects["queue"]),
                        rects["queue"].y0,
                        rects["queue"].x0
                    ),
                    "log": stdscr.subwin(
                        rect_height(rects["log"]),
                        rect_width(rects["log"]),
                        rects["log"].y0,
                        rects["log"].x0
                    ),
                }

                # Reset all scroll offsets on resize to prevent out-of-bounds
                scroll_offset_log = 0
                scroll_offset_errors = 0
                scroll_offset_queue = 0
                auto_scroll = True
                auto_scroll_errors = True
                # Don't reset prev_processing_idx - maintain queue position across resize
                needs_redraw = True
            except curses.error:
                # Terminal too small, skip this iteration
                time.sleep(0.1)
                continue

        # 6. Clear windows only if needed (on redraw)
        # Don't erase stdscr - it causes the help line to scroll up
        # Windows are subwindows of stdscr, so erasing them is sufficient
        if needs_redraw:
            for win in windows.values():
                try:
                    win.erase()  # Use erase() instead of clear() to avoid flicker
                except curses.error:
                    pass

        # 7. Get main log entries from pre-filtered list (O(1))
        filtered_log_lines = get_main_log_lines(stats)

        # Calculate visible log height based on Log window Rect
        if rects is not None:
            log_rect = rects["log"]
            log_window_height = rect_height(log_rect)
            # Subtract 2 for borders, get available lines for content
            visible_log_height = max(1, log_window_height - 2)
        else:
            visible_log_height = 10  # Fallback

        # Calculate max scroll offset for log window
        total_filtered_lines = len(filtered_log_lines)
        max_scroll_offset_log = max(0, total_filtered_lines - visible_log_height)

        # Clamp scroll offsets to valid ranges
        scroll_offset_log = max(0, min(scroll_offset_log, max_scroll_offset_log))

        # 8. Render each window with border and content
        try:
            # Meta window - now with real content
            meta_win = windows["meta"]
            inner_y, inner_x = draw_window_with_border(meta_win, "Meta", stats.pages_processed)
            draw_metadata_window(meta_win, inner_y, inner_x, stats, config)

            # Errors window - scrollable (shows warnings pinned at top)
            errors_win = windows["errors"]
            # Build label showing warn/error counts
            if stats.warn_count > 0 and stats.error_count > 0:
                errors_label = f"Warn:{stats.warn_count}/Err:{stats.error_count}"
            elif stats.warn_count > 0:
                errors_label = f"Warn:{stats.warn_count}"
            else:
                errors_label = f"Errors:{stats.error_count}"
            inner_y, inner_x = draw_window_with_border(errors_win, errors_label, None)
            total_errors = draw_errors_window(errors_win, inner_y, inner_x, stats, scroll_offset_errors, show_full_urls)

            # Calculate max scroll for errors
            if rects is not None:
                errors_rect = rects["errors"]
                errors_height = rect_height(errors_rect)
                visible_errors_height = max(1, errors_height - 2)
                max_scroll_offset_errors = max(0, total_errors - visible_errors_height)

                # Auto-scroll to show newest warnings (bottom)
                if auto_scroll_errors:
                    scroll_offset_errors = max_scroll_offset_errors
                else:
                    scroll_offset_errors = max(0, min(scroll_offset_errors, max_scroll_offset_errors))

            # Calculate max scroll for queue (BEFORE rendering to fix scroll bug)
            total_queue = len(stats.queue_history)
            if rects is not None:
                queue_rect = rects["queue"]
                queue_height = rect_height(queue_rect)
                visible_queue_height = max(1, queue_height - 2)
                max_scroll_offset_queue = max(0, total_queue - visible_queue_height)
                # Only clamp if not auto-centering
                if not auto_center_queue:
                    scroll_offset_queue = max(0, min(scroll_offset_queue, max_scroll_offset_queue))
            else:
                max_scroll_offset_queue = 0  # Fallback

            # Queue window - scrollable with auto-center on processing item
            queue_win = windows["queue"]
            queue_size = stats.queue_size
            inner_y, inner_x = draw_window_with_border(queue_win, "Queue", queue_size)
            total_queue, processing_idx = draw_queue_window(
                queue_win, inner_y, inner_x, stats, scroll_offset_queue, auto_center_queue, prev_processing_idx
            )
            # Update previous processing index for next frame
            prev_processing_idx = processing_idx

            # Log window - scrollable
            log_win = windows["log"]
            log_count = len(filtered_log_lines)
            inner_y, inner_x = draw_window_with_border(log_win, "Fetch", log_count)
            draw_main_log_window(
                log_win,
                inner_y,
                inner_x,
                filtered_log_lines,
                scroll_offset_log,
                visible_log_height,
                show_full_urls,
            )

        except curses.error:
            # Rendering error, skip
            pass

        # 9. Refresh all windows using double-buffering to eliminate flicker
        # Do this BEFORE drawing help line so help line is last thing written
        try:
            for win in windows.values():
                try:
                    win.noutrefresh()
                except curses.error:
                    pass
        except curses.error:
            pass

        # 10. Clear and render help line (after windows to prevent overwrite)
        try:
            # Clear the help line first
            stdscr.move(help_y, 0)
            stdscr.clrtoeol()

            help_text = "q:quit  p:pause  c:center  u:url  m:menu  ↑/↓:scroll  h:help"
            if crawl_done:
                help_text += "  (finished - press q to exit)"

            if len(help_text) > width:
                help_text = help_text[: width - 3] + "..."

            if curses.has_colors():
                stdscr.addstr(help_y, 0, help_text, curses.color_pair(1))
            else:
                stdscr.addstr(help_y, 0, help_text, curses.A_REVERSE)
        except curses.error:
            pass

        # 10b. Show status bar at row 0
        try:
            # Clear status bar row first to remove any previous background
            stdscr.move(status_y, 0)
            stdscr.clrtoeol()

            if stats.paused and not crawl_done:
                # Yellow solid bar for PAUSED
                _render_status_bar(stdscr, status_y, width, "⏸ PAUSED - Press p to resume", 2)
            elif crawl_done and stats.crawler_error is None:
                # Green solid bar for COMPLETE
                _render_status_bar(stdscr, status_y, width, "✓ CRAWL COMPLETE - Press q to exit", 1)
            else:
                # Cyan text (no solid bar) for Running
                running_text = "Running"
                text_x = (width - len(running_text)) // 2
                attr = curses.color_pair(4) | curses.A_BOLD if curses.has_colors() else curses.A_BOLD
                stdscr.addstr(status_y, text_x, running_text, attr)
        except curses.error:
            pass

        # 11. Show error overlay if crawler crashed
        if stats.crawler_error is not None:
            try:
                _render_error_panel(stdscr, height, width, stats.crawler_error)
            except curses.error:
                pass

        # 12. Show help overlay if requested
        if show_help_overlay:
            try:
                draw_help_overlay(stdscr, height, width)
            except curses.error:
                pass

        # 12b. Show config menu overlay if requested
        if show_config_menu and config_menu_state is not None:
            try:
                draw_config_menu_overlay(stdscr, height, width, config, stats, config_menu_state)
            except curses.error:
                pass

        # 12c. Show config save confirmation message (briefly)
        if config_save_message and time.time() - config_save_message_time < 2.0:
            try:
                # Display centered message at top of screen
                msg = f" {config_save_message} "
                msg_x = max(0, (width - len(msg)) // 2)
                msg_y = 1
                if curses.has_colors():
                    stdscr.addstr(msg_y, msg_x, msg, curses.color_pair(3) | curses.A_BOLD | curses.A_REVERSE)
                else:
                    stdscr.addstr(msg_y, msg_x, msg, curses.A_BOLD | curses.A_REVERSE)
            except curses.error:
                pass
        else:
            # Clear message after timeout
            if config_save_message:
                config_save_message = None
                needs_redraw = True

        # 13. Final screen update
        try:
            stdscr.noutrefresh()
            curses.doupdate()  # Single screen update to eliminate flicker
        except curses.error:
            pass

        # Reset redraw flag after successful render
        needs_redraw = False

        # 13. Handle keyboard input
        try:
            key = stdscr.getch()

            # If config menu is open, route keys to menu handler
            if show_config_menu and config_menu_state is not None:
                if key != -1:  # Only process if a key was pressed
                    should_close = handle_config_menu_input(config_menu_state, key, config, stats)
                    if should_close:
                        # If saving, apply auto_scroll change and show confirmation
                        if should_close == "save":
                            auto_scroll = config_menu_state.autoscroll_edit
                            config_save_message = "Configuration updated"
                            config_save_message_time = time.time()
                        # Close menu and clear screen to remove ghost artifacts
                        show_config_menu = False
                        config_menu_state = None
                        stdscr.erase()  # Clear screen to remove menu overlay
                    needs_redraw = True
            elif key == ord("q") or key == ord("Q"):
                # Request exit - this will stop the crawler if still running
                user_requested_exit = True
                stats.stop_requested = True
            elif key == ord("h") or key == ord("H"):
                # Toggle help overlay
                show_help_overlay = not show_help_overlay
                needs_redraw = True
            elif key == ord("m") or key == ord("M"):
                # Toggle config menu
                if show_config_menu:
                    show_config_menu = False
                    config_menu_state = None
                    stdscr.erase()  # Clear screen to remove menu overlay
                else:
                    show_config_menu = True
                    # Initialize config menu state with current values
                    config_menu_state = ConfigMenuState(
                        current_field=0,
                        editing=False,
                        whitelist_edit=config.restrict_prefix or "",
                        blacklist_edit=config.exclude_patterns.copy() if config.exclude_patterns else [],
                        autoscroll_edit=auto_scroll,
                        cursor_pos=0,
                        blacklist_cursor=0,
                    )
                needs_redraw = True
            elif key == 27:  # Esc key
                # Close help overlay if open
                if show_help_overlay:
                    show_help_overlay = False
                    needs_redraw = True
            elif key == ord("p") or key == ord("P"):
                # Only allow pause/resume if crawl is not done
                if not crawl_done:
                    if stats.paused:
                        # Resuming - add pause duration to total pause time
                        if stats.pause_start is not None:
                            stats.pause_time += time.time() - stats.pause_start
                            stats.pause_start = None
                    else:
                        # Pausing - record pause start time
                        stats.pause_start = time.time()
                    stats.paused = not stats.paused
                    needs_redraw = True
            elif key == ord("u") or key == ord("U"):
                # Toggle URL display (full URLs vs paths only)
                show_full_urls = not show_full_urls
                needs_redraw = True
            elif key == ord("c") or key == ord("C"):
                # Re-enable queue auto-center (useful after manual scrolling)
                auto_center_queue = True
                needs_redraw = True
            elif key == curses.KEY_UP:
                # Scroll log window up (into history)
                scroll_offset_log = min(scroll_offset_log + 1, max_scroll_offset_log)
                auto_scroll = False
                needs_redraw = True
            elif key == curses.KEY_DOWN:
                # Scroll log window down (toward recent)
                scroll_offset_log = max(scroll_offset_log - 1, 0)
                if scroll_offset_log == 0:
                    auto_scroll = True
                needs_redraw = True
            elif key == curses.KEY_PPAGE:  # Page Up
                # Scroll log window up by half a page
                scroll_step = max(1, visible_log_height // 2)
                scroll_offset_log = min(scroll_offset_log + scroll_step, max_scroll_offset_log)
                auto_scroll = False
                needs_redraw = True
            elif key == curses.KEY_NPAGE:  # Page Down
                # Scroll log window down by half a page
                scroll_step = max(1, visible_log_height // 2)
                scroll_offset_log = max(scroll_offset_log - scroll_step, 0)
                if scroll_offset_log == 0:
                    auto_scroll = True
                needs_redraw = True
            elif key == curses.KEY_HOME:
                # Jump log window to top (oldest logs)
                scroll_offset_log = max_scroll_offset_log
                auto_scroll = False
                needs_redraw = True
            elif key == curses.KEY_END:
                # Jump log window to bottom (newest logs)
                scroll_offset_log = 0
                auto_scroll = True
                needs_redraw = True
            elif key == curses.KEY_MOUSE:
                # Handle mouse events (scroll wheel) - route to appropriate window
                try:
                    _, mouse_x, mouse_y, _, button = curses.getmouse()

                    # Determine which window the mouse is in
                    in_errors = False
                    in_queue = False
                    in_log = False

                    if rects is not None:
                        # Check if mouse is in errors window
                        err_rect = rects["errors"]
                        if (err_rect.y0 <= mouse_y <= err_rect.y1 and
                            err_rect.x0 <= mouse_x <= err_rect.x1):
                            in_errors = True

                        # Check if mouse is in queue window
                        queue_rect = rects["queue"]
                        if (queue_rect.y0 <= mouse_y <= queue_rect.y1 and
                            queue_rect.x0 <= mouse_x <= queue_rect.x1):
                            in_queue = True

                        # Check if mouse is in log window
                        log_rect = rects["log"]
                        if (log_rect.y0 <= mouse_y <= log_rect.y1 and
                            log_rect.x0 <= mouse_x <= log_rect.x1):
                            in_log = True

                    # BUTTON4_PRESSED is scroll up (into history)
                    # On different systems, scroll down can be BUTTON5_PRESSED or 2097152
                    if button == curses.BUTTON4_PRESSED:  # Scroll wheel up
                        if in_errors:
                            scroll_offset_errors = max(scroll_offset_errors - 3, 0)  # Scroll up = earlier content (decrease offset)
                            auto_scroll_errors = False  # Disable auto-scroll on manual scroll
                        elif in_queue:
                            auto_center_queue = False  # Disable auto-center on manual scroll
                            scroll_offset_queue = max(scroll_offset_queue - 3, 0)  # Scroll up = earlier items
                        elif in_log:
                            scroll_offset_log = min(scroll_offset_log + 3, max_scroll_offset_log)
                            auto_scroll = False
                        needs_redraw = True
                    elif button == 2097152 or button == getattr(curses, 'BUTTON5_PRESSED', 2097152):  # Scroll wheel down
                        if in_errors:
                            scroll_offset_errors = min(scroll_offset_errors + 3, max_scroll_offset_errors)  # Scroll down = later content (increase offset)
                            # Re-enable auto-scroll if scrolled to the bottom
                            if scroll_offset_errors >= max_scroll_offset_errors:
                                auto_scroll_errors = True
                        elif in_queue:
                            auto_center_queue = False  # Disable auto-center on manual scroll
                            scroll_offset_queue = min(scroll_offset_queue + 3, max_scroll_offset_queue)  # Scroll down = later items
                        elif in_log:
                            scroll_offset_log = max(scroll_offset_log - 3, 0)
                            if scroll_offset_log == 0:
                                auto_scroll = True
                        needs_redraw = True
                except:
                    pass
        except:
            pass

        # 14. Update spinner (only if crawl not done)
        if not crawl_done:
            spinner_frame = (spinner_frame + 1) % len(spinner_frames)

        # 15. Sleep briefly to avoid CPU spinning
        time.sleep(0.1)


def _render_status_bar(
    stdscr: "curses.window", y: int, width: int, text: str, color_pair_num: int = 0
) -> None:
    """
    Render a full-width status bar with solid background.

    Args:
        stdscr: Curses window
        y: Y position
        width: Terminal width
        text: Status text to display (will be centered)
        color_pair_num: Color pair number (1=green, 2=yellow, 3=red, 0=default)
    """
    # Create full-width padded string
    padded_text = text.center(width)[:width]

    try:
        # Always use A_REVERSE for solid bar effect
        # Add color on top if specified
        attr = curses.A_REVERSE | curses.A_BOLD
        if curses.has_colors() and color_pair_num > 0:
            attr |= curses.color_pair(color_pair_num)
        stdscr.addstr(y, 0, padded_text, attr)
    except curses.error:
        pass


def _render_current_url(
    stdscr: "curses.window", y: int, width: int, stats: CrawlStats
) -> None:
    """
    Render the current URL line with left-truncation.

    Args:
        stdscr: Curses window
        y: Y position
        width: Terminal width
        stats: Stats object
    """
    prefix = "[PAUSED] " if stats.paused else ""
    current_url = stats.current_url or "(starting...)"

    label = f"{prefix}Current: "
    max_url_len = width - len(label)

    # Left-truncate long URLs
    if len(current_url) > max_url_len:
        display_url = "..." + current_url[-(max_url_len - 3) :]
    else:
        display_url = current_url

    line = label + display_url

    try:
        if stats.paused and curses.has_colors():
            stdscr.addstr(y, 0, line, curses.color_pair(2))
        else:
            stdscr.addstr(y, 0, line)
    except curses.error:
        pass


def _render_log_window(
    stdscr: "curses.window",
    start_y: int,
    end_y: int,
    width: int,
    stats: CrawlStats,
    scroll_offset: int,
) -> None:
    """
    Render the scrollable log window.

    Args:
        stdscr: Curses window
        start_y: Start Y position
        end_y: End Y position (exclusive)
        width: Terminal width
        stats: Stats object
        scroll_offset: Scroll offset from bottom
    """
    available_lines = end_y - start_y
    if available_lines <= 0:
        return

    # Get logs to display (most recent first, then reverse for display)
    total_logs = len(stats.log_entries)
    if total_logs == 0:
        try:
            stdscr.addstr(start_y, 0, "(no logs yet)")
        except curses.error:
            pass
        return

    # Calculate which logs to show
    # scroll_offset = 0 means show most recent logs
    # scroll_offset > 0 means scroll up into history
    start_idx = max(0, total_logs - available_lines - scroll_offset)
    end_idx = total_logs - scroll_offset

    logs_to_show = [str(entry) for entry in stats.log_entries[start_idx:end_idx]]

    # Render logs
    for i, log_line in enumerate(logs_to_show):
        if start_y + i >= end_y:
            break

        # Truncate line to fit width
        if len(log_line) > width:
            display_line = log_line[: width - 3] + "..."
        else:
            display_line = log_line

        try:
            stdscr.addstr(start_y + i, 0, display_line)
        except curses.error:
            pass


def _render_help_line(stdscr: "curses.window", y: int, width: int) -> None:
    """
    Render the help line with keyboard controls.

    Note: This function is currently unused. The main TUI loop renders help inline.

    Args:
        stdscr: Curses window
        y: Y position
        width: Terminal width
    """
    help_text = "q:quit  p:pause  c:center  u:url  m:menu  ↑/↓:scroll  h:help"

    if len(help_text) > width:
        help_text = help_text[: width - 3] + "..."

    try:
        if curses.has_colors():
            stdscr.addstr(y, 0, help_text, curses.color_pair(1))
        else:
            stdscr.addstr(y, 0, help_text, curses.A_REVERSE)
    except curses.error:
        pass


def _render_error_panel(
    stdscr: "curses.window", height: int, width: int, error_text: str
) -> None:
    """
    Render error panel overlay when crawler crashes.

    Args:
        stdscr: Curses window
        height: Terminal height
        width: Terminal width
        error_text: Error traceback text
    """
    # Calculate panel size (centered, 80% of screen)
    panel_height = max(10, int(height * 0.8))
    panel_width = max(40, int(width * 0.8))
    start_y = (height - panel_height) // 2
    start_x = (width - panel_width) // 2

    # Draw border
    try:
        for i in range(panel_height):
            y_pos = start_y + i
            if i == 0 or i == panel_height - 1:
                # Top and bottom border
                line = "+" + "-" * (panel_width - 2) + "+"
                stdscr.addstr(y_pos, start_x, line, curses.A_BOLD)
            else:
                # Side borders
                stdscr.addstr(y_pos, start_x, "|", curses.A_BOLD)
                stdscr.addstr(y_pos, start_x + panel_width - 1, "|", curses.A_BOLD)

        # Title
        title = " CRAWLER ERROR "
        title_x = start_x + (panel_width - len(title)) // 2
        if curses.has_colors():
            stdscr.addstr(start_y, title_x, title, curses.color_pair(3) | curses.A_BOLD)
        else:
            stdscr.addstr(start_y, title_x, title, curses.A_BOLD | curses.A_REVERSE)

        # Error text
        error_lines = error_text.split("\n")
        content_height = panel_height - 4  # Leave room for borders and footer
        content_width = panel_width - 4  # Leave room for borders and padding

        for i, line in enumerate(error_lines[:content_height]):
            if len(line) > content_width:
                line = line[:content_width - 3] + "..."
            y_pos = start_y + 2 + i
            x_pos = start_x + 2
            if curses.has_colors():
                stdscr.addstr(y_pos, x_pos, line, curses.color_pair(3))
            else:
                stdscr.addstr(y_pos, x_pos, line)

        # Footer
        footer = "Press 'q' to quit"
        footer_x = start_x + (panel_width - len(footer)) // 2
        stdscr.addstr(start_y + panel_height - 1, footer_x, footer, curses.A_BOLD)

    except curses.error:
        pass


def _prompt_save_delay(config: Config, original_delay: float) -> None:
    """
    Prompt user to save modified delay to config file.

    Args:
        config: Configuration object with current delay
        original_delay: Original delay value before modifications
    """
    try:
        print(
            f"\nDelay changed from {original_delay:.1f}s to {config.delay:.1f}s during session."
        )
        print("Save new delay to config? [y/N]: ", end="", flush=True)

        # Use select for timeout (Unix-like systems)
        ready, _, _ = select.select([sys.stdin], [], [], 5.0)

        if ready:
            response = sys.stdin.readline().strip().lower()
        else:
            response = "n"  # Default to no after timeout
            print("n (timeout)")

        if response in ("y", "yes"):
            # Update config file with new delay
            _update_config_delay(config.delay)
            print(f"Saved delay={config.delay:.1f}s to config file.")
        else:
            print("Delay not saved.")

    except Exception as e:
        # Non-interactive or error, just skip
        print(f"\nCould not prompt for config save: {e}")


def _update_config_delay(new_delay: float) -> None:
    """
    Update the delay value in the config file.

    Args:
        new_delay: New delay value to save
    """
    import os
    from pathlib import Path

    from .config import find_config_file

    # Try to find existing config file
    config_path = find_config_file()

    # If no config exists, create one in current directory
    if config_path is None:
        config_path = Path.cwd() / "crawl2md.toml"

    try:
        if config_path.exists():
            # Read existing config
            content = config_path.read_text()

            # Check if [crawl2md] section exists
            if "[crawl2md]" in content:
                # Check if delay already exists
                import re

                delay_pattern = r"^delay\s*=\s*[\d.]+\s*$"
                if re.search(delay_pattern, content, re.MULTILINE):
                    # Replace existing delay
                    content = re.sub(
                        delay_pattern,
                        f"delay = {new_delay}",
                        content,
                        flags=re.MULTILINE,
                    )
                else:
                    # Add delay to [crawl2md] section
                    content = content.replace(
                        "[crawl2md]", f"[crawl2md]\ndelay = {new_delay}"
                    )
            else:
                # Add entire [crawl2md] section
                content += f"\n[crawl2md]\ndelay = {new_delay}\n"

            config_path.write_text(content)
        else:
            # Create new config file
            config_path.write_text(f"[crawl2md]\ndelay = {new_delay}\n")

    except Exception as e:
        print(f"Warning: Could not update config file: {e}")


# ============================================================================
# Layout Validation Tests (for development)
# ============================================================================
#
# Uncomment this section to test layout computation:
#
# if __name__ == "__main__":
#     # Test layout computation
#     print("Testing layout computation...\n")
#
#     # Test narrow/square layout (height * 1.2 >= width)
#     rects_narrow, help_y_narrow = compute_layout(40, 40)
#     print(f"Narrow/Square (40x40): help_y={help_y_narrow}")
#     print(f"  Layout type: {'WIDE' if is_wide_layout(40, 40) else 'NARROW'}")
#     for name, rect in rects_narrow.items():
#         print(f"  {name}: {rect} (h={rect_height(rect)}, w={rect_width(rect)})")
#
#     # Test wide layout
#     rects_wide, help_y_wide = compute_layout(30, 120)
#     print(f"\nWide (30x120): help_y={help_y_wide}")
#     print(f"  Layout type: {'WIDE' if is_wide_layout(30, 120) else 'NARROW'}")
#     for name, rect in rects_wide.items():
#         print(f"  {name}: {rect} (h={rect_height(rect)}, w={rect_width(rect)})")
#
#     # Test standard terminal (80x24 rotated = 24 rows x 80 cols)
#     rects_std, help_y_std = compute_layout(24, 80)
#     print(f"\nStandard 80x24 (24x80): help_y={help_y_std}")
#     print(f"  Layout type: {'WIDE' if is_wide_layout(24, 80) else 'NARROW'}")
#     for name, rect in rects_std.items():
#         print(f"  {name}: {rect} (h={rect_height(rect)}, w={rect_width(rect)})")
#
#     # Test edge case - tiny terminal (gets clamped to 10x20)
#     rects_tiny, help_y_tiny = compute_layout(8, 15)
#     print(f"\nTiny (8x15 -> clamped to 10x20): help_y={help_y_tiny}")
#     print(f"  Layout type: {'WIDE' if is_wide_layout(8, 15) else 'NARROW'}")
#     for name, rect in rects_tiny.items():
#         print(f"  {name}: {rect} (h={rect_height(rect)}, w={rect_width(rect)})")
#
#     # Test edge case - very wide terminal
#     rects_very_wide, help_y_very_wide = compute_layout(20, 200)
#     print(f"\nVery wide (20x200): help_y={help_y_very_wide}")
#     print(f"  Layout type: {'WIDE' if is_wide_layout(20, 200) else 'NARROW'}")
#     for name, rect in rects_very_wide.items():
#         print(f"  {name}: {rect} (h={rect_height(rect)}, w={rect_width(rect)})")
#
#     # Test edge case - very tall terminal (narrow)
#     rects_tall, help_y_tall = compute_layout(80, 60)
#     print(f"\nTall (80x60): help_y={help_y_tall}")
#     print(f"  Layout type: {'WIDE' if is_wide_layout(80, 60) else 'NARROW'}")
#     for name, rect in rects_tall.items():
#         print(f"  {name}: {rect} (h={rect_height(rect)}, w={rect_width(rect)})")
#
#     # Verify assertions for all layouts
#     print("\nVerifying layout correctness:")
#     test_cases = [
#         (40, 40, "narrow 40x40"),
#         (30, 120, "wide 30x120"),
#         (24, 80, "standard 24x80"),
#         (10, 20, "tiny 10x20"),
#         (80, 60, "tall 80x60"),
#     ]
#
#     for h, w, name in test_cases:
#         rects, help_y = compute_layout(h, w)
#         # Verify help_y
#         assert help_y == max(10, h) - 1, f"{name}: help_y mismatch"
#         # Verify all rects have positive dimensions
#         for rect_name, rect in rects.items():
#             assert rect_height(rect) >= 1, f"{name}/{rect_name}: non-positive height"
#             assert rect_width(rect) >= 1, f"{name}/{rect_name}: non-positive width"
#         print(f"  {name}: OK")
#
#     print("\nAll tests completed successfully!")
