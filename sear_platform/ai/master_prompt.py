"""AI SEO Master Prompt Generator - massively upgraded."""
from __future__ import annotations

# Import data models representing various SEO metrics and page attributes.
# These models ensure type safety and structured data handling throughout the generation process.
from models.page_data import PageData
from models.reports import CompetitorData
from models.integrations import (
    SearchConsoleData, AnalyticsData, BacklinkData,
    CrawlBudgetReport, LinkGraphData, CoreWebVitals,
)


class AIMasterPromptGenerator:
    """
    Generate an extremely detailed AI prompt for SEO implementation.
    This class aggregates multiple data sources into a single, comprehensive 
    context string designed to guide an AI in producing actionable SEO recommendations.
    """

    @staticmethod
    def generate(
        page: PageData,
        keywords: str,
        competitors: list[CompetitorData],
        search_console: SearchConsoleData = None,
        analytics: AnalyticsData = None,
        backlinks: BacklinkData = None,
        crawl_budget: CrawlBudgetReport = None,
        link_graph: LinkGraphData = None,
        cwv: CoreWebVitals = None,
    ) -> str:
        """
        Generate the master AI SEO prompt.
        
        Args:
            page: Core data about the target webpage.
            keywords: Target keywords for the page.
            competitors: List of competitor page data.
            search_console: Optional Google Search Console metrics.
            analytics: Optional Google Analytics metrics.
            backlinks: Optional backlink profile data.
            crawl_budget: Optional crawl budget analysis report.
            link_graph: Optional internal linking structure data.
            cwv: Optional Core Web Vitals performance metrics.
            
        Returns:
            A fully formatted, implementation-ready string prompt for the AI.
        """

        # Initialize optional data sources with default empty states if not provided.
        # This prevents NoneType errors and ensures the prompt template remains consistent.
        sc = search_console or SearchConsoleData()
        an = analytics or AnalyticsData()
        bl = backlinks or BacklinkData()
        cb = crawl_budget or CrawlBudgetReport()
        lg = link_graph or LinkGraphData()
        cv = cwv or CoreWebVitals()

        # Format competitor data into a readable, ranked string (limiting title and description length).
        comp_str = "\n".join([
            f"  #{c.rank}: {c.url} | Title: {c.title[:80]} | Desc: {c.meta_description[:120]}"
            for c in competitors
        ]) or "  No competitor data available."

        # Format the top 20 detected SEO issues with their severity, category, problem, and solution.
        issues_str = "\n".join([
            f"  [{i.severity}] {i.category}: {i.problem} → {i.solution}"
            for i in page.issues[:20]
        ]) or "  No issues detected."

        # Conditionally build the Search Console data block if the data is available.
        sc_str = ""
        if sc.available:
            sc_str = f"""
SEARCH CONSOLE DATA:
  Total Clicks: {sc.total_clicks} | Impressions: {sc.total_impressions} | Avg CTR: {sc.average_ctr}% | Avg Position: {sc.average_position}
  Top Queries: {', '.join([q.query for q in sc.top_queries[:10]])}
  High Impression/Low CTR Pages: {len(sc.high_impression_low_ctr)}
  Pages at Position 8-15: {len(sc.position_8_15)}
  Zero-Click Pages: {len(sc.zero_click_pages)}
"""

        # Conditionally build the Google Analytics data block if the data is available.
        an_str = ""
        if an.available:
            an_str = f"""
GOOGLE ANALYTICS DATA:
  Sessions: {an.sessions} | Users: {an.users} | Bounce Rate: {an.bounce_rate}%
  Avg Engagement: {an.avg_engagement_time}s | Conversions: {an.conversions}
  Traffic Sources: {an.traffic_sources}
"""

        # Conditionally build the Backlink data block if the data is available.
        bl_str = ""
        if bl.available:
            bl_str = f"""
BACKLINK DATA ({bl.source}):
  Total Backlinks: {bl.total_backlinks} | Referring Domains: {bl.referring_domains} | DR: {bl.domain_rating}
"""

        # Construct the master prompt template. 
        # NOTE: This is a single, comprehensive f-string. Comments are kept outside 
        # to avoid altering the actual generated prompt text delivered to the AI.
        prompt = f"""
═══════════════════════════════════════════════════════════════════════════════
ENTERPRISE AI SEO MASTER PROMPT - IMPLEMENTATION-READY ANALYSIS
═══════════════════════════════════════════════════════════════════════════════

You are a Senior Technical SEO Engineer, Content Strategist, and Digital Marketing Expert
with 15+ years of experience. You have deep expertise in Google's algorithm, Core Web Vitals,
Schema.org, semantic SEO, and enterprise-level site architecture.

Your task: Analyze the following comprehensive SEO data and produce a COMPLETE,
IMPLEMENTATION-READY action plan. Every recommendation must be specific, actionable,
and include exact code snippets where applicable.

═══════════════════════════════════════════════════════════════════════════════
SECTION 1: CURRENT STATE ANALYSIS
═══════════════════════════════════════════════════════════════════════════════

TARGET URL: {page.url}
OVERALL SEO SCORE: {page.overall_score}/100
STATUS CODE: {page.status_code}

SCORE BREAKDOWN:
{chr(10).join([f"  • {k}: {v}/100" for k, v in page.scores.items()])}

TARGET KEYWORDS: {keywords}

═══════════════════════════════════════════════════════════════════════════════
SECTION 2: METADATA & ON-PAGE ELEMENTS
═══════════════════════════════════════════════════════════════════════════════

TITLE TAG: "{page.title}" ({len(page.title)} chars)
META DESCRIPTION: "{page.meta_description}" ({len(page.meta_description)} chars)
META ROBOTS: {page.meta_robots or 'index, follow'}
CANONICAL: {page.canonical_url or 'MISSING'}
META KEYWORDS: {page.meta_keywords or 'None'}
OG TITLE: {page.og_title or 'Missing'}
OG DESCRIPTION: {page.og_description or 'Missing'}
OG IMAGE: {page.og_image or 'Missing'}
TWITTER CARD: {page.twitter_card or 'Missing'}
HREFLANG: {page.hreflang or 'None'} | x-default: {page.x_default or 'None'}
LANGUAGE: {page.accessibility_lang or 'MISSING'}

═══════════════════════════════════════════════════════════════════════════════
SECTION 3: HEADING STRUCTURE
═══════════════════════════════════════════════════════════════════════════════

H1 ({len(page.h1)}): {page.h1 or 'MISSING'}
H2 ({len(page.h2)}): {page.h2[:8]}
H3 ({len(page.h3)}): {page.h3[:8]}
H4 ({len(page.h4)}): {page.h4[:5]}
WORD COUNT: {page.word_count}

═══════════════════════════════════════════════════════════════════════════════
SECTION 4: LINK ANALYSIS
═══════════════════════════════════════════════════════════════════════════════

Total Links: {page.links.total}
Internal: {page.links.internal} | External: {page.links.external}
Nofollow: {page.links.nofollow} | Sponsored: {page.links.sponsored} | UGC: {page.links.ugc}
Empty/Orphan: {page.links.empty_orphan}

═══════════════════════════════════════════════════════════════════════════════
SECTION 5: IMAGE ANALYSIS
═══════════════════════════════════════════════════════════════════════════════

Total Images: {page.images.total}
Missing Alt: {page.images.missing_alt} | Empty Alt: {page.images.empty_alt}
Duplicate Alt: {len(page.images.duplicate_alt)} | Missing Dimensions: {page.images.missing_dimensions}
Modern Formats: {page.images.modern_format} | Lazy Loaded: {page.images.lazy_loaded}

═══════════════════════════════════════════════════════════════════════════════
SECTION 6: STRUCTURED DATA
═══════════════════════════════════════════════════════════════════════════════

Found: {'Yes' if page.structured_data.found else 'No'}
Types: {page.structured_data.types or 'None'}
Errors: {page.structured_data.errors or 'None'}

═══════════════════════════════════════════════════════════════════════════════
SECTION 7: TECHNICAL SEO & SECURITY
═══════════════════════════════════════════════════════════════════════════════

HTTP Version: {page.performance.http_version}
Compression: {page.performance.compression or 'None'}
Server: {page.performance.server or 'Unknown'}
CDN: {page.performance.cdn_detected or 'Not detected'}
TTFB: {page.performance.ttfb_ms}ms
Cache-Control: {page.performance.cache_control or 'Not set'}
ETag: {'Yes' if page.performance.etag else 'No'}
Last-Modified: {'Yes' if page.performance.last_modified else 'No'}

SECURITY HEADERS:
  HSTS: {'✓' if page.security_headers.hsts else '✗ MISSING'}
  CSP: {'✓' if page.security_headers.csp else '✗ MISSING'}
  X-Frame-Options: {page.security_headers.x_frame_options or '✗ MISSING'}
  X-Content-Type-Options: {'✓' if page.security_headers.x_content_type_options else '✗ MISSING'}
  Referrer-Policy: {page.security_headers.referrer_policy or '✗ MISSING'}
  Permissions-Policy: {'✓' if page.security_headers.permissions_policy else '✗ MISSING'}
  COOP: {'✓' if page.security_headers.coop else '✗ MISSING'}
  CORP: {'✓' if page.security_headers.corp else '✗ MISSING'}

SSL/TLS: {page.ssl_data.tls_version or 'Unknown'} | Expiry: {page.ssl_data.expiry_date or 'Unknown'}
Mixed Content: {len(page.ssl_data.mixed_content)} items

═══════════════════════════════════════════════════════════════════════════════
SECTION 8: CORE WEB VITALS (ESTIMATED)
═══════════════════════════════════════════════════════════════════════════════

TTFB: {cv.ttfb_ms}ms
LCP: {cv.lcp_estimate}
CLS: {cv.cls_estimate}
Render-Blocking Resources: {len(cv.render_blocking_resources)}
Recommendations: {cv.recommendations}

═══════════════════════════════════════════════════════════════════════════════
SECTION 9: JAVASCRIPT RENDERING
═══════════════════════════════════════════════════════════════════════════════

Framework: {page.js_rendering.framework_detected or 'None'}
SPA: {'Yes' if page.js_rendering.is_spa else 'No'}
Rendering: {'Client-Side' if page.js_rendering.client_rendered else 'Server-Side' if page.js_rendering.server_rendered else 'Unknown'}
Render-Blocking Scripts: {len(page.js_rendering.render_blocking_scripts)}

═══════════════════════════════════════════════════════════════════════════════
SECTION 10: MOBILE ANALYSIS
═══════════════════════════════════════════════════════════════════════════════

Viewport: {'✓' if page.mobile.has_viewport else '✗ MISSING'}
Mobile Friendly: {'Yes' if page.mobile.is_mobile_friendly else 'No'}
Responsive Images: {'Yes' if page.mobile.responsive_images else 'No'}

═══════════════════════════════════════════════════════════════════════════════
SECTION 11: ALL DETECTED ISSUES
═══════════════════════════════════════════════════════════════════════════════

{issues_str}

═══════════════════════════════════════════════════════════════════════════════
SECTION 12: COMPETITOR ANALYSIS
═══════════════════════════════════════════════════════════════════════════════

{comp_str}

═══════════════════════════════════════════════════════════════════════════════
SECTION 13: CRAWL BUDGET
═══════════════════════════════════════════════════════════════════════════════

Total URLs: {cb.total_urls} | Duplicates: {cb.duplicate_urls} | Redirects: {cb.redirect_urls}
Parameter URLs: {cb.parameter_urls} | Max Depth: {cb.max_crawl_depth}
Wasted Budget: {cb.wasted_budget_pct}%

═══════════════════════════════════════════════════════════════════════════════
SECTION 14: INTERNAL LINK GRAPH
═══════════════════════════════════════════════════════════════════════════════

Total Pages: {lg.total_pages} | Total Links: {lg.total_internal_links}
Orphan Pages: {len(lg.orphan_pages)} | Hub Pages: {len(lg.hub_pages)}
Weak Pages: {len(lg.weak_pages)} | Avg Links/Page: {lg.avg_links_per_page}
{sc_str}{an_str}{bl_str}
═══════════════════════════════════════════════════════════════════════════════
YOUR TASK - PRODUCE ALL OF THE FOLLOWING:
═══════════════════════════════════════════════════════════════════════════════

1. EXECUTIVE SUMMARY (2-3 sentences on overall health)

2. CONTENT GAP ANALYSIS
   - What topics/sections competitors have that we lack
   - Missing semantic entities
   - Content depth comparison

3. TITLE TAG REWRITES (3 options, <60 chars each, with primary keyword)

4. META DESCRIPTION REWRITES (3 options, <160 chars, with CTA)

5. HEADING RESTRUCTURE
   - Ideal H1-H4 tree incorporating target keywords naturally

6. CONTENT REWRITE GUIDELINES
   - Paragraph-by-paragraph improvement suggestions
   - Entity and semantic keyword additions
   - Readability improvements

7. FAQ SUGGESTIONS (5 questions with answers for FAQPage schema)

8. JSON-LD SCHEMA RECOMMENDATIONS
   - Provide COMPLETE, copy-paste-ready JSON-LD code for:
     * Organization/WebSite
     * BreadcrumbList
     * Article or relevant type
     * FAQPage (if applicable)

9. INTERNAL LINKING STRATEGY
   - Specific pages to link to/from
   - Anchor text recommendations
   - Orphan page fix strategy

10. EXTERNAL LINKING SUGGESTIONS
    - Authoritative sources to cite
    - Link-worthy content opportunities

11. TECHNICAL FIXES (prioritized)
    - Security headers implementation (exact code)
    - Performance optimizations
    - Crawl budget fixes

12. CTR OPTIMIZATION
    - SERP snippet improvements
    - Rich result eligibility

13. IMAGE OPTIMIZATION PLAN
    - Fix {page.images.missing_alt} missing alts (provide examples)
    - Format/dimension recommendations

14. PRIORITY ROADMAP:
    - DAY 1: Critical fixes (list specific actions)
    - WEEK 1: High-impact improvements
    - MONTH 1: Strategic content and technical work
    - QUARTER 1: Authority building and advanced optimization

15. EXPECTED IMPACT:
    - Estimated ranking improvement timeline
    - Expected traffic increase percentage
    - CTR improvement projection

16. DAILY/WEEKLY/MONTHLY SEO TASKS:
    - Daily: Monitoring tasks
    - Weekly: Content and link tasks
    - Monthly: Technical audits and strategy reviews

Respond in the same language as the website content. Be extremely specific and actionable.
Include exact code snippets, exact text rewrites, and exact implementation steps.
═══════════════════════════════════════════════════════════════════════════════
"""
        # Return the fully assembled, data-injected prompt string to the caller.
        return prompt