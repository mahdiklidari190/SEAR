"""Redirect Analysis."""
from __future__ import annotations

from models.integrations import RedirectInfo


class RedirectAnalyzer:
    """Analyze redirect chains, loops, and types."""

    def __init__(self):
        self.redirects: list[RedirectInfo] = []

    def add_redirect(self, source: str, target: str, status_code: int, chain: list[str] = None) -> None:
        chain = chain or []
        is_loop = target in chain or target == source
        self.redirects.append(RedirectInfo(
            source_url=source,
            target_url=target,
            status_code=status_code,
            chain_length=len(chain) + 1,
            is_loop=is_loop,
        ))

    def analyze(self) -> dict[str, any]:
        """Produce redirect analysis summary."""
        summary = {
            "total_redirects": len(self.redirects),
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

        for r in self.redirects:
            if r.is_loop:
                summary["loops"].append({"source": r.source_url, "target": r.target_url})
            if r.chain_length > 2:
                summary["long_chains"].append({
                    "source": r.source_url, "target": r.target_url, "length": r.chain_length
                })

        # Detect mixed redirect types (301 -> 302 in chain)
        # This would require chain tracking; simplified here
        if summary["loops"]:
            summary["issues"].append(f"{len(summary['loops'])} redirect loop(s) detected")
        if summary["long_chains"]:
            summary["issues"].append(f"{len(summary['long_chains'])} long redirect chain(s) (>2 hops)")
        if summary["redirect_302"] > 0:
            summary["issues"].append(
                f"{summary['redirect_302']} temporary (302) redirects found - consider converting to 301"
            )

        return summary