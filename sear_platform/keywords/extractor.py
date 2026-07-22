"""Keyword Extractor - preserved from original."""
from __future__ import annotations

import re
from collections import Counter

from models.page_data import PageData
from .processor import PersianTextProcessor


class KeywordExtractor:
    """Extract keywords from page content using TF-based scoring."""

    @staticmethod
    def extract(page: PageData) -> str:
        scores: Counter = Counter()

        def get_ngrams(words: list[str], n: int) -> list[str]:
            return [" ".join(words[i:i + n]) for i in range(len(words) - n + 1) if len(words) >= n]

        for text, weight in [(page.title, 15), (page.og_title, 15), (page.meta_description, 5)]:
            words = PersianTextProcessor.normalize_and_clean(text)
            for w in words:
                scores[w] += weight
            for bg in get_ngrams(words, 2):
                scores[bg] += weight + 5

        for h_list, weight in [(page.h1, 12), (page.h2, 8), (page.h3, 5)]:
            for h in h_list:
                words = PersianTextProcessor.normalize_and_clean(h)
                for w in words:
                    scores[w] += weight
                for bg in get_ngrams(words, 2):
                    scores[bg] += weight + 3

        body_words = PersianTextProcessor.normalize_and_clean(page.text_sample)
        for w in body_words:
            scores[w] += 1
        for bg in get_ngrams(body_words, 2):
            scores[bg] += 1.5

        if page.meta_keywords:
            for kw in [k.strip().lower() for k in re.split(r"[,|،]", page.meta_keywords) if k.strip()]:
                scores[kw] += 30

        top_kws = [item[0] for item in scores.most_common(8)]
        return ", ".join(list(dict.fromkeys(top_kws)))