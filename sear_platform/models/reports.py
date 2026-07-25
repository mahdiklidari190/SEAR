"""Report and competitor models - preserved."""
# This module defines the core data structures used for the final output reports 
# and for storing benchmarking data of competitor webpages.
from __future__ import annotations

from typing import Optional

# Import Pydantic components to ensure strict data validation and easy serialization 
# of the report payloads, which are often sent to frontends or saved as JSON.
from pydantic import BaseModel, Field


class CompetitorData(BaseModel):
    """
    Represents the essential SEO metrics of a single competitor's webpage.
    This data is used for comparative gap analysis, allowing the system to 
    benchmark the target page against top-ranking rivals in the search results.
    """
    # The ranking position of the competitor in the search engine results page (SERP).
    rank: int
    # The full URL of the competitor's page.
    url: str
    # The extracted <title> tag content of the competitor's page.
    title: str = ""
    # The extracted meta description of the competitor's page.
    meta_description: str = ""
    # A list of all <h1> heading tags found on the competitor's page.
    h1: list[str] = Field(default_factory=list)


class AnalysisReport(BaseModel):
    """
    The final output payload generated after a complete SEO analysis.
    This model encapsulates the AI's strategic recommendations, the execution status 
    of the analysis task, and any error details if the process failed.
    """
    # The target URL that was analyzed.
    page_url: str
    # The comprehensive, implementation-ready AI analysis and action plan.
    ai_analysis: str
    # The current status of the report generation (e.g., 'completed', 'failed', 'pending').
    status: str
    # An optional field to store detailed error messages or stack traces if the analysis encounters an issue.
    error_message: Optional[str] = None