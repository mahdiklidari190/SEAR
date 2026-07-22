"""Faceted Navigation Analysis."""
from __future__ import annotations

import re
from urllib.parse import urlparse, parse_qs
from collections import Counter


class FacetedNavigationAnalyzer:
    """Detect and analyze faceted navigation issues."""

    # Common faceted parameters
    FACET_PARAMS = {
        "color", "size", "price", "sort", "order", "filter", "category",
        "brand", "rating", "page", "limit", "offset", "ref", "facet",
        "attr", "attribute", "tag", "type", "material", "style",
    }

    def __init__(self):
        self.urls: list[str] = []

    def add_url(self, url: str) -> None:
        self.urls.append(url)

    def analyze(self) -> dict[str, any]:
        report = {
            "total_parameter_urls": 0,
            "facet_parameters": Counter(),
            "duplicate_parameter_pages": [],
            "recommendations": [],
        }

        param_groups: dict[str, list[str]] = {}

        for url in self.urls:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            if not params:
                continue

            report["total_parameter_urls"] += 1
            base_path = parsed.path

            for key in params:
                if key.lower() in self.FACET_PARAMS:
                    report["facet_parameters"][key] += 1

            # Group by base path
            param_groups.setdefault(base_path, []).append(url)

        # Detect duplicate parameter combinations
        for path, urls in param_groups.items():
            if len(urls) > 5:
                report["duplicate_parameter_pages"].append({
                    "path": path,
                    "count": len(urls),
                    "sample_urls": urls[:3],
                })

        if report["facet_parameters"]:
            report["recommendations"].append(
                "Add canonical tags to faceted pages pointing to the main category page"
            )
            report["recommendations"].append(
                "Use robots.txt or meta robots noindex for low-value parameter combinations"
            )
        if report["duplicate_parameter_pages"]:
            report["recommendations"].append(
                f"{len(report['duplicate_parameter_pages'])} paths have excessive parameter variants"
            )

        return report