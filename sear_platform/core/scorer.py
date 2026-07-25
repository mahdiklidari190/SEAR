"""SEO Scoring Engine - preserved and extended."""
from __future__ import annotations

# Import the core data model that holds all extracted page metrics and the scores to be calculated.
from models.page_data import PageData


class SEOScorer:
    """
    Calculate SEO scores across multiple dimensions.
    This engine evaluates a page's health by starting with perfect scores 
    and applying targeted deductions based on detected issues and missing best practices.
    """

    @staticmethod
    def calculate(page: PageData) -> PageData:
        # Initialize all scoring categories with a perfect baseline of 100.
        scores = {
            "Technical": 100,
            "Metadata": 100,
            "Content": 100,
            "Accessibility": 100,
            "Images": 100,
            "Links": 100,
            "Structured Data": 100,
            "Security": 100,
            "Performance": 100,
            "Mobile": 100,
        }

        # =========================================================================
        # ISSUE-BASED DEDUCTIONS
        # Iterate through all flagged SEO issues and apply severity-based penalties 
        # to the corresponding scoring category.
        # =========================================================================
        for issue in page.issues:
            # Map issue severity to a specific point deduction.
            deduction = {"Critical": 15, "High": 8, "Medium": 4, "Low": 1}.get(issue.severity, 0)
            category = issue.category
            
            # Route the deduction to the most relevant scoring category based on the issue's classification.
            if "Metadata" in category:
                scores["Metadata"] -= deduction
            elif "Heading" in category or "Content" in category or "Duplicate" in category:
                scores["Content"] -= deduction
            elif "Canonical" in category or "Hreflang" in category:
                scores["Technical"] -= deduction
            elif "Accessibility" in category:
                scores["Accessibility"] -= deduction
            elif "Image" in category:
                scores["Images"] -= deduction
            elif "Link" in category:
                scores["Links"] -= deduction
            elif "Structured" in category:
                scores["Structured Data"] -= deduction
            else:
                # Default fallback for uncategorized technical issues.
                scores["Technical"] -= deduction

        # =========================================================================
        # IMAGE DEDUCTIONS
        # Apply specific penalties for missing accessibility (alt text) and 
        # performance (dimensions) attributes on images.
        # =========================================================================
        if page.images.total > 0:
            if page.images.missing_alt > 0:
                # Cap the penalty at 20 points to prevent a single issue from destroying the entire score.
                scores["Images"] -= min(20, page.images.missing_alt * 2)
            if page.images.missing_dimensions > 0:
                scores["Technical"] -= 5

        # =========================================================================
        # ACCESSIBILITY DEDUCTIONS
        # Penalize missing core accessibility features like language declaration.
        # =========================================================================
        if not page.accessibility_lang:
            scores["Accessibility"] -= 10
        if page.accessibility_issues:
            scores["Accessibility"] -= 10

        # =========================================================================
        # STRUCTURED DATA DEDUCTIONS
        # Evaluate the presence and validity of JSON-LD schema markup.
        # =========================================================================
        if not page.structured_data.found:
            # Apply a baseline penalty if no structured data is detected at all.
            scores["Structured Data"] = 50
        if page.structured_data.errors:
            # Apply an additional penalty if the existing structured data contains syntax errors.
            scores["Structured Data"] -= 20

        # =========================================================================
        # SECURITY SCORING
        # Deduct points for missing HTTP security headers, with extra emphasis on HSTS.
        # =========================================================================
        sec_issues = len(page.security_headers.issues)
        scores["Security"] -= sec_issues * 8
        if not page.security_headers.hsts:
            scores["Security"] -= 10

        # =========================================================================
        # PERFORMANCE SCORING
        # Evaluate server response times, compression, and render-blocking resources.
        # =========================================================================
        if page.performance.ttfb_ms > 800:
            scores["Performance"] -= 20
        elif page.performance.ttfb_ms > 400:
            scores["Performance"] -= 10
            
        if not page.performance.compression:
            scores["Performance"] -= 10
            
        if page.js_rendering.render_blocking_scripts:
            # Scale the penalty based on the number of blocking scripts, capped at 15 points.
            scores["Performance"] -= min(15, len(page.js_rendering.render_blocking_scripts) * 3)

        # =========================================================================
        # MOBILE SCORING
        # Assess core mobile usability signals, heavily penalizing missing viewport configuration.
        # =========================================================================
        if not page.mobile.has_viewport:
            scores["Mobile"] -= 30
        if not page.mobile.is_mobile_friendly:
            scores["Mobile"] -= 20
        if not page.mobile.responsive_images:
            scores["Mobile"] -= 5

        # =========================================================================
        # FINAL CALCULATION & CLAMPING
        # Ensure no category score falls below 0 or exceeds 100, then calculate the overall average.
        # =========================================================================
        for k in scores:
            # Clamp the score to the valid 0-100 range.
            scores[k] = max(0, min(100, scores[k]))

        # Assign the categorized scores back to the page object.
        page.scores = scores
        
        # Calculate the overall SEO health score as the integer average of all category scores.
        page.overall_score = int(sum(scores.values()) / len(scores))
        
        return page