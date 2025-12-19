# Trace Scraper

[![PyPI version](https://badge.fury.io/py/trace-scraper.svg)](https://pypi.org/project/trace-scraper/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/boxed-dev/trace/actions/workflows/ci.yml/badge.svg)](https://github.com/boxed-dev/trace/actions/workflows/ci.yml)

**High-performance async web scraper for Python.** Scrape JavaScript-rendered pages, crawl websites recursively, parse sitemaps, and extract clean content — all with built-in anti-bot bypass.

## Why Trace Scraper?

- **Hybrid Engine**: Uses `httpx` for fast static pages, `Playwright` for JavaScript-heavy sites
- **Anti-Bot Bypass**: Built-in detection evasion with realistic browser fingerprints
- **Async & Parallel**: Scrape hundreds of pages concurrently with asyncio
- **Multiple Modes**: Single page, recursive crawl, sitemap parsing, URL lists
- **Clean Output**: Automatic HTML cleanup, content deduplication, PDF extraction
- **Type Safe**: Full type hints with `py.typed` marker

## Installation

```bash
pip install trace-scraper
```

Install Playwright browsers (required for JS rendering):

```bash
playwright install chromium
```

## Quick Start

### Command Line

```bash
# Scrape a single page
trace https://example.com

# Crawl entire website
trace https://docs.example.com --mode recursive --max-pages 100

# Parse sitemap
trace https://example.com/sitemap.xml --mode sitemap

# Use browser for JavaScript sites
trace https://spa-website.com --browser

# Save to JSON
trace https://example.com -o output.json
```

### Python API

```python
import asyncio
from trace_scraper import WebScraper, ScrapeMode

async def main():
    async with WebScraper() as scraper:
        async for doc in scraper.scrape("https://example.com", mode=ScrapeMode.SINGLE):
            print(f"Title: {doc.semantic_identifier}")
            print(f"Content: {doc.sections[0].text}")

asyncio.run(main())
```

### Advanced Configuration

```python
from trace_scraper import WebScraper, ScraperConfig, ScrapeMode

config = ScraperConfig(
    max_concurrent_pages=20,     # Parallel scraping
    page_timeout=15.0,           # Timeout per page
    scroll_pages=True,           # Load lazy content
    extract_pdfs=True,           # Extract PDF text
    use_browser_for_all=False,   # Use httpx when possible
)

async with WebScraper(config) as scraper:
    async for doc in scraper.scrape(
        "https://docs.example.com",
        mode=ScrapeMode.RECURSIVE
    ):
        print(doc.semantic_identifier)
```

## CLI Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--mode` | `-m` | `single` | Mode: `single`, `recursive`, `sitemap` |
| `--output` | `-o` | - | Save results to JSON file |
| `--concurrency` | `-c` | `10` | Max concurrent pages |
| `--timeout` | `-t` | `30` | Page timeout (seconds) |
| `--max-pages` | - | - | Limit pages to scrape |
| `--browser` | - | - | Force browser for all pages |
| `--scroll` | - | - | Scroll to load dynamic content |
| `--delay` | `-d` | `0.1` | Delay between requests |
| `--verbose` | `-v` | - | Enable debug logging |

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_concurrent_pages` | `int` | `10` | Pages to scrape in parallel |
| `max_concurrent_browsers` | `int` | `3` | Browser contexts pool size |
| `page_timeout` | `float` | `30.0` | Page load timeout |
| `request_timeout` | `float` | `10.0` | HTTP request timeout |
| `max_retries` | `int` | `3` | Retry attempts per page |
| `delay_between_requests` | `float` | `0.1` | Rate limiting delay |
| `scroll_pages` | `bool` | `False` | Scroll for lazy-loaded content |
| `extract_pdfs` | `bool` | `True` | Extract text from PDFs |
| `deduplicate_content` | `bool` | `True` | Skip duplicate pages |
| `use_browser_for_all` | `bool` | `False` | Always use Playwright |
| `headless` | `bool` | `True` | Run browser headless |

## Features

### Scraping Modes

- **Single**: Scrape one URL
- **Recursive**: Crawl entire site following internal links
- **Sitemap**: Parse sitemap.xml and scrape all URLs
- **URL List**: Scrape a provided list of URLs

### Content Extraction

- Automatic removal of scripts, styles, navigation, footers
- Clean text extraction with structure preservation
- Link extraction with markdown formatting
- PDF text extraction (optional dependency)

### Anti-Bot Features

- Realistic browser fingerprints
- Custom User-Agent and headers
- Stealth mode scripts
- Automatic retry with browser fallback

## Development

```bash
# Clone repository
git clone https://github.com/boxed-dev/trace.git
cd trace

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check .

# Type check
mypy trace_scraper
```

## License

MIT License - see [LICENSE](LICENSE) for details.
