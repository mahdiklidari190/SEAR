"""Backlink API Connectors (Optional)."""
from __future__ import annotations

import logging
from typing import Optional

from config.settings import get_settings
from models.integrations import BacklinkData

logger = logging.getLogger(__name__)


class BacklinkAPIConnector:
    """Optional backlink data from external APIs."""

    def __init__(self):
        settings = get_settings()
        self.config = settings.backlink_apis

    def fetch_backlinks(self, domain: str) -> BacklinkData:
        """Try to fetch backlink data from available APIs."""
        data = BacklinkData()

        if self.config.ahrefs_key:
            result = self._fetch_ahrefs(domain)
            if result:
                return result

        if self.config.semrush_key:
            result = self._fetch_semrush(domain)
            if result:
                return result

        if self.config.dataforseo_login:
            result = self._fetch_dataforseo(domain)
            if result:
                return result

        return data

    def _fetch_ahrefs(self, domain: str) -> Optional[BacklinkData]:
        """Fetch from Ahrefs API."""
        try:
            import httpx
            resp = httpx.get(
                "https://api.ahrefs.com/v3/site-explorer/domain-rating",
                params={"target": domain, "mode": "domain"},
                headers={"Authorization": f"Bearer {self.config.ahrefs_key}"},
                timeout=15,
            )
            if resp.status_code == 200:
                d = resp.json()
                return BacklinkData(
                    available=True, source="Ahrefs",
                    domain_rating=d.get("domain_rating", 0),
                    total_backlinks=d.get("backlinks", 0),
                    referring_domains=d.get("refdomains", 0),
                )
        except Exception as e:
            logger.debug(f"Ahrefs API failed: {e}")
        return None

    def _fetch_semrush(self, domain: str) -> Optional[BacklinkData]:
        """Fetch from SEMrush API."""
        try:
            import httpx
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
            if resp.status_code == 200:
                return BacklinkData(available=True, source="SEMrush")
        except Exception as e:
            logger.debug(f"SEMrush API failed: {e}")
        return None

    def _fetch_dataforseo(self, domain: str) -> Optional[BacklinkData]:
        """Fetch from DataForSEO API."""
        try:
            import httpx
            resp = httpx.post(
                "https://api.dataforseo.com/v3/backlinks/overview/live",
                json=[{"target": domain}],
                auth=(self.config.dataforseo_login, self.config.dataforseo_password),
                timeout=15,
            )
            if resp.status_code == 200:
                return BacklinkData(available=True, source="DataForSEO")
        except Exception as e:
            logger.debug(f"DataForSEO API failed: {e}")
        return None