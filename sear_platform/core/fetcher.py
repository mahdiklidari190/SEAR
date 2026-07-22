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
        self.content = content
        self.content_type = content_type
        self.status_code = status_code
        self.headers = headers
        self.ttfb_ms = ttfb_ms
        self.total_time_ms = total_time_ms
        self.http_version = http_version
        self.redirect_chain = redirect_chain or []
        self.final_url = final_url


class RobustFetcher:
    """Async HTTP fetcher with retry, rate limiting, and performance tracking."""

    def __init__(self, timeout: int = 30, max_concurrent: int = 5):
        settings = get_settings()
        self.timeout = timeout or settings.request_timeout
        self.semaphore = asyncio.Semaphore(max_concurrent or settings.max_concurrent_requests)
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            http2=True,
            headers={
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9,fa;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Cache-Control": "no-cache",
            },
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(
            (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError)
        ),
    )
    async def fetch(self, url: str) -> FetchResult:
        """Fetch a URL with full metadata collection."""
        async with self.semaphore:
            self.client.headers["User-Agent"] = random.choice(USER_AGENTS)
            start_time = time.perf_counter()

            try:
                response = await self.client.get(url)
                total_time = (time.perf_counter() - start_time) * 1000
                content_type = response.headers.get("content-type", "").lower()

                # Block binary content
                if "text/html" not in content_type and "application/xml" not in content_type:
                    if any(
                        ext in content_type
                        for ext in ["image/", "video/", "audio/", "application/pdf", "octet-stream"]
                    ):
                        raise ValueError("Binary or non-HTML response detected.")

                # Block WAF/Cloudflare
                if response.status_code in [403, 429] or RE_CLOUDFLARE.search(
                    response.text[:2000]
                ):
                    raise ValueError(
                        f"Blocked by security challenge (Status: {response.status_code})."
                    )

                response.raise_for_status()

                # Build redirect chain
                redirect_chain = [str(r.url) for r in response.history] if response.history else []

                # Determine HTTP version
                http_version = response.http_version or "HTTP/1.1"

                # Estimate TTFB (approximate from total time)
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
                if e.response.status_code == 404:
                    raise ValueError("Page not found (404).")
                raise

    async def fetch_head(self, url: str) -> dict[str, str]:
        """Lightweight HEAD request for link checking."""
        async with self.semaphore:
            try:
                response = await self.client.head(url, follow_redirects=True)
                return {"status_code": str(response.status_code), "headers": dict(response.headers)}
            except Exception:
                return {"status_code": "0", "error": "connection_failed"}

    async def close(self) -> None:
        await self.client.aclose()