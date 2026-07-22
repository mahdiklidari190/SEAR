"""Crawl Budget Analysis module."""
from __future__ import annotations

import re
from urllib.parse import urlparse, parse_qs
from collections import Counter

from config.constants import RE_PARAMETER_URL, RE_SESSION_ID, RE_UTM_PARAMS
from models.integrations import CrawlBudgetReport


class CrawlBudgetAnalyzer:
    """Analyze crawl budget efficiency."""

    def __init__(self):
        self.all_urls: list[str] = []
        self.redirect_map: dict[str, str] = {}
        self.blocked_urls: list[str] = []

    def add_url(self, url: str) -> None:
        self.all_urls.append(url)

    def add_redirect(self, source: str, target: str) -> None:
        self.redirect_map[source] = target

    def add_blocked(self, url: str) -> None:
        self.blocked_urls.append(url)

    def analyze(self) -> CrawlBudgetReport:
        """Perform full crawl budget analysis."""
        report = CrawlBudgetReport()
        report.total_urls = len(self.all_urls)

        # Detect duplicate URLs (with/without trailing slash, http/https, www)
        normalized = Counter()
        for url in self.all_urls:
            norm = self._normalize(url)
            normalized[norm] += 1
        report.duplicate_urls = sum(1 for c in normalized.values() if c > 1)

        # Redirect URLs
        report.redirect_urls = len(self.redirect_map)

        # Blocked URLs
        report.blocked_urls = len(self.blocked_urls)

        # Parameter URLs
        param_urls = [u for u in self.all_urls if RE_PARAMETER_URL.search(u)]
        session_urls = [u for u in param_urls if RE_SESSION_ID.search(u)]
        utm_urls = [u for u in param_urls if RE_UTM_PARAMS.search(u)]
        report.parameter_urls = len(set(session_urls + utm_urls))

        # Crawl depth
        depths = [self._get_depth(u) for u in self.all_urls]
        report.max_crawl_depth = max(depths) if depths else 0

        # Wasted budget calculation
        total = max(report.total_urls, 1)
        wasted = report.duplicate_urls + report.redirect_urls + report.parameter_urls + report.blocked_urls
        report.wasted_budget_pct = round((wasted / total) * 100, 1)

        # Recommendations
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
        parsed = urlparse(url)
        path = parsed.path.rstrip("/")
        return f"{parsed.netloc.lower().replace('www.', '')}{path}"

    @staticmethod
    def _get_depth(url: str) -> int:
        path = urlparse(url).path.strip("/")
        return len(path.split("/")) if path else 0