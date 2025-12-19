"""Tests for scraper utilities."""

import pytest

from trace.scraper import (
    ensure_valid_url,
    extract_links,
    is_same_site,
    validate_url,
)
from bs4 import BeautifulSoup


def test_ensure_valid_url_adds_scheme():
    """Test that scheme is added to URLs without one."""
    assert ensure_valid_url("example.com") == "https://example.com"
    assert ensure_valid_url("https://example.com") == "https://example.com"
    assert ensure_valid_url("http://example.com") == "http://example.com"


def test_is_same_site_same_domain():
    """Test same-site detection for same domain."""
    assert is_same_site("https://example.com", "https://example.com/page")
    assert is_same_site("https://example.com", "https://www.example.com/page")
    assert is_same_site("https://www.example.com", "https://example.com/page")


def test_is_same_site_different_domain():
    """Test same-site detection for different domains."""
    assert not is_same_site("https://example.com", "https://other.com/page")
    assert not is_same_site("https://example.com", "https://sub.example.com/page")


def test_is_same_site_with_base_path():
    """Test same-site detection with base path."""
    assert is_same_site("https://example.com/docs", "https://example.com/docs/page")
    assert not is_same_site("https://example.com/docs", "https://example.com/other")


def test_validate_url_valid():
    """Test URL validation with valid URL."""
    # This should not raise (example.com resolves to a global IP)
    validate_url("https://example.com", check_global_ip=False)


def test_validate_url_invalid_scheme():
    """Test URL validation with invalid scheme."""
    with pytest.raises(ValueError, match="Invalid URL scheme"):
        validate_url("ftp://example.com")


def test_validate_url_no_hostname():
    """Test URL validation with missing hostname."""
    with pytest.raises(ValueError, match="URL must include a hostname"):
        validate_url("https:///path")


def test_extract_links():
    """Test link extraction from HTML."""
    html = """
    <html>
    <body>
        <a href="/page1">Page 1</a>
        <a href="https://example.com/page2">Page 2</a>
        <a href="https://external.com/page">External</a>
        <a href="#section">Anchor</a>
    </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    links = extract_links(
        "https://example.com",
        "https://example.com/current",
        soup
    )

    assert "https://example.com/page1" in links
    assert "https://example.com/page2" in links
    assert "https://external.com/page" not in links  # External
    assert len([l for l in links if "#" in l]) == 0  # No anchors
