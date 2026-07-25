"""Google Analytics Integration (Optional)."""
from __future__ import annotations

import logging

# Import the global settings manager to retrieve API credentials.
from config.settings import get_settings
# Import the structured data model used to hold the fetched analytics metrics.
from models.integrations import AnalyticsData

logger = logging.getLogger(__name__)


class AnalyticsIntegration:
    """Optional Google Analytics data retrieval."""

    def __init__(self):
        # Load the application settings to access the Google Analytics configuration.
        settings = get_settings()
        self.config = settings.analytics

    @property
    def is_available(self) -> bool:
        """Check if the Google Analytics integration is fully configured and ready to use."""
        return self.config.is_configured

    def fetch_data(self, days: int = 28) -> AnalyticsData:
        """
        Fetch Google Analytics data for the specified number of days.
        Returns an empty AnalyticsData object if the integration is not configured.
        
        Args:
            days: The number of historical days to retrieve data for (default is 28).
            
        Returns:
            An AnalyticsData object populated with the requested metrics, or empty if unavailable.
        """
        data = AnalyticsData()

        # Exit early and return empty data if the necessary credentials are not provided.
        if not self.is_available:
            return data

        try:
            # Dynamically import Google API libraries to avoid hard dependencies 
            # for users who do not intend to use the Analytics integration.
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            from datetime import datetime, timedelta

            # Construct the OAuth2 credentials object using the stored refresh token and client details.
            creds = Credentials(
                token=None,
                refresh_token=self.config.refresh_token,
                client_id=self.config.client_id,
                client_secret=self.config.client_secret,
                token_uri="https://oauth2.googleapis.com/token",
            )
            
            # Build the Google Analytics Data API v1beta service client.
            service = build("analyticsdata", "v1beta", credentials=creds)

            # Calculate the date range for the report (from `days` ago to today).
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

            # Define the payload for the API request, specifying the date range and desired metrics.
            body = {
                "dateRanges": [{"startDate": start_date, "endDate": end_date}],
                "metrics": [
                    {"name": "sessions"},
                    {"name": "totalUsers"},
                    {"name": "bounceRate"},
                    {"name": "averageSessionDuration"},
                ],
                "limit": 1, # Limit to 1 row since we are fetching aggregate site-wide data.
            }

            # Execute the report request against the specified GA4 property ID.
            response = service.properties().runReport(
                property=f"properties/{self.config.property_id}", body=body
            ).execute()

            # Parse the returned rows and safely extract the metric values.
            rows = response.get("rows", [])
            if rows:
                values = rows[0].get("metricValues", [])
                data.sessions = int(values[0]["value"]) if len(values) > 0 else 0
                data.users = int(values[1]["value"]) if len(values) > 1 else 0
                # Bounce rate is returned as a decimal, so we multiply by 100 to get a percentage.
                data.bounce_rate = round(float(values[2]["value"]) * 100, 1) if len(values) > 2 else 0
                data.avg_engagement_time = round(float(values[3]["value"]), 1) if len(values) > 3 else 0

            # Mark the data object as successfully populated.
            data.available = True

        except Exception as e:
            # Log any authentication, network, or API errors without crashing the application.
            logger.warning(f"Analytics data fetch failed: {e}")

        return data