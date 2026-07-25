# core/competitor_extractor.py
import json
import logging
import asyncio
from pathlib import Path

# Import the robust fetching utility, correctly typed to handle resilient HTTP requests.
from core.fetcher import RobustFetcher

logger = logging.getLogger(__name__)

class CompetitorExtractor:
    """Handles the extraction and local storage of competitor webpage data for comparative analysis."""

    def __init__(self, fetcher: RobustFetcher):
        # Initialize with the provided robust fetcher instance for network operations.
        self.fetcher = fetcher
        
        # Define the output path for the competitor data report and ensure the parent directory exists.
        self.output_file = Path("reports/competitors_data.json")
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

    async def extract_and_save(self, page_url: str, competitor_urls: list[str]):
        """
        Fetch content from competitor URLs and append the extracted data to the local JSON report.
        
        Args:
            page_url: The URL of the target page being analyzed.
            competitor_urls: A list of competitor URLs to fetch and analyze.
        """
        if not competitor_urls:
            return

        # Initialize the data structure for the current target page's competitor analysis.
        competitor_data = {
            "target_page": page_url,
            "competitors": []
        }

        for comp_url in competitor_urls:
            try:
                logger.info(f"Fetching competitor content: {comp_url}")
                
                # Use the robust fetcher to retrieve the full HTTP response from the competitor's page.
                result = await self.fetcher.fetch(comp_url)
                
                # Extract the first 1000 characters of the decoded content as a snippet.
                # This prevents the JSON report from becoming excessively large while retaining context.
                content_text = result.content.decode("utf-8", errors="ignore")[:1000] 
                
                competitor_data["competitors"].append({
                    "url": comp_url,
                    "status": "success",
                    "content_snippet": content_text
                })
                
                # Introduce a brief delay between requests to avoid triggering rate limits or IP blocks.
                await asyncio.sleep(1.5)
                
            except Exception as e:
                # Log the failure and record the error details in the report for transparency.
                logger.error(f"Failed to fetch competitor {comp_url}: {e}")
                competitor_data["competitors"].append({
                    "url": comp_url,
                    "status": "failed",
                    "error": str(e)
                })

        # Persist the aggregated competitor data to the local JSON file.
        self._append_to_json(competitor_data)

    def _append_to_json(self, new_data: dict):
        """
        Safely append new data to the JSON report file, including robust error handling 
        for corrupted or malformed existing files.
        """
        try:
            if self.output_file.exists():
                try:
                    with open(self.output_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        
                    # Ensure the loaded data is a list; if not, reset it to prevent append errors.
                    if not isinstance(data, list):
                        data = []
                except json.JSONDecodeError:
                    # If the existing file is empty or corrupted, start fresh with a new list.
                    logger.warning("Competitor JSON file was corrupted or empty. Resetting.")
                    data = []
            else:
                # If the file does not exist yet, initialize an empty list.
                data = []
            
            # Append the newly extracted competitor data to the existing dataset.
            data.append(new_data)
            
            # Write the updated dataset back to the file with proper formatting and UTF-8 support.
            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                
        except Exception as e:
            # Catch and log any unexpected file I/O or serialization errors.
            logger.error(f"Failed to save competitor data to {self.output_file}: {e}")