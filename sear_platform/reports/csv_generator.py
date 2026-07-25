"""CSV Report Generator."""
# This module handles the generation of Comma-Separated Values (CSV) reports.
# CSV format is highly preferred for exporting tabular SEO data, allowing users 
# to easily import the results into spreadsheet applications like Excel or Google Sheets 
# for advanced filtering, sorting, and manual project management.
from __future__ import annotations

import csv
import io

# Import the core data model containing the extracted page metrics.
from models.page_data import PageData


class CSVReportGenerator:
    """Generate CSV summary reports for bulk SEO data analysis."""

    @staticmethod
    def generate_pages_summary(pages: list[PageData]) -> str:
        """
        Generate a high-level CSV summary of all analyzed pages.
        This provides a quick, at-a-glance overview of the health and key metrics of every crawled URL.
        """
        # Use an in-memory string buffer to build the CSV content.
        # This avoids the overhead and cleanup requirements of writing to temporary physical files.
        output = io.StringIO()
        writer = csv.writer(output)

        # Define and write the header row, establishing the columns for the spreadsheet.
        writer.writerow([
            "URL", "Status", "Score", "Title", "Title Length",
            "Meta Description", "Meta Desc Length", "H1 Count",
            "Word Count", "Internal Links", "External Links",
            "Images", "Missing Alt", "Issues Count", "Critical Issues",
            "Canonical", "Structured Data", "Mobile Friendly",
        ])

        # Iterate through each page to extract and format its core metrics.
        for page in pages:
            # Pre-calculate the number of critical issues to highlight severely broken pages.
            critical_count = len([i for i in page.issues if i.severity == "Critical"])
            
            writer.writerow([
                page.url,
                page.status_code,
                page.overall_score,
                # Truncate long text fields to prevent CSV cell bloat and maintain readability.
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

        # Retrieve the complete CSV string from the memory buffer and return it.
        return output.getvalue()

    @staticmethod
    def generate_issues_csv(pages: list[PageData]) -> str:
        """
        Generate a comprehensive, flattened CSV of all issues detected across all pages.
        This is highly useful for SEO specialists who need to sort, filter, and prioritize 
        technical and on-page errors across the entire website in a single spreadsheet.
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Define the header row specifically tailored for issue tracking and ticketing.
        writer.writerow(["URL", "Category", "Severity", "Problem", "Solution", "Difficulty", "Fix Time"])

        # Iterate through every page, and then through every issue within that page.
        for page in pages:
            for issue in page.issues:
                writer.writerow([
                    page.url, 
                    issue.category, 
                    issue.severity,
                    issue.problem, 
                    issue.solution, 
                    issue.difficulty, 
                    issue.fix_time,
                ])

        return output.getvalue()