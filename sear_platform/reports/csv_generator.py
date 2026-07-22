"""CSV Report Generator."""
from __future__ import annotations

import csv
import io

from models.page_data import PageData


class CSVReportGenerator:
    """Generate CSV summary reports."""

    @staticmethod
    def generate_pages_summary(pages: list[PageData]) -> str:
        """Generate a CSV summary of all analyzed pages."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "URL", "Status", "Score", "Title", "Title Length",
            "Meta Description", "Meta Desc Length", "H1 Count",
            "Word Count", "Internal Links", "External Links",
            "Images", "Missing Alt", "Issues Count", "Critical Issues",
            "Canonical", "Structured Data", "Mobile Friendly",
        ])

        for page in pages:
            critical_count = len([i for i in page.issues if i.severity == "Critical"])
            writer.writerow([
                page.url,
                page.status_code,
                page.overall_score,
                page.title[:100],
                len(page.title),
                page.meta_description[:150],
                len(page.meta_description),
                len(page.h1),
                page.word_count,
                page.links.internal,
                page.links.external,
                page.images.total,
                page.images.missing_alt,
                len(page.issues),
                critical_count,
                page.canonical_url or "MISSING",
                "Yes" if page.structured_data.found else "No",
                "Yes" if page.mobile.is_mobile_friendly else "No",
            ])

        return output.getvalue()

    @staticmethod
    def generate_issues_csv(pages: list[PageData]) -> str:
        """Generate CSV of all issues across pages."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["URL", "Category", "Severity", "Problem", "Solution", "Difficulty", "Fix Time"])

        for page in pages:
            for issue in page.issues:
                writer.writerow([
                    page.url, issue.category, issue.severity,
                    issue.problem, issue.solution, issue.difficulty, issue.fix_time,
                ])

        return output.getvalue()