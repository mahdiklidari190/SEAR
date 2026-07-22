"""JSON Report Generator - complete data export."""
from __future__ import annotations

import json
from typing import Any

from models.page_data import PageData
from models.reports import CompetitorData
from models.integrations import (
    SearchConsoleData, AnalyticsData, BacklinkData,
    CrawlBudgetReport, LinkGraphData, CoreWebVitals,
)
from utils.helpers import model_to_dict  # <--- این خط اضافه شد


class JSONReportGenerator:
    """Generate complete JSON reports with all data."""

    @staticmethod
    def generate(
        page: PageData,
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
    ) -> str:
        # استفاده از model_to_dict به جای model_dump برای جلوگیری از خطا
        data = {
            "report_version": "6.0",
            "page": model_to_dict(page),
            "keywords": keywords,
            "competitors": [model_to_dict(c) for c in competitors],
            "robots_txt": robots_txt[:2000],
            "ai_prompt": ai_prompt,
            "search_console": model_to_dict(search_console or SearchConsoleData()),
            "analytics": model_to_dict(analytics or AnalyticsData()),
            "backlinks": model_to_dict(backlinks or BacklinkData()),
            "crawl_budget": model_to_dict(crawl_budget or CrawlBudgetReport()),
            "link_graph": {
                "total_pages": (link_graph or LinkGraphData()).total_pages,
                "total_internal_links": (link_graph or LinkGraphData()).total_internal_links,
                "orphan_pages": (link_graph or LinkGraphData()).orphan_pages[:20],
                "hub_pages": (link_graph or LinkGraphData()).hub_pages[:20],
                "avg_links_per_page": (link_graph or LinkGraphData()).avg_links_per_page,
            },
            "core_web_vitals": model_to_dict(cwv or CoreWebVitals()),
        }

        return json.dumps(data, indent=2, ensure_ascii=False, default=str)