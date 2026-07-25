"""Mobile Friendly Analysis."""
from __future__ import annotations

# Import the core data model used to pass page-specific information to the analyzer.
from models.page_data import PageData


class MobileFriendlyAnalyzer:
    """Analyze mobile-friendliness."""

    @staticmethod
    def analyze(page: PageData) -> dict[str, any]:
        # Extract the mobile-specific attributes from the main page data object.
        mobile = page.mobile
        
        # Initialize the analysis report. 
        # We start with a perfect score of 100 and will deduct points based on detected mobile UX issues.
        report = {
            "has_viewport": mobile.has_viewport,
            "viewport_content": mobile.viewport_content,
            "is_mobile_friendly": mobile.is_mobile_friendly,
            "responsive_images": mobile.responsive_images,
            "font_issues": mobile.font_size_issues,
            "tap_target_issues": mobile.tap_target_issues,
            "score": 100,
            "recommendations": [],
        }

        # Check 1: The viewport meta tag is absolutely critical for proper mobile rendering.
        # Without it, mobile browsers will render the page at a desktop width and scale it down, ruining the UX.
        if not mobile.has_viewport:
            report["score"] -= 40
            report["recommendations"].append("Add <meta name='viewport' content='width=device-width, initial-scale=1'>")
            
        # Check 2: Responsive images ensure that mobile devices don't download unnecessarily large desktop-sized images.
        # This impacts both page load speed and mobile data usage.
        if not mobile.responsive_images:
            report["score"] -= 10
            report["recommendations"].append("Use srcset/picture elements for responsive images")
            
        # Check 3: Illegible text is a major friction point for mobile users.
        # If font sizes are too small, users are forced to pinch-and-zoom, which severely degrades the experience.
        if mobile.font_size_issues:
            report["score"] -= 15

        # Ensure the final score does not drop below zero, even if multiple severe issues are detected.
        report["score"] = max(0, report["score"])
        
        # Return the comprehensive mobile-friendliness report, including the final calculated score and actionable fixes.
        return report