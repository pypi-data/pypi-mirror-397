"""
Test configuration precedence rules.

Validates that config file < env vars < CLI args precedence is enforced correctly.
"""

import pytest
from pathlib import Path

from crawl2md.config import resolve_config, load_config_file, load_env_config


def test_cli_overrides_env(tmp_path, monkeypatch):
    """Test that CLI arguments override environment variables."""
    # Set environment variable
    monkeypatch.setenv("CRAWL2MD_OUTPUT", "from_env")

    # CLI args take precedence
    cli_args = {
        "start_url": "https://example.com",
        "output": "from_cli",
    }

    config = resolve_config(cli_args)

    assert config.output == "from_cli"


def test_env_overrides_config_file(tmp_path, monkeypatch):
    """Test that environment variables override config file values."""
    # Create a config file
    config_file = tmp_path / "crawl2md.toml"
    config_file.write_text(
        """
[crawl2md]
output = "from_file"
start_url = "https://file.example.com"
"""
    )

    # Change to temp directory so config file is found
    monkeypatch.chdir(tmp_path)

    # Set environment variable
    monkeypatch.setenv("CRAWL2MD_OUTPUT", "from_env")

    # No CLI override for output
    cli_args = {"start_url": None, "output": None}

    config = resolve_config(cli_args)

    assert config.output == "from_env"
    assert config.start_url == "https://file.example.com"


def test_config_file_used_when_no_env_or_cli(tmp_path, monkeypatch):
    """Test that config file values are used when no env or CLI overrides."""
    # Create a config file
    config_file = tmp_path / "crawl2md.toml"
    config_file.write_text(
        """
[crawl2md]
output = "from_file"
start_url = "https://file.example.com"
delay = 1.5
"""
    )

    # Change to temp directory so config file is found
    monkeypatch.chdir(tmp_path)

    # Clear any existing environment variables
    monkeypatch.delenv("CRAWL2MD_OUTPUT", raising=False)
    monkeypatch.delenv("CRAWL2MD_START_URL", raising=False)
    monkeypatch.delenv("CRAWL2MD_DELAY", raising=False)

    # No CLI overrides
    cli_args = {}

    config = resolve_config(cli_args)

    assert config.output == "from_file"
    assert config.start_url == "https://file.example.com"
    assert config.delay == 1.5


def test_defaults_used_when_no_config(tmp_path, monkeypatch):
    """Test that default values are used when no configuration is provided."""
    # Change to temp directory with no config file
    monkeypatch.chdir(tmp_path)

    # Clear environment variables
    monkeypatch.delenv("CRAWL2MD_OUTPUT", raising=False)
    monkeypatch.delenv("CRAWL2MD_DELAY", raising=False)

    # No CLI args
    cli_args = {}

    config = resolve_config(cli_args)

    # Check defaults from Config dataclass
    assert config.output == "docs-md"
    assert config.delay == 0.3
    assert config.no_frontmatter is False


def test_all_three_sources_with_full_precedence(tmp_path, monkeypatch):
    """Test precedence when all three sources provide values."""
    # Create config file
    config_file = tmp_path / "crawl2md.toml"
    config_file.write_text(
        """
[crawl2md]
output = "from_file"
delay = 1.0
max_pages = 10
verbose = false
"""
    )

    monkeypatch.chdir(tmp_path)

    # Set environment variables (override file)
    monkeypatch.setenv("CRAWL2MD_OUTPUT", "from_env")
    monkeypatch.setenv("CRAWL2MD_DELAY", "2.0")
    monkeypatch.setenv("CRAWL2MD_VERBOSE", "true")

    # CLI args (override everything)
    cli_args = {
        "output": "from_cli",
        "delay": None,  # Let env win
        "max_pages": None,  # Let file win
        "verbose": None,  # Let env win
    }

    config = resolve_config(cli_args)

    assert config.output == "from_cli"  # CLI wins
    assert config.delay == 2.0  # Env wins (no CLI override)
    assert config.max_pages == 10  # File wins (no env or CLI override)
    assert config.verbose is True  # Env wins (no CLI override)


def test_env_tags_parsing(monkeypatch):
    """Test that tags from environment are parsed correctly."""
    monkeypatch.setenv("CRAWL2MD_TAGS", "tag1, tag2, tag3")

    env_config = load_env_config()

    assert "tags" in env_config
    assert env_config["tags"] == ["tag1", "tag2", "tag3"]


def test_env_bool_parsing_true(monkeypatch):
    """Test boolean environment variable parsing for true values."""
    monkeypatch.setenv("CRAWL2MD_VERBOSE", "true")
    monkeypatch.setenv("CRAWL2MD_NO_FRONTMATTER", "1")

    env_config = load_env_config()

    assert env_config["verbose"] is True
    assert env_config["no_frontmatter"] is True


def test_env_bool_parsing_false(monkeypatch):
    """Test boolean environment variable parsing for false values."""
    monkeypatch.setenv("CRAWL2MD_VERBOSE", "false")
    monkeypatch.setenv("CRAWL2MD_NO_FRONTMATTER", "0")

    env_config = load_env_config()

    assert env_config["verbose"] is False
    assert env_config["no_frontmatter"] is False


def test_config_file_tags_parsing(tmp_path, monkeypatch):
    """Test that tags from config file are parsed correctly."""
    config_file = tmp_path / "crawl2md.toml"
    config_file.write_text(
        """
[crawl2md]
tags = ["docs", "reference", "tutorial"]
"""
    )

    monkeypatch.chdir(tmp_path)

    file_config = load_config_file()

    assert "tags" in file_config
    assert file_config["tags"] == ["docs", "reference", "tutorial"]


def test_cli_empty_tags_not_overriding(tmp_path, monkeypatch):
    """Test that empty CLI tags list doesn't override file/env values."""
    config_file = tmp_path / "crawl2md.toml"
    config_file.write_text(
        """
[crawl2md]
tags = ["from_file"]
"""
    )

    monkeypatch.chdir(tmp_path)

    # CLI with empty tags list should not override
    cli_args = {"tags": []}

    config = resolve_config(cli_args)

    # Should use file value since empty CLI tags are filtered out
    assert config.tags == ["from_file"]
