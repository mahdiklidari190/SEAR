"""Anchor Text Distribution Analysis."""
from __future__ import annotations

import re
from collections import Counter


class AnchorTextAnalyzer:
    """Analyze anchor text distribution across pages to ensure a natural and SEO-friendly linking profile."""

    def __init__(self):
        # Initialize an empty list to store anchor text data.
        # Each entry is expected to be a dictionary containing 'text', 'url', and 'type' (internal/external).
        self.anchors: list[dict[str, str]] = []

    def add_anchors(self, anchor_list: list[dict[str, str]], page_url: str) -> None:
        """
        Add a list of anchors to the analyzer, enriching each with the source page URL.
        
        Args:
            anchor_list: A list of dictionaries containing anchor text details.
            page_url: The URL of the page where these anchors were found.
        """
        for a in anchor_list:
            # Merge the original anchor data with the source page context.
            self.anchors.append({**a, "source_page": page_url})

    def analyze(self) -> dict[str, any]:
        """
        Process the collected anchor data and produce a comprehensive distribution report.
        
        Returns:
            A dictionary containing metrics, top anchors, and actionable SEO recommendations.
        """
        # Initialize the report structure with default counts and empty lists.
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

        # Define a set of common, non-descriptive phrases that provide little SEO value.
        generic_patterns = {"click here", "read more", "learn more", "here", "this", "link", "more", "view"}
        
        # Use Counter to efficiently track the frequency of each unique anchor text.
        text_counter = Counter()

        # Iterate through all collected anchors to categorize them based on SEO best practices.
        for a in self.anchors:
            text = a.get("text", "").strip().lower()

            if not text:
                # Anchor has no text (common in image links or empty <a> tags).
                distribution["empty"] += 1
            elif text.startswith("http") or re.match(r"^www\.", text):
                # The raw URL itself is being used as the anchor text.
                distribution["url_as_anchor"] += 1
            elif text in generic_patterns:
                # The anchor matches a known low-value generic phrase.
                distribution["generic"] += 1
            elif len(text.split()) <= 2:
                # Short anchors (1-2 words) are typically classified as exact-match or brand keywords.
                distribution["exact_match"] += 1
            else:
                # Longer, multi-word anchors are generally considered partial-match or natural phrases.
                distribution["partial_match"] += 1

            # Track frequency only for non-empty anchor texts.
            if text:
                text_counter[text] += 1

        # Extract the 15 most frequently used anchor texts to identify potential over-optimization patterns.
        distribution["top_anchors"] = [
            {"text": t, "count": c} for t, c in text_counter.most_common(15)
        ]

        # Generate actionable SEO recommendations based on the calculated ratios.
        # Prevent division by zero by ensuring the total is at least 1.
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