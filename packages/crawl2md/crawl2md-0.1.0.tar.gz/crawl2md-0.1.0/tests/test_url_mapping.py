"""
Test URL to filepath mapping logic in DocsCrawler.

Validates the url_to_filepath method correctly maps URLs to output paths.
"""

import pytest
from pathlib import Path

from crawl2md.config import Config
from crawl2md.crawler import DocsCrawler


@pytest.fixture
def crawler(tmp_path):
    """Create a DocsCrawler instance with a temporary output directory."""
    config = Config(start_url="https://example.com/", output=str(tmp_path))
    return DocsCrawler(config)


@pytest.mark.parametrize(
    "url,expected_relative",
    [
        ("https://example.com/", "index.md"),
        ("https://example.com/tutorial/", "tutorial.md"),
        ("https://example.com/tutorial/intro/", "tutorial/intro.md"),
        ("https://example.com/page", "page.md"),
        ("https://example.com/guide/api", "guide/api.md"),
        ("https://example.com/guide/api/reference", "guide/api/reference.md"),
    ],
)
def test_url_to_filepath_mapping(crawler, url, expected_relative):
    """Test that URLs are correctly mapped to filesystem paths."""
    result = crawler.url_to_filepath(url)

    # Verify the path is under the output directory
    assert result.is_relative_to(crawler.output_dir)

    # Verify the relative path matches expected
    relative = result.relative_to(crawler.output_dir)
    assert str(relative) == expected_relative


def test_url_to_filepath_returns_path_object(crawler):
    """Test that url_to_filepath returns a Path object."""
    result = crawler.url_to_filepath("https://example.com/test")
    assert isinstance(result, Path)


def test_url_to_filepath_with_query_params(crawler):
    """Test URL mapping ignores query parameters in path."""
    result = crawler.url_to_filepath("https://example.com/page?id=123")
    relative = result.relative_to(crawler.output_dir)
    assert str(relative) == "page.md"


def test_url_to_filepath_always_ends_with_md(crawler):
    """Test that all mapped paths end with .md extension."""
    test_urls = [
        "https://example.com/",
        "https://example.com/page",
        "https://example.com/deep/nested/path/",
    ]

    for url in test_urls:
        result = crawler.url_to_filepath(url)
        assert result.suffix == ".md"
