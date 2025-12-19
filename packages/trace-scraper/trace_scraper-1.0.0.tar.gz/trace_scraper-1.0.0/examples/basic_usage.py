#!/usr/bin/env python3
"""
Basic usage examples for Trace web scraper.

Run with: python -m examples.basic_usage
"""

import asyncio
import logging

from trace_scraper import Document, ScraperConfig, ScrapeMode, WebScraper

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


async def example_single_page():
    """Scrape a single page."""
    print("\n=== Single Page Scrape ===")

    async with WebScraper() as scraper:
        async for doc in scraper.scrape("https://example.com", mode=ScrapeMode.SINGLE):
            print(f"Title: {doc.semantic_identifier}")
            print(f"URL: {doc.id}")
            print(f"Text length: {len(doc.sections[0].text)} chars")
            print(f"Preview: {doc.sections[0].text[:200]}...")


async def example_recursive_crawl():
    """Recursively crawl a site."""
    print("\n=== Recursive Crawl ===")

    config = ScraperConfig(
        max_concurrent_pages=5,
        delay_between_requests=0.5,  # Be polite
    )

    count = 0
    async with WebScraper(config) as scraper:
        async for doc in scraper.scrape(
            "https://docs.python.org/3/library/asyncio.html",
            mode=ScrapeMode.RECURSIVE,
        ):
            count += 1
            print(f"[{count}] {doc.semantic_identifier}")

            if count >= 10:  # Limit for demo
                break

    print(f"Total pages scraped: {count}")


async def example_sitemap_scrape():
    """Scrape pages from a sitemap."""
    print("\n=== Sitemap Scrape ===")

    config = ScraperConfig(max_concurrent_pages=10)

    count = 0
    async with WebScraper(config) as scraper:
        try:
            async for doc in scraper.scrape(
                "https://www.sitemaps.org/sitemap.xml",
                mode=ScrapeMode.SITEMAP,
            ):
                count += 1
                print(f"[{count}] {doc.semantic_identifier}")

                if count >= 5:  # Limit for demo
                    break
        except ValueError as e:
            print(f"Sitemap error: {e}")

    print(f"Total pages scraped: {count}")


async def example_url_list():
    """Scrape a specific list of URLs."""
    print("\n=== URL List Scrape ===")

    urls = [
        "https://httpbin.org/html",
        "https://httpbin.org/robots.txt",
        "https://httpbin.org/headers",
    ]

    config = ScraperConfig(max_concurrent_pages=3)

    async with WebScraper(config) as scraper:
        docs = await scraper.scrape_urls(urls)
        for doc in docs:
            print(f"- {doc.semantic_identifier}: {len(doc.sections[0].text)} chars")


async def example_high_performance():
    """High-performance scraping configuration."""
    print("\n=== High Performance Config ===")

    config = ScraperConfig(
        max_concurrent_pages=20,      # More parallel pages
        max_concurrent_browsers=5,    # More browser contexts
        page_timeout=15.0,            # Shorter timeout
        request_timeout=5.0,          # Fast HTTP timeout
        delay_between_requests=0.0,   # No delay (use with caution!)
        use_browser_for_all=False,    # Use httpx where possible
        deduplicate_content=True,     # Skip duplicate content
    )

    print(f"Config: {config.max_concurrent_pages} concurrent, "
          f"{config.page_timeout}s timeout")


async def example_with_callback():
    """Using callback for real-time processing."""
    print("\n=== With Callback ===")

    results: list[Document] = []

    def on_page_scraped(doc: Document):
        results.append(doc)
        print(f"Callback received: {doc.semantic_identifier}")

    async with WebScraper() as scraper:
        async for _ in scraper.scrape(
            "https://example.com",
            mode=ScrapeMode.SINGLE,
            on_page_scraped=on_page_scraped,
        ):
            pass

    print(f"Collected {len(results)} documents via callback")


async def main():
    """Run all examples."""
    await example_single_page()
    await example_url_list()
    await example_with_callback()
    await example_high_performance()

    # These examples make more requests - uncomment to run
    # await example_recursive_crawl()
    # await example_sitemap_scrape()


if __name__ == "__main__":
    asyncio.run(main())
