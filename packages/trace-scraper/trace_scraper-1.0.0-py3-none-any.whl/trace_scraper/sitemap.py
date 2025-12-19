"""Sitemap parsing utilities for URL discovery."""

import logging
import re
import xml.etree.ElementTree as ET
from urllib.parse import urljoin

import httpx

logger = logging.getLogger(__name__)


async def get_sitemap_locations_from_robots(
    client: httpx.AsyncClient,
    base_url: str,
    timeout: float = 10.0
) -> set[str]:
    """Extract sitemap URLs from robots.txt."""
    sitemap_urls: set[str] = set()
    try:
        robots_url = urljoin(base_url, "/robots.txt")
        resp = await client.get(robots_url, timeout=timeout)
        if resp.status_code == 200:
            for line in resp.text.splitlines():
                if line.lower().startswith("sitemap:"):
                    sitemap_url = line.split(":", 1)[1].strip()
                    sitemap_urls.add(sitemap_url)
    except Exception as e:
        logger.debug(f"Error fetching robots.txt: {e}")
    return sitemap_urls


async def extract_urls_from_sitemap(
    client: httpx.AsyncClient,
    sitemap_url: str,
    timeout: float = 10.0,
    max_depth: int = 3,
    _depth: int = 0
) -> set[str]:
    """Extract URLs from a sitemap XML file.

    Handles both regular sitemaps and sitemap indexes recursively.
    """
    urls: set[str] = set()

    if _depth >= max_depth:
        logger.warning(f"Max sitemap depth reached at {sitemap_url}")
        return urls

    try:
        resp = await client.get(sitemap_url, timeout=timeout)
        if resp.status_code != 200:
            return urls

        root = ET.fromstring(resp.content)

        # Handle namespace
        namespace = re.match(r"\{.*\}", root.tag)
        ns = namespace.group(0) if namespace else ""

        if root.tag == f"{ns}sitemapindex":
            # Sitemap index - recursively fetch sub-sitemaps
            for sitemap in root.findall(f".//{ns}loc"):
                if sitemap.text:
                    sub_urls = await extract_urls_from_sitemap(
                        client, sitemap.text, timeout, max_depth, _depth + 1
                    )
                    urls.update(sub_urls)
        else:
            # Regular sitemap
            for url in root.findall(f".//{ns}loc"):
                if url.text:
                    urls.add(url.text)

    except ET.ParseError as e:
        logger.warning(f"Invalid XML in sitemap {sitemap_url}: {e}")
    except Exception as e:
        logger.warning(f"Error processing sitemap {sitemap_url}: {e}")

    return urls


async def discover_urls_from_site(
    base_url: str,
    timeout: float = 10.0,
    max_depth: int = 3
) -> list[str]:
    """Discover all URLs from a site's sitemaps.

    Checks:
    - /sitemap.xml
    - /sitemap_index.xml
    - Sitemaps listed in robots.txt
    """
    base_url = base_url.rstrip("/")
    all_urls: set[str] = set()

    async with httpx.AsyncClient(follow_redirects=True) as client:
        # Check common sitemap locations
        sitemap_paths = ["/sitemap.xml", "/sitemap_index.xml"]
        for path in sitemap_paths:
            sitemap_url = urljoin(base_url, path)
            urls = await extract_urls_from_sitemap(client, sitemap_url, timeout, max_depth)
            all_urls.update(urls)

        # Check robots.txt for additional sitemaps
        sitemap_locations = await get_sitemap_locations_from_robots(client, base_url, timeout)
        for sitemap_url in sitemap_locations:
            urls = await extract_urls_from_sitemap(client, sitemap_url, timeout, max_depth)
            all_urls.update(urls)

    return list(all_urls)
