"""Issue model - preserved from original with extensions."""
# This module defines the standardized data structure for logging and reporting 
# SEO issues, ensuring consistency and clarity across all analysis modules.
from __future__ import annotations

# Import Pydantic's BaseModel to enforce type validation and enable easy serialization (e.g., to JSON for reports).
from pydantic import BaseModel


class Issue(BaseModel):
    """
    Represents a single, actionable SEO issue detected during the page analysis.
    Using a strict schema ensures that all generated reports provide uniform, 
    easy-to-understand problem statements and clear remediation steps.
    """
    
    # The broad category of the issue (e.g., "Metadata", "Performance", "Security", "Content").
    category: str
    
    # The priority level of the issue, dictating how urgently it should be addressed by the user.
    severity: str  # Expected values: "Critical", "High", "Medium", "Low"
    
    # A concise, clear description of what is currently wrong or missing on the page.
    problem: str
    
    # A specific, step-by-step recommendation or instruction on how to resolve the issue.
    solution: str
    
    # An explanation of why this issue matters (e.g., how it negatively affects rankings, UX, or crawlability).
    impact: str
    
    # An estimate of the technical effort or skill level required to implement the fix.
    difficulty: str  # Expected values: "Easy", "Medium", "Hard"
    
    # A rough time estimate for a developer, designer, or content creator to apply the fix.
    fix_time: str