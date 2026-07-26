# SEAR Task Board & Backlog

This document tracks upcoming tasks, features, and improvements. Contributors are encouraged to pick up tasks, especially those marked `good first issue`.

## 🌟 Good First Issues (Beginner Friendly)
- [ ] Add type hints to `utils/helpers.py`
- [ ] Improve docstrings in `core/extractor.py`
- [ ] Add unit test for `RobotsParser` empty file handling
- [ ] Fix typo in `README.md` Persian translation section
- [ ] Add `__init__.py` to missing submodules
- [ ] Create a `requirements-dev.txt` with `pytest`, `black`, `ruff`
- [ ] Add a `--version` flag to the CLI in `main.py`

## 📝 Documentation
- [ ] Write a dedicated Wiki page for "Understanding the AI Master Prompt"
- [ ] Create a video tutorial for installing and running SEAR on Windows
- [ ] Document all Pydantic models in `models/` using Sphinx or MkDocs
- [ ] Add a "Troubleshooting" section to the README
- [ ] Translate `CONTRIBUTING.md` to Persian

## 🧪 Testing
- [ ] Add `pytest` fixture for mock `PageData` objects
- [ ] Write integration tests for `ExportManager`
- [ ] Mock `httpx` responses for `RobustFetcher` tests
- [ ] Add test for `KeywordExtractor` with empty text input
- [ ] Test `PDFReportGenerator` with missing ReportLab dependency

## ⚡ Performance
- [ ] Implement connection pooling in `RobustFetcher`
- [ ] Optimize `BeautifulSoup` parsing by using `lxml` parser consistently
- [ ] Add caching for DNS lookups using `aiocache`
- [ ] Reduce memory footprint of `LinkGraphAnalyzer` for sites >10k pages
- [ ] Parallelize `ContentExtractor` validations using `asyncio.gather`

## 🤖 AI & NLP
- [ ] Improve Persian stopword list in `config/constants.py`
- [ ] Add support for extracting Open Graph `article:tag`
- [ ] Refine the AI Master Prompt to include specific schema.org JSON-LD fixes
- [ ] Add sentiment analysis to page content using `vaderSentiment`
- [ ] Implement LLM API direct integration (optional) for auto-generating meta descriptions

## 🕷️ SEO Engine (Core)
- [ ] Add detection for `rel="alternate"` hreflang return tags
- [ ] Implement `CanonicalChain` detection (A points to B, B points to C)
- [ ] Add check for missing `X-Robots-Tag` in HTTP headers
- [ ] Detect JavaScript-rendered content discrepancies (DOM vs. Raw HTML)
- [ ] Add validation for `sitemapindex` nested depth limits

## 📊 Reporting
- [ ] Add a "Print to PDF" button in the HTML Dashboard
- [ ] Include a "Last Crawled" timestamp in all report headers
- [ ] Add a pie chart for "Issue Severity Distribution" in HTML dashboard
- [ ] Generate a `sitemap.xml` of the crawled site as an output option
- [ ] Add CSV export for the Internal Link Graph edges

## 🔒 Security
- [ ] Implement rate limiting per domain in `RobustFetcher`
- [ ] Add sanitization for URLs before passing to `httpx` to prevent SSRF
- [ ] Validate SSL certificate chains more rigorously in `SSLData`
- [ ] Add a check for exposed `.git` or `.env` files in the root directory

## 🔌 Integrations
- [ ] Add connector for Moz API (Domain Authority)
- [ ] Add connector for DataForSEO (SERP features)
- [ ] Implement token refresh logic for Google OAuth integrations
- [ ] Add support for reading credentials from a secure keyring

## 🎨 UI / Dashboard
- [ ] Add dark/light mode toggle to the HTML Dashboard
- [ ] Make the HTML Dashboard fully responsive on mobile devices
- [ ] Add a "Copy to Clipboard" button for individual issue solutions
- [ ] Implement a search filter for the Issues table in the HTML dashboard

## 🔬 Research & Nice to Have
- [ ] Research and implement "Entity Extraction" from page content
- [ ] Add support for crawling and analyzing JavaScript SPAs via Playwright (optional dependency)
- [ ] Benchmark SEAR's crawling speed against Screaming Frog
- [ ] Add a "Health Check" endpoint if running as a FastAPI service
