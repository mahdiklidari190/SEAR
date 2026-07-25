"""Content Similarity Detection using SimHash, MinHash, and Shingling."""
from __future__ import annotations

import hashlib
import re
from typing import Optional

# Attempt to import advanced similarity libraries. 
# If unavailable, the class will gracefully fall back to simpler hash-based methods.
try:
    from datasketch import MinHash, MinHashLSH
    HAS_DATASKETCH = True
except ImportError:
    HAS_DATASKETCH = False


class ContentSimilarityAnalyzer:
    """Detect near-duplicate content across pages."""

    def __init__(self, num_perm: int = 128, threshold: float = 0.8):
        # Initialize the number of permutations for MinHash and the similarity threshold.
        self.num_perm = num_perm
        self.threshold = threshold
        
        # Dictionary to store a truncated version of the page text for each URL.
        self.pages: dict[str, str] = {}  # url -> text
        
        # Dictionary to store the MinHash objects for each URL.
        self.minhashes: dict[str, any] = {}
        
        # Initialize Locality Sensitive Hashing (LSH) if the datasketch library is available.
        # LSH allows for efficient similarity search without comparing every possible pair of documents.
        if HAS_DATASKETCH:
            self.lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)
        else:
            self.lsh = None

    def add_page(self, url: str, text: str) -> None:
        """Add page content for comparison."""
        # Limit the text size to the first 5000 characters to optimize memory usage and processing time.
        self.pages[url] = text[:5000]  

        if HAS_DATASKETCH:
            # Create a new MinHash object with the specified number of permutations.
            mh = MinHash(num_perm=self.num_perm)
            
            # Generate shingles (n-grams of words) from the text.
            shingles = self._get_shingles(text)
            
            # Update the MinHash object with each shingle to build the signature.
            for s in shingles:
                mh.update(s.encode("utf-8"))
                
            # Store the MinHash object for this specific URL.
            self.minhashes[url] = mh
            
            try:
                # Insert the MinHash into the LSH index for fast, approximate similarity queries later.
                self.lsh.insert(url, mh)
            except ValueError:
                # Ignore ValueError if the URL is already present in the LSH index (duplicate key).
                pass  

    def find_near_duplicates(self) -> list[dict[str, any]]:
        """Find near-duplicate page pairs."""
        duplicates = []

        if not HAS_DATASKETCH:
            # Fallback to a simpler, exact-match hash comparison if the datasketch library is not installed.
            return self._simhash_fallback()

        # Keep track of checked pairs to avoid reporting the same duplicate pair twice (e.g., A-B and B-A).
        checked = set()
        
        for url, mh in self.minhashes.items():
            # Query the LSH index for URLs that are likely similar to the current URL's MinHash signature.
            results = self.lsh.query(mh)
            
            for other_url in results:
                # Create a sorted tuple to ensure consistent pair ordering regardless of query direction.
                pair = tuple(sorted([url, other_url]))
                
                # Only process the pair if it hasn't been checked yet and the URLs are not identical.
                if pair not in checked and url != other_url:
                    checked.add(pair)
                    
                    # Calculate the exact Jaccard similarity between the two MinHash objects.
                    similarity = mh.jaccard(self.minhashes[other_url])
                    
                    # If the similarity meets or exceeds the defined threshold, record it as a near-duplicate.
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
        # Dictionary to map a paragraph's MD5 hash to a list of URLs where it was found.
        para_map: dict[str, list[str]] = {}

        for url, text in self.pages.items():
            # Split text into paragraphs, strip whitespace, and filter out very short paragraphs (< 100 chars).
            paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 100]
            
            for para in paragraphs:
                # Generate an MD5 hash of the paragraph to use as a unique, space-efficient identifier.
                key = hashlib.md5(para.encode()).hexdigest()
                
                # Add the current URL to the list of URLs containing this specific paragraph.
                para_map.setdefault(key, []).append(url)

        duplicates = []
        for key, urls in para_map.items():
            # If a paragraph is found on more than one page, it is considered a duplicate.
            if len(urls) > 1:
                duplicates.append({
                    "paragraph_hash": key,
                    "found_on": urls,
                    "count": len(urls),
                })

        # Return only the top 20 duplicate paragraphs to keep the report concise and focused on major issues.
        return duplicates[:20]

    def _get_shingles(self, text: str, k: int = 5) -> set[str]:
        """Generate k-word shingles from text."""
        # Remove punctuation, convert to lowercase, and split into individual words.
        words = re.sub(r"[^\w\s]", "", text.lower()).split()
        
        # If the text has fewer words than the shingle size, return the entire text as a single shingle.
        if len(words) < k:
            return {" ".join(words)}
            
        # Generate a set of k-word contiguous sequences (shingles) from the word list.
        return {" ".join(words[i:i + k]) for i in range(len(words) - k + 1)}

    def _simhash_fallback(self) -> list[dict[str, any]]:
        """Simple hash-based duplicate detection fallback."""
        duplicates = []
        # Dictionary to map a text hash to the first URL where it was encountered.
        hashes: dict[str, str] = {}

        for url, text in self.pages.items():
            # Generate an MD5 hash of the first 1000 characters of the text for a quick exact-match check.
            h = hashlib.md5(text[:1000].encode()).hexdigest()
            
            if h in hashes:
                # If the hash already exists, we have found an exact duplicate.
                duplicates.append({
                    "url_1": hashes[h],
                    "url_2": url,
                    "similarity": 100.0,
                    "type": "exact_duplicate",
                })
            else:
                # Otherwise, store the hash and its corresponding URL for future comparisons.
                hashes[h] = url

        return duplicates