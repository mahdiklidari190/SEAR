"""Sitemap Validation module."""
from __future__ import annotations

from core.parser import SitemapParser
from models.integrations import SitemapValidationResult


class SitemapValidator:
    """Validate sitemap files."""

    @staticmethod
    def validate(xml_content: str, all_crawled_urls: set[str]) -> SitemapValidationResult:
        return SitemapParser.validate_sitemap_content(xml_content, all_crawled_urls)