"""Page data models - preserved and extended."""
# This module defines the comprehensive Pydantic data models used to store 
# all extracted metrics, attributes, and analysis results for a single webpage.
# These models ensure type safety, structured data handling, and easy serialization 
# (e.g., to JSON) for reporting and downstream AI processing.
from __future__ import annotations

from typing import Optional, List, Any
from pydantic import BaseModel, Field

from .issues import Issue


class LinkAnalysis(BaseModel):
    """Stores detailed metrics and data regarding the page's internal and external link profile."""
    total: int = 0
    internal: int = 0
    external: int = 0
    nofollow: int = 0
    sponsored: int = 0
    ugc: int = 0
    empty_orphan: int = 0
    internal_urls: list[str] = Field(default_factory=list)
    external_urls: list[str] = Field(default_factory=list)
    anchor_texts: list[dict[str, str]] = Field(default_factory=list)


class ImageAnalysis(BaseModel):
    """Tracks image optimization metrics, including accessibility (alt text) and performance attributes."""
    total: int = 0
    missing_alt: int = 0
    empty_alt: int = 0
    duplicate_alt: set[str] = Field(default_factory=set)
    missing_dimensions: int = 0
    modern_format: int = 0
    lazy_loaded: int = 0
    oversized_images: list[str] = Field(default_factory=list)
    render_blocking: list[str] = Field(default_factory=list)


class StructuredData(BaseModel):
    """Holds information about JSON-LD or other structured data implementations found on the page."""
    found: bool = False
    types: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    raw_json: list[dict] = Field(default_factory=list)


class SecurityHeaders(BaseModel):
    """Evaluates the presence and correctness of critical HTTP security headers."""
    hsts: bool = False
    csp: bool = False
    x_frame_options: str = ""
    x_content_type_options: bool = False
    referrer_policy: str = ""
    permissions_policy: bool = False
    coop: bool = False
    corp: bool = False
    issues: list[str] = Field(default_factory=list)


class PerformanceData(BaseModel):
    """Captures server-side and network-level performance metrics from the HTTP response."""
    ttfb_ms: float = 0.0
    connection_time_ms: float = 0.0
    total_time_ms: float = 0.0
    http_version: str = ""
    compression: str = ""
    server: str = ""
    cdn_detected: str = ""
    cache_control: str = ""
    etag: bool = False
    last_modified: bool = False


class SSLData(BaseModel):
    """Stores SSL/TLS certificate details and identifies any mixed content security warnings."""
    valid: bool = False
    issuer: str = ""
    expiry_date: str = ""
    tls_version: str = ""
    mixed_content: list[str] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)


class JSRenderingData(BaseModel):
    """Analyzes the JavaScript execution environment, framework detection, and rendering strategy."""
    framework_detected: str = ""
    is_spa: bool = False
    client_rendered: bool = False
    server_rendered: bool = False
    hydration_issues: list[str] = Field(default_factory=list)
    render_blocking_scripts: list[str] = Field(default_factory=list)


class MobileData(BaseModel):
    """Evaluates core mobile usability signals, primarily focusing on viewport configuration and responsive design."""
    has_viewport: bool = False
    viewport_content: str = ""
    font_size_issues: list[str] = Field(default_factory=list)
    tap_target_issues: list[str] = Field(default_factory=list)
    responsive_images: bool = False
    is_mobile_friendly: bool = True


class BreadcrumbData(BaseModel):
    """Tracks the presence and validity of breadcrumb navigation, both visually and via schema markup."""
    found: bool = False
    schema_valid: bool = False
    hierarchy_correct: bool = True
    items: list[str] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)


class PaginationData(BaseModel):
    """Identifies pagination signals (rel=next/prev) and checks for canonicalization conflicts across paginated series."""
    has_next: bool = False
    has_prev: bool = False
    next_url: str = ""
    prev_url: str = ""
    canonical_conflict: bool = False
    depth: int = 0
    issues: list[str] = Field(default_factory=list)


class PageData(BaseModel):
    """
    Complete page analysis data - preserved and extended.
    This is the master aggregation model that combines all extracted metadata, 
    technical metrics, content analysis, and detected issues into a single, 
    cohesive object representing the SEO health of a specific URL.
    """
    url: str
    status_code: int = 0
    
    # Basic Metadata
    title: str = ""
    meta_description: str = ""
    meta_keywords: str = ""
    meta_robots: str = ""
    meta_author: str = ""
    canonical_url: str = ""
    
    # Social Media Metadata
    og_title: str = ""
    og_description: str = ""
    og_image: str = ""
    twitter_card: str = ""
    
    # Heading Structure
    h1: list[str] = Field(default_factory=list)
    h2: list[str] = Field(default_factory=list)
    h3: list[str] = Field(default_factory=list)
    h4: list[str] = Field(default_factory=list)
    
    # Internationalization
    hreflang: dict[str, str] = Field(default_factory=dict)
    x_default: str = ""
    
    # Specialized Analysis Modules
    links: LinkAnalysis = Field(default_factory=LinkAnalysis)
    images: ImageAnalysis = Field(default_factory=ImageAnalysis)
    structured_data: StructuredData = Field(default_factory=StructuredData)
    
    # Accessibility & Content
    accessibility_lang: str = ""
    accessibility_issues: list[str] = Field(default_factory=list)
    text_sample: str = ""
    word_count: int = 0
    
    # Scoring & Issues
    issues: list[Issue] = Field(default_factory=list)
    scores: dict[str, int] = Field(default_factory=dict)
    overall_score: int = 0

    # Extended Technical Metrics
    security_headers: SecurityHeaders = Field(default_factory=SecurityHeaders)
    performance: PerformanceData = Field(default_factory=PerformanceData)
    ssl_data: SSLData = Field(default_factory=SSLData)
    js_rendering: JSRenderingData = Field(default_factory=JSRenderingData)
    mobile: MobileData = Field(default_factory=MobileData)
    breadcrumbs: BreadcrumbData = Field(default_factory=BreadcrumbData)
    pagination: PaginationData = Field(default_factory=PaginationData)
    
    # Crawl & Network Data
    crawl_depth: int = 0
    redirect_chain: list[str] = Field(default_factory=list)
    content_hash: str = ""
    keywords: str = ""
    response_headers: dict[str, str] = Field(default_factory=dict)
    
    # Extensions for Advanced Reporting and AI Integration
    # These fields store comparative competitor data and the generated AI master prompt.
    competitors: List[Any] = Field(default_factory=list)
    ai_prompt: str = ""