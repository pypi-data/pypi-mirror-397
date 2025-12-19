"""HTML parsing and cleanup utilities."""

import re
from dataclasses import dataclass

import bs4


@dataclass
class ParsedHTML:
    """Parsed HTML content."""
    title: str | None
    cleaned_text: str


# Default elements to ignore during parsing
DEFAULT_IGNORED_ELEMENTS = ["script", "style", "noscript", "nav", "footer", "header"]
DEFAULT_IGNORED_CLASSES = ["sidebar", "nav", "footer", "header", "menu", "advertisement", "ad"]
MINTLIFY_UNWANTED = ["sticky", "hidden"]


def strip_excessive_newlines_and_spaces(document: str) -> str:
    """Clean up whitespace in document."""
    document = re.sub(r" +", " ", document)
    document = re.sub(r" +[\n\r]", "\n", document)
    document = re.sub(r"[\n\r]+", "\n", document)
    return document.strip()


def strip_newlines(document: str) -> str:
    """Replace newlines with spaces."""
    return re.sub(r"[\n\r]+", " ", document)


def format_document_soup(
    document: bs4.BeautifulSoup,
    table_cell_separator: str = "\t"
) -> str:
    """Format HTML soup to plain text.

    Goals:
    - Remove HTML newlines (browsers ignore them)
    - Remove repeated whitespace
    - Preserve structure with newlines for headers, paragraphs, lists
    - Handle tables with tab-separated columns
    """
    text = ""
    list_element_start = False
    verbatim_output = 0
    in_table = False
    last_added_newline = False
    link_href: str | None = None

    for e in document.descendants:
        verbatim_output -= 1
        if isinstance(e, bs4.element.NavigableString):
            if isinstance(e, (bs4.element.Comment, bs4.element.Doctype)):
                continue
            element_text = e.text
            if in_table:
                element_text = element_text.replace("\n", " ").strip()

            if last_added_newline and element_text.startswith(" "):
                element_text = element_text[1:]
                last_added_newline = False

            if element_text:
                content_to_add = element_text if verbatim_output > 0 else strip_newlines(element_text)

                # Add link formatting if available
                if link_href and content_to_add.strip():
                    content_to_add = f"[{content_to_add}]({link_href})"

                if (text and not text[-1].isspace()) and (content_to_add and not content_to_add[0].isspace()):
                    text += " "

                text += content_to_add
                list_element_start = False

        elif isinstance(e, bs4.element.Tag):
            if e.name == "table":
                in_table = True
            elif e.name == "tr" and in_table:
                text += "\n"
            elif e.name in ["td", "th"] and in_table:
                text += table_cell_separator
            elif e.name == "/table":
                in_table = False
            elif in_table:
                pass
            elif e.name == "a":
                href_value = e.get("href", None)
                link_href = href_value[0] if isinstance(href_value, list) else href_value
            elif e.name == "/a":
                link_href = None
            elif e.name in ["p", "div"]:
                if not list_element_start:
                    text += "\n"
            elif e.name in ["h1", "h2", "h3", "h4"]:
                text += "\n"
                list_element_start = False
                last_added_newline = True
            elif e.name == "br":
                text += "\n"
                list_element_start = False
                last_added_newline = True
            elif e.name == "li":
                text += "\n- "
                list_element_start = True
            elif e.name == "pre":
                if verbatim_output <= 0:
                    verbatim_output = len(list(e.childGenerator()))

    return strip_excessive_newlines_and_spaces(text)


def clean_html(
    page_content: str | bs4.BeautifulSoup,
    mintlify_cleanup: bool = True,
    ignored_elements: list[str] | None = None,
    ignored_classes: list[str] | None = None,
) -> ParsedHTML:
    """Clean HTML and extract text content.

    Args:
        page_content: Raw HTML string or BeautifulSoup object
        mintlify_cleanup: Remove Mintlify-specific unwanted classes
        ignored_elements: HTML elements to remove (defaults to scripts, styles, nav, etc.)
        ignored_classes: CSS classes to remove (defaults to sidebar, nav, footer, etc.)

    Returns:
        ParsedHTML with title and cleaned text
    """
    if isinstance(page_content, str):
        soup = bs4.BeautifulSoup(page_content, "html.parser")
    else:
        soup = page_content

    # Extract title
    title_tag = soup.find("title")
    title = None
    if title_tag and title_tag.text:
        title = title_tag.text.strip()
        title_tag.extract()

    # Remove unwanted elements by tag
    elements_to_remove = ignored_elements or DEFAULT_IGNORED_ELEMENTS
    for tag_name in elements_to_remove:
        for tag in soup.find_all(tag_name):
            tag.extract()

    # Remove unwanted elements by class
    classes_to_remove = list(ignored_classes or DEFAULT_IGNORED_CLASSES)
    if mintlify_cleanup:
        classes_to_remove.extend(MINTLIFY_UNWANTED)

    for unwanted_class in classes_to_remove:
        for tag in soup.find_all(class_=lambda x: x and unwanted_class in x.split()):
            tag.extract()

    # Convert to text
    page_text = format_document_soup(soup)

    # Clean up zero-width spaces
    cleaned_text = page_text.replace("\u200b", "")

    return ParsedHTML(title=title, cleaned_text=cleaned_text)
