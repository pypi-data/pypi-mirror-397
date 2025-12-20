"""
Web crawler and HTML-to-Markdown converter for crawl2md.

Implements BFS crawling of documentation websites with:
- Internal link detection and filtering
- Main content extraction
- HTML to Markdown conversion
- YAML frontmatter generation
"""

import re
import sys
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from fnmatch import fnmatch
from hashlib import sha256
from pathlib import Path
from typing import Deque, Dict, List, Optional, Set, Tuple, Union
from urllib.parse import urljoin, urlparse, urldefrag

import requests
from bs4 import BeautifulSoup, Tag
from markdownify import markdownify

from .config import Config


class LogType(Enum):
    """Classification of log entry types for filtering and display."""
    FETCH = "fetch"
    SAVE = "save"
    SKIP = "skip"
    QUEUE = "queue"
    ERROR = "error"
    WARN = "warn"
    INFO = "info"


@dataclass
class LogEntry:
    """A typed log entry with classification for proper filtering.

    Attributes:
        type: Classification of this log entry
        message: The log message text
        url: Optional URL associated with this log entry
        source_url: Optional URL where this link was found (for errors)
    """
    type: LogType
    message: str
    url: Optional[str] = None
    source_url: Optional[str] = None

    def __str__(self) -> str:
        """Return the message for display."""
        return self.message


class QueueStatus(Enum):
    """Status of a URL in the queue history."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class QueueEntry:
    """A URL in the queue with its processing status.

    Attributes:
        url: The URL being tracked
        status: Current processing status
        source_url: The URL where this link was found (None for start URL)
    """
    url: str
    status: QueueStatus
    source_url: Optional[str] = None


@dataclass
class CrawlStats:
    """Real-time statistics for monitoring crawl progress.

    This object is designed to be shared between the crawler and a future TUI.
    All fields are updated by the crawler during execution.
    """

    start_time: float = field(default_factory=time.time)
    pause_time: float = 0.0
    pause_start: Optional[float] = None
    pages_processed: int = 0
    files_saved: int = 0
    error_count: int = 0
    warn_count: int = 0
    duplicates_skipped: int = 0
    queue_size: int = 0
    current_url: Optional[str] = None
    last_error: Optional[str] = None
    error_logs: List[LogEntry] = field(default_factory=list)
    warn_logs: List[LogEntry] = field(default_factory=list)
    main_logs: List[LogEntry] = field(default_factory=list)
    log_entries: List[LogEntry] = field(default_factory=list)
    paused: bool = False
    stop_requested: bool = False
    completed: bool = False
    completion_time: Optional[float] = None
    crawler_error: Optional[str] = None
    logs_removed: int = 0
    queue_history: List[QueueEntry] = field(default_factory=list)
    processing_index: int = -1
    queue_sample: List[str] = field(default_factory=list)
    crawler: Optional["DocsCrawler"] = field(default=None, repr=False)
    in_flight: List[str] = field(default_factory=list)

    def add_log(self, log_type: LogType, message: str, url: Optional[str] = None, source_url: Optional[str] = None, max_lines: int = 0) -> None:
        """Add a typed log entry with optional rolling window.

        Args:
            log_type: Type classification of this log entry
            message: Log message to add
            url: Optional URL associated with this entry
            source_url: Optional URL where this link was found (for errors)
            max_lines: Maximum buffer size. 0 = unlimited, >0 = rolling buffer

        Tracks removed logs so viewport stabilization can compensate.
        Routes entries to categorized lists for O(1) filtering.
        """
        entry = LogEntry(type=log_type, message=message, url=url, source_url=source_url)

        if log_type == LogType.ERROR:
            # Note: error_count is incremented by crawler before logging
            self.error_logs.append(entry)
            if max_lines > 0 and len(self.error_logs) > max_lines:
                self.error_logs.pop(0)
                self.logs_removed += 1
        elif log_type == LogType.WARN:
            self.warn_count += 1
            self.warn_logs.append(entry)
            # Keep warnings within max_lines limit (same as errors)
            if max_lines > 0 and len(self.warn_logs) > max_lines:
                self.warn_logs.pop(0)
                self.logs_removed += 1
        elif log_type in {LogType.FETCH, LogType.SAVE, LogType.SKIP, LogType.INFO}:
            self.main_logs.append(entry)
            if max_lines > 0 and len(self.main_logs) > max_lines:
                self.main_logs.pop(0)
                self.logs_removed += 1

        self.log_entries.append(entry)
        if max_lines > 0 and len(self.log_entries) > max_lines:
            self.log_entries.pop(0)

    def get_elapsed_time(self) -> float:
        """Get elapsed time excluding paused periods.

        Returns:
            Elapsed time in seconds, not counting time spent paused.
            Timer freezes when crawl completes.
        """
        # Use completion_time if crawl is done, otherwise current time
        end_time = self.completion_time if self.completion_time else time.time()
        elapsed = end_time - self.start_time - self.pause_time
        if self.pause_start is not None:
            elapsed -= (end_time - self.pause_start)
        return max(0.0, elapsed)

    def mark_crawl_finished(self) -> None:
        """Mark crawl as finished and freeze the timer."""
        if not self.completed:
            self.completed = True
            self.completion_time = time.time()

    def mark_processing(self, url: str) -> None:
        """Mark a URL as currently processing and cache its index.

        Args:
            url: URL to mark as processing

        Optimized to track processing_index for O(1) TUI access.
        """
        for i, entry in enumerate(self.queue_history):
            if entry.url == url and entry.status == QueueStatus.QUEUED:
                entry.status = QueueStatus.PROCESSING
                self.processing_index = i
                break

    def mark_completed(self, url: str, success: bool, skipped: bool = False) -> None:
        """Mark currently processing URL as completed, skipped, or error.

        Args:
            url: URL that finished processing
            success: True if successful, False if error
            skipped: True if URL was skipped (bypassed without saving)

        Uses cached processing_index for O(1) update.
        """
        if self.processing_index >= 0 and self.processing_index < len(self.queue_history):
            entry = self.queue_history[self.processing_index]
            if entry.url == url and entry.status == QueueStatus.PROCESSING:
                if not success:
                    entry.status = QueueStatus.ERROR
                elif skipped:
                    entry.status = QueueStatus.SKIPPED
                else:
                    entry.status = QueueStatus.COMPLETED
                self.processing_index = -1


ASSET_EXTENSIONS = frozenset(
    [
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".svg",
        ".ico",
        ".webp",
        ".avif",
        ".js",
        ".css",
        ".pdf",
        ".zip",
        ".woff",
        ".woff2",
        ".ttf",
        ".eot",
        ".mp3",
        ".mp4",
        ".webm",
        ".ogg",
        ".xml",
        ".json",
        ".rss",
        ".atom",
    ]
)


class DocsCrawler:
    """
    Documentation website crawler that converts pages to Markdown.

    Attributes:
        config: Configuration object with crawl settings.
        base_url: Base URL for the documentation site.
        base_host: Hostname extracted from base_url.
        output_dir: Directory to write Markdown files.
        visited: Set of normalized URLs already processed.
        queue: Queue of URLs to process.
        session: Requests session for HTTP calls.
    """

    config: Config
    start_url: str
    base_url: str
    base_host: str
    output_dir: Path
    restrict_prefix: Optional[str]
    visited: Set[str]
    queue: Deque[str]
    pages_processed: int
    session: requests.Session
    stats: CrawlStats
    _seen_hashes: Dict[str, Path]

    def __init__(self, config: Config) -> None:
        """
        Initialize the crawler with configuration.

        Args:
            config: Configuration object with all settings.

        Raises:
            ValueError: If start_url is not provided in config.
        """
        if not config.start_url:
            raise ValueError("start_url is required")

        self.config = config
        self.start_url = self._normalize_url(config.start_url)

        if config.base_url:
            self.base_url = self._normalize_url(config.base_url)
        else:
            parsed = urlparse(self.start_url)
            self.base_url = f"{parsed.scheme}://{parsed.netloc}"

        self.base_host = urlparse(self.base_url).netloc
        self.output_dir = Path(config.output)

        self.restrict_prefix: Optional[str] = None
        if config.restrict_prefix:
            prefix = config.restrict_prefix.strip()
            if not prefix.startswith("/"):
                prefix = "/" + prefix
            self.restrict_prefix = prefix

        self.visited: Set[str] = set()
        self.queue: Deque[str] = deque()
        self.pages_processed = 0

        self.stats = CrawlStats()
        self.stats.crawler = self  # Allow TUI to access crawler for config updates
        self._seen_hashes: Dict[str, Path] = {}
        self._skip_counts: Dict[str, int] = {}  # Track repeated skips per URL
        self._skip_log_threshold = 3  # Suppress skip logs after this many repeats

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": config.user_agent,
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
                ),
                "Accept-Language": "en-US,en;q=0.5",
            }
        )

    def _get_source_url(self, url: str) -> Optional[str]:
        """Look up the source URL for a given URL from queue history.

        Args:
            url: The URL to look up

        Returns:
            The source URL where this link was found, or None if not found
        """
        for entry in self.stats.queue_history:
            if entry.url == url:
                return entry.source_url
        return None

    def _log(self, log_type: LogType, message: str, url: Optional[str] = None, source_url: Optional[str] = None, force: bool = False) -> None:
        """Log a typed message to stats and optionally print to stdout.

        Args:
            log_type: Classification of this log entry
            message: Log message text
            url: Optional URL associated with this entry
            source_url: Optional URL where this link was found (for errors)
            force: Force print even if not verbose
        """
        # Suppress repeated skip messages for the same URL
        if log_type == LogType.SKIP and url:
            self._skip_counts[url] = self._skip_counts.get(url, 0) + 1
            count = self._skip_counts[url]
            if count == self._skip_log_threshold:
                # Log a warning that we're suppressing this URL
                # Extract just the path for cleaner display
                parsed = urlparse(url)
                short_url = parsed.path or url
                self.stats.add_log(
                    LogType.WARN,
                    f"Suppressing repeated skips: {short_url}",
                    url=url,
                    max_lines=self.config.max_log_lines
                )
            if count >= self._skip_log_threshold:
                return  # Don't log this skip - already warned about it

        self.stats.add_log(log_type, message, url, source_url=source_url, max_lines=self.config.max_log_lines)
        if self.config.verbose or force:
            print(message, file=sys.stderr)

    def _normalize_url(self, url: str) -> str:
        """
        Normalize a URL for consistent comparison and storage.

        - Removes fragment identifiers
        - Preserves query parameters

        Args:
            url: URL to normalize.

        Returns:
            Normalized URL string.
        """
        url, _ = urldefrag(url)

        parsed = urlparse(url)

        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if parsed.query:
            normalized += f"?{parsed.query}"

        return normalized

    def is_internal_doc_link(self, href: str, current_url: str) -> Optional[str]:
        """
        Check if a link is an internal documentation link that should be followed.

        Args:
            href: The href attribute value from an anchor tag.
            current_url: The URL of the page containing this link.

        Returns:
            Normalized absolute URL if internal and should be followed, None otherwise.
        """
        if not href:
            return None

        href = href.strip()

        if href.startswith(("mailto:", "tel:", "javascript:", "data:")):
            return None

        if href.startswith("#"):
            return None

        absolute_url = urljoin(current_url, href)

        normalized = self._normalize_url(absolute_url)

        parsed = urlparse(normalized)

        if parsed.netloc != self.base_host:
            return None

        path_lower = parsed.path.lower()
        for ext in ASSET_EXTENSIONS:
            if path_lower.endswith(ext):
                self._log(LogType.SKIP, f"  Skipped: {normalized} (asset)", url=normalized)
                return None

        if self.restrict_prefix:
            if not parsed.path.startswith(self.restrict_prefix):
                self._log(LogType.SKIP, f"  Skipped: {normalized} (prefix)", url=normalized)
                return None

        if self.config.exclude_patterns:
            for pattern in self.config.exclude_patterns:
                if fnmatch(parsed.path, pattern):
                    self._log(LogType.SKIP, f"  Skipped: {normalized} (excluded)", url=normalized)
                    return None
                if fnmatch(normalized, pattern):
                    self._log(LogType.SKIP, f"  Skipped: {normalized} (excluded)", url=normalized)
                    return None

        return normalized

    def url_to_filepath(self, url: str) -> Path:
        """
        Convert a URL to a local file path under the output directory.

        Mapping rules:
        - https://example.com/ -> OUTPUT/index.md
        - https://example.com/tutorial/ -> OUTPUT/tutorial.md
        - https://example.com/tutorial/intro/ -> OUTPUT/tutorial/intro.md
        - https://example.com/page -> OUTPUT/page.md

        Args:
            url: The URL to convert.

        Returns:
            Path object for the output Markdown file.

        Raises:
            ValueError: If path traversal is detected.
        """
        parsed = urlparse(url)
        path = parsed.path

        if path.startswith("/"):
            path = path[1:]

        if path.endswith("/"):
            path = path[:-1]

        if not path:
            return self.output_dir / "index.md"

        segments = path.split("/")
        safe_segments = [
            s for s in segments if s and s not in (".", "..") and not s.startswith(".")
        ]

        if not safe_segments:
            raise ValueError(f"Invalid path after sanitization: {url}")

        if len(safe_segments) == 1:
            output_path = self.output_dir / f"{safe_segments[0]}.md"
        else:
            dir_path = self.output_dir / "/".join(safe_segments[:-1])
            output_path = dir_path / f"{safe_segments[-1]}.md"

        try:
            resolved_output = output_path.resolve()
            resolved_base = self.output_dir.resolve()
            resolved_output.relative_to(resolved_base)
        except (ValueError, RuntimeError):
            raise ValueError(f"Path traversal detected: {url}")

        return output_path

    def extract_main_html(self, soup: BeautifulSoup) -> Union[BeautifulSoup, Tag]:
        """
        Extract the main content element from an HTML document.

        Preference order:
        1. <main> element
        2. Element with role="main"
        3. <article> element
        4. <body> element
        5. Entire document (fallback)

        Also removes nav, header, footer, aside elements from the extracted content.

        Args:
            soup: Parsed BeautifulSoup document.

        Returns:
            BeautifulSoup or Tag object containing just the main content.
        """
        main_element = None

        main_element = soup.find("main")

        if not main_element:
            main_element = soup.find(attrs={"role": "main"})

        if not main_element:
            main_element = soup.find("article")

        if not main_element:
            main_element = soup.find("body")

        if not main_element:
            main_element = soup

        from copy import deepcopy

        content = deepcopy(main_element)

        for tag in content.find_all(["nav", "header", "footer", "aside"]):
            tag.decompose()

        for element in content.find_all(
            attrs={"role": ["navigation", "banner", "contentinfo", "complementary"]}
        ):
            element.decompose()

        return content

    def clean_markdown(self, md: str) -> str:
        """
        Clean up generated Markdown text.

        - Collapses more than 2 consecutive newlines to 2
        - Trims leading/trailing whitespace

        Args:
            md: Raw Markdown string.

        Returns:
            Cleaned Markdown string.
        """
        md = re.sub(r"\n{3,}", "\n\n", md)

        md = md.strip()

        return md

    def extract_title(self, soup: BeautifulSoup, url: str) -> str:
        """
        Extract a page title from HTML or derive from URL.

        Rules:
        1. Prefer <title> tag content
        2. If title contains " | ", strip the suffix (site name)
        3. Fallback to deriving from URL path slug

        Args:
            soup: Parsed HTML document.
            url: Page URL for fallback derivation.

        Returns:
            Extracted or derived title string.
        """
        title_tag = soup.find("title")

        if title_tag and title_tag.string:
            title = title_tag.string.strip()

            if " | " in title:
                title = title.split(" | ")[0].strip()

            if title:
                return title

        parsed = urlparse(url)
        path = parsed.path.strip("/")

        if not path:
            return "Home"

        segments = path.split("/")
        slug = segments[-1] if segments else "index"

        title = slug.replace("-", " ").replace("_", " ").title()

        return title

    def build_frontmatter(self, title: str, url: str) -> str:
        """
        Build YAML frontmatter block for a Markdown file.

        Args:
            title: Page title.
            url: Source URL.

        Returns:
            YAML frontmatter string including --- delimiters.
        """
        escaped_title = title.replace('"', '\\"')

        lines = [
            "---",
            f'title: "{escaped_title}"',
            f"source: {url}",
            f"created: {date.today().isoformat()}",
        ]

        if self.config.tags:
            lines.append("tags:")
            for tag in self.config.tags:
                lines.append(f"  - {tag}")

        lines.append("---")
        lines.append("")

        return "\n".join(lines)

    def _extract_markdown_body(self, full_content: str) -> str:
        """
        Extract markdown body content, excluding YAML frontmatter.

        Args:
            full_content: Complete markdown content with optional frontmatter.

        Returns:
            Just the body portion (without frontmatter), stripped.
        """
        if not full_content.startswith("---"):
            return full_content.strip()

        lines = full_content.split("\n")
        if len(lines) < 3:
            return full_content.strip()

        closing_index = None
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                closing_index = i
                break

        if closing_index is None:
            return full_content.strip()

        body_lines = lines[closing_index + 1 :]
        return "\n".join(body_lines).strip()

    def fetch_and_save(self, url: str) -> Tuple[List[str], bool, bool]:
        """
        Fetch a page, convert to Markdown, save to file, and extract links.

        Args:
            url: URL to fetch and process.

        Returns:
            Tuple of (list of internal link URLs found, success flag, skipped flag).
            skipped=True means URL was processed but not saved (e.g., non-HTML, dedupe).
        """
        self.stats.current_url = url
        self.stats.in_flight = [url]
        self._log(LogType.FETCH, f"Fetching: {url}", url=url)

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            source = self._get_source_url(url)
            self._log(LogType.ERROR, f"TIME: {url}", url=url, source_url=source, force=True)
            self.stats.error_count += 1
            self.stats.last_error = "Timeout"
            return [], False, False
        except requests.exceptions.ConnectionError as e:
            source = self._get_source_url(url)
            self._log(LogType.ERROR, f"CONN: {url}", url=url, source_url=source, force=True)
            self.stats.error_count += 1
            self.stats.last_error = "Connection error"
            return [], False, False
        except requests.exceptions.HTTPError as e:
            if hasattr(e, 'response') and e.response is not None:
                status_code = getattr(e.response, 'status_code', 'HTTP')
            else:
                status_code = 'HTTP'
            source = self._get_source_url(url)
            self._log(LogType.ERROR, f"{status_code}: {url}", url=url, source_url=source, force=True)
            self.stats.error_count += 1
            self.stats.last_error = f"HTTP {status_code}"
            return [], False, False
        except requests.RequestException as e:
            error_type = type(e).__name__.replace("Error", "").replace("Exception", "").upper()
            if not error_type:
                error_type = "REQ"
            source = self._get_source_url(url)
            self._log(LogType.ERROR, f"{error_type}: {url}", url=url, source_url=source, force=True)
            self.stats.error_count += 1
            self.stats.last_error = str(e)
            return [], False, False

        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type and "application/xhtml" not in content_type:
            self._log(LogType.SKIP, f"  Skipped: {url}", url=url)
            return [], True, True  # skipped: non-HTML content

        soup = BeautifulSoup(response.text, "html.parser")

        # Use final URL after redirects for correct relative link resolution
        # (servers often redirect /path to /path/ and relative hrefs expect the latter)
        resolved_url = response.url

        title = self.extract_title(soup, resolved_url)

        main_content = self.extract_main_html(soup)

        md = markdownify(str(main_content), heading_style="ATX")
        md = self.clean_markdown(md)

        if not self.config.no_frontmatter:
            frontmatter = self.build_frontmatter(title, url)
            full_content = frontmatter + md
        else:
            full_content = md

        output_path = self.url_to_filepath(url)

        if self.config.dedupe:
            # Dedupe compares markdown body only, ignoring frontmatter
            # (timestamps/metadata vary even for identical content)
            markdown_body = self._extract_markdown_body(full_content)
            digest = sha256(markdown_body.encode("utf-8")).hexdigest()

            if digest in self._seen_hashes:
                existing_path = self._seen_hashes[digest]
                self.stats.duplicates_skipped += 1
                self._log(LogType.SKIP, f"  Skipped: {url} (dupe)", url=url)

                links = []
                for anchor in soup.find_all("a", href=True):
                    href_attr = anchor["href"]
                    href = href_attr if isinstance(href_attr, str) else str(href_attr)
                    internal_url = self.is_internal_doc_link(href, resolved_url)
                    if internal_url:
                        links.append(internal_url)

                return links, True, True  # skipped: duplicate content
            else:
                self._seen_hashes[digest] = output_path

        output_path.parent.mkdir(parents=True, exist_ok=True)

        output_path.write_text(full_content, encoding="utf-8")
        self._log(LogType.SAVE, f"  Saved: {output_path}", url=url)
        self.stats.files_saved += 1

        links = []
        for anchor in soup.find_all("a", href=True):
            href_attr = anchor["href"]
            href = href_attr if isinstance(href_attr, str) else str(href_attr)
            internal_url = self.is_internal_doc_link(href, resolved_url)
            if internal_url:
                links.append(internal_url)

        return links, True, False  # not skipped: actually saved

    def crawl(self) -> Tuple[int, bool]:
        """
        Execute the BFS crawl starting from the configured start URL.

        Returns:
            Tuple of (number of pages successfully processed, start URL success flag).
        """
        try:
            return self._crawl_impl()
        except Exception as e:
            import traceback

            self.stats.crawler_error = traceback.format_exc()
            self._log(LogType.ERROR, f"FATAL ERROR: {e}", force=True)
            raise

    def _crawl_impl(self) -> Tuple[int, bool]:
        """Internal crawl implementation with pause/stop support."""
        self.queue.append(self.start_url)
        self.visited.add(self.start_url)
        self.stats.queue_size = len(self.queue)

        self.stats.queue_history.append(QueueEntry(self.start_url, QueueStatus.QUEUED, source_url=None))

        print(f"Starting crawl from: {self.start_url}", file=sys.stderr)
        print(f"Base URL: {self.base_url}", file=sys.stderr)
        print(f"Output directory: {self.output_dir}", file=sys.stderr)
        if self.restrict_prefix:
            print(f"Restricting to prefix: {self.restrict_prefix}", file=sys.stderr)
        if self.config.exclude_patterns:
            print(f"Excluding patterns: {', '.join(self.config.exclude_patterns)}", file=sys.stderr)
        print("", file=sys.stderr)

        start_url_success = False
        first_page = True

        while self.queue:
            while self.stats.paused:
                time.sleep(0.1)
                if self.stats.stop_requested:
                    self._log(LogType.INFO, "Crawl stopped by user", force=True)
                    return self.pages_processed, start_url_success

            if self.stats.stop_requested:
                self._log(LogType.INFO, "Crawl stopped by user", force=True)
                return self.pages_processed, start_url_success

            if self.config.max_pages and self.pages_processed >= self.config.max_pages:
                print(
                    f"\nReached max pages limit ({self.config.max_pages})",
                    file=sys.stderr,
                )
                break

            url = self.queue.popleft()
            self.stats.queue_size = len(self.queue)

            self.stats.queue_sample = list(self.queue)

            self.stats.mark_processing(url)

            new_links, success, skipped = self.fetch_and_save(url)

            self.stats.mark_completed(url, success, skipped=skipped)

            if first_page:
                start_url_success = success
                first_page = False

            if success:
                self.pages_processed += 1
                self.stats.pages_processed = self.pages_processed

            self.stats.in_flight = []

            for link in new_links:
                if link not in self.visited:
                    self.visited.add(link)
                    self.queue.append(link)
                    self.stats.queue_size = len(self.queue)
                    self._log(LogType.QUEUE, f"  Queued: {link}", url=link)
                    self.stats.queue_history.append(QueueEntry(link, QueueStatus.QUEUED, source_url=url))

            if self.config.delay > 0 and self.queue:
                time.sleep(self.config.delay)

        print(
            f"\nCrawl complete. Processed {self.pages_processed} pages.",
            file=sys.stderr,
        )
        return self.pages_processed, start_url_success
