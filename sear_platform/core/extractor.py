"""Content Extractor - preserved from original with all extensions."""
from __future__ import annotations

import json
import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup

# Import global constants for regex matching, framework detection, and schema validation.
from config.constants import RE_EMAIL_TEL, JS_FRAMEWORK_PATTERNS, SUPPORTED_SCHEMA_TYPES
# Import the structured data models that will hold the extracted SEO metrics.
from models.page_data import (
    PageData, SecurityHeaders, PerformanceData, SSLData,
    JSRenderingData, MobileData, BreadcrumbData, PaginationData,
)
from models.issues import Issue
# Import the global singleton used to track duplicate content across the entire crawl session.
from core.duplicate_detector import duplicate_detector
from core.fetcher import FetchResult


class ContentExtractor:
    """
    Extract and validate all page data.
    This class serves as the central parsing engine, transforming raw HTML and HTTP responses 
    into a structured, comprehensive SEO data model while simultaneously flagging common on-page issues.
    """

    @staticmethod
    def _get_meta(soup, name: str = None, property_name: str = None) -> str:
        """
        Safely extract the content of a meta tag by its 'name' or 'property' attribute.
        Returns an empty string if the tag or content is not found, preventing NoneType errors.
        """
        if name:
            meta = soup.find("meta", attrs={"name": lambda x: x and x.lower() == name.lower()})
            if meta and meta.get("content"):
                return meta["content"].strip()
        if property_name:
            meta = soup.find("meta", attrs={"property": lambda x: x and x.lower() == property_name.lower()})
            if meta and meta.get("content"):
                return meta["content"].strip()
        return ""

    @staticmethod
    def extract(fetch_result: FetchResult, base_url: str) -> PageData:
        """
        Main extraction method.
        Parses the raw HTTP response and HTML content to populate the PageData model 
        with metadata, structural elements, performance metrics, and technical SEO signals.
        """
        html_content = fetch_result.content
        status_code = fetch_result.status_code
        # Use html5lib for robust parsing that mimics how modern browsers handle malformed HTML.
        soup = BeautifulSoup(html_content, "html5lib")
        parsed_base = urlparse(base_url)
        base_domain = parsed_base.netloc.lower().replace("www.", "")
        base_scheme = parsed_base.scheme

        # Initialize the PageData object with the core URL and HTTP status.
        page = PageData(url=base_url, status_code=status_code)
        page.response_headers = fetch_result.headers
        page.redirect_chain = fetch_result.redirect_chain

        # =========================================================================
        # BASIC METADATA EXTRACTION
        # =========================================================================
        page.title = soup.title.string.strip() if soup.title and soup.title.string else ""
        page.meta_description = ContentExtractor._get_meta(soup, "description")
        page.meta_keywords = ContentExtractor._get_meta(soup, "keywords")
        page.meta_robots = ContentExtractor._get_meta(soup, "robots")
        page.meta_author = ContentExtractor._get_meta(soup, "author")

        canonical_tag = soup.find("link", rel="canonical")
        page.canonical_url = canonical_tag["href"].strip() if canonical_tag and canonical_tag.get("href") else ""

        page.og_title = ContentExtractor._get_meta(soup, None, "og:title")
        page.og_description = ContentExtractor._get_meta(soup, None, "og:description")
        page.og_image = ContentExtractor._get_meta(soup, None, "og:image")
        page.twitter_card = ContentExtractor._get_meta(soup, "twitter:card")

        page.h1 = [h.get_text(strip=True) for h in soup.find_all("h1") if h.get_text(strip=True)]
        page.h2 = [h.get_text(strip=True) for h in soup.find_all("h2") if h.get_text(strip=True)]
        page.h3 = [h.get_text(strip=True) for h in soup.find_all("h3") if h.get_text(strip=True)]
        page.h4 = [h.get_text(strip=True) for h in soup.find_all("h4") if h.get_text(strip=True)]

        # Extract hreflang tags for international SEO analysis.
        for link in soup.find_all("link", hreflang=True):
            hl = link.get("hreflang", "").lower()
            href = link.get("href", "")
            if hl == "x-default":
                page.x_default = href
            else:
                page.hreflang[hl] = href

        # =========================================================================
        # LINK ANALYSIS
        # Categorize internal vs. external links and track anchor text distribution.
        # =========================================================================
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            page.links.total += 1
            anchor_text = a.get_text(strip=True)

            # Ignore empty links or non-navigational links like mailto/tel/javascript.
            if not href or RE_EMAIL_TEL.match(href):
                page.links.empty_orphan += 1
                continue

            rel = a.get("rel", [])
            if "nofollow" in rel:
                page.links.nofollow += 1
            if "sponsored" in rel:
                page.links.sponsored += 1
            if "ugc" in rel:
                page.links.ugc += 1

            parsed_href = urlparse(href)
            target_netloc = parsed_href.netloc.lower().replace("www.", "")

            # Resolve relative URLs to absolute URLs for accurate graph building.
            if not parsed_href.netloc:
                resolved = f"{base_scheme}://{parsed_base.netloc}{href if href.startswith('/') else '/' + href}"
            else:
                resolved = href

            # Classify the link as internal or external based on the normalized domain.
            if not parsed_href.netloc or target_netloc == base_domain:
                page.links.internal += 1
                page.links.internal_urls.append(resolved)
            else:
                page.links.external += 1
                page.links.external_urls.append(resolved)

            page.links.anchor_texts.append({"text": anchor_text, "url": resolved, "rel": ",".join(rel)})

        # =========================================================================
        # IMAGE ANALYSIS
        # Check for accessibility (alt text) and performance (dimensions, modern formats).
        # =========================================================================
        seen_alts: set[str] = set()
        for img in soup.find_all("img"):
            page.images.total += 1
            alt = img.get("alt", "")
            if alt is None:
                page.images.missing_alt += 1
            elif alt.strip() == "":
                page.images.empty_alt += 1
            else:
                if alt in seen_alts:
                    page.images.duplicate_alt.add(alt)
                seen_alts.add(alt)

            if not img.get("width") or not img.get("height"):
                page.images.missing_dimensions += 1
            if img.get("loading") == "lazy":
                page.images.lazy_loaded += 1

            src = img.get("src", "").lower()
            # Identify modern, highly-compressed image formats or <picture> tag usage.
            if ".webp" in src or ".avif" in src or img.get("type") in ["image/webp", "image/avif"]:
                page.images.modern_format += 1
            elif img.parent and img.parent.name == "picture":
                page.images.modern_format += 1

        # =========================================================================
        # STRUCTURED DATA EXTRACTION
        # Parse JSON-LD scripts to identify schema types and catch syntax errors.
        # =========================================================================
        for script in soup.find_all("script", type="application/ld+json"):
            page.structured_data.found = True
            try:
                data = json.loads(script.string)
                page.structured_data.raw_json.append(data)
                types = []
                if isinstance(data, dict):
                    types = data.get("@type", [])
                    if isinstance(types, str):
                        types = [types]
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and "@type" in item:
                            t = item["@type"]
                            if isinstance(t, str):
                                types.append(t)

                for t in types:
                    if t in SUPPORTED_SCHEMA_TYPES and t not in page.structured_data.types:
                        page.structured_data.types.append(t)
            except json.JSONDecodeError:
                page.structured_data.errors.append("Invalid JSON-LD syntax")

        # =========================================================================
        # ACCESSIBILITY CHECKS
        # =========================================================================
        html_tag = soup.find("html")
        page.accessibility_lang = html_tag.get("lang", "") if html_tag else ""
        if not page.accessibility_lang:
            page.accessibility_issues.append("Missing 'lang' attribute on <html> tag.")

        forms = soup.find_all("form")
        for form in forms:
            if not form.find_all(["label", "aria-label"]):
                page.accessibility_issues.append("Form detected without associated labels or aria-labels.")

        # =========================================================================
        # TECHNICAL & PERFORMANCE ANALYSIS
        # =========================================================================
        page.security_headers = ContentExtractor._analyze_security_headers(fetch_result.headers)

        page.performance = PerformanceData(
            ttfb_ms=fetch_result.ttfb_ms,
            total_time_ms=fetch_result.total_time_ms,
            http_version=fetch_result.http_version,
            compression=fetch_result.headers.get("content-encoding", ""),
            server=fetch_result.headers.get("server", ""),
            cdn_detected=ContentExtractor._detect_cdn(fetch_result.headers),
            cache_control=fetch_result.headers.get("cache-control", ""),
            etag=bool(fetch_result.headers.get("etag")),
            last_modified=bool(fetch_result.headers.get("last-modified")),
        )

        page.js_rendering = ContentExtractor._detect_js_rendering(soup, html_content)
        page.mobile = ContentExtractor._analyze_mobile(soup)
        page.breadcrumbs = ContentExtractor._analyze_breadcrumbs(soup)
        page.pagination = ContentExtractor._analyze_pagination(soup, base_url)

        # =========================================================================
        # TEXT EXTRACTION & CLEANUP
        # Remove non-content elements to get an accurate word count and text sample.
        # =========================================================================
        for element in soup(
            ["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript", "svg", "form", "button", "input"]
        ):
            element.decompose()
        body = soup.body or soup
        text_sample = body.get_text(separator=" ", strip=True)
        text_sample = re.sub(r"\s+", " ", text_sample).strip()
        page.word_count = len(text_sample.split())
        page.text_sample = text_sample[:3000]

        # =========================================================================
        # VALIDATION & ISSUE GENERATION
        # Run all rule-based checks to populate the page's issue list.
        # =========================================================================
        ContentExtractor._validate_metadata(page)
        ContentExtractor._validate_headings(page)
        ContentExtractor._validate_canonical(page, base_domain, base_scheme)
        ContentExtractor._validate_hreflang(page)
        ContentExtractor._validate_duplicates(page)
        ContentExtractor._validate_content(page)

        return page

    @staticmethod
    def _add_issue(page: PageData, category: str, severity: str, problem: str, solution: str, impact: str, difficulty: str, fix_time: str):
        """Helper method to append a structured Issue object to the page's issue list."""
        page.issues.append(Issue(
            category=category, severity=severity, problem=problem,
            solution=solution, impact=impact, difficulty=difficulty, fix_time=fix_time
        ))

    # =========================================================================
    # VALIDATION METHODS
    # These methods evaluate the extracted data against SEO best practices.
    # =========================================================================
    
    @staticmethod
    def _validate_metadata(page: PageData):
        if not page.title:
            ContentExtractor._add_issue(page, "Metadata", "Critical", "Missing Title Tag",
                "Add a unique, descriptive <title> tag (50-60 chars) including the primary keyword.",
                "High negative impact on rankings and CTR.", "Easy", "5 mins")
        elif len(page.title) > 60:
            ContentExtractor._add_issue(page, "Metadata", "Medium", "Title Tag too long",
                "Shorten title to under 60 characters to prevent truncation in SERPs.",
                "Medium impact on CTR.", "Easy", "5 mins")
        if not page.meta_description:
            ContentExtractor._add_issue(page, "Metadata", "High", "Missing Meta Description",
                "Create a unique meta description (140-160 chars) with a call-to-action and primary keyword.",
                "Reduces organic click-through rate.", "Easy", "10 mins")
        if "noindex" in page.meta_robots.lower():
            ContentExtractor._add_issue(page, "Metadata", "Critical", "Page set to NoIndex",
                "Remove 'noindex' from meta robots tag if this page should appear in search results.",
                "Page will be completely excluded from search engines.", "Easy", "2 mins")

    @staticmethod
    def _validate_headings(page: PageData):
        if not page.h1:
            ContentExtractor._add_issue(page, "Headings", "Critical", "Missing H1 Tag",
                "Add exactly one <h1> tag containing the primary keyword to define the main topic.",
                "Search engines struggle to understand page hierarchy.", "Easy", "5 mins")
        elif len(page.h1) > 1:
            ContentExtractor._add_issue(page, "Headings", "High", f"Multiple H1 Tags ({len(page.h1)})",
                "Keep only one H1. Convert additional H1s to H2 or H3.",
                "Dilutes the main topic signal for search engines.", "Easy", "10 mins")
        if page.h1 and len(page.h1) == 1 and not page.h1[0].strip():
            ContentExtractor._add_issue(page, "Headings", "High", "Empty H1 Tag",
                "Ensure the H1 tag contains visible, descriptive text.",
                "Provides no semantic value.", "Easy", "5 mins")

    @staticmethod
    def _validate_canonical(page: PageData, base_domain: str, base_scheme: str):
        if not page.canonical_url:
            ContentExtractor._add_issue(page, "Canonical", "High", "Missing Canonical Tag",
                "Add a self-referencing canonical tag to prevent duplicate content issues.",
                "Risk of duplicate content penalties.", "Easy", "5 mins")
        else:
            parsed_canon = urlparse(page.canonical_url)
            if parsed_canon.netloc.lower().replace("www.", "") != base_domain:
                ContentExtractor._add_issue(page, "Canonical", "Critical", "Canonical points to different domain",
                    "Ensure canonical URL matches the current domain.",
                    "Severe: signals to Google that another domain owns this content.", "Medium", "15 mins")
            if parsed_canon.scheme != base_scheme:
                ContentExtractor._add_issue(page, "Canonical", "High", "HTTP/HTTPS Canonical Mismatch",
                    "Ensure canonical URL uses the same protocol (HTTPS) as the page.",
                    "Can cause crawl budget waste and mixed content warnings.", "Easy", "5 mins")

    @staticmethod
    def _validate_hreflang(page: PageData):
        if page.hreflang and not page.x_default:
            ContentExtractor._add_issue(page, "Hreflang", "Medium", "Missing x-default hreflang",
                "Add an x-default hreflang tag for users who don't match any specific language/region.",
                "May serve incorrect language version to international users.", "Medium", "15 mins")
        for lang, url in page.hreflang.items():
            if not re.match(r"^[a-z]{2}(-[A-Z]{2})?$", lang) and lang != "x-default":
                ContentExtractor._add_issue(page, "Hreflang", "High", f"Invalid hreflang value: {lang}",
                    "Use valid ISO 639-1 language and ISO 3166-1 Alpha 2 country codes (e.g., 'en-US').",
                    "Search engines may ignore the hreflang implementation.", "Easy", "10 mins")

    @staticmethod
    def _validate_duplicates(page: PageData):
        if page.title and page.title in duplicate_detector.seen_titles:
            ContentExtractor._add_issue(page, "Duplicate Content", "High", f"Duplicate Title: '{page.title}'",
                "Make the title tag unique for this page to reflect its specific content.",
                "Confuses search engines about which page to rank.", "Medium", "15 mins")
        elif page.title:
            duplicate_detector.seen_titles[page.title] = page.url

        if page.meta_description and page.meta_description in duplicate_detector.seen_descriptions and len(page.meta_description) > 10:
            ContentExtractor._add_issue(page, "Duplicate Content", "Medium", "Duplicate Meta Description",
                "Write a unique meta description for this page.",
                "Reduces CTR and may trigger duplicate content filters.", "Easy", "10 mins")
        elif page.meta_description:
            duplicate_detector.seen_descriptions[page.meta_description] = page.url

    @staticmethod
    def _validate_content(page: PageData):
        if page.word_count < 300:
            ContentExtractor._add_issue(page, "Content", "High", f"Thin Content ({page.word_count} words)",
                "Expand the content to at least 300-500 words of high-quality, relevant text.",
                "Thin content is often devalued or ignored by search engines.", "Hard", "2+ hours")

    # =========================================================================
    # ANALYSIS HELPER METHODS
    # =========================================================================
    
    @staticmethod
    def _analyze_security_headers(headers: dict[str, str]) -> SecurityHeaders:
        """Analyze security headers from the HTTP response to identify missing protections."""
        sh = SecurityHeaders()
        h = {k.lower(): v for k, v in headers.items()}

        sh.hsts = "strict-transport-security" in h
        sh.csp = "content-security-policy" in h
        sh.x_frame_options = h.get("x-frame-options", "")
        sh.x_content_type_options = h.get("x-content-type-options", "").lower() == "nosniff"
        sh.referrer_policy = h.get("referrer-policy", "")
        sh.permissions_policy = "permissions-policy" in h
        sh.coop = "cross-origin-opener-policy" in h
        sh.corp = "cross-origin-resource-policy" in h

        if not sh.hsts:
            sh.issues.append("Missing Strict-Transport-Security (HSTS) header")
        if not sh.csp:
            sh.issues.append("Missing Content-Security-Policy header")
        if not sh.x_frame_options:
            sh.issues.append("Missing X-Frame-Options header (clickjacking risk)")
        if not sh.x_content_type_options:
            sh.issues.append("Missing X-Content-Type-Options: nosniff")
        if not sh.referrer_policy:
            sh.issues.append("Missing Referrer-Policy header")

        return sh

    @staticmethod
    def _detect_cdn(headers: dict[str, str]) -> str:
        """Detect the CDN provider by inspecting specific HTTP response headers."""
        h = {k.lower(): v.lower() for k, v in headers.items()}
        server = h.get("server", "")
        via = h.get("via", "")
        cf_ray = h.get("cf-ray", "")

        if cf_ray or "cloudflare" in server:
            return "Cloudflare"
        if "amazon" in server or "cloudfront" in via:
            return "AWS CloudFront"
        if "akamai" in via or "akamai" in server:
            return "Akamai"
        if "fastly" in via:
            return "Fastly"
        if "cdn" in server:
            return "Generic CDN"
        return ""

    @staticmethod
    def _detect_js_rendering(soup, raw_html: bytes) -> JSRenderingData:
        """Detect the JavaScript framework and determine if the page is client-side or server-side rendered."""
        js = JSRenderingData()
        # Analyze the first 50KB of raw HTML to find framework-specific signatures.
        html_str = raw_html.decode("utf-8", errors="ignore")[:50000]

        for framework, patterns in JS_FRAMEWORK_PATTERNS.items():
            for pattern in patterns:
                if pattern in html_str:
                    js.framework_detected = framework
                    break
            if js.framework_detected:
                break

        # Detect Single Page Applications (SPA) by looking for empty root divs typical of React/Vue/Next.js.
        root_div = soup.find("div", id="root") or soup.find("div", id="app") or soup.find("div", id="__next")
        if root_div and not root_div.get_text(strip=True):
            js.is_spa = True
            js.client_rendered = True

        # Detect server-side rendering by checking if the body contains substantial text content.
        body = soup.find("body")
        if body and len(body.get_text(strip=True)) > 200:
            js.server_rendered = True

        # Identify render-blocking scripts that lack async or defer attributes.
        for script in soup.find_all("script", src=True):
            if not script.get("async") and not script.get("defer"):
                src = script.get("src", "")
                # Exclude analytics scripts as they are typically non-blocking or handled separately.
                if src and "analytics" not in src.lower():
                    js.render_blocking_scripts.append(src)

        return js

    @staticmethod
    def _analyze_mobile(soup) -> MobileData:
        """Analyze mobile-friendliness signals, primarily focusing on viewport configuration."""
        mobile = MobileData()

        viewport = soup.find("meta", attrs={"name": "viewport"})
        if viewport:
            mobile.has_viewport = True
            mobile.viewport_content = viewport.get("content", "")
            if "width=device-width" not in mobile.viewport_content:
                mobile.is_mobile_friendly = False
                mobile.font_size_issues.append("Viewport missing width=device-width")
        else:
            mobile.has_viewport = False
            mobile.is_mobile_friendly = False
            mobile.font_size_issues.append("No viewport meta tag found")

        # Check for responsive image implementations using <picture> or srcset attributes.
        pictures = soup.find_all("picture")
        srcsets = soup.find_all("img", srcset=True)
        mobile.responsive_images = bool(pictures or srcsets)

        return mobile

    @staticmethod
    def _analyze_breadcrumbs(soup) -> BreadcrumbData:
        """Analyze breadcrumb navigation by checking both structured data and DOM elements."""
        bc = BreadcrumbData()

        # First, check for BreadcrumbList JSON-LD schema.
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get("@type") == "BreadcrumbList":
                    bc.found = True
                    bc.schema_valid = True
                    items = data.get("itemListElement", [])
                    bc.items = [item.get("name", "") for item in items if isinstance(item, dict)]
                    # Validate that the position values match the array index order.
                    for i, item in enumerate(items):
                        if item.get("position", 0) != i + 1:
                            bc.hierarchy_correct = False
                            bc.issues.append(f"Incorrect position at index {i}")
                    break
            except (json.JSONDecodeError, TypeError):
                continue

        # If no schema is found, fall back to checking for visual breadcrumb DOM elements.
        if not bc.found:
            nav = soup.find("nav", attrs={"aria-label": lambda x: x and "breadcrumb" in x.lower()})
            if nav:
                bc.found = True
                bc.items = [a.get_text(strip=True) for a in nav.find_all("a")]
            else:
                bc_cls = soup.find(class_=re.compile(r"breadcrumb", re.I))
                if bc_cls:
                    bc.found = True
                    bc.items = [a.get_text(strip=True) for a in bc_cls.find_all("a")]

        return bc

    @staticmethod
    def _analyze_pagination(soup, base_url: str) -> PaginationData:
        """Analyze pagination signals using rel=next/prev tags and URL patterns."""
        pag = PaginationData()

        next_link = soup.find("link", rel="next")
        prev_link = soup.find("link", rel="prev")

        if next_link:
            pag.has_next = True
            pag.next_url = next_link.get("href", "")
        if prev_link:
            pag.has_prev = True
            pag.prev_url = prev_link.get("href", "")

        # Check for page number indicators in the URL path or query string.
        parsed = urlparse(base_url)
        if re.search(r"[/&]page[/=]\d+", parsed.path + "?" + parsed.query):
            match = re.search(r"page[/=](\d+)", parsed.path + "?" + parsed.query)
            if match:
                pag.depth = int(match.group(1))

        # Check for canonical conflicts where paginated pages point to the first page.
        canonical = soup.find("link", rel="canonical")
        if canonical and pag.has_next:
            canon_href = canonical.get("href", "")
            if canon_href and canon_href != base_url and "page" not in canon_href:
                pag.canonical_conflict = True
                pag.issues.append("Canonical URL doesn't include pagination parameter")

        return pag