"""JSON Report Generator - complete data export."""
# This module is responsible for generating comprehensive, machine-readable JSON reports.
# JSON is the primary format for programmatic consumption, API responses, and seamless 
# integration with frontend dashboards or external data pipelines.
from __future__ import annotations

import json
from typing import Any

# Import the core data models that encapsulate the extracted SEO metrics and analysis results.
from models.page_data import PageData
from models.reports import CompetitorData
from models.integrations import (
    SearchConsoleData, AnalyticsData, BacklinkData,
    CrawlBudgetReport, LinkGraphData, CoreWebVitals,
)

# Import a custom utility function for safe and reliable Pydantic model serialization.
# This acts as a robust fallback to prevent AttributeError issues that can sometimes 
# occur with model_dump() in specific Pydantic versions or with complex nested structures.
from utils.helpers import model_to_dict


class JSONReportGenerator:
    """Generate complete JSON reports with all aggregated SEO data."""

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
        """
        Assemble and serialize all analysis data into a single, structured JSON payload.
        
        Args:
            page: The primary PageData object containing all on-page metrics.
            competitors: A list of CompetitorData objects for benchmarking.
            keywords: The target keywords analyzed for this page.
            robots_txt: The raw content of the site's robots.txt file.
            ai_prompt: The generated AI master prompt for this specific page.
            search_console: Optional Google Search Console performance data.
            analytics: Optional Google Analytics user behavior data.
            backlinks: Optional third-party backlink profile data.
            crawl_budget: Optional crawl efficiency analysis report.
            link_graph: Optional internal linking structure analysis.
            cwv: Optional Core Web Vitals performance estimates.
            
        Returns:
            A formatted JSON string ready to be written to a file or sent via API.
        """
        # Construct the main data dictionary, ensuring all optional parameters 
        # default to empty, valid model instances if not provided.
        data = {
            "report_version": "6.0", # Track the schema version for future compatibility.
            
            # Core page analysis data, safely converted to a dictionary.
            "page": model_to_dict(page),
            
            # Target keywords and the generated AI action plan.
            "keywords": keywords,
            "ai_prompt": ai_prompt,
            
            # Competitor benchmarking data, mapped to dictionaries.
            "competitors": [model_to_dict(c) for c in competitors],
            
            # Truncate robots.txt to 2000 characters to prevent the JSON payload 
            # from becoming excessively large, while still capturing the most critical rules.
            "robots_txt": robots_txt[:2000],
            
            # Optional integration data, defaulting to empty models if unavailable.
            "search_console": model_to_dict(search_console or SearchConsoleData()),
            "analytics": model_to_dict(analytics or AnalyticsData()),
            "backlinks": model_to_dict(backlinks or BacklinkData()),
            "crawl_budget": model_to_dict(crawl_budget or CrawlBudgetReport()),
            
            # For the link graph, we selectively extract only the most critical summary metrics 
            # and cap the lists at 20 items to keep the JSON file size manageable for frontend rendering.
            "link_graph": {
                "total_pages": (link_graph or LinkGraphData()).total_pages,
                "total_internal_links": (link_graph or LinkGraphData()).total_internal_links,
                "orphan_pages": (link_graph or LinkGraphData()).orphan_pages[:20],
                "hub_pages": (link_graph or LinkGraphData()).hub_pages[:20],
                "avg_links_per_page": (link_graph or LinkGraphData()).avg_links_per_page,
            },
            
            "core_web_vitals": model_to_dict(cwv or CoreWebVitals()),
        }

        # Serialize the dictionary to a JSON string.
        # - indent=2: Makes the JSON human-readable and easy to debug.
        # - ensure_ascii=False: Preserves non-ASCII characters (like Persian text) without escaping them.
        # - default=str: A crucial safety net that converts any non-serializable objects 
        #   (e.g., pathlib.Path, datetime) into strings, preventing TypeError crashes.
        return json.dumps(data, indent=2, ensure_ascii=False, default=str)