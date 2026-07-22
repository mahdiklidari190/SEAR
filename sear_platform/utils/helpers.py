"""Utility helper functions."""
from __future__ import annotations

import re
from urllib.parse import urlparse, urljoin


def sanitize_filename(name: str) -> str:
    """Create a safe filename from a URL path."""
    return re.sub(r'[\\/*?:"<>|]', "", name.strip("/").replace("/", "_") or "home")


def normalize_url(url: str, base_url: str = "") -> str:
    """Normalize a URL relative to a base."""
    if not url:
        return ""
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("/"):
        parsed = urlparse(base_url)
        return f"{parsed.scheme}://{parsed.netloc}{url}"
    if not url.startswith("http"):
        return urljoin(base_url, url)
    return url


def get_domain(url: str) -> str:
    """Extract clean domain from URL."""
    parsed = urlparse(url)
    return parsed.netloc.lower().replace("www.", "")


def get_base_domain(url: str) -> str:
    """Get the registrable domain."""
    domain = get_domain(url)
    parts = domain.split(".")
    if len(parts) >= 2:
        return ".".join(parts[-2:])
    return domain


def url_depth(url: str, base_url: str) -> int:
    """Calculate the depth of a URL relative to the base."""
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        return 0
    return len(path.split("/"))


def model_to_dict(obj) -> dict:
    """Compatible with both Pydantic v1 and v2"""
    if hasattr(obj, 'model_dump'):
        return obj.model_dump(mode="json")
    elif hasattr(obj, 'dict'):
        return obj.dict()
    else:
        return {}