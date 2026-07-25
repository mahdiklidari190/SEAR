"""Keyword Cannibalization Detection."""
from __future__ import annotations

# Import defaultdict to easily group URLs by their target keywords without needing to manually check if a key already exists.
from collections import defaultdict


class KeywordCannibalizationDetector:
    """Detect pages competing for the same keywords."""

    def __init__(self):
        # Initialize a dictionary to map each page URL to its list of target keywords.
        # This serves as the foundational data structure for identifying overlapping keyword strategies across the site.
        self.page_keywords: dict[str, list[str]] = {}  # url -> keywords

    def add_page(self, url: str, keywords: str) -> None:
        # Parse the comma-separated keyword string into a clean, lowercase list of individual keywords.
        # This normalization ensures accurate matching regardless of casing or accidental extra whitespace.
        kws = [k.strip().lower() for k in keywords.split(",") if k.strip()]
        
        # Store the processed keywords associated with the specific page URL.
        self.page_keywords[url] = kws

    def detect(self) -> list[dict[str, any]]:
        """Find keyword cannibalization instances."""
        # Create an inverted mapping where each keyword points to a list of URLs targeting it.
        # This structural flip allows us to quickly identify which keywords are being targeted by multiple pages.
        keyword_pages: dict[str, list[str]] = defaultdict(list)

        # Iterate through all pages and their respective keywords to populate the inverted map.
        for url, kws in self.page_keywords.items():
            for kw in kws:
                keyword_pages[kw].append(url)

        cannibalization = []
        
        # Identify keywords that have more than one page competing for them (the definition of cannibalization).
        for kw, urls in keyword_pages.items():
            if len(urls) > 1:
                # Record the cannibalization instance, including the competing pages and a strategic recommendation for resolution.
                cannibalization.append({
                    "keyword": kw,
                    "competing_pages": urls,
                    "count": len(urls),
                    "recommendation": f"Consolidate content for '{kw}' into one authoritative page, "
                                     f"or differentiate targeting for each page.",
                })

        # Sort the detected cannibalization issues by the number of competing pages in descending order.
        # This prioritizes the most severe instances of keyword overlap, where multiple pages are diluting each other's authority.
        cannibalization.sort(key=lambda x: x["count"], reverse=True)
        
        # Return only the top 20 most critical cannibalization instances to keep the final report focused and actionable.
        return cannibalization[:20]