"""Integration and extended analysis models."""
from __future__ import annotations

# Import Pydantic components for robust data validation and structured modeling.
from pydantic import BaseModel, Field


class SearchConsoleQueryData(BaseModel):
    """Represents performance metrics for a single search query."""
    query: str = ""
    clicks: int = 0
    impressions: int = 0
    ctr: float = 0.0
    position: float = 0.0


class SearchConsolePageData(BaseModel):
    """Represents performance metrics for a specific landing page in search results."""
    page: str = ""
    clicks: int = 0
    impressions: int = 0
    ctr: float = 0.0
    position: float = 0.0


class SearchConsoleData(BaseModel):
    """
    Aggregates comprehensive Google Search Console data.
    Includes overall metrics, top-performing queries and pages, 
    and specific opportunity buckets for actionable SEO improvements.
    """
    available: bool = False
    total_clicks: int = 0
    total_impressions: int = 0
    average_ctr: float = 0.0
    average_position: float = 0.0
    top_queries: list[SearchConsoleQueryData] = Field(default_factory=list)
    top_pages: list[SearchConsolePageData] = Field(default_factory=list)
    countries: dict[str, int] = Field(default_factory=dict)
    devices: dict[str, int] = Field(default_factory=dict)
    coverage_issues: list[str] = Field(default_factory=list)
    index_status: str = ""
    # Opportunity buckets for targeted optimization
    high_impression_low_ctr: list[SearchConsolePageData] = Field(default_factory=list)
    position_8_15: list[SearchConsolePageData] = Field(default_factory=list)
    zero_click_pages: list[SearchConsolePageData] = Field(default_factory=list)


class AnalyticsData(BaseModel):
    """
    Aggregates Google Analytics metrics to provide context on user behavior 
    and traffic quality alongside search performance data.
    """
    available: bool = False
    sessions: int = 0
    users: int = 0
    bounce_rate: float = 0.0
    avg_engagement_time: float = 0.0
    landing_pages: list[dict[str, int]] = Field(default_factory=list)
    traffic_sources: dict[str, int] = Field(default_factory=dict)
    conversions: int = 0


class BacklinkData(BaseModel):
    """
    Holds backlink profile data fetched from third-party SEO APIs 
    (e.g., Ahrefs, SEMrush, DataForSEO) to assess domain authority and link equity.
    """
    available: bool = False
    source: str = ""
    total_backlinks: int = 0
    referring_domains: int = 0
    domain_rating: float = 0.0
    top_backlinks: list[dict[str, str]] = Field(default_factory=list)


class CrawlBudgetReport(BaseModel):
    """
    Summarizes crawl efficiency, highlighting how much of the search engine's 
    crawl budget is wasted on non-valuable URLs (duplicates, redirects, parameters).
    """
    total_urls: int = 0
    duplicate_urls: int = 0
    redirect_urls: int = 0
    blocked_urls: int = 0
    parameter_urls: int = 0
    max_crawl_depth: int = 0
    wasted_budget_pct: float = 0.0
    recommendations: list[str] = Field(default_factory=list)


class LinkGraphNode(BaseModel):
    """
    Represents a single page within the internal link graph, 
    detailing its connectivity (inlinks/outlinks) and calculated authority score.
    """
    url: str
    inlinks: int = 0
    outlinks: int = 0
    is_orphan: bool = False
    is_hub: bool = False
    authority_score: float = 0.0


class LinkGraphData(BaseModel):
    """
    Aggregates the entire site's internal linking structure.
    Identifies structural SEO issues such as orphan pages, hub pages, and weakly linked pages.
    """
    total_pages: int = 0
    total_internal_links: int = 0
    orphan_pages: list[str] = Field(default_factory=list)
    hub_pages: list[str] = Field(default_factory=list)
    weak_pages: list[str] = Field(default_factory=list)
    nodes: list[LinkGraphNode] = Field(default_factory=list)
    edges: list[dict[str, str]] = Field(default_factory=list)
    avg_links_per_page: float = 0.0


class RedirectInfo(BaseModel):
    """Details a specific HTTP redirect, including its chain length and whether it forms a loop."""
    source_url: str
    target_url: str
    status_code: int
    chain_length: int = 1
    is_loop: bool = False


class TechnicalSEOResult(BaseModel):
    """
    Captures server-level technical metrics and security configurations, 
    including HTTP protocol versions, compression support, CDN usage, and TLS details.
    """
    http2: bool = False
    http3: bool = False
    compression_type: str = ""
    brotli_supported: bool = False
    gzip_supported: bool = False
    dns_lookup_ms: float = 0.0
    cdn_provider: str = ""
    server_software: str = ""
    tls_version: str = ""
    cert_expiry: str = ""
    mixed_content_count: int = 0
    security_issues: list[str] = Field(default_factory=list)


class CoreWebVitals(BaseModel):
    """
    Holds estimated or actual Core Web Vitals metrics (LCP, CLS, INP, etc.) 
    along with related performance bottlenecks and actionable optimization recommendations.
    """
    lcp_estimate: str = ""
    cls_estimate: str = ""
    inp_estimate: str = ""
    fcp_estimate: str = ""
    tbt_estimate: str = ""
    ttfb_ms: float = 0.0
    speed_index: str = ""
    largest_images: list[str] = Field(default_factory=list)
    render_blocking_resources: list[str] = Field(default_factory=list)
    unused_css_estimate: str = ""
    unused_js_estimate: str = ""
    font_issues: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class SitemapValidationResult(BaseModel):
    """
    Reports on the health and compliance of an XML sitemap, 
    flagging invalid, dead, or orphaned URLs, as well as missing metadata like lastmod.
    """
    sitemap_type: str = ""  # xml, image, video, news
    total_urls: int = 0
    valid_urls: int = 0
    invalid_urls: list[str] = Field(default_factory=list)
    dead_urls: list[str] = Field(default_factory=list)
    orphan_urls: list[str] = Field(default_factory=list)
    missing_lastmod: int = 0
    invalid_lastmod: int = 0
    issues: list[str] = Field(default_factory=list)


class RobotsValidationResult(BaseModel):
    """
    Summarizes the parsed rules of a robots.txt file, 
    flagging any critical blocking issues, syntax errors, or missing sitemap declarations.
    """
    valid_syntax: bool = True
    disallow_rules: list[str] = Field(default_factory=list)
    allow_rules: list[str] = Field(default_factory=list)
    sitemaps_declared: list[str] = Field(default_factory=list)
    crawl_delay: Optional[int] = None
    host: str = ""
    blocked_important_pages: list[str] = Field(default_factory=list)
    syntax_errors: list[str] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)


class SchemaValidationResult(BaseModel):
    """
    Details the findings of structured data (JSON-LD) validation, 
    including found schema types, syntax errors, and missing recommended schemas.
    """
    schemas_found: list[str] = Field(default_factory=list)
    valid_schemas: list[str] = Field(default_factory=list)
    invalid_schemas: list[dict[str, str]] = Field(default_factory=list)
    missing_recommended: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


# Note: The Optional import is placed here as per the original code structure.
# In standard Python practice, this is typically moved to the top of the file alongside other imports.
from typing import Optional