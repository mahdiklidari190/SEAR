"""Robots Manager - Async handling of robots.txt compliance."""
from __future__ import annotations
import asyncio
import logging
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from typing import List, Optional
import httpx

logger = logging.getLogger(__name__)

class RobotsManager:
    """
    Manages robots.txt fetching, parsing, and compliance checking.
    This class ensures that the crawler respects website crawling rules 
    while efficiently caching parsed rules per domain to minimize network overhead.
    """

    def __init__(self, user_agent: str):
        # Store the specific User-Agent string to check against domain-specific rules.
        self.user_agent = user_agent
        
        # Cache dictionary to store parsed RobotFileParser instances per domain.
        # This prevents redundant network requests for the same domain during a crawl session.
        self.parsers: dict[str, RobotFileParser] = {}
        
        # Asyncio lock to ensure thread-safe initialization of the parser cache 
        # when multiple concurrent tasks attempt to fetch the same domain's robots.txt simultaneously.
        self._lock = asyncio.Lock()

    async def _fetch_robots_text(self, domain: str) -> Optional[str]:
        """Fetches the raw robots.txt content from the domain."""
        url = f"https://{domain}/robots.txt"
        try:
            # Use a transient, dedicated client for this lightweight request.
            # This avoids keeping unnecessary connections open in the main crawler's connection pool.
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(url)
                # Only return the text if the file is successfully found (HTTP 200).
                if response.status_code == 200:
                    return response.text
                return None
        except Exception as e:
            # Log network failures at the debug level to avoid cluttering the main logs, 
            # as missing or unreachable robots.txt files are a common and expected occurrence.
            logger.debug(f"Failed to fetch robots.txt for {domain}: {e}")
            return None

    async def get_parser(self, url: str) -> RobotFileParser:
        """Gets or creates a cached RobotFileParser for the given URL's domain."""
        # Extract the root domain from the URL to use as the cache key.
        domain = urlparse(url).netloc
        
        # Acquire the lock to prevent race conditions during cache population.
        async with self._lock:
            # Cache miss: fetch and parse the robots.txt for the first time.
            if domain not in self.parsers:
                parser = RobotFileParser()
                robots_text = await self._fetch_robots_text(domain)
                
                if robots_text:
                    # Parse the raw text line by line into actionable rules.
                    parser.parse(robots_text.splitlines())
                    logger.info(f"Successfully loaded robots.txt for {domain}")
                else:
                    # If no robots.txt exists, parse an empty list. 
                    # By default, RobotFileParser treats empty rules as "allow all".
                    parser.parse([]) 
                    logger.info(f"No robots.txt found for {domain}, allowing all.")
                    
                # Store the initialized parser in the cache for future requests.
                self.parsers[domain] = parser
                
            # Return the cached (or newly created) parser instance.
            return self.parsers[domain]

    async def can_fetch(self, url: str) -> bool:
        """Checks if the given URL is allowed to be fetched by our User-Agent."""
        # Ensure the parser for this specific domain is loaded and cached.
        parser = await self.get_parser(url)
        # Delegate the actual allow/deny evaluation to Python's built-in RobotFileParser logic.
        return parser.can_fetch(self.user_agent, url)

    async def get_sitemaps(self, url: str) -> List[str]:
        """Extracts sitemap URLs declared in the robots.txt file."""
        # Ensure the parser for this domain is available.
        parser = await self.get_parser(url)
        # Return the list of declared sitemaps, falling back to an empty list if none are found.
        return parser.site_maps() or []