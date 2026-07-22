"""Breadcrumb Validation."""
from __future__ import annotations

from models.page_data import PageData


class BreadcrumbValidator:
    """Validate breadcrumb implementation."""

    @staticmethod
    def analyze(page: PageData) -> dict[str, any]:
        bc = page.breadcrumbs
        report = {
            "found": bc.found,
            "schema_valid": bc.schema_valid,
            "hierarchy_correct": bc.hierarchy_correct,
            "items": bc.items,
            "issues": bc.issues,
            "recommendations": [],
        }

        if not bc.found:
            report["recommendations"].append(
                "Add BreadcrumbList JSON-LD schema and visible breadcrumb navigation"
            )
        if bc.found and not bc.schema_valid:
            report["recommendations"].append(
                "Breadcrumb found but missing valid BreadcrumbList schema markup"
            )
        if not bc.hierarchy_correct:
            report["recommendations"].append(
                "Fix breadcrumb position values to match visual hierarchy"
            )

        return report