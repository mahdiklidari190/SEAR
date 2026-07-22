"""Report and competitor models - preserved."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class CompetitorData(BaseModel):
    rank: int
    url: str
    title: str = ""
    meta_description: str = ""
    h1: list[str] = Field(default_factory=list)


class AnalysisReport(BaseModel):
    page_url: str
    ai_analysis: str
    status: str
    error_message: Optional[str] = None