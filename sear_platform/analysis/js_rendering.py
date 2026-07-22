"""JavaScript Rendering Analysis."""
from __future__ import annotations

from models.page_data import PageData, JSRenderingData


class JSRenderingAnalyzer:
    """Analyze JavaScript rendering characteristics."""

    @staticmethod
    def analyze(page: PageData) -> dict[str, any]:
        """Produce JS rendering analysis report."""
        js = page.js_rendering
        report = {
            "framework": js.framework_detected or "None detected",
            "is_spa": js.is_spa,
            "rendering_type": "Client-Side" if js.client_rendered else "Server-Side" if js.server_rendered else "Hybrid/Unknown",
            "render_blocking_scripts": len(js.render_blocking_scripts),
            "hydration_issues": js.hydration_issues,
            "recommendations": [],
        }

        if js.is_spa:
            report["recommendations"].append(
                "SPA detected: Ensure server-side rendering (SSR) or pre-rendering for SEO"
            )
        if js.render_blocking_scripts:
            report["recommendations"].append(
                f"Add defer/async to {len(js.render_blocking_scripts)} render-blocking scripts"
            )
        if js.framework_detected in ("React", "Vue", "Angular") and not js.server_rendered:
            report["recommendations"].append(
                f"{js.framework_detected} app without SSR: Consider Next.js/Nuxt for better SEO"
            )

        return report