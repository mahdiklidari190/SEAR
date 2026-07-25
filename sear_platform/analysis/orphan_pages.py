"""Orphan Page Detection."""
from __future__ import annotations

# Import the data model that represents the internal link graph structure.
from models.integrations import LinkGraphData


class OrphanPageDetector:
    """Detect pages with no internal links pointing to them."""

    @staticmethod
    def detect(link_graph: LinkGraphData, sitemap_urls: list[str]) -> list[dict[str, str]]:
        """
        Find orphan pages by comparing sitemap URLs with the actual linked pages in the crawl.
        
        Args:
            link_graph: The analyzed internal link graph containing nodes and edges.
            sitemap_urls: A list of URLs extracted from the site's XML sitemap(s).
            
        Returns:
            A list of dictionaries detailing the orphaned URLs, the reason they are orphaned, 
            and the SEO severity of the issue.
        """
        orphans = []

        # Build a comprehensive set of all pages that participate in the internal link graph.
        # We include both sources and targets to get a complete picture of connected pages.
        # Using a set ensures O(1) time complexity for the subsequent membership checks.
        linked_pages = set()
        for edge in link_graph.edges:
            linked_pages.add(edge.get("target", ""))
            linked_pages.add(edge.get("source", ""))

        # The link graph analyzer already identifies structural orphans (nodes with zero in-degree).
        # We extract these and flag them as 'High' severity since they are completely disconnected 
        # from the site's internal navigation, making them very difficult for crawlers to discover.
        for node in link_graph.nodes:
            if node.is_orphan:
                orphans.append({
                    "url": node.url,
                    "reason": "No internal links pointing to this page",
                    "severity": "High",
                })

        # Check for 'sitemap orphans'. These are pages declared in the XML sitemap but completely 
        # missing from the crawled link graph. They are flagged as 'Medium' severity because, 
        # while they lack internal links, the sitemap still provides a discovery path for search engine crawlers.
        for url in sitemap_urls:
            if url not in linked_pages:
                orphans.append({
                    "url": url,
                    "reason": "In sitemap but not linked from any crawled page",
                    "severity": "Medium",
                })

        # Return the consolidated list of all detected orphan pages.
        return orphans