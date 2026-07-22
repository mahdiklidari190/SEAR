"""Google Analytics Integration (Optional)."""
from __future__ import annotations

import logging

from config.settings import get_settings
from models.integrations import AnalyticsData

logger = logging.getLogger(__name__)


class AnalyticsIntegration:
    """Optional Google Analytics data retrieval."""

    def __init__(self):
        settings = get_settings()
        self.config = settings.analytics

    @property
    def is_available(self) -> bool:
        return self.config.is_configured

    def fetch_data(self, days: int = 28) -> AnalyticsData:
        """Fetch Analytics data. Returns empty if not configured."""
        data = AnalyticsData()

        if not self.is_available:
            return data

        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            from datetime import datetime, timedelta

            creds = Credentials(
                token=None,
                refresh_token=self.config.refresh_token,
                client_id=self.config.client_id,
                client_secret=self.config.client_secret,
                token_uri="https://oauth2.googleapis.com/token",
            )
            service = build("analyticsdata", "v1beta", credentials=creds)

            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

            body = {
                "dateRanges": [{"startDate": start_date, "endDate": end_date}],
                "metrics": [
                    {"name": "sessions"},
                    {"name": "totalUsers"},
                    {"name": "bounceRate"},
                    {"name": "averageSessionDuration"},
                ],
                "limit": 1,
            }

            response = service.properties().runReport(
                property=f"properties/{self.config.property_id}", body=body
            ).execute()

            rows = response.get("rows", [])
            if rows:
                values = rows[0].get("metricValues", [])
                data.sessions = int(values[0]["value"]) if len(values) > 0 else 0
                data.users = int(values[1]["value"]) if len(values) > 1 else 0
                data.bounce_rate = round(float(values[2]["value"]) * 100, 1) if len(values) > 2 else 0
                data.avg_engagement_time = round(float(values[3]["value"]), 1) if len(values) > 3 else 0

            data.available = True

        except Exception as e:
            logger.warning(f"Analytics data fetch failed: {e}")

        return data