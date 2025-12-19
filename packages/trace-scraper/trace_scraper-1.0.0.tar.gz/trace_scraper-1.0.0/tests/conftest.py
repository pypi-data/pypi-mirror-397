"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def sample_html() -> str:
    """Sample HTML for testing."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
        <script>console.log('test');</script>
        <style>.test { color: red; }</style>
    </head>
    <body>
        <nav>Navigation</nav>
        <main>
            <h1>Main Content</h1>
            <p>This is a test paragraph.</p>
            <a href="/page1">Page 1</a>
            <a href="/page2">Page 2</a>
            <a href="https://external.com">External</a>
        </main>
        <footer>Footer</footer>
    </body>
    </html>
    """


@pytest.fixture
def sample_sitemap() -> str:
    """Sample sitemap XML for testing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url><loc>https://example.com/page1</loc></url>
        <url><loc>https://example.com/page2</loc></url>
        <url><loc>https://example.com/page3</loc></url>
    </urlset>
    """
