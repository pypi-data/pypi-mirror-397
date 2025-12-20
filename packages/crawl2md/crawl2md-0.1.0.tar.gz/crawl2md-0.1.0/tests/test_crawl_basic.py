"""
Test basic crawling functionality with mocked network requests.

Validates the crawl method behavior without making real HTTP requests.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from crawl2md.config import Config
from crawl2md.crawler import DocsCrawler


# Test HTML fixture
TEST_HTML = """
<html>
<head><title>Test Page</title></head>
<body>
<main>
  <h1>Welcome</h1>
  <p>Content here.</p>
  <a href="/other">Other page</a>
  <a href="/docs/guide">Guide</a>
</main>
</body>
</html>
"""

TEST_HTML_OTHER = """
<html>
<head><title>Other Page</title></head>
<body>
<main>
  <h1>Other Content</h1>
  <p>This is another page.</p>
</main>
</body>
</html>
"""


@pytest.fixture
def crawler(tmp_path):
    """Create a DocsCrawler instance with a temporary output directory."""
    config = Config(
        start_url="https://example.com/", output=str(tmp_path), delay=0.0
    )
    return DocsCrawler(config)


@pytest.fixture
def mock_response():
    """Create a mock HTTP response."""

    def _create_response(html_content, status_code=200):
        response = Mock()
        response.status_code = status_code
        response.text = html_content
        response.headers = {"Content-Type": "text/html; charset=utf-8"}
        response.raise_for_status = Mock()
        return response

    return _create_response


def test_crawl_single_page(crawler, mock_response):
    """Test crawling a single page and following its internal links."""
    with patch.object(crawler.session, "get") as mock_get:
        mock_get.return_value = mock_response(TEST_HTML)

        pages, success = crawler.crawl()

        # TEST_HTML contains links to /other and /docs/guide
        # So it should crawl 3 pages total (start + 2 links)
        assert pages == 3
        assert success is True


def test_crawl_follows_internal_links(crawler, mock_response):
    """Test that crawler follows internal links."""

    def mock_get_side_effect(url, timeout):
        if url == "https://example.com/":
            return mock_response(TEST_HTML)
        elif url == "https://example.com/other":
            return mock_response(TEST_HTML_OTHER)
        elif url == "https://example.com/docs/guide":
            return mock_response(TEST_HTML_OTHER)
        else:
            response = Mock()
            response.status_code = 404
            response.raise_for_status.side_effect = Exception("Not found")
            return response

    with patch.object(crawler.session, "get") as mock_get:
        mock_get.side_effect = mock_get_side_effect

        pages, success = crawler.crawl()

        # Should crawl start page + 2 linked pages
        assert pages == 3
        assert success is True


def test_crawl_writes_markdown_files(crawler, mock_response):
    """Test that crawl writes markdown files to expected paths."""
    with patch.object(crawler.session, "get") as mock_get:
        mock_get.return_value = mock_response(TEST_HTML)

        crawler.crawl()

        # Check that index.md was created
        index_file = crawler.output_dir / "index.md"
        assert index_file.exists()

        # Read the content
        content = index_file.read_text()

        # Should contain markdown content
        assert "Welcome" in content
        assert "Content here" in content


def test_crawl_includes_frontmatter(crawler, mock_response):
    """Test that generated markdown includes YAML frontmatter."""
    with patch.object(crawler.session, "get") as mock_get:
        mock_get.return_value = mock_response(TEST_HTML)

        crawler.crawl()

        index_file = crawler.output_dir / "index.md"
        content = index_file.read_text()

        # Check for frontmatter delimiters
        assert content.startswith("---\n")
        assert "title:" in content
        assert "source:" in content
        assert "created:" in content


def test_crawl_without_frontmatter(tmp_path, mock_response):
    """Test crawling with frontmatter disabled."""
    config = Config(
        start_url="https://example.com/",
        output=str(tmp_path),
        delay=0.0,
        no_frontmatter=True,
    )
    crawler = DocsCrawler(config)

    with patch.object(crawler.session, "get") as mock_get:
        mock_get.return_value = mock_response(TEST_HTML)

        crawler.crawl()

        index_file = crawler.output_dir / "index.md"
        content = index_file.read_text()

        # Should not have frontmatter
        assert not content.startswith("---")
        # But should have the markdown content
        assert "Welcome" in content


def test_crawl_with_tags_in_frontmatter(tmp_path, mock_response):
    """Test that tags from config appear in frontmatter."""
    config = Config(
        start_url="https://example.com/",
        output=str(tmp_path),
        delay=0.0,
        tags=["docs", "test"],
    )
    crawler = DocsCrawler(config)

    with patch.object(crawler.session, "get") as mock_get:
        mock_get.return_value = mock_response(TEST_HTML)

        crawler.crawl()

        index_file = crawler.output_dir / "index.md"
        content = index_file.read_text()

        # Check for tags in frontmatter
        assert "tags:" in content
        assert "  - docs" in content
        assert "  - test" in content


def test_crawl_max_pages_limit(tmp_path, mock_response):
    """Test that max_pages limit is respected."""
    config = Config(
        start_url="https://example.com/", output=str(tmp_path), delay=0.0, max_pages=1
    )
    crawler = DocsCrawler(config)

    with patch.object(crawler.session, "get") as mock_get:
        mock_get.return_value = mock_response(TEST_HTML)

        pages, success = crawler.crawl()

        # Should only process 1 page despite links present
        assert pages == 1
        assert mock_get.call_count == 1


def test_crawl_creates_subdirectories(crawler, mock_response):
    """Test that crawler creates subdirectories for nested URLs."""
    html_with_nested_link = """
    <html>
    <head><title>Test</title></head>
    <body>
    <main>
      <a href="/docs/guide/intro">Intro</a>
    </main>
    </body>
    </html>
    """

    def mock_get_side_effect(url, timeout):
        if url == "https://example.com/":
            return mock_response(html_with_nested_link)
        elif url == "https://example.com/docs/guide/intro":
            return mock_response(TEST_HTML_OTHER)
        else:
            return mock_response(TEST_HTML)

    with patch.object(crawler.session, "get") as mock_get:
        mock_get.side_effect = mock_get_side_effect

        crawler.crawl()

        # Check that subdirectory structure was created
        nested_file = crawler.output_dir / "docs" / "guide" / "intro.md"
        assert nested_file.exists()


def test_crawl_handles_network_error(crawler):
    """Test that crawler handles RequestException gracefully."""
    import requests

    with patch.object(crawler.session, "get") as mock_get:
        # Use requests.RequestException which is actually caught by the code
        mock_get.side_effect = requests.RequestException("Network error")

        pages, success = crawler.crawl()

        # Should fail but not crash
        assert pages == 0
        assert success is False


def test_crawl_returns_expected_page_count(crawler, mock_response):
    """Test that crawl returns the correct number of processed pages."""

    def mock_get_side_effect(url, timeout):
        if url == "https://example.com/":
            return mock_response(
                """
                <html><body><main>
                  <a href="/page1">Page 1</a>
                  <a href="/page2">Page 2</a>
                </main></body></html>
            """
            )
        else:
            return mock_response(TEST_HTML_OTHER)

    with patch.object(crawler.session, "get") as mock_get:
        mock_get.side_effect = mock_get_side_effect

        pages, success = crawler.crawl()

        # Start page + 2 linked pages = 3 total
        assert pages == 3
        assert success is True


def test_crawl_skips_duplicate_urls(crawler, mock_response):
    """Test that crawler doesn't process the same URL twice."""
    html_with_duplicate_links = """
    <html>
    <head><title>Test</title></head>
    <body>
    <main>
      <a href="/page">Link 1</a>
      <a href="/page">Link 2</a>
      <a href="/page">Link 3</a>
    </main>
    </body>
    </html>
    """

    def mock_get_side_effect(url, timeout):
        if url == "https://example.com/":
            return mock_response(html_with_duplicate_links)
        elif url == "https://example.com/page":
            return mock_response(TEST_HTML_OTHER)
        else:
            return mock_response(TEST_HTML)

    with patch.object(crawler.session, "get") as mock_get:
        mock_get.side_effect = mock_get_side_effect

        pages, success = crawler.crawl()

        # Should only fetch /page once despite multiple links
        assert pages == 2  # Start page + /page
        assert mock_get.call_count == 2
