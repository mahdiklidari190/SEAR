"""Robots.txt Validation module."""
from __future__ import annotations

from core.parser import RobotsParser
from models.integrations import RobotsValidationResult


class RobotsValidator:
    """Validate robots.txt file."""

    @staticmethod
    def validate(robots_text: str, important_paths: list[str] = None) -> RobotsValidationResult:
        return RobotsParser.validate(robots_text, important_paths)