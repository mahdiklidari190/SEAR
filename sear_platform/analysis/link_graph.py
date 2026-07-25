"""Internal Link Graph Analysis."""
from __future__ import annotations

# Import defaultdict to automatically initialize lists and integers for our graph adjacency mappings.
from collections import defaultdict

# Import the data models used to structure the final link graph report and individual node data.
from models.integrations import LinkGraphData, LinkGraphNode


class LinkGraphAnalyzer:
    """Build and analyze the internal link graph."""

    def __init__(self):
        # Initialize the core data structures needed to build the directed graph.
        # 'edges' stores the raw connections, 'all_pages' tracks unique URLs,
        # and 'outlinks'/'inlinks' provide quick adjacency list lookups for graph traversal.
        self.edges: list[tuple[str, str]] = []
        self.all_pages: set[str] = set()
        self.outlinks: dict[str, list[str]] = defaultdict(list)
        self.inlinks: dict[str, list[str]] = defaultdict(list)

    def add_page(self, url: str) -> None:
        # Register a discovered page URL in our global set of tracked pages.
        self.all_pages.add(url)

    def add_link(self, source: str, target: str) -> None:
        # Record a directed internal link from a source page to a target page.
        # We update the raw edge list, the adjacency lists for both directions,
        # and ensure both the source and target URLs are tracked in the global page set.
        self.edges.append((source, target))
        self.outlinks[source].append(target)
        self.inlinks[target].append(source)
        self.all_pages.add(source)
        self.all_pages.add(target)

    def analyze(self) -> LinkGraphData:
        """Compute graph metrics."""
        # Initialize the report data structure and populate the basic aggregate counts.
        data = LinkGraphData()
        data.total_pages = len(self.all_pages)
        data.total_internal_links = len(self.edges)

        # If no pages were discovered during the crawl, return the empty report immediately to avoid division by zero.
        if not self.all_pages:
            return data

        # Calculate the in-degree (number of incoming links) and out-degree (number of outgoing links)
        # for every page in the graph. These metrics are fundamental for identifying structural SEO issues.
        in_degree: dict[str, int] = defaultdict(int)
        out_degree: dict[str, int] = defaultdict(int)

        for src, tgt in self.edges:
            out_degree[src] += 1
            in_degree[tgt] += 1

        # Identify "orphan" pages: pages that have outgoing links but receive zero internal links.
        # These pages are essentially dead-ends for crawlers navigating from within the site.
        for page in self.all_pages:
            if in_degree.get(page, 0) == 0 and out_degree.get(page, 0) > 0:
                data.orphan_pages.append(page)

        # Identify "hub" pages: pages that link out significantly more than the average page.
        # We define a hub as having an out-degree greater than twice the site's average out-degree.
        avg_out = sum(out_degree.values()) / max(len(out_degree), 1)
        for page, degree in out_degree.items():
            if degree > avg_out * 2:
                data.hub_pages.append(page)

        # Identify "weak" pages: pages that receive very little internal link equity.
        # We flag pages that have at least one inlink, but no more than one, indicating poor internal linking support.
        for page in self.all_pages:
            if 0 < in_degree.get(page, 0) <= 1:
                data.weak_pages.append(page)

        # Build the detailed node data for each page, including a simplified authority score.
        # This score is a basic PageRank-like metric calculated as the percentage of total site links
        # that point to this specific page, giving a quick indicator of its relative SEO weight.
        total_links = max(len(self.edges), 1)
        for page in self.all_pages:
            in_d = in_degree.get(page, 0)
            out_d = out_degree.get(page, 0)
            authority = round(in_d / total_links * 100, 2)
            data.nodes.append(LinkGraphNode(
                url=page,
                inlinks=in_d,
                outlinks=out_d,
                is_orphan=page in data.orphan_pages,
                is_hub=page in data.hub_pages,
                authority_score=authority,
            ))

        # Format the edges for frontend visualization.
        # We cap this at 500 edges to prevent the resulting JSON payload from becoming excessively large and slow to render.
        data.edges = [{"source": s, "target": t} for s, t in self.edges[:500]]  # Limit for JSON size

        # Calculate the average number of internal links per page across the entire site.
        data.avg_links_per_page = round(len(self.edges) / max(len(self.all_pages), 1), 1)

        # Return the fully populated link graph data object to the caller.
        return data