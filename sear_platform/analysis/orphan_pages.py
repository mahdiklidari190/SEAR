"""Orphan Page Detection."""
from __future__ import annotations

from models.integrations import LinkGraphData


class OrphanPageDetector:
    """Detect pages with no internal links pointing to them."""

    @staticmethod
    def detect(link_graph: LinkGraphData, sitemap_urls: list[str]) -> list[dict[str, str]]:
        """Find orphan pages by comparing sitemap URLs with linked pages."""
        orphans = []

        # Pages in sitemap but not in link graph
        linked_pages = set()
        for edge in link_graph.edges:
            linked_pages.add(edge.get("target", ""))
            linked_pages.add(edge.get("source", ""))

        for node in link_graph.nodes:
            if node.is_orphan:
                orphans.append({
                    "url": node.url,
                    "reason": "No internal links pointing to this page",
                    "severity": "High",
                })

        # Sitemap URLs not found in crawl
        for url in sitemap_urls:
            if url not in linked_pages:
                orphans.append({
                    "url": url,
                    "reason": "In sitemap but not linked from any crawled page",
                    "severity": "Medium",
                })

        return orphans