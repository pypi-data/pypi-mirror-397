"""
Trace: High-performance async web scraper.
"""

from .scraper import WebScraper, ScraperConfig, ScrapeMode
from .models import Document, TextSection, ScrapedPage

__version__ = "1.0.0"
__all__ = [
    "WebScraper",
    "ScraperConfig",
    "ScrapeMode",
    "Document",
    "TextSection",
    "ScrapedPage",
]
