"""Redirect Analysis."""
# This module is responsible for analyzing HTTP redirects across the website.
# It identifies problematic redirect patterns such as infinite loops, long chains,
# and improper use of temporary redirects, which can negatively impact SEO and user experience.
from __future__ import annotations

# Import the data model used to structure individual redirect records.
from models.integrations import RedirectInfo


class RedirectAnalyzer:
    """Analyze redirect chains, loops, and types."""

    def __init__(self):
        # Initialize an empty list to store all discovered redirect events during the crawl.
        self.redirects: list[RedirectInfo] = []

    def add_redirect(self, source: str, target: str, status_code: int, chain: list[str] = None) -> None:
        # Ensure the chain parameter is an empty list if None is passed, preventing type errors during length calculation.
        chain = chain or []
        
        # Determine if this redirect creates an infinite loop.
        # A loop occurs if the target URL is already present in the redirect chain, or if it points back to itself.
        is_loop = target in chain or target == source
        
        # Create and store a structured RedirectInfo object for this specific redirect event.
        self.redirects.append(RedirectInfo(
            source_url=source,
            target_url=target,
            status_code=status_code,
            # The total chain length includes the current hop plus the length of the preceding chain.
            chain_length=len(chain) + 1,
            is_loop=is_loop,
        ))

    def analyze(self) -> dict[str, any]:
        """Produce redirect analysis summary."""
        # Initialize the summary report structure with default counters and empty lists for tracking issues.
        summary = {
            "total_redirects": len(self.redirects),
            # Count the occurrences of each specific HTTP redirect status code to understand the redirect strategy.
            "redirect_301": len([r for r in self.redirects if r.status_code == 301]),
            "redirect_302": len([r for r in self.redirects if r.status_code == 302]),
            "redirect_307": len([r for r in self.redirects if r.status_code == 307]),
            "redirect_308": len([r for r in self.redirects if r.status_code == 308]),
            "chains": [],
            "loops": [],
            "mixed_chains": [],
            "long_chains": [],
            "issues": [],
        }

        # Iterate through all recorded redirects to identify structural problems.
        for r in self.redirects:
            # Flag any redirects that result in an infinite loop, which will cause crawlers to drop the page.
            if r.is_loop:
                summary["loops"].append({"source": r.source_url, "target": r.target_url})
                
            # Flag redirect chains that are excessively long (more than 2 hops).
            # Long chains waste crawl budget, increase page load time, and dilute link equity.
            if r.chain_length > 2:
                summary["long_chains"].append({
                    "source": r.source_url,
                    "target": r.target_url,
                    "length": r.chain_length
                })

        # Note: Detecting mixed redirect types (e.g., 301 followed by 302 in the same chain) 
        # would require deeper chain tracking logic, which is simplified in this current implementation.
        
        # Generate actionable SEO recommendations based on the detected issues.
        if summary["loops"]:
            summary["issues"].append(f"{len(summary['loops'])} redirect loop(s) detected")
            
        if summary["long_chains"]:
            summary["issues"].append(f"{len(summary['long_chains'])} long redirect chain(s) (>2 hops)")
            
        # Temporary redirects (302) do not pass full link equity to the target page. 
        # If the move is permanent, they should be updated to 301s to preserve SEO value.
        if summary["redirect_302"] > 0:
            summary["issues"].append(
                f"{summary['redirect_302']} temporary (302) redirects found - consider converting to 301"
            )

        # Return the fully populated redirect analysis summary to the caller.
        return summary