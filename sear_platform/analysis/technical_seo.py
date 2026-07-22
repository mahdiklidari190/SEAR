"""Technical SEO Analysis - security, compression, SSL, DNS."""
from __future__ import annotations

import asyncio
import ssl
import socket
import time
from datetime import datetime
from urllib.parse import urlparse
from typing import Optional

from models.integrations import TechnicalSEOResult
from models.page_data import PageData


class TechnicalSEOAnalyzer:
    """Deep technical SEO analysis."""

    @staticmethod
    def analyze_from_page(page: PageData) -> TechnicalSEOResult:
        """Extract technical SEO data from already-fetched page."""
        result = TechnicalSEOResult()
        h = {k.lower(): v for k, v in page.response_headers.items()}

        result.http2 = page.performance.http_version in ("HTTP/2", "h2", "2")
        result.http3 = page.performance.http_version in ("HTTP/3", "h3", "3")
        result.compression_type = page.performance.compression
        result.brotli_supported = "br" in page.performance.compression
        result.gzip_supported = "gzip" in page.performance.compression
        result.cdn_provider = page.performance.cdn_detected
        result.server_software = page.performance.server
        result.tls_version = page.ssl_data.tls_version
        result.cert_expiry = page.ssl_data.expiry_date
        result.mixed_content_count = len(page.ssl_data.mixed_content)

        # Security issues
        result.security_issues = page.security_headers.issues[:]

        return result

    @staticmethod
    async def check_ssl(domain: str, port: int = 443) -> dict[str, str]:
        """Check SSL certificate details."""
        try:
            loop = asyncio.get_running_loop()
            def _check():
                ctx = ssl.create_default_context()
                with socket.create_connection((domain, port), timeout=10) as sock:
                    with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                        cert = ssock.getpeercert()
                        tls_ver = ssock.version()
                        expiry = cert.get("notAfter", "")
                        issuer = dict(x[0] for x in cert.get("issuer", [])).get("organizationName", "")
                        return {
                            "valid": "true",
                            "tls_version": tls_ver or "",
                            "expiry": expiry,
                            "issuer": issuer,
                        }
            return await loop.run_in_executor(None, _check)
        except Exception as e:
            return {"valid": "false", "error": str(e)}

    @staticmethod
    async def dns_lookup(domain: str) -> float:
        """Measure DNS lookup time in ms."""
        try:
            loop = asyncio.get_running_loop()
            start = time.perf_counter()
            await loop.getaddrinfo(domain, None)
            return round((time.perf_counter() - start) * 1000, 2)
        except Exception:
            return -1.0

    @staticmethod
    def detect_mixed_content(html_content: str, page_url: str) -> list[str]:
        """Detect HTTP resources on HTTPS page."""
        if not page_url.startswith("https"):
            return []
        import re
        http_resources = re.findall(r'(?:src|href)=["\']http://[^"\']+["\']', html_content)
        return [r.split('"')[1] if '"' in r else r.split("'")[1] for r in http_resources[:20]]