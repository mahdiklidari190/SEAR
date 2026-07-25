# =============================================================================
# SEO ANALYSIS MODULES IMPORTS
# These modules provide specialized tools for comprehensive technical, 
# structural, and content-based SEO auditing.
# =============================================================================

# Analyzes how efficiently search engine bots crawl the site and identifies wasted crawl budget.
from .crawl_budget import CrawlBudgetAnalyzer

# Evaluates the internal linking structure, page authority distribution, and site hierarchy.
from .link_graph import LinkGraphAnalyzer

# Identifies pages that have no internal links pointing to them, making them hard for crawlers to discover.
from .orphan_pages import OrphanPageDetector

# Scans the website for broken links (e.g., 4xx or 5xx HTTP status codes) that harm user experience and crawl efficiency.
from .broken_links import BrokenLinkChecker

# Checks for redirect chains, loops, and improper redirect types (e.g., temporary vs. permanent) that dilute link equity.
from .redirect_analysis import RedirectAnalyzer

# Ensures XML sitemaps are correctly formatted, accessible, and contain only indexable, canonical URLs.
from .sitemap_validation import SitemapValidator

# Verifies robots.txt rules to ensure critical resources are not accidentally blocked from search engine crawlers.
from .robots_validation import RobotsValidator

# Checks for correct canonical tag implementation across the site to prevent duplicate content indexing issues.
from .canonical_validation import CanonicalValidator

# Performs broad technical SEO checks, including HTTP headers, security configurations, and server response analysis.
from .technical_seo import TechnicalSEOAnalyzer

# Measures and analyzes page experience metrics, specifically LCP, INP/FID, and CLS, against Google's thresholds.
from .core_web_vitals import CoreWebVitalsAnalyzer

# Assesses how well search engine bots can render, parse, and index JavaScript-heavy content and single-page applications.
from .js_rendering import JSRenderingAnalyzer

# Validates responsive design, viewport configuration, and overall mobile usability standards.
from .mobile_friendly import MobileFriendlyAnalyzer

# Ensures breadcrumb navigation is structurally sound, logically reflects the site hierarchy, and is correctly marked up.
from .breadcrumb_validation import BreadcrumbValidator

# Validates structured data (JSON-LD) for syntax errors, completeness, and eligibility for search engine rich results.
from .schema_validation import SchemaValidator

# Reviews pagination implementations (e.g., rel="next"/"prev", load more, or infinite scroll) for crawlability and indexation.
from .pagination_analysis import PaginationAnalyzer

# Prevents crawl waste and duplicate content issues arising from faceted navigation (filter and sort URL parameters).
from .faceted_navigation import FacetedNavigationAnalyzer

# Detects near-duplicate, thin, or overly similar content across different pages on the same website.
from .content_similarity import ContentSimilarityAnalyzer

# Identifies instances where multiple pages on the same site are unintentionally competing for the same target keywords.
from .keyword_cannibalization import KeywordCannibalizationDetector

# Evaluates the relevance, diversity, and optimization of internal and external anchor text profiles.
from .anchor_text import AnchorTextAnalyzer