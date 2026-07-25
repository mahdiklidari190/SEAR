# Import core crawling and analysis components from the local package.
# These modules handle the foundational steps of the SEO auditing pipeline: 
# fetching data, extracting content, scoring, and parsing standard web files.

# Handles resilient HTTP requests, including retry logic, timeout management, 
# and robust error handling to ensure reliable data collection from target websites.
from .fetcher import RobustFetcher

# Parses raw HTML content to extract structured SEO-relevant data, 
# such as meta tags, headings, links, images, and text content.
from .extractor import ContentExtractor

# Evaluates the extracted page data against established SEO best practices 
# to generate a quantitative, multi-dimensional SEO health score.
from .scorer import SEOScorer

# Identifies exact or near-duplicate content across different pages to prevent 
# keyword cannibalization and index bloat. Includes both the class and a pre-instantiated singleton.
from .duplicate_detector import DuplicateDetector, duplicate_detector

# Provides specialized parsing logic for standard web crawler directive files.
# SitemapParser handles XML sitemap validation and URL extraction, 
# while RobotsParser interprets robots.txt rules and crawl allowances.
from .parser import SitemapParser, RobotsParser