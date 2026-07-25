"""Duplicate content detector - preserved from original."""
from __future__ import annotations


class DuplicateDetector:
    """Track duplicate titles, descriptions, and H1s across pages."""

    def __init__(self):
        # Initialize dictionaries to map content strings to the URLs where they were first encountered.
        # This allows the system to quickly identify and flag duplicate on-page SEO elements across the entire site crawl.
        self.seen_titles: dict[str, str] = {}
        self.seen_descriptions: dict[str, str] = {}
        self.seen_h1: dict[str, str] = {}

    def reset(self):
        """
        Clear all tracked content records.
        This is useful when starting a fresh crawl session or re-evaluating a new set of pages 
        without carrying over state from previous analyses.
        """
        self.seen_titles.clear()
        self.seen_descriptions.clear()
        self.seen_h1.clear()


# Instantiate a global singleton object to maintain a centralized state of duplicate content 
# across different modules and analysis phases without needing to pass the instance around manually.
duplicate_detector = DuplicateDetector()