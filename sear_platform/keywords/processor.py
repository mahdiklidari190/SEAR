"""Text processing for keyword extraction - preserved from original."""
from __future__ import annotations

# Import the regular expression module for advanced text pattern matching and cleaning.
import re

# Import the predefined set of common stopwords (in both English and Persian) 
# to filter out non-semantic words during the keyword extraction process.
from config.constants import STOPWORDS


class PersianTextProcessor:
    """
    Normalize and clean text for both Persian and English.
    This class handles language-specific preprocessing, ensuring that variations 
    in character encoding, typography, and punctuation do not skew keyword analysis.
    """

    @staticmethod
    def normalize_and_clean(text: str) -> list[str]:
        """
        Process raw text into a clean list of meaningful words.
        This involves standardizing Persian characters, removing punctuation, 
        and filtering out short tokens and stopwords.
        """
        # Guard clause: return an empty list immediately if the input text is empty or falsy.
        if not text:
            return []
            
        # Standardize Persian typography and encoding:
        # 1. Replace the Zero-Width Non-Joiner (ZWNJ) with a standard space to ensure words are separated correctly.
        # 2. Replace the Arabic 'Kaf' (ك) with the standard Persian 'Kaf' (ک).
        # 3. Replace the Arabic 'Yeh' (ي) with the standard Persian 'Yeh' (ی).
        text = text.replace("\u200c", " ").replace("ك", "ک").replace("ي", "ی")
        
        # Clean the text using a regular expression:
        # - Convert to lowercase for case-insensitive matching.
        # - Replace any character that is NOT a standard word character, whitespace, 
        #   or within the specific Persian/Arabic Unicode ranges with a space.
        # This effectively strips out punctuation, emojis, and special symbols while preserving the native script.
        cleaned = re.sub(r"[^\w\s\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]", " ", text.lower())
        
        # Tokenize the cleaned string into individual words.
        # Strip leading/trailing whitespace from each token and filter out single-character words, 
        # as they are typically noise and do not contribute to meaningful keyword analysis.
        words = [w.strip() for w in cleaned.split() if w.strip() and len(w.strip()) > 1]
        
        # Final filtering step: remove any words that exist in the predefined STOPWORDS set.
        # This ensures that only semantically significant terms are returned for downstream scoring.
        return [w for w in words if w not in STOPWORDS]