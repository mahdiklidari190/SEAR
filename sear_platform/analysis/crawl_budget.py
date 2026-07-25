"""Crawl Budget Analysis module."""
from __future__ import annotations

import re
from urllib.parse import urlparse, parse_qs
from collections import Counter

# Import predefined regular expression patterns for identifying specific URL types.
from config.constants import RE_PARAMETER_URL, RE_SESSION_ID, RE_UTM_PARAMS
# Import the data model used to structure and return the crawl budget analysis report.
from models.integrations import CrawlBudgetReport


class CrawlBudgetAnalyzer:
    """Analyze crawl budget efficiency by identifying wasteful URL patterns and structural issues."""

    def __init__(self):
        # Initialize data structures to collect URLs, redirect chains, and blocked resources during the crawl.
        self.all_urls: list[str] = []
        self.redirect_map: dict[str, str] = {}
        self.blocked_urls: list[str] = []

    def add_url(self, url: str) -> None:
        """Record a discovered URL for later analysis."""
        self.all_urls.append(url)

    def add_redirect(self, source: str, target: str) -> None:
        """Map a source URL to its redirect target to identify redirect chains."""
        self.redirect_map[source] = target

    def add_blocked(self, url: str) -> None:
        """Record a URL that was blocked by robots.txt or meta robots tags."""
        self.blocked_urls.append(url)

    def analyze(self) -> CrawlBudgetReport:
        """Perform a full crawl budget analysis and generate an actionable report."""
        report = CrawlBudgetReport()
        report.total_urls = len(self.all_urls)

        # 1. Detect duplicate URLs by normalizing them (e.g., handling trailing slashes, http/https, www).
        normalized = Counter()
        for url in self.all_urls:
            norm = self._normalize(url)
            normalized[norm] += 1
        # Count how many normalized URLs appear more than once.
        report.duplicate_urls = sum(1 for c in normalized.values() if c > 1)

        # 2. Count the total number of internal links pointing to redirected URLs.
        report.redirect_urls = len(self.redirect_map)

        # 3. Count the total number of URLs blocked from crawling.
        report.blocked_urls = len(self.blocked_urls)

        # 4. Identify URLs containing parameters, specifically focusing on session IDs and UTM tracking parameters.
        param_urls = [u for u in self.all_urls if RE_PARAMETER_URL.search(u)]
        session_urls = [u for u in param_urls if RE_SESSION_ID.search(u)]
        utm_urls = [u for u in param_urls if RE_UTM_PARAMS.search(u)]
        # Use a set to ensure we count unique parameter-based URLs only once.
        report.parameter_urls = len(set(session_urls + utm_urls))

        # 5. Calculate the maximum crawl depth across all discovered URLs.
        depths = [self._get_depth(u) for u in self.all_urls]
        report.max_crawl_depth = max(depths) if depths else 0

        # 6. Calculate the percentage of the crawl budget wasted on non-valuable URLs.
        total = max(report.total_urls, 1) # Prevent division by zero.
        wasted = report.duplicate_urls + report.redirect_urls + report.parameter_urls + report.blocked_urls
        report.wasted_budget_pct = round((wasted / total) * 100, 1)

        # 7. Generate specific, actionable recommendations based on the detected issues.
        if report.duplicate_urls > 0:
            report.recommendations.append(
                f"Consolidate {report.duplicate_urls} duplicate URL variants (trailing slash, www, protocol)"
            )
        if report.redirect_urls > 0:
            report.recommendations.append(
                f"Update {report.redirect_urls} internal links pointing to redirected URLs"
            )
        if report.parameter_urls > 0:
            report.recommendations.append(
                f"Add canonical tags or robots.txt rules for {report.parameter_urls} parameter-based URLs"
            )
        if report.blocked_urls > 0:
            report.recommendations.append(
                f"Review {report.blocked_urls} blocked URLs - ensure important pages aren't blocked"
            )
        if report.max_crawl_depth > 5:
            report.recommendations.append(
                f"Reduce crawl depth (max: {report.max_crawl_depth}). Flatten site architecture."
            )

        return report

    @staticmethod
    def _normalize(url: str) -> str:
        """
        Normalize a URL to identify duplicates.
        Removes trailing slashes, converts the domain to lowercase, and strips 'www.' prefixes.
        """
        parsed = urlparse(url)
        path = parsed.path.rstrip("/")
        return f"{parsed.netloc.lower().replace('www.', '')}{path}"

    @staticmethod
    def _get_depth(url: str) -> int:
        """
        Calculate the directory depth of a URL based on its path segments.
        A root path '/' returns 0, '/about/' returns 1, '/about/team/' returns 2, etc.
        """
        path = urlparse(url).path.strip("/")
        return len(path.split("/")) if path else 0