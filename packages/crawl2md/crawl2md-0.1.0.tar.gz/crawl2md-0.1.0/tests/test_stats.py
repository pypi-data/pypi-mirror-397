"""Unit tests for CrawlStats dataclass."""

import time

from crawl2md.crawler import CrawlStats


def test_crawl_stats_initialization():
    """Verify CrawlStats initializes with correct defaults."""
    stats = CrawlStats()
    assert stats.pages_processed == 0
    assert stats.files_saved == 0
    assert stats.error_count == 0
    assert stats.duplicates_skipped == 0
    assert stats.queue_size == 0
    assert stats.current_url is None
    assert stats.last_error is None
    assert stats.log_lines == []
    assert stats.paused is False
    assert stats.stop_requested is False
    assert stats.crawler_error is None
    assert isinstance(stats.start_time, float)
    assert stats.start_time <= time.time()


def test_crawl_stats_add_log():
    """Verify log lines are added correctly."""
    stats = CrawlStats()
    stats.add_log("First log")
    stats.add_log("Second log")
    assert len(stats.log_lines) == 2
    assert stats.log_lines[0] == "First log"
    assert stats.log_lines[1] == "Second log"


def test_crawl_stats_add_log_overflow():
    """Verify oldest logs removed when exceeding max_lines."""
    stats = CrawlStats()
    for i in range(250):
        stats.add_log(f"Log {i}", max_lines=200)
    # Should only keep last 200
    assert len(stats.log_lines) == 200
    assert stats.log_lines[0] == "Log 50"
    assert stats.log_lines[-1] == "Log 249"
    assert stats.logs_removed == 50


def test_crawl_stats_add_log_unlimited():
    """Verify unlimited buffer when max_lines=0."""
    stats = CrawlStats()
    for i in range(500):
        stats.add_log(f"Log {i}", max_lines=0)
    # Should keep all logs
    assert len(stats.log_lines) == 500
    assert stats.log_lines[0] == "Log 0"
    assert stats.log_lines[-1] == "Log 499"
    assert stats.logs_removed == 0


def test_crawl_stats_modifications():
    """Verify stats can be modified."""
    stats = CrawlStats()

    stats.pages_processed = 10
    stats.files_saved = 8
    stats.duplicates_skipped = 2
    stats.error_count = 1
    stats.queue_size = 5
    stats.current_url = "https://example.com/test"
    stats.last_error = "Test error"
    stats.paused = True
    stats.stop_requested = True

    assert stats.pages_processed == 10
    assert stats.files_saved == 8
    assert stats.duplicates_skipped == 2
    assert stats.error_count == 1
    assert stats.queue_size == 5
    assert stats.current_url == "https://example.com/test"
    assert stats.last_error == "Test error"
    assert stats.paused is True
    assert stats.stop_requested is True


def test_crawl_stats_elapsed_time():
    """Verify elapsed time calculation."""
    stats = CrawlStats()
    time.sleep(0.1)
    elapsed = time.time() - stats.start_time
    assert elapsed >= 0.1
    assert elapsed < 1.0  # Should be quick


def test_crawl_stats_log_custom_max_lines():
    """Verify custom max_lines parameter works."""
    stats = CrawlStats()
    for i in range(15):
        stats.add_log(f"Log {i}", max_lines=10)

    # Should only keep last 10
    assert len(stats.log_lines) == 10
    assert stats.log_lines[0] == "Log 5"
    assert stats.log_lines[-1] == "Log 14"


def test_crawl_stats_crawler_error():
    """Verify crawler_error field can store traceback."""
    stats = CrawlStats()
    assert stats.crawler_error is None

    error_traceback = "Traceback (most recent call last):\n  File test.py, line 1\nError: test"
    stats.crawler_error = error_traceback

    assert stats.crawler_error == error_traceback
    assert "Traceback" in stats.crawler_error
