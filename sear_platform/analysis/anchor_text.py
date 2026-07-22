"""Anchor Text Distribution Analysis."""
from __future__ import annotations

import re
from collections import Counter


class AnchorTextAnalyzer:
    """Analyze anchor text distribution across pages."""

    def __init__(self):
        self.anchors: list[dict[str, str]] = []  # {"text": ..., "url": ..., "type": internal/external}

    def add_anchors(self, anchor_list: list[dict[str, str]], page_url: str) -> None:
        for a in anchor_list:
            self.anchors.append({**a, "source_page": page_url})

    def analyze(self) -> dict[str, any]:
        """Produce anchor text distribution report."""
        distribution = {
            "total_anchors": len(self.anchors),
            "exact_match": 0,
            "partial_match": 0,
            "generic": 0,
            "brand": 0,
            "empty": 0,
            "image_anchors": 0,
            "url_as_anchor": 0,
            "top_anchors": [],
            "recommendations": [],
        }

        generic_patterns = {"click here", "read more", "learn more", "here", "this", "link", "more", "view"}
        text_counter = Counter()

        for a in self.anchors:
            text = a.get("text", "").strip().lower()

            if not text:
                distribution["empty"] += 1
            elif text.startswith("http") or re.match(r"^www\.", text):
                distribution["url_as_anchor"] += 1
            elif text in generic_patterns:
                distribution["generic"] += 1
            elif len(text.split()) <= 2:
                distribution["exact_match"] += 1
            else:
                distribution["partial_match"] += 1

            if text:
                text_counter[text] += 1

        distribution["top_anchors"] = [
            {"text": t, "count": c} for t, c in text_counter.most_common(15)
        ]

        # Recommendations
        total = max(distribution["total_anchors"], 1)
        if distribution["generic"] / total > 0.3:
            distribution["recommendations"].append(
                "Too many generic anchors ('click here', 'read more'). Use descriptive anchor text."
            )
        if distribution["empty"] / total > 0.1:
            distribution["recommendations"].append(
                f"{distribution['empty']} empty anchor texts found. Add descriptive text."
            )
        if distribution["exact_match"] / total > 0.5:
            distribution["recommendations"].append(
                "Over-optimized anchor text detected. Diversify with partial match and natural phrases."
            )

        return distribution