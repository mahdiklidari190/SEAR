"""Broken Link Detection."""
from __future__ import annotations

import asyncio
import logging
from typing import Optional

from core.fetcher import RobustFetcher

logger = logging.getLogger(__name__)


class BrokenLinkChecker:
    """Check internal and external links for errors."""

    def __init__(self, fetcher: RobustFetcher, max_concurrent: int = 10):
        self.fetcher = fetcher
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def check_links(self, urls: list[str]) -> list[dict[str, str]]:
        """Check a list of URLs for broken links."""
        tasks = [self._check_single(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        broken = []
        for result in results:
            if isinstance(result, dict) and result.get("broken"):
                broken.append(result)
        return broken

    async def _check_single(self, url: str) -> Optional[dict[str, str]]:
        """Check a single URL."""
        async with self.semaphore:
            try:
                result = await self.fetcher.fetch_head(url)
                status = int(result.get("status_code", 0))

                if status == 0:
                    return {"url": url, "status": "DNS/Connection Error", "broken": True, "type": "connection"}
                elif status in (404, 410):
                    return {"url": url, "status": str(status), "broken": True, "type": "not_found"}
                elif status in (500, 502, 503):
                    return {"url": url, "status": str(status), "broken": True, "type": "server_error"}
                elif status == 403:
                    return {"url": url, "status": "403", "broken": True, "type": "forbidden"}

                return None
            except Exception as e:
                error_str = str(e).lower()
                if "ssl" in error_str or "certificate" in error_str:
                    return {"url": url, "status": "SSL Error", "broken": True, "type": "ssl"}
                elif "timeout" in error_str:
                    return {"url": url, "status": "Timeout", "broken": True, "type": "timeout"}
                elif "dns" in error_str or "name resolution" in error_str:
                    return {"url": url, "status": "DNS Error", "broken": True, "type": "dns"}
                return {"url": url, "status": str(e)[:100], "broken": True, "type": "unknown"}