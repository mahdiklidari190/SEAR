# ==============================================================================
# MODELS PACKAGE INITIALIZATION
# This module acts as the central registry for the application's data structures.
# It exposes the core data models used to pass structured, type-safe information 
# between the crawling, extraction, analysis, and reporting phases of the SEO engine.
# ==============================================================================

# Import the foundational data models representing a single webpage's extracted attributes.
# 'PageData' is the primary container, while 'LinkAnalysis', 'ImageAnalysis', 
# and 'StructuredData' encapsulate specific on-page element metrics and relationships.
from .page_data import PageData, LinkAnalysis, ImageAnalysis, StructuredData

# Import the standardized Issue model.
# This structure is used to consistently log, categorize, and report every SEO 
# error, warning, and recommendation generated during the page analysis process.
from .issues import Issue

# Import high-level reporting and competitor benchmarking models.
# 'AnalysisReport' aggregates the final scores and findings for the user, 
# while 'CompetitorData' holds the scraped metrics of rival pages for comparative gap analysis.
from .reports import AnalysisReport, CompetitorData

# Import specialized data models for external API integrations and deep technical audits.
# These structures map the complex JSON responses from services like Google Search Console, 
# Google Analytics, and backlink APIs, as well as internal technical checks like 
# crawl budget, link graphs, Core Web Vitals, and validation results for sitemaps and robots.txt.
from .integrations import (
    SearchConsoleData, AnalyticsData, BacklinkData,
    CrawlBudgetReport, LinkGraphData, TechnicalSEOResult,
    CoreWebVitals, RedirectInfo, SitemapValidationResult,
    RobotsValidationResult, SchemaValidationResult,
)