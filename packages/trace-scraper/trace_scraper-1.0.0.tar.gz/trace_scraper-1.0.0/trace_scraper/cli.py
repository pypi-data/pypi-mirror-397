"""Command-line interface for the web scraper."""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

from .models import Document
from .scraper import ScrapeMode, ScraperConfig, WebScraper


def setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def document_to_dict(doc: Document) -> dict:
    """Convert Document to JSON-serializable dict."""
    return {
        "id": doc.id,
        "title": doc.semantic_identifier,
        "source": doc.source,
        "text": doc.sections[0].text if doc.sections else "",
        "url": doc.sections[0].link if doc.sections else doc.id,
        "metadata": doc.metadata,
        "updated_at": doc.doc_updated_at.isoformat() if doc.doc_updated_at else None,
    }


async def run_scraper(args: argparse.Namespace) -> list[Document]:
    """Run the scraper with given arguments."""
    config = ScraperConfig(
        max_concurrent_pages=args.concurrency,
        page_timeout=args.timeout,
        max_retries=args.retries,
        scroll_pages=args.scroll,
        use_browser_for_all=args.browser,
        headless=not args.headed,
        delay_between_requests=args.delay,
    )

    mode = ScrapeMode(args.mode)
    documents: list[Document] = []
    count = 0

    async with WebScraper(config) as scraper:
        async for doc in scraper.scrape(args.url, mode=mode):
            documents.append(doc)
            count += 1
            print(f"[{count}] Scraped: {doc.semantic_identifier} ({doc.id})")

            if args.max_pages and count >= args.max_pages:
                break

    return documents


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Trace: High-performance web scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape a single page
  trace https://example.com --mode single

  # Recursively crawl a site
  trace https://docs.example.com --mode recursive --max-pages 100

  # Parse a sitemap
  trace https://example.com/sitemap.xml --mode sitemap

  # Output to JSON file
  trace https://example.com --mode recursive -o output.json
        """,
    )

    parser.add_argument("url", help="URL to scrape (base URL, sitemap URL, or single page)")
    parser.add_argument(
        "--mode", "-m",
        choices=["single", "recursive", "sitemap"],
        default="single",
        help="Scraping mode (default: single)",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output JSON file path",
    )
    parser.add_argument(
        "--concurrency", "-c",
        type=int,
        default=10,
        help="Maximum concurrent pages (default: 10)",
    )
    parser.add_argument(
        "--timeout", "-t",
        type=float,
        default=30.0,
        help="Page timeout in seconds (default: 30)",
    )
    parser.add_argument(
        "--retries", "-r",
        type=int,
        default=3,
        help="Maximum retries per page (default: 3)",
    )
    parser.add_argument(
        "--delay", "-d",
        type=float,
        default=0.1,
        help="Delay between requests in seconds (default: 0.1)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        help="Maximum number of pages to scrape",
    )
    parser.add_argument(
        "--scroll",
        action="store_true",
        help="Scroll pages to load dynamic content",
    )
    parser.add_argument(
        "--browser",
        action="store_true",
        help="Use browser for all pages (slower but more reliable)",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run browser in headed mode (visible)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    try:
        documents = asyncio.run(run_scraper(args))

        if args.output:
            output_data = [document_to_dict(doc) for doc in documents]
            args.output.write_text(json.dumps(output_data, indent=2, ensure_ascii=False))
            print(f"\nSaved {len(documents)} documents to {args.output}")
        else:
            print(f"\nScraped {len(documents)} pages")

    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
