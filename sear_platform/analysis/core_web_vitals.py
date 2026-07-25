"""Core Web Vitals estimation from HTML analysis."""
from __future__ import annotations

# Import the data models required for structuring the Core Web Vitals report and accessing page data.
from models.integrations import CoreWebVitals
from models.page_data import PageData


class CoreWebVitalsAnalyzer:
    """Estimate Core Web Vitals from page structure and performance metrics."""

    @staticmethod
    def analyze(page: PageData) -> CoreWebVitals:
        # Initialize a new Core Web Vitals report object to be populated with estimated metrics.
        cwv = CoreWebVitals()

        # Extract Time to First Byte (TTFB) directly from the page's existing performance data.
        cwv.ttfb_ms = page.performance.ttfb_ms

        # Estimate Largest Contentful Paint (LCP) by checking if the page relies on large images or text blocks.
        if page.images.total > 0:
            cwv.lcp_estimate = "Image-based LCP likely"
            # Capture the top 5 oversized images as they are the most probable LCP candidates.
            cwv.largest_images = page.images.oversized_images[:5]
        else:
            cwv.lcp_estimate = "Text-based LCP likely"

        # Calculate a risk score for Cumulative Layout Shift (CLS) based on common triggering factors.
        cls_factors = 0
        if page.images.missing_dimensions > 0:
            # Each image missing explicit width/height attributes contributes to layout shift risk.
            cls_factors += page.images.missing_dimensions
        if not page.mobile.has_viewport:
            # A missing viewport meta tag is a severe layout stability issue on mobile devices.
            cls_factors += 3
            
        # Assign a qualitative risk level based on the accumulated factor count.
        cwv.cls_estimate = f"Risk: {'High' if cls_factors > 5 else 'Medium' if cls_factors > 2 else 'Low'} ({cls_factors} factors)"

        # Capture the top 10 render-blocking resources (scripts) that may delay initial page rendering.
        cwv.render_blocking_resources = page.js_rendering.render_blocking_scripts[:10]

        # Flag potential font loading delays if server-side compression is disabled.
        if not page.performance.compression:
            cwv.font_issues.append("No compression - fonts may load slowly")

        # Generate specific, actionable performance recommendations based on the detected thresholds and issues.
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

        # Return the fully populated Core Web Vitals analysis report.
        return cwv