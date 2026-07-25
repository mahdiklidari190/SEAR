"""Tests for RobotsManager."""
# This module contains asynchronous unit tests for the RobotsManager class.
# It validates that the manager correctly interprets robots.txt rules 
# and extracts sitemap declarations from live websites.
import pytest

# Import the target class to be tested.
from core.robots_manager import RobotsManager


@pytest.mark.asyncio
async def test_robots_manager_allows_valid_url():
    """
    Test that a standard public URL is allowed by the RobotsManager.
    
    This test verifies the core functionality of the `can_fetch` method 
    by querying a known, permissive domain (example.com). It ensures that 
    the manager correctly defaults to allowing access when no restrictive 
    rules are present for the specified User-Agent.
    """
    # Initialize the manager with the standard SEARBot User-Agent.
    manager = RobotsManager(user_agent="SEARBot/1.0 (+https://klidari.ir/searbot)")
    
    # example.com is a standard IANA-reserved domain with a permissive robots.txt.
    # We test a generic public path to confirm it is not blocked.
    can_fetch = await manager.can_fetch("https://example.com/public-page")
    
    # Assert that the fetch is permitted (True).
    assert can_fetch is True


@pytest.mark.asyncio
async def test_robots_manager_extracts_sitemaps():
    """
    Test that sitemap URLs are correctly extracted from a robots.txt file.
    
    This test validates the `get_sitemaps` method by querying a well-known 
    domain (github.com) that explicitly declares sitemap locations in its 
    robots.txt file. It ensures the parser successfully identifies and 
    returns these URLs as a list.
    """
    # Initialize the manager with a generic User-Agent.
    manager = RobotsManager(user_agent="SEARBot/1.0")
    
    # github.com is a reliable target for this test as it consistently 
    # includes `Sitemap:` directives in its root robots.txt file.
    # Note: We pass the base URL, and the manager will append `/robots.txt` internally.
    sitemaps = await manager.get_sitemaps("https://github.com")
    
    # Assert that the result is a list (even if empty, though github returns multiple).
    # This confirms the method handles the parsing and return type correctly without crashing.
    assert isinstance(sitemaps, list)
    
    # Optional but recommended: Assert that the list is not empty for this specific domain.
    assert len(sitemaps) > 0, "Expected github.com to declare at least one sitemap in robots.txt"