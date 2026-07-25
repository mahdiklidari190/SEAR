"""Sitemap and Robots.txt parsers - preserved and extended."""
from __future__ import annotations

import re
from typing import Optional
from urllib.parse import urlparse

# Import the pre-compiled regex for efficiently extracting <loc> tags from XML.
from config.constants import RE_LOC
# Import the structured data models used to return comprehensive validation results.
from models.integrations import SitemapValidationResult, RobotsValidationResult


class SitemapParser:
    """Parse and validate XML sitemaps."""

    @staticmethod
    async def parse_recursive(fetcher, url: str, seen_urls: set[str]) -> list[str]:
        """
        Recursively parse sitemap index files and child sitemaps.
        This ensures that all nested sitemaps are discovered and their URLs extracted.
        
        Args:
            fetcher: The HTTP client instance used to fetch the sitemap content.
            url: The URL of the sitemap or sitemap index to parse.
            seen_urls: A set of already processed URLs to prevent infinite loops and duplicates.
            
        Returns:
            A list of valid, unique URLs extracted from the sitemap(s).
        """
        try:
            result = await fetcher.fetch(url)
            text = result.content.decode("utf-8", errors="ignore")

            # Check if this is a sitemap index file containing references to other sitemaps.
            if "<sitemapindex" in text or "<sitemap>" in text:
                child_sitemaps = RE_LOC.findall(text)
                results = []
                for child in child_sitemaps:
                    # Only process child sitemaps that haven't been visited yet.
                    if child not in seen_urls:
                        seen_urls.add(child)
                        results.extend(
                            await SitemapParser.parse_recursive(fetcher, child, seen_urls)
                        )
                return results
            else:
                # This is a standard sitemap; extract all <loc> URLs.
                urls = RE_LOC.findall(text)
                valid_urls = []
                for u in urls:
                    # Ensure the URL is valid (starts with http) and hasn't been seen before.
                    if u not in seen_urls and u.startswith("http"):
                        seen_urls.add(u)
                        valid_urls.append(u)
                return valid_urls
        except Exception:
            # Gracefully handle network or parsing errors by returning an empty list.
            return []

    @staticmethod
    def validate_sitemap_content(xml_text: str, all_site_urls: set[str]) -> SitemapValidationResult:
        """
        Validate the structure, content, and best practices of a sitemap file.
        
        Args:
            xml_text: The raw XML content of the sitemap.
            all_site_urls: A set of all URLs discovered during the site crawl, used for cross-referencing.
            
        Returns:
            A SitemapValidationResult object containing metrics, errors, and recommendations.
        """
        result = SitemapValidationResult()

        # Detect the specific type of sitemap based on the namespaces or tags present.
        if "<image:image" in xml_text:
            result.sitemap_type = "image"
        elif "<video:video" in xml_text:
            result.sitemap_type = "video"
        elif "<news:news" in xml_text:
            result.sitemap_type = "news"
        else:
            result.sitemap_type = "xml"

        # Extract all URLs declared in the sitemap.
        urls = RE_LOC.findall(xml_text)
        result.total_urls = len(urls)

        for url in urls:
            # Check for malformed URLs that don't use a proper protocol.
            if not url.startswith("http"):
                result.invalid_urls.append(url)
            # Check for "orphan" URLs: URLs in the sitemap that were never actually found during the crawl.
            elif url not in all_site_urls and all_site_urls:
                result.orphan_urls.append(url)
            else:
                result.valid_urls += 1

        # Validate the <lastmod> tags to ensure they follow the correct ISO 8601 date format.
        lastmod_pattern = re.compile(r"<lastmod>(.*?)</lastmod>")
        lastmods = lastmod_pattern.findall(xml_text)
        result.missing_lastmod = result.total_urls - len(lastmods)

        for lm in lastmods:
            if not re.match(r"\d{4}-\d{2}-\d{2}", lm):
                result.invalid_lastmod += 1

        # Generate actionable issues based on the validation findings.
        if result.invalid_urls:
            result.issues.append(f"{len(result.invalid_urls)} invalid URLs found in sitemap")
        if result.missing_lastmod > result.total_urls * 0.5:
            result.issues.append("Majority of URLs missing <lastmod> tag")

        return result


class RobotsParser:
    """Parse and validate robots.txt."""

    @staticmethod
    def validate(robots_text: str, important_paths: Optional[list[str]] = None) -> RobotsValidationResult:
        """
        Parse and validate the contents of a robots.txt file against SEO best practices.
        
        Args:
            robots_text: The raw text content of the robots.txt file.
            important_paths: An optional list of critical URL paths that must not be blocked.
            
        Returns:
            A RobotsValidationResult object containing parsed rules, syntax errors, and warnings.
        """
        result = RobotsValidationResult()

        # Handle the edge case where the robots.txt file is completely empty or missing.
        if not robots_text.strip():
            result.issues.append("robots.txt is empty or not found")
            return result

        lines = robots_text.strip().split("\n")
        current_agent = ""

        # Parse the file line by line to extract directives.
        for i, line in enumerate(lines, 1):
            line = line.strip()
            # Ignore empty lines and comments.
            if not line or line.startswith("#"):
                continue

            # A valid directive must contain a colon separating the key and the value.
            if ":" not in line:
                result.syntax_errors.append(f"Line {i}: Invalid syntax - '{line}'")
                result.valid_syntax = False
                continue

            key, _, value = line.partition(":")
            key = key.strip().lower()
            value = value.strip()

            # Track the current User-Agent context to apply rules correctly.
            if key == "user-agent":
                current_agent = value
            # Record Disallow rules specifically for the wildcard (*) User-Agent.
            elif key == "disallow" and current_agent == "*":
                result.disallow_rules.append(value)
            # Record Allow rules specifically for the wildcard (*) User-Agent.
            elif key == "allow" and current_agent == "*":
                result.allow_rules.append(value)
            # Extract any declared sitemap URLs.
            elif key == "sitemap":
                result.sitemaps_declared.append(value)
            # Parse the crawl-delay directive, ensuring it's a valid integer.
            elif key == "crawl-delay":
                try:
                    result.crawl_delay = int(value)
                except ValueError:
                    result.syntax_errors.append(f"Line {i}: Invalid crawl-delay value '{value}'")
            # Record the preferred host directive.
            elif key == "host":
                result.host = value

        # Cross-reference the Disallow rules against the list of important paths to prevent accidental blocking.
        if important_paths:
            for path in important_paths:
                for rule in result.disallow_rules:
                    if rule and path.startswith(rule):
                        # Check if there's a specific Allow rule that overrides this Disallow rule.
                        allowed = any(
                            path.startswith(a) for a in result.allow_rules if a
                        )
                        if not allowed:
                            result.blocked_important_pages.append(path)

        # Generate final warnings based on the parsed rules.
        if result.blocked_important_pages:
            result.issues.append(
                f"Important pages blocked: {', '.join(result.blocked_important_pages[:5])}"
            )
        if not result.sitemaps_declared:
            result.issues.append("No Sitemap directive found in robots.txt")

        return result