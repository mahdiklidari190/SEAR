"""Duplicate content detector - preserved from original."""
from __future__ import annotations


class DuplicateDetector:
    """Track duplicate titles, descriptions, and H1s across pages."""

    def __init__(self):
        self.seen_titles: dict[str, str] = {}
        self.seen_descriptions: dict[str, str] = {}
        self.seen_h1: dict[str, str] = {}

    def reset(self):
        self.seen_titles.clear()
        self.seen_descriptions.clear()
        self.seen_h1.clear()


# Global singleton - preserved from original
duplicate_detector = DuplicateDetector()