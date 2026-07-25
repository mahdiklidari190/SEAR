"""Tests for the new Weighted and Context-Aware SEOScorer."""
import pytest
from core.scorer import SEOScorer, ContextDetector
from models.page_data import PageData, CoreWebVitals, EstimatedCWVRisk

def test_context_detector_product():
    """Test if product pages are correctly identified."""
    page_type = ContextDetector.detect_page_type(
        url="https://site.com/shop/product/123", 
        title="Buy Running Shoes", 
        h1=["Best Running Shoes"]
    )
    assert page_type == "product"

def test_weighted_scoring_schema_penalty():
    """Test that missing schema on a product page penalizes correctly, not drastically."""
    page = PageData(
        url="https://site.com/product/123", 
        title="Test Product", 
        word_count=500,
        h1=["Test Product"],
        has_robots_txt=True,
        status_code=200
    )
    page.has_schema = False # Should incur a specific penalty
    
    scored_page = SEOScorer.calculate(page)
    
    # Product page missing schema should lose exactly 10 points from structured_data (100 - 10 = 90)
    assert scored_page.scores['structured_data'] == 90.0 
    # Overall score should remain healthy because other weights compensate
    assert scored_page.overall_score > 85.0 