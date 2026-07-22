"""SEO Scoring Engine - preserved and extended."""
from __future__ import annotations

from models.page_data import PageData


class SEOScorer:
    """Calculate SEO scores across multiple dimensions."""

    @staticmethod
    def calculate(page: PageData) -> PageData:
        scores = {
            "Technical": 100,
            "Metadata": 100,
            "Content": 100,
            "Accessibility": 100,
            "Images": 100,
            "Links": 100,
            "Structured Data": 100,
            "Security": 100,
            "Performance": 100,
            "Mobile": 100,
        }

        # === PRESERVED: Issue-based deductions ===
        for issue in page.issues:
            deduction = {"Critical": 15, "High": 8, "Medium": 4, "Low": 1}.get(issue.severity, 0)
            category = issue.category
            if "Metadata" in category:
                scores["Metadata"] -= deduction
            elif "Heading" in category or "Content" in category or "Duplicate" in category:
                scores["Content"] -= deduction
            elif "Canonical" in category or "Hreflang" in category:
                scores["Technical"] -= deduction
            elif "Accessibility" in category:
                scores["Accessibility"] -= deduction
            elif "Image" in category:
                scores["Images"] -= deduction
            elif "Link" in category:
                scores["Links"] -= deduction
            elif "Structured" in category:
                scores["Structured Data"] -= deduction
            else:
                scores["Technical"] -= deduction

        # === PRESERVED: Image deductions ===
        if page.images.total > 0:
            if page.images.missing_alt > 0:
                scores["Images"] -= min(20, page.images.missing_alt * 2)
            if page.images.missing_dimensions > 0:
                scores["Technical"] -= 5

        # === PRESERVED: Accessibility deductions ===
        if not page.accessibility_lang:
            scores["Accessibility"] -= 10
        if page.accessibility_issues:
            scores["Accessibility"] -= 10

        # === PRESERVED: Structured data deductions ===
        if not page.structured_data.found:
            scores["Structured Data"] = 50
        if page.structured_data.errors:
            scores["Structured Data"] -= 20

        # === NEW: Security scoring ===
        sec_issues = len(page.security_headers.issues)
        scores["Security"] -= sec_issues * 8
        if not page.security_headers.hsts:
            scores["Security"] -= 10

        # === NEW: Performance scoring ===
        if page.performance.ttfb_ms > 800:
            scores["Performance"] -= 20
        elif page.performance.ttfb_ms > 400:
            scores["Performance"] -= 10
        if not page.performance.compression:
            scores["Performance"] -= 10
        if page.js_rendering.render_blocking_scripts:
            scores["Performance"] -= min(15, len(page.js_rendering.render_blocking_scripts) * 3)

        # === NEW: Mobile scoring ===
        if not page.mobile.has_viewport:
            scores["Mobile"] -= 30
        if not page.mobile.is_mobile_friendly:
            scores["Mobile"] -= 20
        if not page.mobile.responsive_images:
            scores["Mobile"] -= 5

        # Clamp all scores
        for k in scores:
            scores[k] = max(0, min(100, scores[k]))

        page.scores = scores
        page.overall_score = int(sum(scores.values()) / len(scores))
        return page