"""Enhanced Canonical Validation."""
from __future__ import annotations

from urllib.parse import urlparse

from models.page_data import PageData
from models.issues import Issue


class CanonicalValidator:
    """Deep canonical analysis across multiple pages."""

    def __init__(self):
        self.canonical_map: dict[str, str] = {}  # url -> canonical

    def add_page(self, page: PageData) -> None:
        self.canonical_map[page.url] = page.canonical_url

    def analyze(self) -> list[dict[str, str]]:
        """Detect canonical issues across all pages."""
        issues = []

        # Detect canonical chains (A -> B -> C)
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

        # Detect canonical loops
        for url, canonical in self.canonical_map.items():
            if canonical and canonical in self.canonical_map:
                if self.canonical_map.get(canonical) == url:
                    issues.append({
                        "url": url,
                        "issue": "canonical_loop",
                        "detail": f"{url} <-> {canonical}",
                        "severity": "Critical",
                    })

        # Detect cross-domain canonicals
        for url, canonical in self.canonical_map.items():
            if canonical:
                url_domain = urlparse(url).netloc.lower().replace("www.", "")
                canon_domain = urlparse(canonical).netloc.lower().replace("www.", "")
                if url_domain != canon_domain:
                    issues.append({
                        "url": url,
                        "issue": "cross_domain_canonical",
                        "detail": f"Points to {canon_domain}",
                        "severity": "Critical",
                    })

        # Detect multiple pages pointing to same canonical (potential mismatch)
        canonical_targets: dict[str, list[str]] = {}
        for url, canonical in self.canonical_map.items():
            if canonical:
                canonical_targets.setdefault(canonical, []).append(url)

        for target, sources in canonical_targets.items():
            if len(sources) > 3:
                issues.append({
                    "url": target,
                    "issue": "canonical_consolidation",
                    "detail": f"{len(sources)} pages point to this canonical",
                    "severity": "Medium",
                })

        return issues