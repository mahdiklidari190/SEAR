"""Competitor Finder - preserved from original."""
from __future__ import annotations

import asyncio
import logging

from models.reports import CompetitorData
from core.fetcher import RobustFetcher

logger = logging.getLogger(__name__)


class CompetitorFinder:
    """Find competitors via search engine queries."""

    def __init__(self, fetcher: RobustFetcher):
        self.fetcher = fetcher

    async def find_competitors(self, keywords: str, num_results: int = 3) -> list[CompetitorData]:
        if not keywords:
            return []
        query = " ".join(keywords.split(",")[:3])

        try:
            from duckduckgo_search import DDGS

            loop = asyncio.get_running_loop()

            def _search():
                try:
                    with DDGS() as ddgs:
                        return list(ddgs.text(query, region="wt-wt", max_results=num_results * 2))
                except Exception as e:
                    logger.warning(f"DDGS Search failed: {e}")
                    return []

            search_results = await loop.run_in_executor(None, _search)
            results = []
            rank_counter = 1
            for item in search_results:
                if len(results) >= num_results:
                    break
                url = item.get("href")
                if not url or not url.startswith("http"):
                    continue
                results.append(CompetitorData(
                    rank=rank_counter,
                    url=url,
                    title=item.get("title", ""),
                    meta_description=item.get("body", ""),
                    h1=[],
                ))
                rank_counter += 1
            return results
        except ImportError:
            return []
        except Exception as e:
            logger.error(f"Competitor search failed: {e}")
            return []