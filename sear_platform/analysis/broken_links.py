"""Broken Link Detection."""
from __future__ import annotations

# Standard library imports for asynchronous execution, logging, and type hinting.
import asyncio
import logging
from typing import Optional

# Import the custom HTTP fetching utility used to perform the actual network requests.
from core.fetcher import RobustFetcher

# Initialize the logger for this specific module to track errors and operational status.
logger = logging.getLogger(__name__)


class BrokenLinkChecker:
    """Check internal and external links for errors."""

    def __init__(self, fetcher: RobustFetcher, max_concurrent: int = 10):
        # Store the injected HTTP fetcher instance to be used for making requests.
        self.fetcher = fetcher
        
        # Initialize an asyncio Semaphore to limit the number of concurrent network requests.
        # This prevents overwhelming the target server or exhausting local network resources.
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def check_links(self, urls: list[str]) -> list[dict[str, str]]:
        """Check a list of URLs for broken links."""
        # Create a list of asynchronous tasks, one for each URL to be checked.
        tasks = [self._check_single(url) for url in urls]
        
        # Execute all tasks concurrently using asyncio.gather. 
        # return_exceptions=True ensures that if one task fails, the others still complete.
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter the results to extract only the dictionaries that indicate a broken link.
        broken = []
        for result in results:
            if isinstance(result, dict) and result.get("broken"):
                broken.append(result)
                
        # Return the consolidated list of broken link reports.
        return broken

    async def _check_single(self, url: str) -> Optional[dict[str, str]]:
        """Check a single URL."""
        # Acquire the semaphore before making the network request to respect the concurrency limit.
        async with self.semaphore:
            try:
                # Perform an HTTP HEAD request to check the link's status without downloading the full body.
                result = await self.fetcher.fetch_head(url)
                status = int(result.get("status_code", 0))

                # Categorize the HTTP response status code to determine the specific type of link failure.
                if status == 0:
                    # A status of 0 typically indicates a fundamental network or DNS failure.
                    return {"url": url, "status": "DNS/Connection Error", "broken": True, "type": "connection"}
                elif status in (404, 410):
                    # 404 (Not Found) and 410 (Gone) mean the resource no longer exists.
                    return {"url": url, "status": str(status), "broken": True, "type": "not_found"}
                elif status in (500, 502, 503):
                    # 5xx errors indicate server-side issues preventing the link from resolving properly.
                    return {"url": url, "status": str(status), "broken": True, "type": "server_error"}
                elif status == 403:
                    # 403 Forbidden means the server understands the request but refuses to authorize it.
                    return {"url": url, "status": "403", "broken": True, "type": "forbidden"}

                # If the status code is successful (e.g., 200) or a valid redirect, the link is not broken.
                return None
                
            except Exception as e:
                # Catch and analyze network-level exceptions that occur during the fetch attempt.
                error_str = str(e).lower()
                
                # Classify the exception based on the error message string to provide actionable insights.
                if "ssl" in error_str or "certificate" in error_str:
                    return {"url": url, "status": "SSL Error", "broken": True, "type": "ssl"}
                elif "timeout" in error_str:
                    return {"url": url, "status": "Timeout", "broken": True, "type": "timeout"}
                elif "dns" in error_str or "name resolution" in error_str:
                    return {"url": url, "status": "DNS Error", "broken": True, "type": "dns"}
                    
                # Fallback for any unrecognized exceptions, truncating the error message to keep the report clean.
                return {"url": url, "status": str(e)[:100], "broken": True, "type": "unknown"}