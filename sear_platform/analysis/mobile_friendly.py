"""Mobile Friendly Analysis."""
from __future__ import annotations

from models.page_data import PageData


class MobileFriendlyAnalyzer:
    """Analyze mobile-friendliness."""

    @staticmethod
    def analyze(page: PageData) -> dict[str, any]:
        mobile = page.mobile
        report = {
            "has_viewport": mobile.has_viewport,
            "viewport_content": mobile.viewport_content,
            "is_mobile_friendly": mobile.is_mobile_friendly,
            "responsive_images": mobile.responsive_images,
            "font_issues": mobile.font_size_issues,
            "tap_target_issues": mobile.tap_target_issues,
            "score": 100,
            "recommendations": [],
        }

        if not mobile.has_viewport:
            report["score"] -= 40
            report["recommendations"].append("Add <meta name='viewport' content='width=device-width, initial-scale=1'>")
        if not mobile.responsive_images:
            report["score"] -= 10
            report["recommendations"].append("Use srcset/picture elements for responsive images")
        if mobile.font_size_issues:
            report["score"] -= 15

        report["score"] = max(0, report["score"])
        return report