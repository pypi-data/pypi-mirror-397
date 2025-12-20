"""Integration tests for end-to-end workflows."""

import subprocess
import sys
import threading
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from crawl2md.cli import main
from crawl2md.config import Config
from crawl2md.crawler import DocsCrawler


def test_no_tui_mode_basic_crawl(tmp_path):
    """Test basic crawl in no-TUI mode completes successfully."""
    # Mock a simple successful crawl
    with patch("crawl2md.cli.DocsCrawler") as MockCrawler:
        mock_instance = Mock()
        mock_instance.crawl.return_value = (5, True)  # 5 pages, success
        mock_instance.pages_processed = 5
        MockCrawler.return_value = mock_instance

        result = main(
            [
                "--start",
                "https://example.com",
                "--output",
                str(tmp_path),
                "--max-pages",
                "5",
                "--no-tui",
            ]
        )

        assert result == 0
        mock_instance.crawl.assert_called_once()


def test_no_tui_mode_no_pages(tmp_path):
    """Test no-TUI mode returns error when no pages processed."""
    with patch("crawl2md.cli.DocsCrawler") as MockCrawler:
        mock_instance = Mock()
        mock_instance.crawl.return_value = (0, True)
        mock_instance.pages_processed = 0
        MockCrawler.return_value = mock_instance

        result = main(["--start", "https://example.com", "--output", str(tmp_path), "--no-tui"])

        assert result == 1


def test_no_tui_mode_start_url_failure(tmp_path):
    """Test no-TUI mode returns error when start URL fails."""
    with patch("crawl2md.cli.DocsCrawler") as MockCrawler:
        mock_instance = Mock()
        mock_instance.crawl.return_value = (0, False)  # Start URL failed
        mock_instance.pages_processed = 0
        MockCrawler.return_value = mock_instance

        result = main(["--start", "https://example.com", "--output", str(tmp_path), "--no-tui"])

        assert result == 1


def test_tui_mode_basic_crawl(tmp_path):
    """Test basic crawl in TUI mode (default)."""
    with patch("crawl2md.cli.DocsCrawler") as MockCrawler, patch(
        "crawl2md.tui.run_tui"
    ) as mock_tui:
        mock_instance = Mock()
        mock_instance.pages_processed = 5
        mock_instance.stats = Mock()
        mock_instance.stats.crawler_error = None
        MockCrawler.return_value = mock_instance

        # Mock the TUI to do nothing
        def fake_tui(config, stats, thread):
            # Wait a bit for thread to start
            time.sleep(0.1)
            stats.stop_requested = True

        mock_tui.side_effect = fake_tui

        result = main(
            [
                "--start",
                "https://example.com",
                "--output",
                str(tmp_path),
            ]
        )

        assert result == 0
        mock_tui.assert_called_once()


def test_tui_mode_crawler_error(tmp_path):
    """Test TUI mode returns error when crawler crashes."""
    with patch("crawl2md.cli.DocsCrawler") as MockCrawler, patch(
        "crawl2md.tui.run_tui"
    ) as mock_tui:
        mock_instance = Mock()
        mock_instance.pages_processed = 0
        mock_instance.stats = Mock()
        mock_instance.stats.crawler_error = "Test error"
        MockCrawler.return_value = mock_instance

        mock_tui.return_value = None

        result = main(
            [
                "--start",
                "https://example.com",
                "--output",
                str(tmp_path),
            ]
        )

        assert result == 1


def test_missing_start_url():
    """Test error when start URL is not provided in --no-tui mode."""
    # With TUI enabled (default), no-args launches config form
    # With --no-tui, no-args should error
    result = main(["--no-tui"])
    assert result == 1


def test_dedupe_flag_integration(tmp_path):
    """Test --dedupe flag is properly passed to crawler."""
    config = Config(
        start_url="https://example.com", output=str(tmp_path), dedupe=True
    )
    crawler = DocsCrawler(config)
    assert crawler.config.dedupe is True


def test_no_tui_flag_integration():
    """Test --no-tui flag is properly parsed."""
    from crawl2md.cli import parse_args

    # Without --no-tui, no_tui should be falsy (TUI is default)
    args = parse_args(["--start", "https://example.com"])
    assert not args.no_tui

    # With --no-tui, no_tui should be True
    args = parse_args(["--start", "https://example.com", "--no-tui"])
    assert args.no_tui is True


def test_crawler_pause_stop_integration():
    """Test crawler respects pause and stop flags."""
    config = Config(start_url="https://example.com", delay=0.1)
    crawler = DocsCrawler(config)

    # Mock the fetch to succeed quickly
    with patch.object(crawler, "fetch_and_save") as mock_fetch:
        mock_fetch.return_value = ([], True)

        # Start crawler in background thread
        def run_crawler():
            try:
                crawler.crawl()
            except:
                pass

        thread = threading.Thread(target=run_crawler, daemon=True)
        thread.start()

        # Let it start
        time.sleep(0.05)

        # Pause it
        crawler.stats.paused = True
        paused_count = crawler.stats.pages_processed
        time.sleep(0.2)

        # Should not have processed more while paused
        assert crawler.stats.pages_processed == paused_count

        # Stop it
        crawler.stats.stop_requested = True
        thread.join(timeout=1.0)

        # Thread should have stopped
        assert not thread.is_alive()


def test_config_delay_modification():
    """Test that config.delay can be modified at runtime."""
    config = Config(start_url="https://example.com", delay=0.5)
    assert config.delay == 0.5

    config.delay = 1.0
    assert config.delay == 1.0

    config.delay = 0.0
    assert config.delay == 0.0


def test_stats_tracking_during_crawl(tmp_path):
    """Test that stats are updated correctly during crawl."""
    config = Config(
        start_url="https://example.com",
        output=str(tmp_path),
        dedupe=False,
        no_frontmatter=True,
    )
    crawler = DocsCrawler(config)

    # Mock successful page fetch
    mock_response = Mock()
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.text = (
        "<html><body><main><h1>Test</h1><a href='/page2'>Link</a></main></body></html>"
    )

    with patch.object(crawler.session, "get", return_value=mock_response):
        # Fetch one page
        links, success = crawler.fetch_and_save("https://example.com/page1")

        assert success is True
        assert crawler.stats.current_url == "https://example.com/page1"
        assert crawler.stats.files_saved == 1
        assert crawler.stats.error_count == 0
        assert len(crawler.stats.log_lines) > 0


def test_stats_error_tracking(tmp_path):
    """Test that stats track errors correctly."""
    import requests

    config = Config(start_url="https://example.com", output=str(tmp_path))
    crawler = DocsCrawler(config)

    # Mock failed request with requests.RequestException
    with patch.object(crawler.session, "get", side_effect=requests.RequestException("Test error")):
        links, success = crawler.fetch_and_save("https://example.com/page1")

        assert success is False
        assert crawler.stats.error_count == 1
        assert crawler.stats.last_error is not None
        assert "Test error" in crawler.stats.last_error


def test_deduplication_stats(tmp_path):
    """Test that deduplication stats are tracked correctly."""
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
    mock_response.text = "<html><body><main><h1>Same</h1></main></body></html>"

    with patch.object(crawler.session, "get", return_value=mock_response):
        # Fetch same content twice
        crawler.fetch_and_save("https://example.com/page1")
        crawler.fetch_and_save("https://example.com/page2")

        assert crawler.stats.files_saved == 1
        assert crawler.stats.duplicates_skipped == 1
