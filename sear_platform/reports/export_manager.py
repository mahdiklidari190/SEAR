"""Export Manager - orchestrates all report formats with robust error handling."""
# This module acts as the central orchestrator for the reporting engine.
# It manages the generation and file system storage of all SEO analysis outputs,
# ensuring that if one specific format fails (e.g., PDF generation), the others 
# (e.g., JSON, CSV) still complete successfully.
from __future__ import annotations

import logging
from pathlib import Path

# Import core data models required for report generation.
from models.page_data import PageData
from models.reports import CompetitorData
from models.integrations import (
    SearchConsoleData, AnalyticsData, BacklinkData,
    CrawlBudgetReport, LinkGraphData, CoreWebVitals,
)

# Import the specific generator classes for each supported output format.
from .txt_generator import TXTReportGenerator
from .json_generator import JSONReportGenerator
from .csv_generator import CSVReportGenerator
from .html_dashboard import HTMLDashboardGenerator
from .pdf_generator import PDFReportGenerator

logger = logging.getLogger(__name__)


class ExportManager:
    """
    Manage the export of all report formats.
    This class handles directory creation, filename sanitization, and delegates 
    the actual content generation to specialized generator classes.
    """

    def __init__(self, base_dir: Path):
        # Define the root directory for all exports.
        self.base_dir = base_dir
        
        # Create specific subdirectories for each report format to keep the output organized.
        self.txt_dir = base_dir / "txt"
        self.json_dir = base_dir / "json"
        self.csv_dir = base_dir / "csv"
        self.pdf_dir = base_dir / "pdf"
        # Prepared for future storage of screenshots, charts, or supplementary assets.
        self.assets_dir = base_dir / "assets"

        # Ensure all required directories exist, creating them recursively if necessary.
        for d in [self.txt_dir, self.json_dir, self.csv_dir, self.pdf_dir, self.assets_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def export_page(
        self,
        page: PageData,
        filename: str,
        competitors: list[CompetitorData],
        keywords: str,
        robots_txt: str,
        ai_prompt: str,
        search_console: SearchConsoleData = None,
        analytics: AnalyticsData = None,
        backlinks: BacklinkData = None,
        crawl_budget: CrawlBudgetReport = None,
        link_graph: LinkGraphData = None,
        cwv: CoreWebVitals = None,
    ) -> dict[str, Path]:
        """
        Export a single page's analysis in all available detailed formats (TXT, JSON, PDF).
        
        Returns:
            A dictionary mapping the format name to the Path of the successfully generated file.
        """
        paths = {}
        # Prevent empty filenames by providing a safe default fallback.
        safe_filename = filename if filename else "homepage"

        # =========================================================================
        # 1. TEXT REPORT (TXT)
        # Generates a human-readable, plain text summary of the page analysis.
        # =========================================================================
        try:
            txt_content = TXTReportGenerator.generate(
                page, competitors, keywords, robots_txt, ai_prompt, search_console, analytics
            )
            txt_path = self.txt_dir / f"{safe_filename}.txt"
            txt_path.write_text(txt_content, encoding="utf-8")
            paths["txt"] = txt_path
        except Exception as e:
            # Log the error but continue execution to ensure other formats are still generated.
            logger.error(f"TXT export failed for {safe_filename}: {e}")

        # =========================================================================
        # 2. JSON REPORT
        # Generates a comprehensive, machine-readable JSON payload containing all raw data.
        # =========================================================================
        try:
            json_content = JSONReportGenerator.generate(
                page, competitors, keywords, robots_txt, ai_prompt,
                search_console, analytics, backlinks, crawl_budget, link_graph, cwv
            )
            json_path = self.json_dir / f"{safe_filename}.json"
            json_path.write_text(json_content, encoding="utf-8")
            paths["json"] = json_path
        except Exception as e:
            logger.error(f"JSON export failed for {safe_filename}: {e}")

        # =========================================================================
        # 3. PDF REPORT (Single Page Detail)
        # Generates a polished, printable PDF document for the specific page.
        # =========================================================================
        try:
            pdf_path = self.pdf_dir / f"{safe_filename}.pdf"
            PDFReportGenerator.generate(page, keywords, pdf_path)
            paths["pdf"] = pdf_path
        except Exception as e:
            logger.error(f"PDF export failed for {safe_filename}: {e}")

        return paths

    def export_site_summary(
        self,
        pages: list[PageData],
        competitors: list[CompetitorData],
        site_name: str,
        search_console: SearchConsoleData = None,
        link_graph: LinkGraphData = None,
    ) -> dict[str, Path]:
        """
        Export site-level summary reports (CSV, HTML Dashboard, Executive PDF).
        These reports aggregate data across all crawled pages to provide a holistic view.
        
        Returns:
            A dictionary mapping the format name to the Path of the successfully generated file.
        """
        paths = {}
        # Sanitize the site name to ensure it is safe for use as a filename 
        # (removing characters like colons or slashes that are invalid in file paths).
        safe_site_name = site_name.replace(":", "_").replace("/", "_")

        # =========================================================================
        # 1. CSV PAGES SUMMARY
        # Generates a tabular overview of all pages for easy spreadsheet analysis.
        # =========================================================================
        try:
            csv_content = CSVReportGenerator.generate_pages_summary(pages)
            csv_path = self.csv_dir / f"{safe_site_name}_pages.csv"
            csv_path.write_text(csv_content, encoding="utf-8")
            paths["csv_pages"] = csv_path
        except Exception as e:
            logger.error(f"CSV pages export failed: {e}")

        # =========================================================================
        # 2. CSV ISSUES SUMMARY
        # Generates a flattened list of all detected issues across the entire site.
        # =========================================================================
        try:
            issues_csv = CSVReportGenerator.generate_issues_csv(pages)
            issues_path = self.csv_dir / f"{safe_site_name}_issues.csv"
            issues_path.write_text(issues_csv, encoding="utf-8")
            paths["csv_issues"] = issues_path
        except Exception as e:
            logger.error(f"CSV issues export failed: {e}")

        # =========================================================================
        # 3. HTML DASHBOARD (Interactive)
        # Generates a rich, interactive web-based dashboard for exploring the data.
        # =========================================================================
        try:
            html_content = HTMLDashboardGenerator.generate(
                pages, competitors, site_name, search_console, link_graph
            )
            html_path = self.base_dir / "report.html"
            html_path.write_text(html_content, encoding="utf-8")
            paths["html"] = html_path
        except Exception as e:
            logger.error(f"HTML dashboard export failed: {e}")

        # =========================================================================
        # 4. PDF SITE-WIDE SUMMARY (Executive Summary)
        # Generates the comprehensive, high-level PDF report for stakeholders.
        # =========================================================================
        try:
            pdf_path = self.pdf_dir / f"{safe_site_name}_executive_summary.pdf"
            PDFReportGenerator.generate_site_summary(
                site_name=site_name,
                pages=pages,
                competitors=competitors,
                output_path=pdf_path
            )
            paths["pdf_summary"] = pdf_path
        except Exception as e:
            logger.error(f"PDF site summary export failed: {e}")

        return paths