"""Google Search Console Integration (Optional)."""
from __future__ import annotations

import logging
from typing import Optional

from config.settings import get_settings
from models.integrations import (
    SearchConsoleData, SearchConsoleQueryData, SearchConsolePageData
)

logger = logging.getLogger(__name__)


class SearchConsoleIntegration:
    """Optional Google Search Console data retrieval."""

    def __init__(self):
        settings = get_settings()
        self.config = settings.search_console
        self._service = None

    @property
    def is_available(self) -> bool:
        return self.config.is_configured

    def _get_service(self):
        """Initialize GSC API service."""
        if self._service:
            return self._service

        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build

            creds = Credentials(
                token=None,
                refresh_token=self.config.refresh_token,
                client_id=self.config.client_id,
                client_secret=self.config.client_secret,
                token_uri="https://oauth2.googleapis.com/token",
            )
            self._service = build("searchconsole", "v1", credentials=creds)
            return self._service
        except Exception as e:
            logger.warning(f"Search Console initialization failed: {e}")
            return None

    def fetch_data(self, days: int = 28) -> SearchConsoleData:
        """Fetch Search Console data. Returns empty data if not configured."""
        data = SearchConsoleData()

        if not self.is_available:
            return data

        service = self._get_service()
        if not service:
            return data

        try:
            from datetime import datetime, timedelta
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

            # Query data
            body = {
                "startDate": start_date,
                "endDate": end_date,
                "dimensions": ["query"],
                "rowLimit": 100,
            }
            response = service.searchanalytics().query(
                siteUrl=self.config.property_url, body=body
            ).execute()

            for row in response.get("rows", []):
                data.top_queries.append(SearchConsoleQueryData(
                    query=row["keys"][0],
                    clicks=row["clicks"],
                    impressions=row["impressions"],
                    ctr=round(row["ctr"] * 100, 2),
                    position=round(row["position"], 1),
                ))
                data.total_clicks += row["clicks"]
                data.total_impressions += row["impressions"]

            # Page data
            body["dimensions"] = ["page"]
            response = service.searchanalytics().query(
                siteUrl=self.config.property_url, body=body
            ).execute()

            for row in response.get("rows", []):
                page_data = SearchConsolePageData(
                    page=row["keys"][0],
                    clicks=row["clicks"],
                    impressions=row["impressions"],
                    ctr=round(row["ctr"] * 100, 2),
                    position=round(row["position"], 1),
                )
                data.top_pages.append(page_data)

                # High impressions, low CTR
                if page_data.impressions > 100 and page_data.ctr < 2.0:
                    data.high_impression_low_ctr.append(page_data)
                # Position 8-15 (striking distance)
                if 8 <= page_data.position <= 15:
                    data.position_8_15.append(page_data)
                # Zero clicks
                if page_data.clicks == 0 and page_data.impressions > 50:
                    data.zero_click_pages.append(page_data)

            if data.total_impressions > 0:
                data.average_ctr = round(data.total_clicks / data.total_impressions * 100, 2)

            data.available = True

        except Exception as e:
            logger.warning(f"Search Console data fetch failed: {e}")

        return data