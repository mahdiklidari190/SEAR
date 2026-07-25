"""Enhanced Canonical Validation."""
from __future__ import annotations

# Import urlparse to extract and compare domain names from URLs.
from urllib.parse import urlparse

# Import data models representing page information and SEO issues.
from models.page_data import PageData
from models.issues import Issue


class CanonicalValidator:
    """Deep canonical analysis across multiple pages."""

    def __init__(self):
        # Dictionary to map each page URL to its declared canonical URL.
        # This allows for cross-referencing and detecting complex canonicalization issues.
        self.canonical_map: dict[str, str] = {}  # url -> canonical

    def add_page(self, page: PageData) -> None:
        """
        Add a page's URL and its canonical URL to the tracking map.
        
        Args:
            page: The PageData object containing the URL and canonical information.
        """
        self.canonical_map[page.url] = page.canonical_url

    def analyze(self) -> list[dict[str, str]]:
        """
        Detect canonical issues across all tracked pages.
        
        Returns:
            A list of dictionaries, each representing a detected canonical issue 
            with its URL, issue type, details, and severity level.
        """
        issues = []

        # 1. Detect canonical chains (e.g., Page A points to Page B, which points to Page C).
        # Search engines may drop canonical signals if the chain is too long.
        for url, canonical in self.canonical_map.items():
            if canonical and canonical in self.canonical_map:
                next_canon = self.canonical_map[canonical]
                if next_canon and next_canon != canonical:
                    issues.append({
                        "url": url,
                        "issue": "canonical_chain",
                        "detail": f"{url} -> {canonical} -> {next_canon}",
                        "severity": "High",
                    })

        # 2. Detect canonical loops (e.g., Page A points to Page B, and Page B points back to Page A).
        # This creates an infinite resolution loop that confuses search engine crawlers.
        for url, canonical in self.canonical_map.items():
            if canonical and canonical in self.canonical_map:
                if self.canonical_map.get(canonical) == url:
                    issues.append({
                        "url": url,
                        "issue": "canonical_loop",
                        "detail": f"{url} <-> {canonical}",
                        "severity": "Critical",
                    })

        # 3. Detect cross-domain canonicals.
        # A page should generally point to a canonical URL on the same domain, 
        # unless it's a specific syndication or migration scenario.
        for url, canonical in self.canonical_map.items():
            if canonical:
                # Normalize domains by converting to lowercase and removing 'www.' for accurate comparison.
                url_domain = urlparse(url).netloc.lower().replace("www.", "")
                canon_domain = urlparse(canonical).netloc.lower().replace("www.", "")
                
                if url_domain != canon_domain:
                    issues.append({
                        "url": url,
                        "issue": "cross_domain_canonical",
                        "detail": f"Points to {canon_domain}",
                        "severity": "Critical",
                    })

        # 4. Detect multiple pages pointing to the same canonical (potential consolidation mismatch).
        # While sometimes intentional, a high number of pages pointing to one canonical 
        # might indicate a site structure issue or accidental duplication.
        canonical_targets: dict[str, list[str]] = {}
        for url, canonical in self.canonical_map.items():
            if canonical:
                # Group all source URLs by their target canonical URL.
                canonical_targets.setdefault(canonical, []).append(url)

        for target, sources in canonical_targets.items():
            # Flag if more than 3 distinct pages are pointing to the exact same canonical target.
            if len(sources) > 3:
                issues.append({
                    "url": target,
                    "issue": "canonical_consolidation",
                    "detail": f"{len(sources)} pages point to this canonical",
                    "severity": "Medium",
                })

        # Return the compiled list of all detected canonical issues for reporting.
        return issues