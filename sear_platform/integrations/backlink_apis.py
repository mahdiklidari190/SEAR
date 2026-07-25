"""Backlink API Connectors (Optional)."""
from __future__ import annotations

import logging
from typing import Optional

# Import the global settings manager to retrieve third-party API credentials.
from config.settings import get_settings
# Import the structured data model used to hold the fetched backlink metrics.
from models.integrations import BacklinkData

logger = logging.getLogger(__name__)


class BacklinkAPIConnector:
    """Optional backlink data from external APIs."""
    # This class acts as a fallback chain for fetching backlink metrics. 
    # It attempts to connect to configured providers in a specific order of preference.

    def __init__(self):
        # Load the global application settings to access the stored API credentials.
        settings = get_settings()
        self.config = settings.backlink_apis

    def fetch_backlinks(self, domain: str) -> BacklinkData:
        """Try to fetch backlink data from available APIs."""
        # Initialize an empty data object to return if all API calls fail or are unconfigured.
        data = BacklinkData()

        # Implement a priority-based fallback chain. 
        # Attempt Ahrefs first, as it typically provides the most detailed metric breakdown.
        if self.config.ahrefs_key:
            result = self._fetch_ahrefs(domain)
            if result:
                return result

        # If Ahrefs is unavailable or fails, fall back to SEMrush.
        if self.config.semrush_key:
            result = self._fetch_semrush(domain)
            if result:
                return result

        # Finally, attempt DataForSEO if the previous providers are not configured.
        if self.config.dataforseo_login:
            result = self._fetch_dataforseo(domain)
            if result:
                return result

        # Return the empty data object if no configured APIs were successful.
        return data

    def _fetch_ahrefs(self, domain: str) -> Optional[BacklinkData]:
        """Fetch from Ahrefs API."""
        try:
            # Dynamically import httpx to keep the dependency optional for users who don't need this feature.
            import httpx
            
            # Query the Ahrefs Site Explorer API for domain-level metrics.
            resp = httpx.get(
                "https://api.ahrefs.com/v3/site-explorer/domain-rating",
                params={"target": domain, "mode": "domain"},
                headers={"Authorization": f"Bearer {self.config.ahrefs_key}"},
                timeout=15,
            )
            
            # If the request is successful, parse the JSON response and map it to our data model.
            if resp.status_code == 200:
                d = resp.json()
                return BacklinkData(
                    available=True, source="Ahrefs",
                    domain_rating=d.get("domain_rating", 0),
                    total_backlinks=d.get("backlinks", 0),
                    referring_domains=d.get("refdomains", 0),
                )
        except Exception as e:
            # Log the failure at the debug level to avoid cluttering production logs, 
            # as API failures are expected to naturally trigger the fallback chain.
            logger.debug(f"Ahrefs API failed: {e}")
            
        # Return None to signal the orchestrator to try the next provider in the chain.
        return None

    def _fetch_semrush(self, domain: str) -> Optional[BacklinkData]:
        """Fetch from SEMrush API."""
        try:
            import httpx
            
            # Query the SEMrush Analytics API for a backlink overview.
            resp = httpx.get(
                "https://api.semrush.com/analytics/v1/",
                params={
                    "key": self.config.semrush_key,
                    "type": "backlinks_overview",
                    "export_columns": "Dn,Rd,Bs",
                    "target": domain,
                },
                timeout=15,
            )
            
            # Note: The current implementation returns a basic success marker. 
            # Further parsing can be added here if detailed SEMrush metrics are required.
            if resp.status_code == 200:
                return BacklinkData(available=True, source="SEMrush")
        except Exception as e:
            logger.debug(f"SEMrush API failed: {e}")
            
        return None

    def _fetch_dataforseo(self, domain: str) -> Optional[BacklinkData]:
        """Fetch from DataForSEO API."""
        try:
            import httpx
            
            # DataForSEO uses a POST request with a JSON payload and HTTP Basic Authentication.
            resp = httpx.post(
                "https://api.dataforseo.com/v3/backlinks/overview/live",
                json=[{"target": domain}],
                auth=(self.config.dataforseo_login, self.config.dataforseo_password),
                timeout=15,
            )
            
            # Return a basic success marker upon a valid 200 OK response.
            if resp.status_code == 200:
                return BacklinkData(available=True, source="DataForSEO")
        except Exception as e:
            logger.debug(f"DataForSEO API failed: {e}")
            
        return None