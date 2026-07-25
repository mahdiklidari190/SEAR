"""HTTP Fetcher - preserved and enhanced with performance metrics."""
from __future__ import annotations

import asyncio
import random
import ssl
import time
from typing import Optional
from urllib.parse import urlparse

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config.constants import USER_AGENTS, RE_CLOUDFLARE
from config.settings import get_settings


class FetchResult:
    """Encapsulates a fetch response with metadata."""

    def __init__(
        self,
        content: bytes,
        content_type: str,
        status_code: int,
        headers: dict[str, str],
        ttfb_ms: float = 0.0,
        total_time_ms: float = 0.0,
        http_version: str = "",
        redirect_chain: Optional[list[str]] = None,
        final_url: str = "",
    ):
        # Store the raw byte content of the HTTP response.
        self.content = content
        # Store the MIME type of the response (e.g., 'text/html').
        self.content_type = content_type
        # Store the HTTP status code (e.g., 200, 404).
        self.status_code = status_code
        # Store all response headers as a dictionary.
        self.headers = headers
        # Store the estimated Time to First Byte in milliseconds.
        self.ttfb_ms = ttfb_ms
        # Store the total request duration in milliseconds.
        self.total_time_ms = total_time_ms
        # Store the HTTP protocol version used (e.g., 'HTTP/2').
        self.http_version = http_version
        # Store the sequence of URLs visited during redirects.
        self.redirect_chain = redirect_chain or []
        # Store the final resolved URL after any redirects.
        self.final_url = final_url


class RobustFetcher:
    """Async HTTP fetcher with retry, rate limiting, and performance tracking."""

    def __init__(self, timeout: int = 30, max_concurrent: int = 5):
        # Load global application settings to apply default limits if not explicitly provided.
        settings = get_settings()
        self.timeout = timeout or settings.request_timeout
        
        # Use an asyncio Semaphore to limit the number of concurrent network requests, preventing server overload.
        self.semaphore = asyncio.Semaphore(max_concurrent or settings.max_concurrent_requests)
        
        # Initialize the asynchronous HTTP client with robust default configurations.
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            http2=True, # Enable HTTP/2 for better performance and connection multiplexing.
            headers={
                # Rotate User-Agents to mimic legitimate browser traffic and avoid basic bot detection.
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9,fa;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Cache-Control": "no-cache", # Ensure we always fetch fresh content, not cached versions.
            },
        )

    @retry(
        # Automatically retry up to 3 times on specific transient network failures.
        stop=stop_after_attempt(3),
        # Use exponential backoff (2s, 4s, 8s...) to avoid hammering a struggling server.
        wait=wait_exponential(multiplier=1, min=2, max=10),
        # Only retry on recoverable network-level exceptions, not on logical errors like 404.
        retry=retry_if_exception_type(
            (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError)
        ),
    )
    async def fetch(self, url: str) -> FetchResult:
        """Fetch a URL with full metadata collection."""
        # Acquire the semaphore to respect the concurrency limit before making the request.
        async with self.semaphore:
            # Refresh the User-Agent for each request to further reduce the chance of pattern-based blocking.
            self.client.headers["User-Agent"] = random.choice(USER_AGENTS)
            start_time = time.perf_counter()

            try:
                response = await self.client.get(url)
                total_time = (time.perf_counter() - start_time) * 1000
                content_type = response.headers.get("content-type", "").lower()

                # Prevent processing of binary files (images, PDFs, etc.) to save memory and processing time.
                if "text/html" not in content_type and "application/xml" not in content_type:
                    if any(
                        ext in content_type
                        for ext in ["image/", "video/", "audio/", "application/pdf", "octet-stream"]
                    ):
                        raise ValueError("Binary or non-HTML response detected.")

                # Detect and block requests that are intercepted by Web Application Firewalls (WAFs) like Cloudflare.
                if response.status_code in [403, 429] or RE_CLOUDFLARE.search(
                    response.text[:2000]
                ):
                    raise ValueError(
                        f"Blocked by security challenge (Status: {response.status_code})."
                    )

                # Raise an exception for 4xx and 5xx HTTP status codes (except those handled above).
                response.raise_for_status()

                # Build the redirect chain by extracting URLs from the response history.
                redirect_chain = [str(r.url) for r in response.history] if response.history else []

                # Determine the HTTP version used for the successful connection.
                http_version = response.http_version or "HTTP/1.1"

                # Estimate Time to First Byte (TTFB) as a rough percentage of the total request time.
                # Note: For precise TTFB, lower-level socket metrics would be required.
                ttfb = total_time * 0.4  # rough estimate

                headers_dict = dict(response.headers)

                return FetchResult(
                    content=response.content,
                    content_type=content_type,
                    status_code=response.status_code,
                    headers=headers_dict,
                    ttfb_ms=round(ttfb, 2),
                    total_time_ms=round(total_time, 2),
                    http_version=http_version,
                    redirect_chain=redirect_chain,
                    final_url=str(response.url),
                )

            except httpx.HTTPStatusError as e:
                # Explicitly handle 404 errors to provide a clearer, domain-specific error message.
                if e.response.status_code == 404:
                    raise ValueError("Page not found (404).")
                # Re-raise other HTTP status errors for higher-level handling.
                raise

    async def fetch_head(self, url: str) -> dict[str, str]:
        """Lightweight HEAD request for link checking."""
        async with self.semaphore:
            try:
                # Use a HEAD request to check link validity without downloading the full response body.
                response = await self.client.head(url, follow_redirects=True)
                return {"status_code": str(response.status_code), "headers": dict(response.headers)}
            except Exception:
                # Return a standardized failure response for broken or unreachable links.
                return {"status_code": "0", "error": "connection_failed"}

    async def close(self) -> None:
        """Gracefully close the underlying HTTP client and release network resources."""
        await self.client.aclose()