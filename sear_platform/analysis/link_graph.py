"""Internal Link Graph Analysis."""
from __future__ import annotations

from collections import defaultdict

from models.integrations import LinkGraphData, LinkGraphNode


class LinkGraphAnalyzer:
    """Build and analyze the internal link graph."""

    def __init__(self):
        self.edges: list[tuple[str, str]] = []
        self.all_pages: set[str] = set()
        self.outlinks: dict[str, list[str]] = defaultdict(list)
        self.inlinks: dict[str, list[str]] = defaultdict(list)

    def add_page(self, url: str) -> None:
        self.all_pages.add(url)

    def add_link(self, source: str, target: str) -> None:
        self.edges.append((source, target))
        self.outlinks[source].append(target)
        self.inlinks[target].append(source)
        self.all_pages.add(source)
        self.all_pages.add(target)

    def analyze(self) -> LinkGraphData:
        """Compute graph metrics."""
        data = LinkGraphData()
        data.total_pages = len(self.all_pages)
        data.total_internal_links = len(self.edges)

        if not self.all_pages:
            return data

        # Calculate in-degree and out-degree
        in_degree: dict[str, int] = defaultdict(int)
        out_degree: dict[str, int] = defaultdict(int)

        for src, tgt in self.edges:
            out_degree[src] += 1
            in_degree[tgt] += 1

        # Orphan pages: no inlinks
        for page in self.all_pages:
            if in_degree.get(page, 0) == 0 and out_degree.get(page, 0) > 0:
                data.orphan_pages.append(page)

        # Hub pages: high out-degree
        avg_out = sum(out_degree.values()) / max(len(out_degree), 1)
        for page, degree in out_degree.items():
            if degree > avg_out * 2:
                data.hub_pages.append(page)

        # Weak pages: very few inlinks
        for page in self.all_pages:
            if 0 < in_degree.get(page, 0) <= 1:
                data.weak_pages.append(page)

        # Build node data with simple PageRank-like authority
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

        # Edges for visualization
        data.edges = [{"source": s, "target": t} for s, t in self.edges[:500]]  # Limit for JSON size

        data.avg_links_per_page = round(len(self.edges) / max(len(self.all_pages), 1), 1)

        return data