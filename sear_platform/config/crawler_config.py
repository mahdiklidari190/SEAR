"""Crawler Configuration - Centralized settings for the SEAR crawling engine."""
# Import Pydantic's BaseModel and Field to define a robust, type-safe, and validated configuration schema.
from pydantic import BaseModel, Field

class CrawlerConfig(BaseModel):
    """
    Configuration model for the SEAR Crawler.
    This class defines and validates all operational parameters for the web crawler,
    ensuring safe, compliant, and efficient crawling behavior across different target domains.
    """
    
    # =========================================================================
    # IDENTITY
    # Defines how the crawler presents itself to web servers. 
    # Using a transparent, descriptive User-Agent helps prevent unnecessary blocking 
    # and allows webmasters to contact the operator if needed.
    # =========================================================================
    user_agent: str = Field(
        default="SEARBot/1.0 (+https://klidari.ir/searbot)",
        description="Fixed User-Agent for professional identification"
    )
    
    # =========================================================================
    # COMPLIANCE & BEHAVIOR
    # Controls how the crawler interacts with target servers to ensure 
    # ethical scraping practices and prevent overloading the target infrastructure.
    # =========================================================================
    respect_robots: bool = Field(
        default=True,
        description="Whether to respect robots.txt rules"
    )
    crawl_delay: float = Field(
        default=1.0,
        ge=0.0, # Greater than or equal to 0.0
        description="Delay in seconds between requests to the same domain"
    )
    
    # =========================================================================
    # LIMITS
    # Defines the operational boundaries and safety nets for the crawling session.
    # These constraints prevent infinite loops, resource exhaustion, or excessive execution time.
    # =========================================================================
    max_pages: int = Field(
        default=500,
        ge=1,   # Greater than or equal to 1
        le=10000, # Less than or equal to 10000
        description="Maximum number of pages to crawl per session"
    )
    timeout: float = Field(
        default=15.0,
        ge=5.0, # Greater than or equal to 5.0 seconds to allow for slow server responses
        description="HTTP request timeout in seconds"
    )
    max_retries: int = Field(
        default=3,
        ge=1,   # Greater than or equal to 1
        description="Maximum number of retry attempts for failed or transient network requests"
    )