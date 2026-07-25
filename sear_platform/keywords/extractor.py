"""Keyword Extractor - preserved from original."""
from __future__ import annotations

import re
from collections import Counter

# Import the core data model containing the extracted page attributes.
from models.page_data import PageData
# Import the language-specific text processing utility for accurate Persian NLP and normalization.
from .processor import PersianTextProcessor


class KeywordExtractor:
    """Extract keywords from page content using Term Frequency (TF)-based scoring."""

    @staticmethod
    def extract(page: PageData) -> str:
        # Initialize a Counter to accumulate weighted scores for each extracted keyword or phrase.
        scores: Counter = Counter()

        def get_ngrams(words: list[str], n: int) -> list[str]:
            """
            Generate n-grams (contiguous sequences of n words) from a list of words.
            This helps capture meaningful multi-word phrases (e.g., bigrams) that carry 
            more semantic weight and specificity than single isolated words.
            """
            return [" ".join(words[i:i + n]) for i in range(len(words) - n + 1) if len(words) >= n]

        # =========================================================================
        # 1. METADATA WEIGHTING
        # Assign high importance to keywords found in critical metadata fields.
        # =========================================================================
        for text, weight in [(page.title, 15), (page.og_title, 15), (page.meta_description, 5)]:
            # Normalize and clean the text (e.g., remove stopwords, standardize Persian characters).
            words = PersianTextProcessor.normalize_and_clean(text)
            for w in words:
                scores[w] += weight
            # Boost the score for 2-word phrases (bigrams) found in metadata, as they often represent core topics.
            for bg in get_ngrams(words, 2):
                scores[bg] += weight + 5

        # =========================================================================
        # 2. HEADING WEIGHTING
        # Assign descending importance to keywords found in heading tags (H1 > H2 > H3).
        # =========================================================================
        for h_list, weight in [(page.h1, 12), (page.h2, 8), (page.h3, 5)]:
            for h in h_list:
                words = PersianTextProcessor.normalize_and_clean(h)
                for w in words:
                    scores[w] += weight
                # Apply a slight bonus for bigrams within headings to capture structured topic clusters.
                for bg in get_ngrams(words, 2):
                    scores[bg] += weight + 3

        # =========================================================================
        # 3. BODY CONTENT WEIGHTING
        # Analyze the main text sample with a baseline weight, reflecting natural keyword density.
        # =========================================================================
        body_words = PersianTextProcessor.normalize_and_clean(page.text_sample)
        for w in body_words:
            scores[w] += 1
        for bg in get_ngrams(body_words, 2):
            scores[bg] += 1.5

        # =========================================================================
        # 4. EXPLICIT KEYWORD WEIGHTING
        # If the legacy meta keywords tag is present, give its contents a massive boost.
        # Even though deprecated by modern search engines, it represents the author's explicit intent.
        # =========================================================================
        if page.meta_keywords:
            # Split by English comma or Persian comma (،), clean whitespace, and convert to lowercase.
            for kw in [k.strip().lower() for k in re.split(r"[,|،]", page.meta_keywords) if k.strip()]:
                scores[kw] += 30

        # =========================================================================
        # FINAL EXTRACTION
        # Retrieve the top 8 highest-scoring keywords/phrases.
        # Use dict.fromkeys() to remove any accidental duplicates while preserving the original ranking order,
        # then join them into a single, comma-separated string for downstream use.
        # =========================================================================
        top_kws = [item[0] for item in scores.most_common(8)]
        return ", ".join(list(dict.fromkeys(top_kws)))