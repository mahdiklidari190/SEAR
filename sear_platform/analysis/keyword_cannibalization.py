"""Keyword Cannibalization Detection."""
from __future__ import annotations

from collections import defaultdict


class KeywordCannibalizationDetector:
    """Detect pages competing for the same keywords."""

    def __init__(self):
        self.page_keywords: dict[str, list[str]] = {}  # url -> keywords

    def add_page(self, url: str, keywords: str) -> None:
        kws = [k.strip().lower() for k in keywords.split(",") if k.strip()]
        self.page_keywords[url] = kws

    def detect(self) -> list[dict[str, any]]:
        """Find keyword cannibalization instances."""
        keyword_pages: dict[str, list[str]] = defaultdict(list)

        for url, kws in self.page_keywords.items():
            for kw in kws:
                keyword_pages[kw].append(url)

        cannibalization = []
        for kw, urls in keyword_pages.items():
            if len(urls) > 1:
                cannibalization.append({
                    "keyword": kw,
                    "competing_pages": urls,
                    "count": len(urls),
                    "recommendation": f"Consolidate content for '{kw}' into one authoritative page, "
                                     f"or differentiate targeting for each page.",
                })

        # Sort by number of competing pages
        cannibalization.sort(key=lambda x: x["count"], reverse=True)
        return cannibalization[:20]