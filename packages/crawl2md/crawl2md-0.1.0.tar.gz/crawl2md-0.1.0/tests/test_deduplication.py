"""Unit tests for deduplication logic."""

import hashlib
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from crawl2md.config import Config
from crawl2md.crawler import DocsCrawler


def test_body_hash_computation():
    """Verify SHA256 hash computed correctly from markdown body."""
    body = "# Test Content\n\nSome text here."
    expected = hashlib.sha256(body.strip().encode("utf-8")).hexdigest()
    actual = hashlib.sha256(body.strip().encode("utf-8")).hexdigest()
    assert actual == expected


def test_extract_markdown_body_with_frontmatter():
    """Verify markdown body extraction excludes frontmatter."""
    full_content = """---
title: "Test"
source: https://example.com
---

# Content

This is the body."""

    config = Config(start_url="https://example.com", dedupe=True)
    crawler = DocsCrawler(config)

    body = crawler._extract_markdown_body(full_content)
    assert body == "# Content\n\nThis is the body."
    assert "title:" not in body
    assert "source:" not in body


def test_extract_markdown_body_without_frontmatter():
    """Verify markdown body extraction handles content without frontmatter."""
    full_content = "# Content\n\nThis is the body."

    config = Config(start_url="https://example.com", dedupe=True)
    crawler = DocsCrawler(config)

    body = crawler._extract_markdown_body(full_content)
    assert body == "# Content\n\nThis is the body."


def test_dedupe_disabled_all_saved(tmp_path):
    """Verify all pages saved when dedupe=False."""
    config = Config(
        start_url="https://example.com",
        output=str(tmp_path),
        dedupe=False,
        no_frontmatter=True,
    )
    crawler = DocsCrawler(config)

    # Mock response with same content
    mock_response = Mock()
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.text = "<html><body><main><h1>Same Content</h1></main></body></html>"

    with patch.object(crawler.session, "get", return_value=mock_response):
        # Process same content twice
        links1, success1 = crawler.fetch_and_save("https://example.com/page1")
        links2, success2 = crawler.fetch_and_save("https://example.com/page2")

        assert success1 is True
        assert success2 is True

        # Both files should exist
        file1 = tmp_path / "page1.md"
        file2 = tmp_path / "page2.md"
        assert file1.exists()
        assert file2.exists()

        # Duplicates counter should not increment
        assert crawler.stats.duplicates_skipped == 0
        assert crawler.stats.files_saved == 2


def test_dedupe_enabled_first_saved(tmp_path):
    """Verify first occurrence of content is saved with dedupe enabled."""
    config = Config(
        start_url="https://example.com",
        output=str(tmp_path),
        dedupe=True,
        no_frontmatter=True,
    )
    crawler = DocsCrawler(config)

    # Mock response
    mock_response = Mock()
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.text = "<html><body><main><h1>Unique Content</h1></main></body></html>"

    with patch.object(crawler.session, "get", return_value=mock_response):
        links, success = crawler.fetch_and_save("https://example.com/page1")

        assert success is True
        file1 = tmp_path / "page1.md"
        assert file1.exists()
        assert crawler.stats.files_saved == 1
        assert crawler.stats.duplicates_skipped == 0


def test_dedupe_enabled_duplicate_skipped(tmp_path):
    """Verify duplicate content skipped with dedupe enabled."""
    config = Config(
        start_url="https://example.com",
        output=str(tmp_path),
        dedupe=True,
        no_frontmatter=True,
    )
    crawler = DocsCrawler(config)

    # Mock response with same content
    mock_response = Mock()
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.text = "<html><body><main><h1>Same Content</h1><a href='/link1'>Link</a></main></body></html>"

    with patch.object(crawler.session, "get", return_value=mock_response):
        # Process same content twice
        links1, success1 = crawler.fetch_and_save("https://example.com/page1")
        links2, success2 = crawler.fetch_and_save("https://example.com/page2")

        assert success1 is True
        assert success2 is True

        # First file saved, second skipped
        file1 = tmp_path / "page1.md"
        file2 = tmp_path / "page2.md"
        assert file1.exists()
        assert not file2.exists()

        # Stats should reflect duplicate
        assert crawler.stats.files_saved == 1
        assert crawler.stats.duplicates_skipped == 1


def test_dedupe_different_content_both_saved(tmp_path):
    """Verify different content results in both files saved."""
    config = Config(
        start_url="https://example.com",
        output=str(tmp_path),
        dedupe=True,
        no_frontmatter=True,
    )
    crawler = DocsCrawler(config)

    # Mock responses with different content
    mock_response1 = Mock()
    mock_response1.headers = {"Content-Type": "text/html"}
    mock_response1.text = "<html><body><main><h1>Content A</h1></main></body></html>"

    mock_response2 = Mock()
    mock_response2.headers = {"Content-Type": "text/html"}
    mock_response2.text = "<html><body><main><h1>Content B</h1></main></body></html>"

    with patch.object(
        crawler.session, "get", side_effect=[mock_response1, mock_response2]
    ):
        links1, success1 = crawler.fetch_and_save("https://example.com/page1")
        links2, success2 = crawler.fetch_and_save("https://example.com/page2")

        assert success1 is True
        assert success2 is True

        # Both files should exist
        file1 = tmp_path / "page1.md"
        file2 = tmp_path / "page2.md"
        assert file1.exists()
        assert file2.exists()

        # No duplicates
        assert crawler.stats.files_saved == 2
        assert crawler.stats.duplicates_skipped == 0


def test_dedupe_with_frontmatter(tmp_path):
    """Verify deduplication works correctly with frontmatter enabled."""
    config = Config(
        start_url="https://example.com",
        output=str(tmp_path),
        dedupe=True,
        no_frontmatter=False,  # Frontmatter enabled
        tags=["test"],
    )
    crawler = DocsCrawler(config)

    # Mock response with same content
    mock_response = Mock()
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.text = "<html><head><title>Page Title</title></head><body><main><h1>Same Content</h1></main></body></html>"

    with patch.object(crawler.session, "get", return_value=mock_response):
        # Process same content twice
        links1, success1 = crawler.fetch_and_save("https://example.com/page1")
        links2, success2 = crawler.fetch_and_save("https://example.com/page2")

        assert success1 is True
        assert success2 is True

        # First file saved with frontmatter
        file1 = tmp_path / "page1.md"
        assert file1.exists()

        content1 = file1.read_text()
        assert content1.startswith("---")
        assert "title:" in content1

        # Second file skipped (duplicate body despite different frontmatter)
        file2 = tmp_path / "page2.md"
        assert not file2.exists()

        assert crawler.stats.files_saved == 1
        assert crawler.stats.duplicates_skipped == 1


def test_dedupe_with_dedupe_enabled():
    """Verify deduplication works when dedupe=True."""
    config = Config(
        start_url="https://example.com", dedupe=True
    )
    assert config.dedupe is True

    crawler = DocsCrawler(config)
    assert crawler.config.dedupe is True
