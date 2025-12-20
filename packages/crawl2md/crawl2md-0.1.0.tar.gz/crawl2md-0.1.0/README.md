# crawl2md

Crawl documentation websites and convert them to Markdown files.

`crawl2md` is a command-line tool that:

- Crawls documentation websites using breadth-first search
- Extracts the main content from each page
- Converts HTML to clean Markdown
- Adds optional Obsidian-compatible YAML frontmatter
- Mirrors the URL structure as a local directory tree

## Installation

### Using pip

```bash
pip install .
```

### Using pipx (recommended for CLI tools)

```bash
pipx install .
```

### Development install

```bash
make dev-install
# or
pip install -e .
```

### Installing the man page

```bash
sudo make man-install
```

## Quick Start

Crawl an entire documentation site:

```bash
crawl2md -s https://docs.example.com/
```

Crawl only a specific section:

```bash
crawl2md -s https://docs.example.com/tutorial/ -p /tutorial
```

Crawl with custom output directory and tags:

```bash
crawl2md -s https://docs.example.com/ -o my-docs -t docs reference
```

Crawl with plain output (disables default TUI):

```bash
crawl2md -s https://docs.example.com/ --no-tui
```

Crawl with deduplication to skip duplicate content:

```bash
crawl2md -s https://docs.example.com/ --dedupe
```

## Usage

```
crawl2md [options]

Options:
  -s, --start URL           Starting URL to crawl (required)
  -b, --base BASE_URL       Base URL to constrain crawling
  -o, --output DIR          Output directory (default: docs-md)
  -t, --tags TAG [TAG ...]  Tags for YAML frontmatter
  -p, --restrict-prefix PREFIX  Only crawl paths starting with PREFIX
  -e, --exclude-patterns PATTERN [...]  Exclude URLs matching patterns
  -d, --delay SECONDS       Delay between requests (default: 0.3)
  -m, --max-pages N         Maximum pages to process
  --no-frontmatter          Disable YAML frontmatter
  --user-agent STRING       Custom User-Agent header
  -v, --verbose             Enable verbose logging
  --no-tui                  Disable TUI, use plain output (TUI is default)
  --dedupe                  Enable content deduplication
  --scroll-lines N          Lines to scroll per keypress in TUI (default: auto)
  --max-log-lines N         Maximum log buffer size in TUI (default: unlimited)
  --version                 Show version and exit
```

## Output Format

### Directory Structure

URLs are mapped to local files:

| URL | File |
|-----|------|
| `https://example.com/` | `docs-md/index.md` |
| `https://example.com/intro/` | `docs-md/intro.md` |
| `https://example.com/guide/` | `docs-md/guide/index.md` |
| `https://example.com/guide/api/` | `docs-md/guide/api.md` |

### YAML Frontmatter

By default, each file includes Obsidian-compatible frontmatter:

```yaml
---
title: "Page Title"
source: https://example.com/page/
created: 2025-12-01
tags:
  - docs
  - tutorial
---
```

Use `--no-frontmatter` to disable this.

## Interactive TUI Mode

The curses-based TUI provides real-time monitoring and control for long-running crawls.
TUI mode is enabled by default; use `--no-tui` for plain output.

### TUI Features

**Real-time Statistics:**
- Pages processed, files saved, duplicates skipped, errors
- Current URL being crawled
- Queue size and elapsed time
- Current crawl speed (delay between requests)

**Interactive Controls:**

| Key | Action | Description |
|-----|--------|-------------|
| `q` | Quit | Stop crawl and exit |
| `p` | Pause/Resume | Pause or resume the crawl |
| `h` | Help | Toggle help overlay with all controls |
| `m` | Menu | Open mid-crawl configuration menu |
| `c` | Center | Re-center queue view on current item |
| `u` | URL Toggle | Switch between path-only and full URL display |
| `↑/↓` | Scroll | Scroll log window up/down by one line |
| `PgUp/PgDn` | Page Scroll | Scroll log window by half page |
| `Home/End` | Jump | Jump to oldest/newest logs |
| `Esc` | Close | Close help overlay or config menu |

**Mouse Support:**
- Scroll wheel to scroll log window

**Adaptive Layout:**
- Works on terminals as small as 1 line (graceful degradation)
- Automatically adjusts panel visibility based on terminal size
- Shows warning when terminal is too small for full view
- Handles terminal resize without crashes

**Error Handling:**
- Terminal always restored on exit (even on crashes)
- Crawler errors displayed in overlay panel
- Clean exit with 'q' even in error state

### TUI Screenshot

```
[⠋] Pages: 1234 | Saved: 1180 | Dups: 54 | Errors: 0 | Queue: 23 | Elapsed: 05:32 | Speed: 0.5s
Current: ...example.com/docs/advanced/configuration#authentication
Fetching: https://example.com/docs/setup
  Saved: docs-md/setup.md
  Queued: https://example.com/docs/install
Fetching: https://example.com/docs/install
  DUPLICATE body: https://example.com/docs/install → same as docs-md/setup.md
q:quit  p:pause  c:center  u:url  m:menu  ↑/↓:scroll  h:help
```

### Troubleshooting TUI

**Terminal Issues:**
- If terminal appears broken after crash, run: `reset`
- Ensure terminal supports Unicode (for spinner animation)
- Minimum terminal size: 1 line (but 10+ lines recommended for full view)

**Performance:**
- TUI updates at ~10 Hz (every 100ms)
- No significant overhead on crawler performance
- Safe to use on long-running crawls (hours+)

## Content Deduplication

Skip saving duplicate content to avoid redundant files:

```bash
crawl2md -s https://docs.example.com/ --dedupe
```

**How it works:**
- Computes SHA256 hash of markdown body (excluding frontmatter)
- First occurrence is saved normally
- Subsequent pages with identical content are skipped
- Duplicates counter incremented in stats/logs

**Use cases:**
- Documentation sites with mirrors/aliases
- Sites with "print" versions of pages
- Multi-language sites with untranslated pages

## Configuration

Configuration can be provided via:

1. **CLI arguments** (highest priority)
2. **Environment variables**
3. **Config file** (`crawl2md.toml`)
4. **Built-in defaults** (lowest priority)

### Config File

Create `crawl2md.toml` in your working directory or `~/.config/crawl2md/`:

```toml
[crawl2md]
start_url = "https://docs.example.com/"
output = "my-docs"
tags = ["docs", "reference"]
delay = 0.5
verbose = true
no_tui = false
dedupe = true
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `CRAWL2MD_START_URL` | Starting URL |
| `CRAWL2MD_BASE_URL` | Base URL constraint |
| `CRAWL2MD_OUTPUT` | Output directory |
| `CRAWL2MD_TAGS` | Comma-separated tags |
| `CRAWL2MD_RESTRICT_PREFIX` | Path prefix filter |
| `CRAWL2MD_EXCLUDE_PATTERNS` | Comma-separated URL exclusion patterns |
| `CRAWL2MD_DELAY` | Request delay (seconds) |
| `CRAWL2MD_MAX_PAGES` | Max pages to process |
| `CRAWL2MD_NO_FRONTMATTER` | Disable frontmatter ("1" or "true") |
| `CRAWL2MD_USER_AGENT` | Custom User-Agent |
| `CRAWL2MD_VERBOSE` | Enable verbose mode ("1" or "true") |
| `CRAWL2MD_NO_TUI` | Disable TUI ("1" or "true") |
| `CRAWL2MD_DEDUPE` | Enable deduplication ("1" or "true") |
| `CRAWL2MD_SCROLL_LINES` | Lines to scroll per keypress in TUI |
| `CRAWL2MD_MAX_LOG_LINES` | Maximum log buffer size in TUI |

## Development

Install dev dependencies:

```bash
pip install -e ".[dev]"
```

Run checks:

- `make format` - Format code with Black
- `make lint` - Lint with Ruff
- `make typecheck` - Type check with mypy
- `make test` - Run tests with pytest (tests are in `tests/`)
- `make check` - Run all checks (format check, lint, typecheck)

## Requirements

- Python 3.9+
- requests
- beautifulsoup4
- markdownify
- tomli (Python < 3.11 only)

## Limitations

- Designed for static HTML documentation sites
- Does not execute JavaScript (no headless browser)
- Does not download images or rewrite internal links

## License

MIT
