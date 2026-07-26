# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Initial project structure and core asynchronous crawling engine.
- 19+ specialized SEO analysis modules (Technical, Content, Links, Performance).
- Multi-format export system (TXT, JSON, CSV, PDF, HTML).
- AI Master Prompt generator for LLM integration.
- Native Persian (Farsi) NLP text processing support.

## [0.1.0] - 2023-10-01
### Added
- Core `RobustFetcher` with retry logic and HTTP/2 support.
- Basic `ContentExtractor` for metadata, headings, and links.
- Initial `SEOScorer` with 5 dimensional scoring.
- Command-line interface (CLI) entry point.

## [0.2.0] - 2023-11-15
### Added
- `LinkGraphAnalyzer` using NetworkX for orphan and hub page detection.
- `DuplicateDetector` using MinHash and Shingling.
- Interactive HTML Dashboard generator with Chart.js.
- PDF Report generation using ReportLab.

## [0.5.0] - 2024-01-20
### Added
- Google Search Console and Analytics integration scaffolding.
- Competitor discovery engine via DuckDuckGo and Selenium.
- Enhanced `RobotsParser` and `SitemapParser` with recursive support.
- Comprehensive type hinting and Pydantic models across the codebase.
