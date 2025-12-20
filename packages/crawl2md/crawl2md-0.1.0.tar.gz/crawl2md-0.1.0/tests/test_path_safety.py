"""
Test path traversal prevention in DocsCrawler.

Validates that url_to_filepath properly sanitizes potentially dangerous paths.
"""

import pytest

from crawl2md.config import Config
from crawl2md.crawler import DocsCrawler


@pytest.fixture
def crawler(tmp_path):
    """Create a DocsCrawler instance with a temporary output directory."""
    config = Config(start_url="https://example.com/", output=str(tmp_path))
    return DocsCrawler(config)


def test_path_with_dotdot_raises_error(crawler):
    """Test that URLs with .. segments raise ValueError after sanitization."""
    with pytest.raises(ValueError, match="Invalid path after sanitization"):
        crawler.url_to_filepath("https://example.com/..")


def test_path_with_dotdot_in_middle_sanitized(crawler):
    """Test that URLs with .. in the middle are sanitized (.. removed)."""
    # The implementation filters out ".." segments but keeps the rest
    result = crawler.url_to_filepath("https://example.com/../etc/passwd")
    relative = result.relative_to(crawler.output_dir)
    # "../etc/passwd" -> "etc/passwd.md"
    assert str(relative) == "etc/passwd.md"


def test_path_with_dot_segment_sanitized(crawler):
    """Test that URLs with . segments are sanitized (removed)."""
    # The implementation filters out "." segments
    # If only "." remains, it should raise ValueError
    with pytest.raises(ValueError, match="Invalid path after sanitization"):
        crawler.url_to_filepath("https://example.com/.")


def test_path_with_dotgit_sanitized(crawler):
    """Test that URLs with .git (hidden directory) are sanitized."""
    # The implementation filters out segments starting with "."
    # So "/.git/config" becomes "/config" which is valid
    result = crawler.url_to_filepath("https://example.com/.git/config")
    relative = result.relative_to(crawler.output_dir)
    assert str(relative) == "config.md"


def test_path_with_multiple_dotgit_segments(crawler):
    """Test URL with multiple hidden directory segments."""
    # /.hidden/.git/file -> /file.md
    result = crawler.url_to_filepath("https://example.com/.hidden/.git/file")
    relative = result.relative_to(crawler.output_dir)
    assert str(relative) == "file.md"


def test_path_all_hidden_raises_error(crawler):
    """Test that paths with only hidden segments raise ValueError."""
    with pytest.raises(ValueError, match="Invalid path after sanitization"):
        crawler.url_to_filepath("https://example.com/.hidden/.git")


def test_safe_path_remains_within_output_dir(crawler):
    """Test that normal paths stay within the output directory."""
    result = crawler.url_to_filepath("https://example.com/docs/guide")

    # Resolve both paths and verify the result is under output_dir
    resolved_result = result.resolve()
    resolved_output = crawler.output_dir.resolve()

    # This should not raise ValueError
    resolved_result.relative_to(resolved_output)


def test_empty_path_after_sanitization_raises_error(crawler):
    """Test that URLs resulting in empty paths raise ValueError."""
    # URL with only dots or hidden segments
    with pytest.raises(ValueError, match="Invalid path after sanitization"):
        crawler.url_to_filepath("https://example.com/./.")
