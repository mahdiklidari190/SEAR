"""Faceted Navigation Analysis."""
from __future__ import annotations

import re
from urllib.parse import urlparse, parse_qs
from collections import Counter


class FacetedNavigationAnalyzer:
    """Detect and analyze faceted navigation issues that may cause crawl traps or duplicate content."""

    # A predefined set of common URL parameters used in faceted navigation (filters, sorting, pagination).
    # Tracking these helps identify URLs that might generate thin or duplicate content.
    FACET_PARAMS = {
        "color", "size", "price", "sort", "order", "filter", "category",
        "brand", "rating", "page", "limit", "offset", "ref", "facet",
        "attr", "attribute", "tag", "type", "material", "style",
    }

    def __init__(self):
        # Initialize an empty list to store the URLs that will be analyzed.
        self.urls: list[str] = []

    def add_url(self, url: str) -> None:
        """Add a URL to the analyzer's dataset."""
        self.urls.append(url)

    def analyze(self) -> dict[str, any]:
        """
        Analyze the collected URLs to identify faceted navigation patterns and potential SEO risks.
        
        Returns:
            A dictionary containing metrics on parameter usage, duplicate path detection, 
            and actionable recommendations for managing faceted navigation.
        """
        # Initialize the report structure with default values and empty collections.
        report = {
            "total_parameter_urls": 0,
            "facet_parameters": Counter(),
            "duplicate_parameter_pages": [],
            "recommendations": [],
        }

        # Dictionary to group URLs by their base path (excluding query parameters).
        # This helps identify if a single page has an excessive number of filter variations.
        param_groups: dict[str, list[str]] = {}

        for url in self.urls:
            # Parse the URL to separate the base path from the query string.
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            
            # If there are no query parameters, skip to the next URL.
            if not params:
                continue

            # Increment the counter for URLs that contain at least one parameter.
            report["total_parameter_urls"] += 1
            base_path = parsed.path

            # Check each parameter key against the predefined set of known faceted navigation parameters.
            for key in params:
                if key.lower() in self.FACET_PARAMS:
                    report["facet_parameters"][key] += 1

            # Group the current URL under its base path for later duplicate/variant analysis.
            param_groups.setdefault(base_path, []).append(url)

        # Detect paths that have an excessive number of parameterized variations (potential duplicate content).
        for path, urls in param_groups.items():
            if len(urls) > 5:
                report["duplicate_parameter_pages"].append({
                    "path": path,
                    "count": len(urls),
                    "sample_urls": urls[:3],  # Provide up to 3 sample URLs for debugging/verification.
                })

        # Generate actionable SEO recommendations based on the analysis findings.
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

        # Return the comprehensive faceted navigation analysis report.
        return report