"""Pagination Analysis."""
# This module focuses on evaluating how a website handles paginated content (e.g., page 2, page 3 of a category).
# Proper pagination is crucial for ensuring search engines can crawl and index all items without getting trapped in infinite loops.
from __future__ import annotations

from models.page_data import PageData


class PaginationAnalyzer:
    """Analyze pagination implementation."""
    # This class tracks paginated pages across the site and evaluates their structural depth and canonical correctness.

    def __init__(self):
        # Initialize an empty list to store pages that exhibit pagination characteristics.
        self.paginated_pages: list[PageData] = []

    def add_page(self, page: PageData) -> None:
        # Check if the current page shows signs of being part of a paginated series.
        # A page is considered paginated if it has a 'next' link, a 'previous' link, or a pagination depth greater than 0.
        if page.pagination.has_next or page.pagination.has_prev or page.pagination.depth > 0:
            self.paginated_pages.append(page)

    def analyze(self) -> dict[str, any]:
        # Initialize the analysis report structure with default values and empty lists for tracking issues.
        report = {
            "total_paginated_pages": len(self.paginated_pages),
            "max_depth": 0,
            "canonical_conflicts": [],
            "issues": [],
            "recommendations": [],
        }

        # Iterate through all identified paginated pages to calculate the maximum pagination depth 
        # and collect any URLs that have conflicting canonical tags.
        for page in self.paginated_pages:
            # Update the maximum depth encountered so far to understand how deep the pagination goes.
            report["max_depth"] = max(report["max_depth"], page.pagination.depth)
            
            # If the page has a canonical conflict (e.g., pointing to page 1 instead of itself), record the URL.
            if page.pagination.canonical_conflict:
                report["canonical_conflicts"].append(page.url)

        # Evaluate the maximum depth. Deep pagination (e.g., > 10 pages) can waste crawl budget 
        # and dilute link equity, so we flag it and suggest alternatives like a 'View All' page.
        if report["max_depth"] > 10:
            report["issues"].append(f"Deep pagination detected (depth: {report['max_depth']})")
            report["recommendations"].append("Implement 'View All' page or infinite scroll with proper canonical")
            
        # Evaluate canonical conflicts. Paginated pages should typically use self-referencing canonical tags 
        # to ensure each page is indexed individually, rather than consolidating all link equity to page 1.
        if report["canonical_conflicts"]:
            report["issues"].append(f"{len(report['canonical_conflicts'])} pagination canonical conflicts")
            report["recommendations"].append("Ensure paginated pages use self-referencing canonicals")

        # Return the finalized pagination analysis report containing all metrics and actionable recommendations.
        return report