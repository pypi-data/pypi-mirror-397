"""Data models for the web scraper."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class TextSection:
    """A section of text from a scraped page."""
    text: str
    link: str


@dataclass
class ScrapedPage:
    """Raw scraped page data before conversion to Document."""
    url: str
    title: str | None
    text: str
    html: str | None = None
    last_modified: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Document:
    """A document extracted from a web page."""
    id: str
    sections: list[TextSection]
    source: str = "web"
    semantic_identifier: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    doc_updated_at: datetime | None = None

    @classmethod
    def from_scraped_page(cls, page: ScrapedPage) -> "Document":
        """Create a Document from a ScrapedPage."""
        return cls(
            id=page.url,
            sections=[TextSection(text=page.text, link=page.url)],
            source="web",
            semantic_identifier=page.title or page.url.split("/")[-1] or page.url,
            metadata=page.metadata,
            doc_updated_at=page.last_modified,
        )
