"""Sitemap and Robots.txt parsers - preserved and extended."""
from __future__ import annotations

import re
from typing import Optional
from urllib.parse import urlparse

from config.constants import RE_LOC
from models.integrations import SitemapValidationResult, RobotsValidationResult


class SitemapParser:
    """Parse and validate XML sitemaps."""

    @staticmethod
    async def parse_recursive(fetcher, url: str, seen_urls: set[str]) -> list[str]:
        """Recursively parse sitemap index and child sitemaps. Preserved from original."""
        try:
            result = await fetcher.fetch(url)
            text = result.content.decode("utf-8", errors="ignore")

            if "<sitemapindex" in text or "<sitemap>" in text:
                child_sitemaps = RE_LOC.findall(text)
                results = []
                for child in child_sitemaps:
                    if child not in seen_urls:
                        seen_urls.add(child)
                        results.extend(
                            await SitemapParser.parse_recursive(fetcher, child, seen_urls)
                        )
                return results
            else:
                urls = RE_LOC.findall(text)
                valid_urls = []
                for u in urls:
                    if u not in seen_urls and u.startswith("http"):
                        seen_urls.add(u)
                        valid_urls.append(u)
                return valid_urls
        except Exception:
            return []

    @staticmethod
    def validate_sitemap_content(xml_text: str, all_site_urls: set[str]) -> SitemapValidationResult:
        """Validate sitemap structure and content."""
        result = SitemapValidationResult()

        # Detect type
        if "<image:image" in xml_text:
            result.sitemap_type = "image"
        elif "<video:video" in xml_text:
            result.sitemap_type = "video"
        elif "<news:news" in xml_text:
            result.sitemap_type = "news"
        else:
            result.sitemap_type = "xml"

        urls = RE_LOC.findall(xml_text)
        result.total_urls = len(urls)

        for url in urls:
            if not url.startswith("http"):
                result.invalid_urls.append(url)
            elif url not in all_site_urls and all_site_urls:
                result.orphan_urls.append(url)
            else:
                result.valid_urls += 1

        # Check lastmod
        lastmod_pattern = re.compile(r"<lastmod>(.*?)</lastmod>")
        lastmods = lastmod_pattern.findall(xml_text)
        result.missing_lastmod = result.total_urls - len(lastmods)

        for lm in lastmods:
            if not re.match(r"\d{4}-\d{2}-\d{2}", lm):
                result.invalid_lastmod += 1

        if result.invalid_urls:
            result.issues.append(f"{len(result.invalid_urls)} invalid URLs found in sitemap")
        if result.missing_lastmod > result.total_urls * 0.5:
            result.issues.append("Majority of URLs missing <lastmod> tag")

        return result


class RobotsParser:
    """Parse and validate robots.txt."""

    @staticmethod
    def validate(robots_text: str, important_paths: Optional[list[str]] = None) -> RobotsValidationResult:
        """Validate robots.txt content."""
        result = RobotsValidationResult()

        if not robots_text.strip():
            result.issues.append("robots.txt is empty or not found")
            return result

        lines = robots_text.strip().split("\n")
        current_agent = ""

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if ":" not in line:
                result.syntax_errors.append(f"Line {i}: Invalid syntax - '{line}'")
                result.valid_syntax = False
                continue

            key, _, value = line.partition(":")
            key = key.strip().lower()
            value = value.strip()

            if key == "user-agent":
                current_agent = value
            elif key == "disallow" and current_agent == "*":
                result.disallow_rules.append(value)
            elif key == "allow" and current_agent == "*":
                result.allow_rules.append(value)
            elif key == "sitemap":
                result.sitemaps_declared.append(value)
            elif key == "crawl-delay":
                try:
                    result.crawl_delay = int(value)
                except ValueError:
                    result.syntax_errors.append(f"Line {i}: Invalid crawl-delay value '{value}'")
            elif key == "host":
                result.host = value

        # Check if important pages are blocked
        if important_paths:
            for path in important_paths:
                for rule in result.disallow_rules:
                    if rule and path.startswith(rule):
                        # Check if there's an Allow override
                        allowed = any(
                            path.startswith(a) for a in result.allow_rules if a
                        )
                        if not allowed:
                            result.blocked_important_pages.append(path)

        if result.blocked_important_pages:
            result.issues.append(
                f"Important pages blocked: {', '.join(result.blocked_important_pages[:5])}"
            )
        if not result.sitemaps_declared:
            result.issues.append("No Sitemap directive found in robots.txt")

        return result