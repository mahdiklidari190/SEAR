"""Text processing for keyword extraction - preserved from original."""
from __future__ import annotations

import re

from config.constants import STOPWORDS


class PersianTextProcessor:
    """Normalize and clean text for both Persian and English."""

    @staticmethod
    def normalize_and_clean(text: str) -> list[str]:
        if not text:
            return []
        text = text.replace("\u200c", " ").replace("ك", "ک").replace("ي", "ی")
        cleaned = re.sub(r"[^\w\s\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]", " ", text.lower())
        words = [w.strip() for w in cleaned.split() if w.strip() and len(w.strip()) > 1]
        return [w for w in words if w not in STOPWORDS]