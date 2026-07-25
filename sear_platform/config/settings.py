"""Application settings with optional integration credentials."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

# Import Pydantic components for robust data validation and settings management.
from pydantic import BaseModel, Field


class SearchConsoleConfig(BaseModel):
    """Optional Google Search Console credentials."""
    client_id: str = ""
    client_secret: str = ""
    refresh_token: str = ""
    property_url: str = ""

    @property
    def is_configured(self) -> bool:
        # Check if all required credential fields are populated to determine if the integration is ready to use.
        return all([self.client_id, self.client_secret, self.refresh_token, self.property_url])


class AnalyticsConfig(BaseModel):
    """Optional Google Analytics credentials."""
    client_id: str = ""
    client_secret: str = ""
    refresh_token: str = ""
    property_id: str = ""

    @property
    def is_configured(self) -> bool:
        # Check if all required credential fields are populated to determine if the integration is ready to use.
        return all([self.client_id, self.client_secret, self.refresh_token, self.property_id])


class BacklinkAPIConfig(BaseModel):
    """Optional backlink API keys."""
    # Store API credentials for various third-party SEO and backlink data providers.
    # Empty strings indicate that the specific provider is not configured.
    ahrefs_key: str = ""
    semrush_key: str = ""
    moz_key: str = ""
    majestic_key: str = ""
    dataforseo_login: str = ""
    dataforseo_password: str = ""


class Settings(BaseModel):
    """Master application settings."""
    # Core operational limits for the crawling and analysis engine.
    max_concurrent_requests: int = 5
    request_timeout: int = 30
    max_pages: int = 500
    
    # Define default directories and configuration file paths using factories to ensure proper instantiation.
    reports_dir: Path = Field(default_factory=lambda: Path("seo_reports"))
    config_file: Path = Field(default_factory=lambda: Path("sear_config.json"))

    # Nested configuration models for optional third-party integrations.
    search_console: SearchConsoleConfig = Field(default_factory=SearchConsoleConfig)
    analytics: AnalyticsConfig = Field(default_factory=AnalyticsConfig)
    backlink_apis: BacklinkAPIConfig = Field(default_factory=BacklinkAPIConfig)

    @classmethod
    def load(cls) -> "Settings":
        """Load settings from config file if it exists."""
        config_path = Path("sear_config.json")
        if config_path.exists():
            try:
                # Read the JSON file and parse its contents into the Settings model.
                data = json.loads(config_path.read_text(encoding="utf-8"))
                return cls(**data)
            except Exception:
                # If the file is corrupted or unreadable, silently fail and fall back to default settings.
                pass
        # Return a new instance with default values if the config file does not exist or failed to load.
        return cls()

    def save(self) -> None:
        """Persist settings to config file."""
        # Serialize the current settings instance to a formatted JSON string and write it to the config file.
        # ensure_ascii=False preserves non-ASCII characters (like Persian text) in the output file.
        self.config_file.write_text(
            json.dumps(self.model_dump(mode="json"), indent=2, ensure_ascii=False),
            encoding="utf-8"
        )


# Global variable to cache the settings instance, implementing a simple Singleton pattern.
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Retrieve the global application settings instance.
    If the instance has not been initialized yet, it loads it from the configuration file.
    This ensures the config file is only read once per application lifecycle, improving performance.
    """
    global _settings
    if _settings is None:
        _settings = Settings.load()
    return _settings