"""Issue model - preserved from original with extensions."""
from __future__ import annotations

from pydantic import BaseModel


class Issue(BaseModel):
    """A single SEO issue detected during analysis."""
    category: str
    severity: str  # Critical, High, Medium, Low
    problem: str
    solution: str
    impact: str
    difficulty: str  # Easy, Medium, Hard
    fix_time: str