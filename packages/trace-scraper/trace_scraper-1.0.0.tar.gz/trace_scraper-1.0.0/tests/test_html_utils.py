"""Tests for HTML utilities."""

import pytest

from trace.html_utils import clean_html, strip_excessive_newlines_and_spaces


def test_clean_html_extracts_title(sample_html: str):
    """Test that clean_html extracts the title."""
    result = clean_html(sample_html)
    assert result.title == "Test Page"


def test_clean_html_removes_script_and_style(sample_html: str):
    """Test that scripts and styles are removed."""
    result = clean_html(sample_html)
    assert "console.log" not in result.cleaned_text
    assert "color: red" not in result.cleaned_text


def test_clean_html_removes_nav_and_footer(sample_html: str):
    """Test that nav and footer elements are removed."""
    result = clean_html(sample_html)
    assert "Navigation" not in result.cleaned_text
    assert "Footer" not in result.cleaned_text


def test_clean_html_preserves_main_content(sample_html: str):
    """Test that main content is preserved."""
    result = clean_html(sample_html)
    assert "Main Content" in result.cleaned_text
    assert "test paragraph" in result.cleaned_text


def test_strip_excessive_newlines():
    """Test whitespace cleanup."""
    text = "Hello   \n\n\n  World"
    result = strip_excessive_newlines_and_spaces(text)
    assert result == "Hello\nWorld"
