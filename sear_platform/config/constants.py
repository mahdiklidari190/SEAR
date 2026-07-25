"""Global constants, regex patterns, user agents, and stopwords."""
from __future__ import annotations

import re

# =============================================================================
# DEPENDENCY MAPPING
# Maps pip package names to their actual Python import names.
# This is used by the system to verify that all required third-party 
# libraries are correctly installed before running heavy analysis tasks.
# =============================================================================
PACKAGE_IMPORT_MAP: dict[str, str] = {
    "httpx": "httpx",
    "lxml": "lxml",
    "pydantic": "pydantic",
    "tenacity": "tenacity",
    "rich": "rich",
    "beautifulsoup4": "bs4",
    "brotli": "brotli",
    "duckduckgo-search": "duckduckgo_search",
    "html5lib": "html5lib",
    "networkx": "networkx",
    "datasketch": "datasketch",
    "cryptography": "cryptography",
    "dnspython": "dns",
    "aiofiles": "aiofiles",
    "jinja2": "jinja2",
    "reportlab": "reportlab",
}

# =============================================================================
# PRE-COMPILED REGEX PATTERNS
# Pre-compiling these regular expressions improves performance during 
# high-volume text parsing, HTML extraction, and URL normalization.
# =============================================================================

# Extracts URLs from <loc> tags, primarily used for parsing XML sitemaps.
RE_LOC = re.compile(r'<loc>(.*?)</loc>', re.IGNORECASE | re.DOTALL)

# Detects common Cloudflare anti-bot, WAF, or access denied challenge pages.
RE_CLOUDFLARE = re.compile(r'just a moment|cloudflare|access denied|ray id', re.IGNORECASE)

# Identifies non-navigational links that should be ignored during internal link graph analysis.
RE_EMAIL_TEL = re.compile(r'^(mailto:|tel:|javascript:|#)')

# Detects the presence of any query parameters in a URL.
RE_PARAMETER_URL = re.compile(r'[?&]')

# Identifies session tracking parameters that can cause duplicate content and waste crawl budget.
RE_SESSION_ID = re.compile(r'(jsessionid|phpsessid|sid|session_id)=[^&]+', re.IGNORECASE)

# Identifies standard Google Analytics/Ads marketing tracking parameters.
RE_UTM_PARAMS = re.compile(r'utm_(source|medium|campaign|term|content)=[^&]*', re.IGNORECASE)

# =============================================================================
# CRAWLING CONFIGURATION
# A rotating list of modern, realistic browser User-Agents.
# Rotating these helps prevent the crawler from being immediately flagged 
# or blocked by anti-bot systems and Web Application Firewalls (WAFs).
# =============================================================================
USER_AGENTS: list[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
]

# =============================================================================
# NATURAL LANGUAGE PROCESSING (NLP)
# A comprehensive set of stopwords in both English and Persian.
# These are filtered out during keyword extraction, content similarity 
# analysis, and text density calculations to focus on meaningful terms.
# =============================================================================
STOPWORDS: set[str] = {
    "the", "and", "of", "to", "a", "in", "is", "that", "for", "on", "with", "as", "by", "this", "it", "not",
    "from", "or", "are", "be", "an", "has", "have", "was", "were", "will", "would", "can", "could", "should",
    "از", "به", "با", "که", "تا", "در", "برای", "یا", "هم", "و", "را", "این", "آن", "است", "بود", "شد", "یک",
    "خود", "من", "ما", "تو", "شما", "آنها", "او", "نیز", "روی", "دهد", "کنند", "کند", "کرد", "دارد", "دارند",
    "باید", "دیگر", "همه", "هیچ", "طریق", "بین", "پیش", "پس", "مورد", "تحت", "بخش", "بر", "حتی", "بسیار",
    "بسیاری", "درباره", "چون", "چرا", "چگونه", "اگر", "اما", "ولی", "همین", "همان", "هر", "تنها", "بلکه",
    "زیرا", "بنابراین", "سپس", "هست", "هستند", "بودن", "شدن", "کردن", "داشتن", "برخی", "کدام", "کجا", "کی",
    "چه", "چند", "چندین", "یکدیگر", "دوباره", "همواره", "همیشه", "هیچگاه", "هیچوقت", "هنوز", "البته", "شاید",
    "احتمالا", "مثلا", "مانند", "مثل", "همچون", "بهتر", "بزرگ", "کوچک", "جدید", "قدیم", "اول", "آخر", "دوم", "سوم",
    "ها", "های", "هایش", "هایی", "ام", "ات", "اش", "مان", "تان", "شان", "تر", "ترین", "می", "نماید", "نمایند",
    "شدید", "گردید", "گردد", "گردند", "داشت", "داشتند", "بودند", "باشند", "باشد", "بوده", "شده", "کرده", "کرده‌اند",
    "شود", "می‌شود", "شده‌اند", "کنیم", "کنید", "می‌تواند", "بی", "نیست",
}

# =============================================================================
# SCHEMA.ORG VALIDATION
# The specific Schema.org types that the analyzer actively validates 
# for required fields and proper implementation to ensure rich result eligibility.
# =============================================================================
SUPPORTED_SCHEMA_TYPES: list[str] = [
    "Organization", "Article", "FAQPage", "HowTo", "BreadcrumbList",
    "Product", "Review", "Event", "LocalBusiness", "Person",
    "VideoObject", "WebSite", "SearchAction",
]

# =============================================================================
# SECURITY & HEADERS
# Standard HTTP security headers that should be present on enterprise sites 
# to prevent common web vulnerabilities (XSS, Clickjacking, MIME-sniffing).
# =============================================================================
SECURITY_HEADERS: list[str] = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
    "Permissions-Policy",
    "Cross-Origin-Opener-Policy",
    "Cross-Origin-Resource-Policy",
]

# =============================================================================
# JAVASCRIPT FRAMEWORK DETECTION
# HTML/DOM signatures and specific script markers used to automatically 
# identify the underlying JavaScript framework or meta-framework of a webpage.
# This helps tailor the rendering and SEO recommendations accordingly.
# =============================================================================
JS_FRAMEWORK_PATTERNS: dict[str, list[str]] = {
    "React": ["react", "react-dom", "__NEXT_DATA__", "_reactRootContainer"],
    "Vue": ["vue", "vue-router", "__vue__", "data-v-"],
    "Angular": ["ng-version", "angular", "ng-app", "_nghost"],
    "Next.js": ["__NEXT_DATA__", "_next/static", "next/router"],
    "Nuxt": ["__NUXT__", "_nuxt/", "nuxt-link"],
    "Svelte": ["svelte", "__svelte"],
}