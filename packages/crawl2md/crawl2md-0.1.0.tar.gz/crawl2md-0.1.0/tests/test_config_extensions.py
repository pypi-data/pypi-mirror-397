"""Unit tests for config extensions (no_tui, dedupe, exclude_patterns, etc.)."""

import os

import pytest

from crawl2md.config import Config, load_env_config, merge_configs, parse_bool_env


def test_config_new_fields_defaults():
    """Verify no_tui, dedupe default values."""
    config = Config()
    assert config.no_tui is False
    assert config.dedupe is False
    assert config.exclude_patterns == []
    assert config.scroll_lines == 0
    assert config.max_log_lines == 0


def test_config_no_tui_values():
    """Verify no_tui accepts boolean values."""
    config = Config(no_tui=False)
    assert config.no_tui is False

    config = Config(no_tui=True)
    assert config.no_tui is True


def test_config_dedupe_values():
    """Verify dedupe accepts boolean values."""
    config = Config(dedupe=False)
    assert config.dedupe is False

    config = Config(dedupe=True)
    assert config.dedupe is True


def test_config_exclude_patterns_values():
    """Verify exclude_patterns accepts list values."""
    config = Config(exclude_patterns=["*.php", "/admin/*"])
    assert config.exclude_patterns == ["*.php", "/admin/*"]

    config = Config(exclude_patterns=[])
    assert config.exclude_patterns == []


def test_parse_bool_env():
    """Verify parse_bool_env correctly parses various string values."""
    assert parse_bool_env("1") is True
    assert parse_bool_env("true") is True
    assert parse_bool_env("True") is True
    assert parse_bool_env("TRUE") is True
    assert parse_bool_env("yes") is True
    assert parse_bool_env("YES") is True
    assert parse_bool_env("on") is True
    assert parse_bool_env("ON") is True

    assert parse_bool_env("0") is False
    assert parse_bool_env("false") is False
    assert parse_bool_env("False") is False
    assert parse_bool_env("no") is False
    assert parse_bool_env("off") is False
    assert parse_bool_env("") is False
    assert parse_bool_env("random") is False


def test_load_env_config_no_tui(monkeypatch):
    """Verify CRAWL2MD_NO_TUI env var is loaded."""
    monkeypatch.setenv("CRAWL2MD_NO_TUI", "true")
    config = load_env_config()
    assert config["no_tui"] is True

    monkeypatch.setenv("CRAWL2MD_NO_TUI", "false")
    config = load_env_config()
    assert config["no_tui"] is False


def test_load_env_config_dedupe(monkeypatch):
    """Verify CRAWL2MD_DEDUPE env var is loaded."""
    monkeypatch.setenv("CRAWL2MD_DEDUPE", "true")
    config = load_env_config()
    assert config["dedupe"] is True

    monkeypatch.setenv("CRAWL2MD_DEDUPE", "false")
    config = load_env_config()
    assert config["dedupe"] is False


def test_load_env_config_exclude_patterns(monkeypatch):
    """Verify CRAWL2MD_EXCLUDE_PATTERNS env var is loaded."""
    monkeypatch.setenv("CRAWL2MD_EXCLUDE_PATTERNS", "*.php,/admin/*,*.aspx")
    config = load_env_config()
    assert config["exclude_patterns"] == ["*.php", "/admin/*", "*.aspx"]


def test_load_env_config_scroll_lines(monkeypatch):
    """Verify CRAWL2MD_SCROLL_LINES env var is loaded."""
    monkeypatch.setenv("CRAWL2MD_SCROLL_LINES", "5")
    config = load_env_config()
    assert config["scroll_lines"] == 5


def test_load_env_config_max_log_lines(monkeypatch):
    """Verify CRAWL2MD_MAX_LOG_LINES env var is loaded."""
    monkeypatch.setenv("CRAWL2MD_MAX_LOG_LINES", "1000")
    config = load_env_config()
    assert config["max_log_lines"] == 1000


def test_merge_configs_precedence():
    """Verify CLI args override env vars override config file."""
    file_config = {"no_tui": False, "dedupe": False, "delay": 0.5}
    env_config = {"no_tui": True, "dedupe": True}
    cli_config = {"dedupe": False}

    config = merge_configs(file_config, env_config, cli_config)

    # CLI wins for dedupe
    assert config.dedupe is False
    # Env wins for no_tui (no CLI override)
    assert config.no_tui is True
    # File wins for delay (no env or CLI override)
    assert config.delay == 0.5


def test_merge_configs_all_new_fields():
    """Verify all new fields can be set via merge."""
    file_config = {}
    env_config = {}
    cli_config = {
        "no_tui": True,
        "dedupe": True,
        "exclude_patterns": ["*.php"],
        "scroll_lines": 10,
        "max_log_lines": 500,
    }

    config = merge_configs(file_config, env_config, cli_config)

    assert config.no_tui is True
    assert config.dedupe is True
    assert config.exclude_patterns == ["*.php"]
    assert config.scroll_lines == 10
    assert config.max_log_lines == 500


def test_config_with_all_fields():
    """Verify Config works with all fields including new ones."""
    config = Config(
        start_url="https://example.com",
        base_url="https://example.com",
        output="test-output",
        tags=["tag1", "tag2"],
        restrict_prefix="/docs",
        exclude_patterns=["*.php", "/admin/*"],
        delay=0.5,
        max_pages=100,
        no_frontmatter=True,
        user_agent="test-agent",
        verbose=True,
        no_tui=True,
        dedupe=True,
        scroll_lines=5,
        max_log_lines=1000,
    )

    assert config.start_url == "https://example.com"
    assert config.base_url == "https://example.com"
    assert config.output == "test-output"
    assert config.tags == ["tag1", "tag2"]
    assert config.restrict_prefix == "/docs"
    assert config.exclude_patterns == ["*.php", "/admin/*"]
    assert config.delay == 0.5
    assert config.max_pages == 100
    assert config.no_frontmatter is True
    assert config.user_agent == "test-agent"
    assert config.verbose is True
    assert config.no_tui is True
    assert config.dedupe is True
    assert config.scroll_lines == 5
    assert config.max_log_lines == 1000


def test_env_config_multiple_fields(monkeypatch):
    """Verify multiple env vars load correctly together."""
    monkeypatch.setenv("CRAWL2MD_START_URL", "https://test.com")
    monkeypatch.setenv("CRAWL2MD_NO_TUI", "1")
    monkeypatch.setenv("CRAWL2MD_DEDUPE", "1")
    monkeypatch.setenv("CRAWL2MD_EXCLUDE_PATTERNS", "*.php,*.asp")
    monkeypatch.setenv("CRAWL2MD_DELAY", "1.5")
    monkeypatch.setenv("CRAWL2MD_SCROLL_LINES", "10")
    monkeypatch.setenv("CRAWL2MD_MAX_LOG_LINES", "500")

    config = load_env_config()

    assert config["start_url"] == "https://test.com"
    assert config["no_tui"] is True
    assert config["dedupe"] is True
    assert config["exclude_patterns"] == ["*.php", "*.asp"]
    assert config["delay"] == 1.5
    assert config["scroll_lines"] == 10
    assert config["max_log_lines"] == 500
