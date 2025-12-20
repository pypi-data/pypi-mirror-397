"""
Command-line interface for crawl2md.

Provides the main entry point and argument parsing for the crawl2md tool.
"""

import argparse
import sys
from typing import List, Optional

from . import __version__
from .config import resolve_config
from .crawler import DocsCrawler


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.

    Args:
        args: Command-line arguments to parse. If None, uses sys.argv[1:].

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        prog="crawl2md",
        description="Crawl documentation websites and convert to Markdown files.",
        epilog="For more information, see the man page: man crawl2md",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-s",
        "--start",
        metavar="URL",
        dest="start_url",
        help="Starting URL to crawl (required unless set via config/env)",
    )

    parser.add_argument(
        "-b",
        "--base",
        metavar="BASE_URL",
        dest="base_url",
        help="Base URL to constrain crawling. If omitted, derived from --start.",
    )

    parser.add_argument(
        "-o",
        "--output",
        metavar="DIR",
        help="Output directory for Markdown files (default: docs-md)",
    )

    parser.add_argument(
        "-t",
        "--tags",
        metavar="TAG",
        nargs="+",
        help="Tags to include in YAML frontmatter",
    )

    parser.add_argument(
        "-p",
        "--restrict-prefix",
        metavar="PREFIX",
        dest="restrict_prefix",
        help="Only crawl URLs whose path starts with this prefix (e.g., /tutorial)",
    )

    parser.add_argument(
        "-e",
        "--exclude-patterns",
        metavar="PATTERN",
        nargs="+",
        dest="exclude_patterns",
        help="Exclude URLs matching these patterns (supports wildcards: *.php, /admin/*, etc.)",
    )

    parser.add_argument(
        "-d",
        "--delay",
        metavar="SECONDS",
        type=float,
        help="Delay between HTTP requests (default: 0.3)",
    )

    parser.add_argument(
        "-m",
        "--max-pages",
        metavar="N",
        dest="max_pages",
        type=int,
        help="Maximum number of pages to process",
    )

    parser.add_argument(
        "--no-frontmatter",
        dest="no_frontmatter",
        action="store_true",
        default=None,
        help="Disable YAML frontmatter in output files",
    )

    parser.add_argument(
        "--user-agent",
        metavar="STRING",
        dest="user_agent",
        help="Custom User-Agent header for HTTP requests",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=None,
        help="Enable verbose logging to stderr",
    )

    parser.add_argument(
        "--no-tui",
        dest="no_tui",
        action="store_true",
        help="Disable TUI, use plain terminal output instead (TUI is default)",
    )

    parser.add_argument(
        "--dedupe",
        action="store_true",
        default=None,
        help="Enable content deduplication to skip pages with identical markdown body (ignores frontmatter differences)",
    )

    parser.add_argument(
        "--scroll-lines",
        metavar="N",
        type=int,
        dest="scroll_lines",
        help="Number of lines to scroll per keypress in TUI (default: auto = half-page)",
    )

    parser.add_argument(
        "--max-log-lines",
        metavar="N",
        type=int,
        dest="max_log_lines",
        help="Maximum log buffer size in TUI (default: 0 = unlimited)",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"crawl2md {__version__}",
    )

    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the crawl2md CLI.

    Args:
        args: Command-line arguments. If None, uses sys.argv[1:].

    Returns:
        Exit code (0 for success, 1 for error).
    """
    parsed = parse_args(args)

    cli_args = {
        "start_url": parsed.start_url,
        "base_url": parsed.base_url,
        "output": parsed.output,
        "tags": parsed.tags if parsed.tags else [],
        "restrict_prefix": parsed.restrict_prefix,
        "exclude_patterns": parsed.exclude_patterns if parsed.exclude_patterns else [],
        "delay": parsed.delay,
        "max_pages": parsed.max_pages,
        "no_frontmatter": parsed.no_frontmatter,
        "user_agent": parsed.user_agent,
        "verbose": parsed.verbose,
        "no_tui": parsed.no_tui,
        "dedupe": parsed.dedupe,
        "scroll_lines": parsed.scroll_lines,
        "max_log_lines": parsed.max_log_lines,
    }

    config = resolve_config(cli_args)

    if config.scroll_lines < 0:
        config.scroll_lines = 0
    if config.max_log_lines < 0:
        config.max_log_lines = 0

    # Handle no-args launch: show config form if TUI enabled and no start_url
    if not config.start_url:
        if config.no_tui:
            # Plain CLI mode requires start_url
            print(
                "Error: Starting URL is required. "
                "Provide via --start, CRAWL2MD_START_URL, or config file.",
                file=sys.stderr,
            )
            return 1
        else:
            # TUI mode: show config form
            from .tui import run_config_tui

            new_config = run_config_tui(config)
            if new_config is None:
                # User cancelled
                return 0
            if not new_config.start_url:
                # Form submitted but still no URL (shouldn't happen, but be safe)
                print("Error: No start URL provided.", file=sys.stderr)
                return 1
            config = new_config

            # Small delay to allow terminal to reset after config TUI exits
            import time
            time.sleep(0.05)

    try:
        crawler = DocsCrawler(config)

        if not config.no_tui:
            import threading

            from .tui import run_tui

            crawler_thread = threading.Thread(
                target=lambda: crawler.crawl(), daemon=True
            )
            crawler_thread.start()

            run_tui(config, crawler.stats, crawler_thread)

            crawler_thread.join(timeout=1.0)

            if crawler.stats.crawler_error:
                return 1

            if crawler.pages_processed == 0:
                print("Warning: No pages were processed.", file=sys.stderr)
                return 1

            return 0

        else:
            pages, start_url_success = crawler.crawl()

            if not start_url_success:
                return 1

            if pages == 0:
                print("Warning: No pages were processed.", file=sys.stderr)
                return 1

            return 0

    except KeyboardInterrupt:
        print("\nCrawl interrupted by user.", file=sys.stderr)
        return 130

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if config.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
