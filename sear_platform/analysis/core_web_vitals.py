"""Core Web Vitals estimation from HTML analysis."""
from __future__ import annotations

from models.integrations import CoreWebVitals
from models.page_data import PageData


class CoreWebVitalsAnalyzer:
    """Estimate Core Web Vitals from page structure."""

    @staticmethod
    def analyze(page: PageData) -> CoreWebVitals:
        cwv = CoreWebVitals()

        # TTFB from performance data
        cwv.ttfb_ms = page.performance.ttfb_ms

        # Estimate LCP based on largest image or text block
        if page.images.total > 0:
            cwv.lcp_estimate = "Image-based LCP likely"
            cwv.largest_images = page.images.oversized_images[:5]
        else:
            cwv.lcp_estimate = "Text-based LCP likely"

        # CLS estimation
        cls_factors = 0
        if page.images.missing_dimensions > 0:
            cls_factors += page.images.missing_dimensions
        if not page.mobile.has_viewport:
            cls_factors += 3
        cwv.cls_estimate = f"Risk: {'High' if cls_factors > 5 else 'Medium' if cls_factors > 2 else 'Low'} ({cls_factors} factors)"

        # Render blocking resources
        cwv.render_blocking_resources = page.js_rendering.render_blocking_scripts[:10]

        # Font issues
        if not page.performance.compression:
            cwv.font_issues.append("No compression - fonts may load slowly")

        # Recommendations
        if cwv.ttfb_ms > 600:
            cwv.recommendations.append("Reduce TTFB: Enable server-side caching, use CDN")
        if page.images.missing_dimensions > 0:
            cwv.recommendations.append(f"Add width/height to {page.images.missing_dimensions} images to prevent CLS")
        if page.js_rendering.render_blocking_scripts:
            cwv.recommendations.append(f"Add async/defer to {len(page.js_rendering.render_blocking_scripts)} render-blocking scripts")
        if page.images.lazy_loaded == 0 and page.images.total > 3:
            cwv.recommendations.append("Implement lazy loading for below-fold images")
        if not page.performance.compression:
            cwv.recommendations.append("Enable Brotli/Gzip compression on server")

        return cwv