"""Competitor Finder - Updated to use Google Chrome automation with robust driver management."""
from __future__ import annotations
import asyncio
import logging
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from models.reports import CompetitorData

logger = logging.getLogger(__name__)

class CompetitorFinder:
    """Find competitors via Google Chrome search automation."""

    def __init__(self, fetcher=None):
        # Store the optional HTTP fetcher instance for potential future use or fallback mechanisms.
        self.fetcher = fetcher

    async def find_competitors(self, keywords: str, num_results: int = 3) -> list[CompetitorData]:
        """Search Google and extract competitor data asynchronously."""
        if not keywords:
            return []
        
        # Retrieve the current running event loop to execute the synchronous Selenium operations 
        # in a separate thread, preventing the async application from blocking.
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, 
            self._sync_find_competitors, 
            keywords, 
            num_results
        )

    def _sync_find_competitors(self, keywords: str, num_results: int) -> list[CompetitorData]:
        # Extract the first three keywords from the comma-separated string to form a concise search query.
        query = " ".join(keywords.split(",")[:3])
        results = []
        
        # Configure Chrome options for headless, automated browsing.
        chrome_options = Options()
        chrome_options.add_argument("--headless=new") # Use the new headless mode for better reliability and performance
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled") # Hide automation flags to avoid detection
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Rotate through a list of realistic user agents to avoid immediate detection and blocking by Google.
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        ]
        chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")

        driver = None
        try:
            # Explicitly use ChromeDriverManager to automatically download and manage the correct ChromeDriver 
            # version, resolving common path and compatibility issues, especially on Windows environments.
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Construct the Google search URL, requesting double the desired number of results 
            # to account for filtering out social media and irrelevant domains later.
            search_url = f"https://www.google.com/search?q={query}&num={num_results * 2}"
            logger.info(f"Searching Google for competitors: {query}")
            driver.get(search_url)
            
            # Introduce a random delay to simulate human behavior and allow the page to fully render dynamic content.
            time.sleep(random.uniform(3.0, 5.0))
            
            # Locate all anchor tags within the main search result containers (class "g") that start with "http".
            elements = driver.find_elements(By.CSS_SELECTOR, "div.g a[href^='http']")
            
            rank_counter = 1
            for el in elements:
                # Stop collecting once we have reached the requested number of valid competitors.
                if len(results) >= num_results:
                    break
                
                url = el.get_attribute("href")
                
                # Filter out irrelevant results, including Google's own services and major social media platforms.
                if not url or any(x in url for x in ["google.com", "youtube.com", "facebook.com", "twitter.com", "linkedin.com"]):
                    continue
                
                try:
                    # Attempt to extract the visible title from the H3 tag within the search result.
                    title = el.find_element(By.TAG_NAME, "h3").text
                except Exception:
                    # Fallback to the URL itself if the title cannot be extracted due to DOM variations.
                    title = url

                # Append the extracted data as a structured CompetitorData object.
                results.append(CompetitorData(
                    rank=rank_counter,
                    url=url,
                    title=title,
                    meta_description="",
                    h1=[],
                ))
                rank_counter += 1
                
            return results
            
        except Exception as e:
            # Log any unexpected errors during the Chrome automation process for debugging and monitoring purposes.
            logger.error(f"Chrome competitor search failed for '{query}': {e}")
            return []
        finally:
            # Ensure the browser instance is properly closed and system resources are freed, even if an error occurs.
            if driver:
                driver.quit()