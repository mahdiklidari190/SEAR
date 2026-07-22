"""TXT Report Generator - preserved from original with extensions."""
from __future__ import annotations

from models.page_data import PageData
from models.reports import CompetitorData
from models.integrations import SearchConsoleData, AnalyticsData


class TXTReportGenerator:
    """Generate comprehensive TXT reports."""

    @staticmethod
    def generate(
        page: PageData,
        competitors: list[CompetitorData],
        keywords: str,
        robots_txt: str,
        ai_prompt: str,
        search_console: SearchConsoleData = None,
        analytics: AnalyticsData = None,
    ) -> str:
        issues_sorted = sorted(
            page.issues,
            key=lambda x: {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}.get(x.severity, 4)
        )
        critical_issues = [i for i in issues_sorted if i.severity == "Critical"]
        warnings = [i for i in issues_sorted if i.severity in ["High", "Medium"]]
        quick_wins = [i for i in issues_sorted if i.difficulty == "Easy" and i.fix_time in ["2 mins", "5 mins", "10 mins"]]

        comp_str = "\n".join([f"• [#{c.rank}] {c.url} | Title: {c.title[:50]}..." for c in competitors]) or "No competitors found."

        sc_section = ""
        if search_console and search_console.available:
            sc_section = f"""
========================================================================
[11] SEARCH CONSOLE DATA
========================================================================
• Total Clicks: {search_console.total_clicks}
• Total Impressions: {search_console.total_impressions}
• Average CTR: {search_console.average_ctr}%
• Average Position: {search_console.average_position}
• High Impression/Low CTR Pages: {len(search_console.high_impression_low_ctr)}
• Pages at Position 8-15: {len(search_console.position_8_15)}
• Zero-Click Pages: {len(search_console.zero_click_pages)}
"""

        an_section = ""
        if analytics and analytics.available:
            an_section = f"""
========================================================================
[12] GOOGLE ANALYTICS DATA
========================================================================
• Sessions: {analytics.sessions}
• Users: {analytics.users}
• Bounce Rate: {analytics.bounce_rate}%
• Avg Engagement: {analytics.avg_engagement_time}s
"""

        report = f"""========================================================================
  ENTERPRISE SEO ANALYSIS REPORT - SEAR
========================================================================
TARGET URL: {page.url}
OVERALL SEO SCORE: {page.overall_score}/100
EXTRACTED KEYWORDS: {keywords}

[SCORE BREAKDOWN]
{chr(10).join([f"• {k}: {v}/100" for k, v in page.scores.items()])}

========================================================================
[1] CRITICAL ISSUES (Fix Immediately)
========================================================================
""" + ("".join([f"🔴 [{i.category}] {i.problem}\n   ➤ Solution: {i.solution}\n   ➤ Impact: {i.impact} | Difficulty: {i.difficulty} | Time: {i.fix_time}\n\n" for i in critical_issues]) or "✅ No critical issues found.\n") + f"""
========================================================================
[2] WARNINGS & RECOMMENDATIONS
========================================================================
""" + ("".join([f"🟠 [{i.category}] {i.problem}\n   ➤ Solution: {i.solution}\n   ➤ Impact: {i.impact} | Difficulty: {i.difficulty} | Time: {i.fix_time}\n\n" for i in warnings[:10]]) or "✅ No major warnings.\n") + f"""
========================================================================
[3] QUICK WINS (High Impact, Low Effort)
========================================================================
""" + ("".join([f"🟢 {i.problem} ➤ {i.solution} ({i.fix_time})\n" for i in quick_wins[:5]]) or "Complete basic optimizations first.\n") + f"""
========================================================================
[4] TECHNICAL & METADATA DETAILS
========================================================================
• Title: {page.title or 'MISSING'} ({len(page.title)} chars)
• Meta Description: {page.meta_description or 'MISSING'} ({len(page.meta_description)} chars)
• Meta Robots: {page.meta_robots or 'index, follow'}
• Canonical: {page.canonical_url or 'MISSING'}
• Hreflang: {', '.join([f'{k}:{v}' for k,v in page.hreflang.items()]) or 'None'} (x-default: {page.x_default or 'None'})
• Language Attribute: {page.accessibility_lang or 'MISSING'}
• HTTP Version: {page.performance.http_version}
• Compression: {page.performance.compression or 'None'}
• Server: {page.performance.server or 'Unknown'}
• CDN: {page.performance.cdn_detected or 'Not detected'}
• TTFB: {page.performance.ttfb_ms}ms

========================================================================
[5] HEADING STRUCTURE
========================================================================
• H1 ({len(page.h1)}): {', '.join(page.h1) or 'MISSING'}
• H2 ({len(page.h2)}): {', '.join(page.h2[:5]) or 'None'}
• H3 ({len(page.h3)}): {', '.join(page.h3[:5]) or 'None'}

========================================================================
[6] CONTENT & LINKS STATISTICS
========================================================================
• Word Count: {page.word_count}
• Internal Links: {page.links.internal} | External: {page.links.external}
• Nofollow: {page.links.nofollow} | Sponsored: {page.links.sponsored} | UGC: {page.links.ugc}
• Empty/Orphan Links: {page.links.empty_orphan}

========================================================================
[7] IMAGE ANALYSIS
========================================================================
• Total Images: {page.images.total}
• Missing Alt: {page.images.missing_alt} | Empty Alt: {page.images.empty_alt}
• Duplicate Alt Texts: {len(page.images.duplicate_alt)}
• Missing Width/Height: {page.images.missing_dimensions}
• Modern Formats (WebP/AVIF/Picture): {page.images.modern_format}
• Lazy Loaded: {page.images.lazy_loaded}

========================================================================
[8] STRUCTURED DATA (JSON-LD)
========================================================================
• Detected: {'Yes' if page.structured_data.found else 'No'}
• Types Found: {', '.join(page.structured_data.types) or 'None'}
• Errors: {', '.join(page.structured_data.errors) or 'None'}

========================================================================
[9] SECURITY & PERFORMANCE
========================================================================
• HSTS: {'✓' if page.security_headers.hsts else '✗'}
• CSP: {'✓' if page.security_headers.csp else '✗'}
• X-Frame-Options: {page.security_headers.x_frame_options or '✗'}
• Referrer-Policy: {page.security_headers.referrer_policy or '✗'}
• JS Framework: {page.js_rendering.framework_detected or 'None'}
• Mobile Friendly: {'Yes' if page.mobile.is_mobile_friendly else 'No'}

========================================================================
[10] COMPETITOR ANALYSIS
========================================================================
{comp_str}

========================================================================
[10.5] ROBOTS.TXT SUMMARY
========================================================================
""" + (robots_txt[:1000].replace('\n', ' | ') + "..." if len(robots_txt) > 1000 else robots_txt or "Could not fetch robots.txt") + f"""
{sc_section}{an_section}
========================================================================
🤖 AI SEO MASTER PROMPT
========================================================================
{ai_prompt}
========================================================================
"""
        return report