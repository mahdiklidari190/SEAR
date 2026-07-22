"""Application settings with optional integration credentials."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class SearchConsoleConfig(BaseModel):
    """Optional Google Search Console credentials."""
    client_id: str = ""
    client_secret: str = ""
    refresh_token: str = ""
    property_url: str = ""

    @property
    def is_configured(self) -> bool:
        return all([self.client_id, self.client_secret, self.refresh_token, self.property_url])


class AnalyticsConfig(BaseModel):
    """Optional Google Analytics credentials."""
    client_id: str = ""
    client_secret: str = ""
    refresh_token: str = ""
    property_id: str = ""

    @property
    def is_configured(self) -> bool:
        return all([self.client_id, self.client_secret, self.refresh_token, self.property_id])


class BacklinkAPIConfig(BaseModel):
    """Optional backlink API keys."""
    ahrefs_key: str = ""
    semrush_key: str = ""
    moz_key: str = ""
    majestic_key: str = ""
    dataforseo_login: str = ""
    dataforseo_password: str = ""


class Settings(BaseModel):
    """Master application settings."""
    max_concurrent_requests: int = 5
    request_timeout: int = 30
    max_pages: int = 500
    reports_dir: Path = Field(default_factory=lambda: Path("seo_reports"))
    config_file: Path = Field(default_factory=lambda: Path("sear_config.json"))

    search_console: SearchConsoleConfig = Field(default_factory=SearchConsoleConfig)
    analytics: AnalyticsConfig = Field(default_factory=AnalyticsConfig)
    backlink_apis: BacklinkAPIConfig = Field(default_factory=BacklinkAPIConfig)

    @classmethod
    def load(cls) -> "Settings":
        """Load settings from config file if it exists."""
        config_path = Path("sear_config.json")
        if config_path.exists():
            try:
                data = json.loads(config_path.read_text(encoding="utf-8"))
                return cls(**data)
            except Exception:
                pass
        return cls()

    def save(self) -> None:
        """Persist settings to config file."""
        self.config_file.write_text(
            json.dumps(self.model_dump(mode="json"), indent=2, ensure_ascii=False),
            encoding="utf-8"
        )


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings.load()
    return _settings