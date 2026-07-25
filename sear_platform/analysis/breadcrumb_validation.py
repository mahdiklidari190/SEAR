"""Breadcrumb Validation."""
from __future__ import annotations

# Import the core data model used to pass page-specific information to the validator.
from models.page_data import PageData


class BreadcrumbValidator:
    """Validate breadcrumb implementation."""

    @staticmethod
    def analyze(page: PageData) -> dict[str, any]:
        # Extract the specific breadcrumb data object from the main page data model for cleaner and more readable access.
        bc = page.breadcrumbs
        
        # Initialize the validation report structure. 
        # This dictionary aggregates the raw breadcrumb data, boolean validation flags, and an empty list for actionable recommendations.
        report = {
            "found": bc.found,
            "schema_valid": bc.schema_valid,
            "hierarchy_correct": bc.hierarchy_correct,
            "items": bc.items,
            "issues": bc.issues,
            "recommendations": [],
        }

        # Evaluate the breadcrumb implementation against SEO best practices and generate specific recommendations for any detected issues.
        
        # Check 1: If no breadcrumbs are detected on the page at all.
        if not bc.found:
            report["recommendations"].append(
                "Add BreadcrumbList JSON-LD schema and visible breadcrumb navigation"
            )
            
        # Check 2: If breadcrumbs exist visually but lack valid structured data (schema markup).
        if bc.found and not bc.schema_valid:
            report["recommendations"].append(
                "Breadcrumb found but missing valid BreadcrumbList schema markup"
            )
            
        # Check 3: If the logical hierarchy (position values) doesn't match the visual order on the page.
        if not bc.hierarchy_correct:
            report["recommendations"].append(
                "Fix breadcrumb position values to match visual hierarchy"
            )

        # Return the comprehensive validation report, including all findings and actionable steps, to the caller.
        return report