"""JavaScript Rendering Analysis."""
from __future__ import annotations

# Import the data models required to access page-specific JavaScript rendering metrics.
from models.page_data import PageData, JSRenderingData


class JSRenderingAnalyzer:
    """Analyze JavaScript rendering characteristics to identify potential SEO bottlenecks."""

    @staticmethod
    def analyze(page: PageData) -> dict[str, any]:
        """
        Produce a comprehensive JavaScript rendering analysis report.
        
        Args:
            page: The PageData object containing the JavaScript rendering metrics.
            
        Returns:
            A dictionary containing the rendering profile and actionable SEO recommendations.
        """
        # Extract the specific JavaScript rendering data object from the main page data model.
        js = page.js_rendering
        
        # Initialize the report structure with the current state of the page's JavaScript implementation.
        report = {
            "framework": js.framework_detected or "None detected",
            "is_spa": js.is_spa,
            # Determine the rendering strategy based on the detected flags.
            "rendering_type": "Client-Side" if js.client_rendered else "Server-Side" if js.server_rendered else "Hybrid/Unknown",
            "render_blocking_scripts": len(js.render_blocking_scripts),
            "hydration_issues": js.hydration_issues,
            "recommendations": [],
        }

        # Evaluate the rendering setup against SEO best practices and generate targeted recommendations.
        
        # Check 1: Single Page Applications (SPAs) are notoriously difficult for crawlers to index without pre-rendering.
        if js.is_spa:
            report["recommendations"].append(
                "SPA detected: Ensure server-side rendering (SSR) or pre-rendering for SEO"
            )
            
        # Check 2: Render-blocking scripts delay the initial paint and content visibility for both users and crawlers.
        if js.render_blocking_scripts:
            report["recommendations"].append(
                f"Add defer/async to {len(js.render_blocking_scripts)} render-blocking scripts"
            )
            
        # Check 3: Major modern frameworks require SSR to ensure content is immediately available in the initial HTML response.
        if js.framework_detected in ("React", "Vue", "Angular") and not js.server_rendered:
            report["recommendations"].append(
                f"{js.framework_detected} app without SSR: Consider Next.js/Nuxt for better SEO"
            )

        # Return the fully populated JavaScript rendering analysis report.
        return report