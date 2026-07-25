"""Technical SEO Analysis - security, compression, SSL, DNS."""
from __future__ import annotations

# Standard library imports for asynchronous execution, secure socket layer operations, 
# network connections, high-resolution timing, and URL parsing.
import asyncio
import ssl
import socket
import time
from datetime import datetime
from urllib.parse import urlparse
from typing import Optional

# Import the data models used to structure the technical SEO report and access page-level metrics.
from models.integrations import TechnicalSEOResult
from models.page_data import PageData


class TechnicalSEOAnalyzer:
    """Deep technical SEO analysis."""

    @staticmethod
    def analyze_from_page(page: PageData) -> TechnicalSEOResult:
        """
        Extract technical SEO data from an already-fetched page.
        This method avoids redundant network requests by leveraging data 
        that was already collected during the initial page crawl.
        """
        result = TechnicalSEOResult()
        
        # Normalize all response header keys to lowercase for case-insensitive lookups.
        h = {k.lower(): v for k, v in page.response_headers.items()}

        # Evaluate HTTP protocol versions to determine if modern, faster protocols are in use.
        result.http2 = page.performance.http_version in ("HTTP/2", "h2", "2")
        result.http3 = page.performance.http_version in ("HTTP/3", "h3", "3")
        
        # Assess server-side compression capabilities, which are critical for reducing payload size and improving load times.
        result.compression_type = page.performance.compression
        result.brotli_supported = "br" in page.performance.compression
        result.gzip_supported = "gzip" in page.performance.compression
        
        # Identify infrastructure details that impact performance and geographic content delivery.
        result.cdn_provider = page.performance.cdn_detected
        result.server_software = page.performance.server
        
        # Extract SSL/TLS security metrics to ensure the connection is secure and up to modern standards.
        result.tls_version = page.ssl_data.tls_version
        result.cert_expiry = page.ssl_data.expiry_date
        result.mixed_content_count = len(page.ssl_data.mixed_content)

        # Propagate any pre-identified security header issues (e.g., missing HSTS, CSP) to the final report.
        result.security_issues = page.security_headers.issues[:]

        return result

    @staticmethod
    async def check_ssl(domain: str, port: int = 443) -> dict[str, str]:
        """
        Check SSL certificate details asynchronously.
        
        Args:
            domain: The domain name to check.
            port: The port to connect to (defaults to 443 for HTTPS).
            
        Returns:
            A dictionary containing the certificate's validity, TLS version, expiry date, and issuer.
        """
        try:
            # Get the current running event loop to execute the blocking socket operation in a separate thread.
            # This prevents the synchronous socket connection from freezing the entire async application.
            loop = asyncio.get_running_loop()
            
            def _check():
                # Create a default SSL context for secure connection negotiation.
                ctx = ssl.create_default_context()
                
                # Establish a raw TCP connection to the domain with a 10-second timeout.
                with socket.create_connection((domain, port), timeout=10) as sock:
                    # Wrap the socket with the SSL context, verifying the server hostname matches the certificate.
                    with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                        cert = ssock.getpeercert()
                        tls_ver = ssock.version()
                        
                        # Extract key certificate details for the SEO/security report.
                        expiry = cert.get("notAfter", "")
                        issuer = dict(x[0] for x in cert.get("issuer", [])).get("organizationName", "")
                        
                        return {
                            "valid": "true",
                            "tls_version": tls_ver or "",
                            "expiry": expiry,
                            "issuer": issuer,
                        }
            
            # Execute the blocking _check function in the default thread pool executor.
            return await loop.run_in_executor(None, _check)
            
        except Exception as e:
            # Catch and return any connection or SSL handshake errors gracefully.
            return {"valid": "false", "error": str(e)}

    @staticmethod
    async def dns_lookup(domain: str) -> float:
        """
        Measure DNS lookup time in milliseconds asynchronously.
        
        Args:
            domain: The domain name to resolve.
            
        Returns:
            The time taken for the DNS resolution in milliseconds, or -1.0 if it fails.
        """
        try:
            loop = asyncio.get_running_loop()
            
            # Use perf_counter for high-resolution timing to accurately measure the network delay.
            start = time.perf_counter()
            
            # Perform the asynchronous DNS resolution.
            await loop.getaddrinfo(domain, None)
            
            # Calculate the elapsed time and convert it to milliseconds, rounded to 2 decimal places.
            return round((time.perf_counter() - start) * 1000, 2)
            
        except Exception:
            # Return -1.0 to indicate a failed DNS resolution (e.g., invalid domain or network issue).
            return -1.0

    @staticmethod
    def detect_mixed_content(html_content: str, page_url: str) -> list[str]:
        """
        Detect HTTP resources embedded on an HTTPS page.
        Mixed content compromises security and triggers browser warnings, negatively impacting user trust and SEO.
        
        Args:
            html_content: The raw HTML source code of the page.
            page_url: The URL of the page being analyzed.
            
        Returns:
            A list of up to 20 HTTP resource URLs found on the page.
        """
        # If the page itself is not served over HTTPS, mixed content is not applicable.
        if not page_url.startswith("https"):
            return []
            
        import re
        
        # Use a regular expression to find any 'src' or 'href' attributes that explicitly start with 'http://'.
        http_resources = re.findall(r'(?:src|href)=["\']http://[^"\']+["\']', html_content)
        
        # Extract the clean URL string from the matched attribute by splitting on the quote character.
        # We limit the output to the first 20 instances to keep the report concise and prevent memory bloat.
        return [r.split('"')[1] if '"' in r else r.split("'")[1] for r in http_resources[:20]]