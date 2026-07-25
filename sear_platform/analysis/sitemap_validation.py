"""Sitemap Validation module."""
from __future__ import annotations

# Import the core parsing logic responsible for analyzing XML structure, syntax, and sitemap-specific rules.
from core.parser import SitemapParser

# Import the structured data model used to return the validation results, including any detected errors, warnings, or parsed URLs.
from models.integrations import SitemapValidationResult


class SitemapValidator:
    """Validate sitemap files."""

    @staticmethod
    def validate(xml_content: str, all_crawled_urls: set[str]) -> SitemapValidationResult:
        # This method acts as a clean, high-level interface for sitemap validation.
        # It accepts the raw XML content of the sitemap and a set of all URLs discovered during the crawl for cross-referencing.
        
        # Delegate the actual XML parsing, syntax checking, and URL validation logic to the core SitemapParser.
        # This separation of concerns keeps the validator class lightweight and focused on orchestration, 
        # while relying on the specialized parser for the heavy lifting.
        return SitemapParser.validate_sitemap_content(xml_content, all_crawled_urls)