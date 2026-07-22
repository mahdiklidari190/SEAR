"""Pagination Analysis."""
from __future__ import annotations

from models.page_data import PageData


class PaginationAnalyzer:
    """Analyze pagination implementation."""

    def __init__(self):
        self.paginated_pages: list[PageData] = []

    def add_page(self, page: PageData) -> None:
        if page.pagination.has_next or page.pagination.has_prev or page.pagination.depth > 0:
            self.paginated_pages.append(page)

    def analyze(self) -> dict[str, any]:
        report = {
            "total_paginated_pages": len(self.paginated_pages),
            "max_depth": 0,
            "canonical_conflicts": [],
            "issues": [],
            "recommendations": [],
        }

        for page in self.paginated_pages:
            report["max_depth"] = max(report["max_depth"], page.pagination.depth)
            if page.pagination.canonical_conflict:
                report["canonical_conflicts"].append(page.url)

        if report["max_depth"] > 10:
            report["issues"].append(f"Deep pagination detected (depth: {report['max_depth']})")
            report["recommendations"].append("Implement 'View All' page or infinite scroll with proper canonical")
        if report["canonical_conflicts"]:
            report["issues"].append(f"{len(report['canonical_conflicts'])} pagination canonical conflicts")
            report["recommendations"].append("Ensure paginated pages use self-referencing canonicals")

        return report