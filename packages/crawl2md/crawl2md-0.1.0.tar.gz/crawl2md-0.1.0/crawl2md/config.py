"""
Configuration handling for crawl2md.

Supports loading configuration from:
1. TOML config files (crawl2md.toml)
2. Environment variables (CRAWL2MD_*)
3. CLI arguments

Precedence (highest to lowest): CLI > Environment > Config file > Defaults
"""

import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None  # type: ignore

from .theme import Theme, DEFAULT_THEME, PRESET_THEMES


@dataclass
class Config:
    """Configuration container for crawl2md.

    TUI is the default interface. Set no_tui=True to use plain terminal output.
    Dedupe compares markdown body content only, ignoring frontmatter differences.
    """

    start_url: Optional[str] = None
    base_url: Optional[str] = None
    output: str = "docs-md"
    tags: List[str] = field(default_factory=list)
    restrict_prefix: Optional[str] = None
    exclude_patterns: List[str] = field(default_factory=list)
    delay: float = 0.3
    max_pages: Optional[int] = None
    no_frontmatter: bool = False
    user_agent: str = "crawl2md/0.1.0 (Documentation Crawler)"
    verbose: bool = False
    no_tui: bool = False
    dedupe: bool = False
    scroll_lines: int = 0
    max_log_lines: int = 0


@dataclass
class Profile:
    """Named configuration profile.

    Profiles store partial configuration values that can be loaded
    and applied to the base configuration. Values set to None are
    not overridden when the profile is applied.
    """

    name: str
    start_url: Optional[str] = None
    base_url: Optional[str] = None
    output: Optional[str] = None
    tags: Optional[List[str]] = None
    restrict_prefix: Optional[str] = None
    exclude_patterns: Optional[List[str]] = None
    delay: Optional[float] = None
    max_pages: Optional[int] = None
    no_frontmatter: Optional[bool] = None
    user_agent: Optional[str] = None
    verbose: Optional[bool] = None
    no_tui: Optional[bool] = None
    dedupe: Optional[bool] = None
    scroll_lines: Optional[int] = None
    max_log_lines: Optional[int] = None


@dataclass
class SavedValues:
    """Container for saved/commonly-used configuration values.

    These values are presented as multi-select options in the TUI
    to reduce repetitive typing.
    """

    tags: List[str] = field(default_factory=list)
    restrict_prefixes: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    user_agents: List[str] = field(default_factory=list)


def extract_domain(url: Optional[str]) -> str:
    """Extract domain from URL, or return empty string.

    Args:
        url: URL to extract domain from

    Returns:
        Domain name (netloc) or empty string if URL is None or invalid.
    """
    if not url:
        return ""
    parsed = urlparse(url)
    return parsed.netloc or ""


def expand_variables(value: str, context: Dict[str, str]) -> str:
    """Expand {variable} placeholders in config values.

    Replaces {variable} placeholders with values from the context dictionary.
    If a variable is not in the context, it is left unchanged.

    Args:
        value: String potentially containing {variable} placeholders
        context: Dictionary of variable names to values

    Returns:
        String with variables expanded.

    Examples:
        >>> expand_variables("output/{domain}/{date}", {"domain": "example.com", "date": "2025-12-05"})
        'output/example.com/2025-12-05'

        >>> expand_variables("output/{unknown}", {})
        'output/{unknown}'
    """
    result = value
    for var_name, var_value in context.items():
        placeholder = f"{{{var_name}}}"
        result = result.replace(placeholder, var_value)
    return result


def find_config_file() -> Optional[Path]:
    """
    Search for crawl2md.toml in standard locations.

    Search order:
    1. Current working directory
    2. $XDG_CONFIG_HOME/crawl2md/crawl2md.toml
    3. $HOME/.config/crawl2md/crawl2md.toml

    Returns the first found config file path, or None if not found.
    """
    cwd_config = Path.cwd() / "crawl2md.toml"
    if cwd_config.is_file():
        return cwd_config

    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config_home:
        xdg_config = Path(xdg_config_home) / "crawl2md" / "crawl2md.toml"
        if xdg_config.is_file():
            return xdg_config

    home = os.environ.get("HOME")
    if home:
        home_config = Path(home) / ".config" / "crawl2md" / "crawl2md.toml"
        if home_config.is_file():
            return home_config

    return None


def load_config_file(path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load configuration from a TOML file.

    Args:
        path: Explicit path to config file. If None, searches standard locations.

    Returns:
        Dictionary of configuration values from the [crawl2md] table,
        or empty dict if no config file found or tomllib not available.
    """
    if tomllib is None:
        return {}

    if path is None:
        path = find_config_file()

    if path is None or not path.is_file():
        return {}

    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return data.get("crawl2md", {})
    except tomllib.TOMLDecodeError as e:
        print(f"Warning: TOML syntax error in {path}: {e}", file=sys.stderr)
        return {}
    except Exception:
        return {}


def load_profiles(path: Optional[Path] = None) -> Dict[str, Profile]:
    """
    Load configuration profiles from TOML file.

    Profiles are stored in [profiles.*] sections, e.g.:
        [profiles.work-docs]
        tags = ["internal"]
        delay = 0.5

    Args:
        path: Explicit path to config file. If None, searches standard locations.

    Returns:
        Dictionary mapping profile names to Profile objects.
        Empty dict if no profiles found or tomllib not available.
    """
    if tomllib is None:
        return {}

    if path is None:
        path = find_config_file()

    if path is None or not path.is_file():
        return {}

    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        print(f"Warning: TOML syntax error in {path}: {e}", file=sys.stderr)
        return {}
    except Exception:
        return {}

    profiles = {}
    profiles_section = data.get("profiles", {})

    for name, profile_data in profiles_section.items():
        if not isinstance(profile_data, dict):
            continue

        profile = Profile(name=name)

        # Map TOML values to Profile attributes
        for key, value in profile_data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)

        profiles[name] = profile

    return profiles


def load_saved_values(path: Optional[Path] = None) -> SavedValues:
    """
    Load saved/commonly-used values from TOML file.

    Saved values are stored in [saved] section, e.g.:
        [saved]
        tags = ["api", "guide", "reference"]
        restrict_prefixes = ["/docs", "/api"]
        exclude_patterns = ["*.php", "/admin/*"]
        user_agents = ["crawl2md/0.1.0", "Mozilla/5.0"]

    Args:
        path: Explicit path to config file. If None, searches standard locations.

    Returns:
        SavedValues object with lists of saved options.
        Empty lists if no saved values found or tomllib not available.
    """
    if tomllib is None:
        return SavedValues()

    if path is None:
        path = find_config_file()

    if path is None or not path.is_file():
        return SavedValues()

    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        print(f"Warning: TOML syntax error in {path}: {e}", file=sys.stderr)
        return SavedValues()
    except Exception:
        return SavedValues()

    saved_section = data.get("saved", {})

    # Extract saved values, defaulting to empty lists
    saved = SavedValues(
        tags=saved_section.get("tags", []),
        restrict_prefixes=saved_section.get("restrict_prefixes", []),
        exclude_patterns=saved_section.get("exclude_patterns", []),
        user_agents=saved_section.get("user_agents", []),
    )

    return saved


def parse_bool_env(value: str) -> bool:
    """Parse a boolean from an environment variable string."""
    return value.lower() in ("1", "true", "yes", "on")


def load_env_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables.

    Supported variables:
    - CRAWL2MD_START_URL
    - CRAWL2MD_BASE_URL
    - CRAWL2MD_OUTPUT
    - CRAWL2MD_TAGS (comma-separated)
    - CRAWL2MD_RESTRICT_PREFIX
    - CRAWL2MD_EXCLUDE_PATTERNS (comma-separated)
    - CRAWL2MD_DELAY
    - CRAWL2MD_MAX_PAGES
    - CRAWL2MD_NO_FRONTMATTER
    - CRAWL2MD_USER_AGENT
    - CRAWL2MD_VERBOSE
    - CRAWL2MD_NO_TUI
    - CRAWL2MD_DEDUPE
    - CRAWL2MD_SCROLL_LINES
    - CRAWL2MD_MAX_LOG_LINES

    Returns:
        Dictionary of configuration values from environment.
    """
    config: Dict[str, Any] = {}

    if "CRAWL2MD_START_URL" in os.environ:
        config["start_url"] = os.environ["CRAWL2MD_START_URL"]

    if "CRAWL2MD_BASE_URL" in os.environ:
        config["base_url"] = os.environ["CRAWL2MD_BASE_URL"]

    if "CRAWL2MD_OUTPUT" in os.environ:
        config["output"] = os.environ["CRAWL2MD_OUTPUT"]

    if "CRAWL2MD_TAGS" in os.environ:
        tags_str = os.environ["CRAWL2MD_TAGS"].strip()
        if tags_str:
            config["tags"] = [t.strip() for t in tags_str.split(",") if t.strip()]

    if "CRAWL2MD_RESTRICT_PREFIX" in os.environ:
        config["restrict_prefix"] = os.environ["CRAWL2MD_RESTRICT_PREFIX"]

    if "CRAWL2MD_EXCLUDE_PATTERNS" in os.environ:
        patterns_str = os.environ["CRAWL2MD_EXCLUDE_PATTERNS"].strip()
        if patterns_str:
            config["exclude_patterns"] = [p.strip() for p in patterns_str.split(",") if p.strip()]

    if "CRAWL2MD_DELAY" in os.environ:
        try:
            delay = float(os.environ["CRAWL2MD_DELAY"])
            if delay >= 0:
                config["delay"] = delay
        except ValueError:
            pass

    if "CRAWL2MD_MAX_PAGES" in os.environ:
        try:
            max_pages = int(os.environ["CRAWL2MD_MAX_PAGES"])
            if max_pages > 0:
                config["max_pages"] = max_pages
        except ValueError:
            pass

    if "CRAWL2MD_NO_FRONTMATTER" in os.environ:
        config["no_frontmatter"] = parse_bool_env(os.environ["CRAWL2MD_NO_FRONTMATTER"])

    if "CRAWL2MD_USER_AGENT" in os.environ:
        config["user_agent"] = os.environ["CRAWL2MD_USER_AGENT"]

    if "CRAWL2MD_VERBOSE" in os.environ:
        config["verbose"] = parse_bool_env(os.environ["CRAWL2MD_VERBOSE"])

    if "CRAWL2MD_NO_TUI" in os.environ:
        config["no_tui"] = parse_bool_env(os.environ["CRAWL2MD_NO_TUI"])

    if "CRAWL2MD_DEDUPE" in os.environ:
        config["dedupe"] = parse_bool_env(os.environ["CRAWL2MD_DEDUPE"])

    if "CRAWL2MD_SCROLL_LINES" in os.environ:
        try:
            scroll_lines = int(os.environ["CRAWL2MD_SCROLL_LINES"])
            if scroll_lines >= 0:
                config["scroll_lines"] = scroll_lines
        except ValueError:
            pass

    if "CRAWL2MD_MAX_LOG_LINES" in os.environ:
        try:
            max_log_lines = int(os.environ["CRAWL2MD_MAX_LOG_LINES"])
            if max_log_lines >= 0:
                config["max_log_lines"] = max_log_lines
        except ValueError:
            pass

    return config


def merge_configs(
    file_config: Dict[str, Any], env_config: Dict[str, Any], cli_config: Dict[str, Any]
) -> Config:
    """
    Merge configuration from all sources with proper precedence.

    Precedence (highest to lowest): CLI > Environment > Config file > Defaults

    Args:
        file_config: Configuration from TOML file
        env_config: Configuration from environment variables
        cli_config: Configuration from CLI arguments

    Returns:
        Merged Config object with final values.
    """
    config = Config()

    for key, value in file_config.items():
        if hasattr(config, key) and value is not None:
            if key == "delay" and isinstance(value, (int, float)):
                if value >= 0:
                    setattr(config, key, value)
            elif key == "max_pages" and isinstance(value, int):
                if value > 0:
                    setattr(config, key, value)
            else:
                setattr(config, key, value)

    for key, value in env_config.items():
        if hasattr(config, key) and value is not None:
            setattr(config, key, value)

    for key, value in cli_config.items():
        if hasattr(config, key) and value is not None:
            setattr(config, key, value)

    return config


def resolve_config(cli_args: Dict[str, Any], profile_name: Optional[str] = None) -> Config:
    """
    Resolve final configuration from all sources.

    Precedence (highest to lowest):
    CLI > Environment > Profile > Config file > Defaults

    After merging, expands variables in string fields like:
    - {domain} - extracted from start_url
    - {date} - current date as YYYY-MM-DD
    - {profile} - current profile name (or "default")

    Args:
        cli_args: Dictionary of CLI argument values (may contain None for unset options)
        profile_name: Optional profile name to load and apply

    Returns:
        Final merged Config object with variables expanded.
    """
    file_config = load_config_file()
    env_config = load_env_config()

    # Load and apply profile if specified
    if profile_name:
        profiles = load_profiles()
        if profile_name in profiles:
            profile = profiles[profile_name]
            # Convert profile to config dict, excluding None values
            profile_config = {}
            for key in dir(profile):
                if not key.startswith("_") and key != "name":
                    value = getattr(profile, key)
                    if value is not None:
                        profile_config[key] = value
            # Merge profile into file config (profile takes precedence)
            file_config = {**file_config, **profile_config}

    cli_config = {k: v for k, v in cli_args.items() if v is not None}

    if "tags" in cli_config and cli_config["tags"] == []:
        del cli_config["tags"]

    if "exclude_patterns" in cli_config and cli_config["exclude_patterns"] == []:
        del cli_config["exclude_patterns"]

    config = merge_configs(file_config, env_config, cli_config)

    # Build context for variable expansion
    context = {
        "domain": extract_domain(config.start_url),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "profile": profile_name or "default",
    }

    # Expand variables in string fields
    if config.output:
        config.output = expand_variables(config.output, context)

    if config.restrict_prefix:
        config.restrict_prefix = expand_variables(config.restrict_prefix, context)

    if config.user_agent:
        config.user_agent = expand_variables(config.user_agent, context)

    return config


def save_profile(profile_name: str, config: Config, path: Optional[Path] = None) -> bool:
    """
    Save current configuration as a named profile to TOML file.

    Creates or updates a [profiles.<name>] section in the config file.
    If the file doesn't exist, creates it in the current directory.

    Args:
        profile_name: Name for the profile
        config: Configuration to save
        path: Optional path to config file. If None, uses current directory.

    Returns:
        True if save succeeded, False otherwise.
    """
    if path is None:
        path = Path.cwd() / "crawl2md.toml"

    # Read existing config or start fresh
    existing_data = {}
    if path.is_file():
        if tomllib is None:
            print("Warning: tomllib not available, cannot save profile", file=sys.stderr)
            return False

        try:
            with open(path, "rb") as f:
                existing_data = tomllib.load(f)
        except Exception as e:
            print(f"Warning: Could not read existing config: {e}", file=sys.stderr)
            # Continue with empty data - will overwrite file

    # Ensure profiles section exists
    if "profiles" not in existing_data:
        existing_data["profiles"] = {}

    # Build profile data from config (only non-default values)
    profile_data = {}

    if config.start_url:
        profile_data["start_url"] = config.start_url
    if config.base_url:
        profile_data["base_url"] = config.base_url
    if config.output and config.output != "docs-md":
        profile_data["output"] = config.output
    if config.tags:
        profile_data["tags"] = config.tags
    if config.restrict_prefix:
        profile_data["restrict_prefix"] = config.restrict_prefix
    if config.exclude_patterns:
        profile_data["exclude_patterns"] = config.exclude_patterns
    if config.delay != 0.3:
        profile_data["delay"] = config.delay
    if config.max_pages:
        profile_data["max_pages"] = config.max_pages
    if config.no_frontmatter:
        profile_data["no_frontmatter"] = config.no_frontmatter
    if config.user_agent and config.user_agent != "crawl2md/0.1.0 (Documentation Crawler)":
        profile_data["user_agent"] = config.user_agent
    if config.dedupe:
        profile_data["dedupe"] = config.dedupe
    if config.scroll_lines:
        profile_data["scroll_lines"] = config.scroll_lines
    if config.max_log_lines:
        profile_data["max_log_lines"] = config.max_log_lines

    # Add/update profile
    existing_data["profiles"][profile_name] = profile_data

    # Write to file
    try:
        import toml
    except ImportError:
        print("Warning: toml library not available, cannot save profile", file=sys.stderr)
        return False

    try:
        with open(path, "w") as f:
            toml.dump(existing_data, f)
        return True
    except Exception as e:
        print(f"Error: Could not save profile: {e}", file=sys.stderr)
        return False


def save_custom_value(field: str, value: str, path: Optional[Path] = None) -> bool:
    """
    Save a custom value to the [saved] section in TOML file.

    Adds the value to the appropriate list if not already present.

    Args:
        field: Field name (tags, restrict_prefixes, exclude_patterns, user_agents)
        value: Value to add
        path: Optional path to config file. If None, uses current directory.

    Returns:
        True if save succeeded, False otherwise.
    """
    if path is None:
        path = Path.cwd() / "crawl2md.toml"

    # Map field names to saved section keys
    field_map = {
        "tags": "tags",
        "restrict_prefix": "restrict_prefixes",
        "exclude_patterns": "exclude_patterns",
        "user_agent": "user_agents",
    }

    if field not in field_map:
        return False

    saved_key = field_map[field]

    # Read existing config or start fresh
    existing_data = {}
    if path.is_file():
        if tomllib is None:
            print("Warning: tomllib not available, cannot save value", file=sys.stderr)
            return False

        try:
            with open(path, "rb") as f:
                existing_data = tomllib.load(f)
        except Exception as e:
            print(f"Warning: Could not read existing config: {e}", file=sys.stderr)
            # Continue with empty data

    # Ensure saved section exists
    if "saved" not in existing_data:
        existing_data["saved"] = {}

    # Add value to list if not already present
    if saved_key not in existing_data["saved"]:
        existing_data["saved"][saved_key] = []

    if value not in existing_data["saved"][saved_key]:
        existing_data["saved"][saved_key].append(value)

    # Write to file
    try:
        import toml
    except ImportError:
        print("Warning: toml library not available, cannot save value", file=sys.stderr)
        return False

    try:
        with open(path, "w") as f:
            toml.dump(existing_data, f)
        return True
    except Exception as e:
        print(f"Error: Could not save custom value: {e}", file=sys.stderr)
        return False


def load_themes(path: Optional[Path] = None) -> Dict[str, Theme]:
    """
    Load all named themes from [themes.*] sections.

    Themes are stored in [themes.*] sections, e.g.:
        [themes.dark]
        primary = "cyan"
        dim = "bright_black"

        [themes.light]
        primary = "blue"
        dim = "white"

    Args:
        path: Explicit path to config file. If None, searches standard locations.

    Returns:
        Dictionary mapping theme names to Theme objects.
        Empty dict if no themes found or tomllib not available.
    """
    if tomllib is None:
        return {}

    if path is None:
        path = find_config_file()

    if path is None or not path.is_file():
        return {}

    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        print(f"Warning: TOML syntax error in {path}: {e}", file=sys.stderr)
        return {}
    except Exception:
        return {}

    themes = {}
    themes_section = data.get("themes", {})

    for name, theme_data in themes_section.items():
        if not isinstance(theme_data, dict):
            continue

        # Build theme from data, using DEFAULT_THEME values as fallback
        theme = Theme(
            name=name,
            primary=theme_data.get("primary", DEFAULT_THEME.primary),
            accent=theme_data.get("accent", DEFAULT_THEME.accent),
            dim=theme_data.get("dim", DEFAULT_THEME.dim),
            success=theme_data.get("success", DEFAULT_THEME.success),
            warning=theme_data.get("warning", DEFAULT_THEME.warning),
            error=theme_data.get("error", DEFAULT_THEME.error),
            text=theme_data.get("text", DEFAULT_THEME.text),
            extended_colors=theme_data.get("extended_colors", DEFAULT_THEME.extended_colors),
        )

        themes[name] = theme

    return themes


def load_theme(path: Optional[Path] = None) -> tuple[Theme, Optional[str]]:
    """
    Load theme from TOML config with support for named themes and presets.

    Fallback chain:
    1. If [theme].active is set, load named theme from [themes.X] sections
    2. If not found in config, check built-in PRESET_THEMES
    3. If no active or theme not found, use [theme] direct color values
    4. If no [theme] section, use DEFAULT_THEME

    Built-in preset themes (use with active = "theme-name"):
    - default: Current color scheme (cyan/green/yellow/red)
    - forge-dark: Higher contrast variant with bright blues and gold
    - solarized-tui: Solarized-inspired earthy colors
    - monokai-terminal: Vibrant magenta/cyan accents
    - nord-frost: Cool blues with minimal warm tones
    - amber-terminal: Retro VT100-style amber monochrome

    Example TOML with preset:
        [theme]
        active = "nord-frost"

    Example TOML with custom theme:
        [themes.dark]
        primary = "cyan"
        dim = "bright_black"

        [theme]
        active = "dark"

    Or direct values without named themes:
        [theme]
        primary = "blue"
        accent = "magenta"
        extended_colors = true

    Args:
        path: Explicit path to config file. If None, searches standard locations.

    Returns:
        Tuple of (Theme object, Optional warning message).
        Warning is None if theme loaded successfully, or a string describing the issue.
    """
    if tomllib is None:
        return DEFAULT_THEME, None

    if path is None:
        path = find_config_file()

    if path is None or not path.is_file():
        return DEFAULT_THEME, None

    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        warning = f"TOML syntax error in {path.name}: {e}"
        print(f"Warning: {warning}", file=sys.stderr)
        return DEFAULT_THEME, warning
    except Exception as e:
        warning = f"Error reading config file: {e}"
        return DEFAULT_THEME, warning

    theme_section = data.get("theme", {})

    # If no theme section, return default
    if not theme_section:
        return DEFAULT_THEME, None

    # Check for active theme reference
    active_theme = theme_section.get("active")
    if active_theme:
        # Load named themes and try to find the active one
        themes = load_themes(path)
        if active_theme in themes:
            return themes[active_theme], None
        # Check preset themes if not found in config
        elif active_theme in PRESET_THEMES:
            return PRESET_THEMES[active_theme], None
        else:
            warning = f"Theme '{active_theme}' not found in config or presets. Available presets: {', '.join(PRESET_THEMES.keys())}"
            print(f"Warning: {warning}", file=sys.stderr)
            return DEFAULT_THEME, warning

    # No active theme, use direct color values from [theme] section
    theme = Theme(
        name=theme_section.get("name", DEFAULT_THEME.name),
        primary=theme_section.get("primary", DEFAULT_THEME.primary),
        accent=theme_section.get("accent", DEFAULT_THEME.accent),
        dim=theme_section.get("dim", DEFAULT_THEME.dim),
        success=theme_section.get("success", DEFAULT_THEME.success),
        warning=theme_section.get("warning", DEFAULT_THEME.warning),
        error=theme_section.get("error", DEFAULT_THEME.error),
        text=theme_section.get("text", DEFAULT_THEME.text),
        extended_colors=theme_section.get("extended_colors", DEFAULT_THEME.extended_colors),
    )

    return theme, None
