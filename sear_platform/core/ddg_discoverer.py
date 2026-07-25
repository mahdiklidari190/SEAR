"""DuckDuckGo Discoverer - Finds sitemaps and pages via DDG search."""
from __future__ import annotations
import logging
import time
import random
# Import the modern DuckDuckGo search library for programmatic query execution.
from ddgs import DDGS  
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class DDGDiscoverer:
    """Utility class for discovering website sitemaps and indexed pages using DuckDuckGo search queries."""

    @staticmethod
    def _clean_domain(domain: str) -> str:
        """
        Normalize a domain string by removing protocols and 'www' prefixes.
        This ensures the 'site:' search operator targets the root domain accurately without false negatives.
        """
        # Strip common protocol prefixes and the 'www.' subdomain to isolate the core domain.
        domain = domain.replace("http://", "").replace("https://", "").replace("www.", "")
        # Split by '/' and return only the first part to guarantee we only have the pure domain name.
        return domain.split("/")[0]

    @staticmethod
    def find_sitemaps(domain: str, max_results: int = 10) -> list[str]:
        """
        Search DuckDuckGo to discover XML sitemap files associated with a specific domain.
        """
        clean_domain = DDGDiscoverer._clean_domain(domain)
        # Construct an advanced search query targeting common sitemap file naming conventions.
        query = f"site:{clean_domain} inurl:sitemap.xml OR inurl:sitemap_index.xml OR inurl:sitemap"
        logger.info(f"Searching DuckDuckGo for sitemaps: {query}")
        
        sitemaps = []
        try:
            # Initialize the DDGS context manager to ensure safe resource handling and connection cleanup.
            with DDGS() as ddgs:
                # Execute the text search with a worldwide region scope to maximize result coverage.
                results = ddgs.text(query, region="wt-wt", max_results=max_results)
                for item in results:
                    href = item.get("href")
                    # Validate that the result is a valid URL and explicitly belongs to the target domain.
                    if href and clean_domain in href:
                        sitemaps.append(href)
                
                # Introduce a random delay to mimic human browsing patterns and avoid IP rate limiting or temporary bans.
                time.sleep(random.uniform(1.0, 2.0))
        except Exception as e:
            logger.warning(f"DDG Sitemap search failed: {e}")
            
        # Return a deduplicated list of discovered sitemap URLs to prevent redundant processing downstream.
        return list(set(sitemaps))

    @staticmethod
    def find_all_pages(domain: str, max_results: int = 100) -> list[str]:
        """
        Discover indexed pages by executing multiple targeted search queries.
        This aggressive discovery technique helps uncover deep pages that might be missed by standard crawling.
        """
        clean_domain = DDGDiscoverer._clean_domain(domain)
        # Use a set to automatically handle the deduplication of discovered URLs across multiple queries.
        all_urls = set()
        
        # Define a list of strategic queries to cover different common URL structures (e.g., posts, pages, categories, products).
        queries = [
            f"site:{clean_domain}",
            f"site:{clean_domain} inurl:post",
            f"site:{clean_domain} inurl:page",
            f"site:{clean_domain} inurl:category",
            f"site:{clean_domain} inurl:product",
        ]
        
        logger.info(f"Starting aggressive DDG discovery for {clean_domain}...")
        
        try:
            with DDGS() as ddgs:
                for query in queries:
                    try:
                        logger.info(f"Querying DDG: {query}")
                        results = ddgs.text(query, region="wt-wt", max_results=max_results)
                        for item in results:
                            href = item.get("href")
                            # Ensure the discovered URL is valid and belongs to the target domain before adding it to the set.
                            if href and clean_domain in href:
                                all_urls.add(href)
                        
                        # Apply a randomized delay between different query executions to prevent triggering anti-bot protections.
                        time.sleep(random.uniform(1.5, 3.0))
                    except Exception as e:
                        # Log the failure for the specific query but continue execution with the remaining queries to ensure partial success.
                        logger.warning(f"DDG query failed '{query}': {e}")
                        continue
        except Exception as e:
            logger.error(f"DDG overall discovery failed: {e}")
                    
        logger.info(f"Total unique pages discovered via DDG: {len(all_urls)}")
        # Convert the set back to a list for standard consumption and iteration by other modules.
        return list(all_urls)