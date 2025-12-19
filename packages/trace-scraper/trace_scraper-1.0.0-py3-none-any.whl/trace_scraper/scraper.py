"""
High-performance async web scraper with parallel processing.

Features:
- Async/parallel scraping with configurable concurrency
- Playwright for JS-rendered pages
- httpx for fast static page fetching
- Anti-bot detection bypass
- Recursive crawling, sitemap parsing, single page modes
- PDF extraction support
- Content deduplication
- Rate limiting and retry logic
"""

import asyncio
import hashlib
import io
import ipaddress
import logging
import socket
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import AsyncIterator, Callable
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from .html_utils import clean_html
from .models import Document, ScrapedPage
from .sitemap import discover_urls_from_site, extract_urls_from_sitemap

logger = logging.getLogger(__name__)


class ScrapeMode(str, Enum):
    """Scraping mode options."""
    RECURSIVE = "recursive"  # Crawl entire site from base URL
    SINGLE = "single"        # Scrape single page only
    SITEMAP = "sitemap"      # Parse sitemap.xml for URLs
    URL_LIST = "url_list"    # Scrape provided list of URLs


@dataclass
class ScraperConfig:
    """Configuration for the web scraper."""
    # Concurrency settings
    max_concurrent_pages: int = 10
    max_concurrent_browsers: int = 3

    # Timeouts (in seconds)
    page_timeout: float = 30.0
    request_timeout: float = 10.0

    # Retry settings
    max_retries: int = 3
    retry_delay: float = 1.0

    # Rate limiting
    delay_between_requests: float = 0.1  # seconds
    respect_robots_txt: bool = False

    # Content settings
    scroll_pages: bool = False
    max_scroll_attempts: int = 10
    extract_pdfs: bool = True
    deduplicate_content: bool = True

    # URL filtering
    validate_urls: bool = True
    same_domain_only: bool = True

    # Browser settings
    headless: bool = True
    use_browser_for_all: bool = False  # Use Playwright for all pages (slower but more reliable)

    # Ignored elements/classes for HTML cleanup
    ignored_elements: list[str] = field(default_factory=lambda: [
        "script", "style", "noscript", "nav", "footer", "header"
    ])
    ignored_classes: list[str] = field(default_factory=lambda: [
        "sidebar", "nav", "footer", "header", "menu", "advertisement", "ad"
    ])


# Browser headers to mimic real browser
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

DEFAULT_HEADERS = {
    "User-Agent": DEFAULT_USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Sec-CH-UA": '"Chromium";v="120", "Google Chrome";v="120"',
    "Sec-CH-UA-Mobile": "?0",
    "Sec-CH-UA-Platform": '"macOS"',
}

PDF_MIME_TYPES = [
    "application/pdf", "application/x-pdf", "application/acrobat",
    "application/vnd.pdf", "text/pdf", "text/x-pdf",
]


def validate_url(url: str, check_global_ip: bool = True) -> None:
    """Validate URL is safe to scrape (prevents SSRF attacks)."""
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Invalid URL scheme: {parsed.scheme}")

    if not parsed.hostname:
        raise ValueError("URL must include a hostname")

    if check_global_ip:
        try:
            info = socket.getaddrinfo(parsed.hostname, None)
            for addr in info:
                ip = addr[4][0]
                if not ipaddress.ip_address(ip).is_global:
                    raise ValueError(f"Non-global IP address: {ip}")
        except socket.gaierror as e:
            raise ConnectionError(f"DNS resolution failed for {parsed.hostname}: {e}")


def is_same_site(base_url: str, candidate_url: str) -> bool:
    """Check if candidate URL is on the same site as base URL."""
    base = urlparse(base_url)
    candidate = urlparse(candidate_url)

    base_netloc = base.netloc.lower().removeprefix("www.")
    candidate_netloc = candidate.netloc.lower().removeprefix("www.")

    if base_netloc != candidate_netloc:
        return False

    base_path = (base.path or "/").rstrip("/")
    if base_path in ("", "/"):
        return True

    candidate_path = candidate.path or "/"
    return candidate_path == base_path or candidate_path.startswith(f"{base_path}/")


def ensure_valid_url(url: str) -> str:
    """Ensure URL has a scheme."""
    if "://" not in url:
        return "https://" + url
    return url


def extract_links(base_url: str, current_url: str, soup: BeautifulSoup) -> set[str]:
    """Extract internal links from page."""
    links: set[str] = set()

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        if not href:
            continue

        # Fix malformed URLs
        href = href.replace("\\", "/")

        # Handle fragments (keep hashbang URLs for SPAs)
        if "#" in href and "#!" not in href:
            href = href.split("#")[0]

        if not href:
            continue

        # Convert relative URLs to absolute
        if not urlparse(href).netloc:
            href = urljoin(current_url, href)

        # Only include same-site URLs
        if is_same_site(base_url, href):
            links.add(href)

    return links


def parse_last_modified(header: str | None) -> datetime | None:
    """Parse Last-Modified header to datetime."""
    if not header:
        return None
    try:
        return datetime.strptime(header, "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


class WebScraper:
    """High-performance async web scraper."""

    def __init__(self, config: ScraperConfig | None = None):
        self.config = config or ScraperConfig()
        self._browser: Browser | None = None
        self._contexts: list[BrowserContext] = []
        self._http_client: httpx.AsyncClient | None = None
        self._visited: set[str] = set()
        self._content_hashes: set[str] = set()
        self._semaphore: asyncio.Semaphore | None = None

    async def __aenter__(self) -> "WebScraper":
        await self._initialize()
        return self

    async def __aexit__(self, *args) -> None:
        await self._cleanup()

    async def _initialize(self) -> None:
        """Initialize browser and HTTP client."""
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent_pages)

        # Initialize HTTP client
        self._http_client = httpx.AsyncClient(
            headers=DEFAULT_HEADERS,
            follow_redirects=True,
            timeout=httpx.Timeout(self.config.request_timeout),
        )

        # Initialize Playwright browser
        playwright = await async_playwright().start()
        self._playwright = playwright

        self._browser = await playwright.chromium.launch(
            headless=self.config.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-site-isolation-trials",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
            ],
        )

        # Create browser contexts pool
        for _ in range(self.config.max_concurrent_browsers):
            context = await self._create_browser_context()
            self._contexts.append(context)

    async def _create_browser_context(self) -> BrowserContext:
        """Create a browser context with anti-detection settings."""
        if not self._browser:
            raise RuntimeError("Browser not initialized")

        context = await self._browser.new_context(
            user_agent=DEFAULT_USER_AGENT,
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2.0,
            locale="en-US",
            timezone_id="America/Los_Angeles",
            java_script_enabled=True,
            bypass_csp=True,
            ignore_https_errors=True,
        )

        # Anti-detection script
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        """)

        await context.set_extra_http_headers({
            "Accept": DEFAULT_HEADERS["Accept"],
            "Accept-Language": DEFAULT_HEADERS["Accept-Language"],
            "Sec-CH-UA": DEFAULT_HEADERS["Sec-CH-UA"],
            "Sec-CH-UA-Mobile": DEFAULT_HEADERS["Sec-CH-UA-Mobile"],
            "Sec-CH-UA-Platform": DEFAULT_HEADERS["Sec-CH-UA-Platform"],
        })

        return context

    async def _cleanup(self) -> None:
        """Cleanup resources."""
        for context in self._contexts:
            try:
                await context.close()
            except Exception:
                pass
        self._contexts.clear()

        if self._browser:
            try:
                await self._browser.close()
            except Exception:
                pass
            self._browser = None

        if hasattr(self, "_playwright"):
            try:
                await self._playwright.stop()
            except Exception:
                pass

        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    def _get_context(self) -> BrowserContext:
        """Get a browser context from the pool (round-robin)."""
        if not self._contexts:
            raise RuntimeError("No browser contexts available")
        # Simple round-robin
        context = self._contexts[0]
        self._contexts.append(self._contexts.pop(0))
        return context

    async def _scrape_with_browser(self, url: str) -> ScrapedPage | None:
        """Scrape a page using Playwright browser."""
        context = self._get_context()
        page: Page | None = None

        try:
            page = await context.new_page()

            response = await page.goto(
                url,
                timeout=int(self.config.page_timeout * 1000),
                wait_until="domcontentloaded",
            )

            if not response:
                return None

            # Handle redirects
            final_url = page.url
            if final_url != url:
                if self.config.validate_urls:
                    validate_url(final_url, check_global_ip=self.config.validate_urls)
                if final_url in self._visited:
                    return None
                self._visited.add(final_url)
                url = final_url

            # Check response status
            if response.status >= 400:
                logger.warning(f"HTTP {response.status} for {url}")
                return None

            # Scroll if configured
            if self.config.scroll_pages:
                await self._scroll_page(page)

            # Get content
            content = await page.content()
            last_modified = response.headers.get("last-modified")

            # Parse HTML
            soup = BeautifulSoup(content, "html.parser")
            parsed = clean_html(
                soup,
                ignored_elements=self.config.ignored_elements,
                ignored_classes=self.config.ignored_classes,
            )

            return ScrapedPage(
                url=url,
                title=parsed.title,
                text=parsed.cleaned_text,
                html=content,
                last_modified=parse_last_modified(last_modified),
            )

        except Exception as e:
            logger.error(f"Browser scrape failed for {url}: {e}")
            return None
        finally:
            if page:
                try:
                    await page.close()
                except Exception:
                    pass

    async def _scroll_page(self, page: Page) -> None:
        """Scroll page to load dynamic content."""
        for _ in range(self.config.max_scroll_attempts):
            prev_height = await page.evaluate("document.body.scrollHeight")
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

            try:
                await page.wait_for_load_state("networkidle", timeout=5000)
            except Exception:
                pass

            await asyncio.sleep(0.3)

            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height == prev_height:
                break

    async def _scrape_with_httpx(self, url: str) -> ScrapedPage | None:
        """Scrape a page using httpx (faster, for static pages)."""
        if not self._http_client:
            raise RuntimeError("HTTP client not initialized")

        try:
            response = await self._http_client.get(url)

            if response.status_code >= 400:
                logger.warning(f"HTTP {response.status_code} for {url}")
                return None

            # Handle redirects
            final_url = str(response.url)
            if final_url != url:
                if self.config.validate_urls:
                    validate_url(final_url, check_global_ip=self.config.validate_urls)
                if final_url in self._visited:
                    return None
                self._visited.add(final_url)
                url = final_url

            content_type = response.headers.get("content-type", "").lower()

            # Handle PDFs
            if self.config.extract_pdfs and any(pt in content_type for pt in PDF_MIME_TYPES):
                return await self._extract_pdf(url, response.content)

            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")
            parsed = clean_html(
                soup,
                ignored_elements=self.config.ignored_elements,
                ignored_classes=self.config.ignored_classes,
            )

            last_modified = response.headers.get("last-modified")

            return ScrapedPage(
                url=url,
                title=parsed.title,
                text=parsed.cleaned_text,
                html=response.text,
                last_modified=parse_last_modified(last_modified),
            )

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                # Retry with browser
                return await self._scrape_with_browser(url)
            logger.error(f"HTTP error for {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"httpx scrape failed for {url}: {e}")
            return None

    async def _extract_pdf(self, url: str, content: bytes) -> ScrapedPage | None:
        """Extract text from PDF content."""
        try:
            import pypdf

            reader = pypdf.PdfReader(io.BytesIO(content))
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

            if not text_parts:
                return None

            return ScrapedPage(
                url=url,
                title=url.split("/")[-1],
                text="\n\n".join(text_parts),
                metadata={"type": "pdf", "pages": len(reader.pages)},
            )
        except ImportError:
            logger.warning("pypdf not installed, skipping PDF extraction")
            return None
        except Exception as e:
            logger.error(f"PDF extraction failed for {url}: {e}")
            return None

    async def _scrape_url(self, url: str, use_browser: bool = False) -> ScrapedPage | None:
        """Scrape a single URL with retry logic."""
        async with self._semaphore:  # type: ignore
            for attempt in range(self.config.max_retries):
                try:
                    if attempt > 0:
                        await asyncio.sleep(self.config.retry_delay * (2 ** attempt))

                    if use_browser or self.config.use_browser_for_all:
                        result = await self._scrape_with_browser(url)
                    else:
                        result = await self._scrape_with_httpx(url)

                    if result:
                        # Deduplicate by content hash
                        if self.config.deduplicate_content:
                            content_hash = hashlib.md5(
                                f"{result.title}:{result.text}".encode()
                            ).hexdigest()
                            if content_hash in self._content_hashes:
                                logger.debug(f"Duplicate content: {url}")
                                return None
                            self._content_hashes.add(content_hash)

                        return result

                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")

            return None

    async def scrape(
        self,
        url: str,
        mode: ScrapeMode = ScrapeMode.SINGLE,
        urls: list[str] | None = None,
        on_page_scraped: Callable[[Document], None] | None = None,
    ) -> AsyncIterator[Document]:
        """
        Scrape URLs based on the specified mode.

        Args:
            url: Base URL or sitemap URL
            mode: Scraping mode (single, recursive, sitemap, url_list)
            urls: List of URLs (for URL_LIST mode)
            on_page_scraped: Optional callback for each scraped page

        Yields:
            Document objects for each successfully scraped page
        """
        url = ensure_valid_url(url)

        if self.config.validate_urls:
            validate_url(url)

        # Determine URLs to scrape
        to_scrape: list[str] = []

        if mode == ScrapeMode.SINGLE:
            to_scrape = [url]

        elif mode == ScrapeMode.URL_LIST:
            if not urls:
                raise ValueError("urls parameter required for URL_LIST mode")
            to_scrape = [ensure_valid_url(u) for u in urls]

        elif mode == ScrapeMode.SITEMAP:
            async with httpx.AsyncClient(headers=DEFAULT_HEADERS, follow_redirects=True) as client:
                sitemap_urls = await extract_urls_from_sitemap(client, url)
                if not sitemap_urls:
                    sitemap_urls = await discover_urls_from_site(url)
            to_scrape = list(sitemap_urls)
            if not to_scrape:
                raise ValueError(f"No URLs found in sitemap: {url}")

        elif mode == ScrapeMode.RECURSIVE:
            to_scrape = [url]

        # Process URLs
        base_url = url
        queue = asyncio.Queue()
        for u in to_scrape:
            await queue.put(u)

        async def worker():
            while True:
                try:
                    current_url = queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

                if current_url in self._visited:
                    continue

                self._visited.add(current_url)

                if self.config.validate_urls:
                    try:
                        validate_url(current_url)
                    except Exception as e:
                        logger.warning(f"Invalid URL {current_url}: {e}")
                        continue

                # Rate limiting
                if self.config.delay_between_requests > 0:
                    await asyncio.sleep(self.config.delay_between_requests)

                logger.info(f"Scraping: {current_url}")
                result = await self._scrape_url(current_url)

                if result:
                    # Extract links for recursive mode
                    if mode == ScrapeMode.RECURSIVE and result.html:
                        soup = BeautifulSoup(result.html, "html.parser")
                        links = extract_links(base_url, current_url, soup)
                        for link in links:
                            if link not in self._visited:
                                await queue.put(link)

                    doc = Document.from_scraped_page(result)
                    if on_page_scraped:
                        on_page_scraped(doc)
                    return doc

                return None

        # Run workers concurrently
        while not queue.empty():
            # Create batch of workers
            tasks = []
            batch_size = min(queue.qsize(), self.config.max_concurrent_pages)
            for _ in range(batch_size):
                tasks.append(asyncio.create_task(worker()))

            # Wait for batch to complete
            results = await asyncio.gather(*tasks)

            for result in results:
                if result:
                    yield result

    async def scrape_urls(
        self,
        urls: list[str],
        on_page_scraped: Callable[[Document], None] | None = None,
    ) -> list[Document]:
        """
        Scrape a list of URLs concurrently.

        Args:
            urls: List of URLs to scrape
            on_page_scraped: Optional callback for each scraped page

        Returns:
            List of Document objects
        """
        documents: list[Document] = []

        async for doc in self.scrape(
            urls[0] if urls else "",
            mode=ScrapeMode.URL_LIST,
            urls=urls,
            on_page_scraped=on_page_scraped,
        ):
            documents.append(doc)

        return documents


async def scrape_url(url: str, config: ScraperConfig | None = None) -> Document | None:
    """Convenience function to scrape a single URL."""
    async with WebScraper(config) as scraper:
        async for doc in scraper.scrape(url, mode=ScrapeMode.SINGLE):
            return doc
    return None


async def scrape_site(
    url: str,
    mode: ScrapeMode = ScrapeMode.RECURSIVE,
    config: ScraperConfig | None = None,
) -> list[Document]:
    """Convenience function to scrape a site."""
    documents: list[Document] = []
    async with WebScraper(config) as scraper:
        async for doc in scraper.scrape(url, mode=mode):
            documents.append(doc)
    return documents
