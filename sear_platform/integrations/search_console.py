"""Google Search Console Integration (Optional)."""
from __future__ import annotations

import logging
from typing import Optional

# Import the global settings manager to retrieve Google Search Console API credentials.
from config.settings import get_settings
# Import the structured data models used to hold the fetched Search Console metrics.
from models.integrations import (
    SearchConsoleData, SearchConsoleQueryData, SearchConsolePageData
)

logger = logging.getLogger(__name__)


class SearchConsoleIntegration:
    """Optional Google Search Console data retrieval."""
    # This class handles authentication and data extraction from the Google Search Console API,
    # providing critical insights into search queries, impressions, clicks, and average positions.

    def __init__(self):
        # Load the application settings to access the Search Console configuration.
        settings = get_settings()
        self.config = settings.search_console
        # Initialize the API service placeholder to None for lazy loading.
        self._service = None

    @property
    def is_available(self) -> bool:
        """Check if the Google Search Console integration is fully configured and ready to use."""
        return self.config.is_configured

    def _get_service(self):
        """
        Initialize and cache the Google Search Console API service.
        Uses lazy initialization to avoid unnecessary overhead if the integration is never called.
        """
        # Return the cached service instance if it has already been initialized.
        if self._service:
            return self._service

        try:
            # Dynamically import Google API libraries to keep them as optional dependencies.
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build

            # Construct the OAuth2 credentials object using the stored refresh token and client details.
            creds = Credentials(
                token=None,
                refresh_token=self.config.refresh_token,
                client_id=self.config.client_id,
                client_secret=self.config.client_secret,
                token_uri="https://oauth2.googleapis.com/token",
            )
            
            # Build and cache the Search Console v1 API service client.
            self._service = build("searchconsole", "v1", credentials=creds)
            return self._service
            
        except Exception as e:
            # Log any authentication or initialization errors without crashing the application.
            logger.warning(f"Search Console initialization failed: {e}")
            return None

    def fetch_data(self, days: int = 28) -> SearchConsoleData:
        """
        Fetch Search Console data for the specified number of days.
        Returns an empty SearchConsoleData object if the integration is not configured or fails.
        
        Args:
            days: The number of historical days to retrieve data for (default is 28).
            
        Returns:
            A SearchConsoleData object populated with the requested metrics and opportunity buckets.
        """
        data = SearchConsoleData()

        # Exit early and return empty data if the necessary credentials are not provided.
        if not self.is_available:
            return data

        # Ensure the API service is initialized; if it fails, return empty data.
        service = self._get_service()
        if not service:
            return data

        try:
            from datetime import datetime, timedelta
            
            # Calculate the date range for the report (from `days` ago to today).
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

            # =========================================================================
            # 1. FETCH QUERY DATA
            # Retrieve the top search queries driving traffic to the property.
            # =========================================================================
            body = {
                "startDate": start_date,
                "endDate": end_date,
                "dimensions": ["query"], # Group the results by search query.
                "rowLimit": 100,
            }
            response = service.searchanalytics().query(
                siteUrl=self.config.property_url, body=body
            ).execute()

            # Parse the query data and aggregate the total clicks and impressions.
            for row in response.get("rows", []):
                data.top_queries.append(SearchConsoleQueryData(
                    query=row["keys"][0],
                    clicks=row["clicks"],
                    impressions=row["impressions"],
                    ctr=round(row["ctr"] * 100, 2), # Convert decimal CTR to percentage.
                    position=round(row["position"], 1),
                ))
                data.total_clicks += row["clicks"]
                data.total_impressions += row["impressions"]

            # =========================================================================
            # 2. FETCH PAGE DATA & IDENTIFY SEO OPPORTUNITIES
            # Retrieve the top landing pages and categorize them into actionable buckets.
            # =========================================================================
            body["dimensions"] = ["page"] # Switch the grouping dimension to landing page URL.
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

                # Opportunity 1: High impressions but low CTR (indicates a need for better title/meta description).
                if page_data.impressions > 100 and page_data.ctr < 2.0:
                    data.high_impression_low_ctr.append(page_data)
                    
                # Opportunity 2: "Striking distance" rankings (positions 8-15) where a small push could reach page 1.
                if 8 <= page_data.position <= 15:
                    data.position_8_15.append(page_data)
                    
                # Opportunity 3: Zero-click pages with decent impressions (indicates poor relevance or featured snippet competition).
                if page_data.clicks == 0 and page_data.impressions > 50:
                    data.zero_click_pages.append(page_data)

            # Calculate the overall average CTR for the property based on the aggregated totals.
            if data.total_impressions > 0:
                data.average_ctr = round(data.total_clicks / data.total_impressions * 100, 2)

            # Mark the data object as successfully populated.
            data.available = True

        except Exception as e:
            # Log any network, API, or parsing errors gracefully.
            logger.warning(f"Search Console data fetch failed: {e}")

        return data