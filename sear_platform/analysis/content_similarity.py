"""Content Similarity Detection using SimHash, MinHash, and Shingling."""
from __future__ import annotations

import hashlib
import re
from typing import Optional

try:
    from datasketch import MinHash, MinHashLSH
    HAS_DATASKETCH = True
except ImportError:
    HAS_DATASKETCH = False


class ContentSimilarityAnalyzer:
    """Detect near-duplicate content across pages."""

    def __init__(self, num_perm: int = 128, threshold: float = 0.8):
        self.num_perm = num_perm
        self.threshold = threshold
        self.pages: dict[str, str] = {}  # url -> text
        self.minhashes: dict[str, any] = {}
        if HAS_DATASKETCH:
            self.lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)
        else:
            self.lsh = None

    def add_page(self, url: str, text: str) -> None:
        """Add page content for comparison."""
        self.pages[url] = text[:5000]  # Limit text size

        if HAS_DATASKETCH:
            mh = MinHash(num_perm=self.num_perm)
            shingles = self._get_shingles(text)
            for s in shingles:
                mh.update(s.encode("utf-8"))
            self.minhashes[url] = mh
            try:
                self.lsh.insert(url, mh)
            except ValueError:
                pass  # Duplicate key

    def find_near_duplicates(self) -> list[dict[str, any]]:
        """Find near-duplicate page pairs."""
        duplicates = []

        if not HAS_DATASKETCH:
            # Fallback: simple SimHash comparison
            return self._simhash_fallback()

        checked = set()
        for url, mh in self.minhashes.items():
            results = self.lsh.query(mh)
            for other_url in results:
                pair = tuple(sorted([url, other_url]))
                if pair not in checked and url != other_url:
                    checked.add(pair)
                    similarity = mh.jaccard(self.minhashes[other_url])
                    if similarity >= self.threshold:
                        duplicates.append({
                            "url_1": url,
                            "url_2": other_url,
                            "similarity": round(similarity * 100, 1),
                            "type": "near_duplicate",
                        })

        return duplicates

    def find_duplicate_paragraphs(self) -> list[dict[str, any]]:
        """Find paragraphs duplicated across pages."""
        para_map: dict[str, list[str]] = {}

        for url, text in self.pages.items():
            paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 100]
            for para in paragraphs:
                key = hashlib.md5(para.encode()).hexdigest()
                para_map.setdefault(key, []).append(url)

        duplicates = []
        for key, urls in para_map.items():
            if len(urls) > 1:
                duplicates.append({
                    "paragraph_hash": key,
                    "found_on": urls,
                    "count": len(urls),
                })

        return duplicates[:20]

    def _get_shingles(self, text: str, k: int = 5) -> set[str]:
        """Generate k-word shingles from text."""
        words = re.sub(r"[^\w\s]", "", text.lower()).split()
        if len(words) < k:
            return {" ".join(words)}
        return {" ".join(words[i:i + k]) for i in range(len(words) - k + 1)}

    def _simhash_fallback(self) -> list[dict[str, any]]:
        """Simple hash-based duplicate detection fallback."""
        duplicates = []
        hashes: dict[str, str] = {}

        for url, text in self.pages.items():
            h = hashlib.md5(text[:1000].encode()).hexdigest()
            if h in hashes:
                duplicates.append({
                    "url_1": hashes[h],
                    "url_2": url,
                    "similarity": 100.0,
                    "type": "exact_duplicate",
                })
            else:
                hashes[h] = url

        return duplicates