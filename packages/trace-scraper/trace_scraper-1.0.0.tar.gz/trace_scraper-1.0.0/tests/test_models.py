"""Tests for data models."""

from datetime import datetime, timezone

from trace.models import Document, ScrapedPage, TextSection


def test_text_section_creation():
    """Test TextSection creation."""
    section = TextSection(text="Hello", link="https://example.com")
    assert section.text == "Hello"
    assert section.link == "https://example.com"


def test_scraped_page_creation():
    """Test ScrapedPage creation with defaults."""
    page = ScrapedPage(url="https://example.com", title="Test", text="Content")
    assert page.url == "https://example.com"
    assert page.title == "Test"
    assert page.text == "Content"
    assert page.html is None
    assert page.last_modified is None
    assert page.metadata == {}


def test_document_from_scraped_page():
    """Test Document creation from ScrapedPage."""
    now = datetime.now(timezone.utc)
    page = ScrapedPage(
        url="https://example.com/page",
        title="Test Page",
        text="Page content",
        last_modified=now,
        metadata={"key": "value"},
    )

    doc = Document.from_scraped_page(page)

    assert doc.id == "https://example.com/page"
    assert doc.semantic_identifier == "Test Page"
    assert doc.source == "web"
    assert len(doc.sections) == 1
    assert doc.sections[0].text == "Page content"
    assert doc.sections[0].link == "https://example.com/page"
    assert doc.doc_updated_at == now
    assert doc.metadata == {"key": "value"}


def test_document_from_scraped_page_without_title():
    """Test Document uses URL as identifier when no title."""
    page = ScrapedPage(url="https://example.com/mypage", title=None, text="Content")
    doc = Document.from_scraped_page(page)
    assert doc.semantic_identifier == "mypage"
