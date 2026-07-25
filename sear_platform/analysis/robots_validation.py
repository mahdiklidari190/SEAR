"""Robots.txt Validation module."""
from __future__ import annotations

# Import the core parsing logic that handles the actual syntax checking and rule evaluation of the robots.txt file.
from core.parser import RobotsParser

# Import the structured data model used to return the validation results, including any detected issues, warnings, or parsed rules.
from models.integrations import RobotsValidationResult


class RobotsValidator:
    """Validate robots.txt file."""

    @staticmethod
    def validate(robots_text: str, important_paths: list[str] = None) -> RobotsValidationResult:
        # This method acts as a clean, high-level interface for robots.txt validation.
        # It accepts the raw text content of the file and an optional list of critical URL paths that must not be blocked.
        
        # Delegate the actual parsing, syntax checking, and rule-matching logic to the core RobotsParser.
        # This separation of concerns keeps the validator class lightweight while relying on the specialized parser for the heavy lifting.
        return RobotsParser.validate(robots_text, important_paths)