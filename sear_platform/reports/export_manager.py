"""Export Manager - orchestrates all report formats with error handling."""
from __future__ import annotations

import logging
from pathlib import Path

from models.page_data import PageData
from models.reports import CompetitorData
from models.integrations import (
    SearchConsoleData, AnalyticsData, BacklinkData,
    CrawlBudgetReport, LinkGraphData, CoreWebVitals,
)
from .txt_generator import TXTReportGenerator
from .json_generator import JSONReportGenerator
from .csv_generator import CSVReportGenerator
from .html_dashboard import HTMLDashboardGenerator
from .pdf_generator import PDFReportGenerator

logger = logging.getLogger(__name__)


class ExportManager:
    """Manage export of all report formats."""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.txt_dir = base_dir / "txt"
        self.json_dir = base_dir / "json"
        self.csv_dir = base_dir / "csv"
        self.pdf_dir = base_dir / "pdf"
        self.assets_dir = base_dir / "assets"

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
        """Export a single page in all formats."""
        paths = {}

        # 1. TXT (همیشه اول اجرا می‌شود)
        try:
            txt_content = TXTReportGenerator.generate(
                page, competitors, keywords, robots_txt, ai_prompt, search_console, analytics
            )
            txt_path = self.txt_dir / f"{filename}.txt"
            txt_path.write_text(txt_content, encoding="utf-8")
            paths["txt"] = txt_path
        except Exception as e:
            logger.error(f"TXT export failed for {filename}: {e}")

        # 2. JSON (اگر خطا دهد، برنامه متوقف نمی‌شود)
        try:
            json_content = JSONReportGenerator.generate(
                page, competitors, keywords, robots_txt, ai_prompt,
                search_console, analytics, backlinks, crawl_budget, link_graph, cwv
            )
            json_path = self.json_dir / f"{filename}.json"
            json_path.write_text(json_content, encoding="utf-8")
            paths["json"] = json_path
        except Exception as e:
            logger.error(f"JSON export failed for {filename}: {e}")

        # 3. PDF
        try:
            pdf_path = self.pdf_dir / f"{filename}.pdf"
            PDFReportGenerator.generate(page, keywords, pdf_path)
            paths["pdf"] = pdf_path
        except Exception as e:
            logger.error(f"PDF export failed for {filename}: {e}")

        return paths

    def export_site_summary(
        self,
        pages: list[PageData],
        competitors: list[CompetitorData],
        site_name: str,
        search_console: SearchConsoleData = None,
        link_graph: LinkGraphData = None,
    ) -> dict[str, Path]:
        """Export site-level summary reports."""
        paths = {}

        # CSV Pages
        try:
            csv_content = CSVReportGenerator.generate_pages_summary(pages)
            csv_path = self.csv_dir / f"{site_name}_pages.csv"
            csv_path.write_text(csv_content, encoding="utf-8")
            paths["csv_pages"] = csv_path
        except Exception as e:
            logger.error(f"CSV pages export failed: {e}")

        # CSV Issues
        try:
            issues_csv = CSVReportGenerator.generate_issues_csv(pages)
            issues_path = self.csv_dir / f"{site_name}_issues.csv"
            issues_path.write_text(issues_csv, encoding="utf-8")
            paths["csv_issues"] = issues_path
        except Exception as e:
            logger.error(f"CSV issues export failed: {e}")

        # HTML Dashboard
        try:
            html_content = HTMLDashboardGenerator.generate(
                pages, competitors, site_name, search_console, link_graph
            )
            html_path = self.base_dir / "report.html"
            html_path.write_text(html_content, encoding="utf-8")
            paths["html"] = html_path
        except Exception as e:
            logger.error(f"HTML dashboard export failed: {e}")

        return paths