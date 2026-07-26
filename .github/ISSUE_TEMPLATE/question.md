---
name: Question
about: Ask a question about using or developing SEAR
title: '[QUESTION] '
labels: question
assignees: ''
---

**Your Question**
A clear and concise description of your question.

**What have you tried?**
Let us know what documentation you've read or what solutions you've already attempted.

**Environment (if relevant)**
- OS: 
- Python Version: 
---
GitHub Discussions Categories Recommendation
```
# Recommended GitHub Discussions Categories

1. **📢 Announcements**: Official releases, major updates, and roadmap changes (Maintainers only).
2. **💡 Ideas**: Propose new features, SEO checks, or integrations.
3. **🙏 Q&A**: Ask questions about installation, usage, or configuration.
4. **🐛 Show and Tell**: Share how you are using SEAR, custom reports you've built, or success stories.
5. **🌍 Translations**: Coordinate efforts to translate the UI or documentation into other languages.
```
---
GitHub Labels Recommendation
```
# Recommended GitHub Labels (with Hex Colors)

| Label Name | Color | Description |
| :--- | :--- | :--- |
| `bug` | `#d73a4a` | Something isn't working |
| `critical` | `#b60205` | Blocks release or causes data loss |
| `documentation` | `#0075ca` | Improvements or additions to docs |
| `duplicate` | `#cfd3d7` | This issue or pull request already exists |
| `enhancement` | `#a2eeef` | New feature or request |
| `good first issue` | `#7057ff` | Good for newcomers |
| `help wanted` | `#008672` | Extra attention is needed |
| `invalid` | `#e4e669` | This doesn't seem right |
| `question` | `#d876e3` | Further information is requested |
| `wontfix` | `#ffffff` | This will not be worked on |
| `seo` | `#F59E0B` | Related to SEO analysis logic |
| `ai` | `#8B5CF6` | Related to AI prompt or NLP features |
| `performance` | `#10B981` | Related to speed, memory, or crawling efficiency |
| `security` | `#EF4444` | Related to vulnerabilities or secure practices |
| `backend` | `#3776AB` | Python, crawling, or data processing |
| `frontend` | `#61DAFB` | HTML dashboard or UI related |
```
---
GitHub Project Board Recommendation
```
# Recommended Kanban Project Board Columns

1. **📥 Ideas / Backlog**: Unprioritized feature requests and bug reports.
2. **📋 Ready**: Issues that are well-defined, have acceptance criteria, and are ready to be picked up by a contributor.
3. **🏃 In Progress**: Issues currently being worked on (assignee should be tagged).
4. **👀 Review**: Pull requests that are open and awaiting code review.
5. **🧪 Testing**: Merged into `develop`, undergoing QA or automated CI checks.
6. **✅ Done**: Completed and ready to be included in the next release.
7. **🚀 Released**: Shipped to the `main` branch and published in a release.
```
---
GitHub Actions Workflow Recommendation
```
# Recommended GitHub Actions Workflows

Create these files in `.github/workflows/`:

### 1. `lint-and-test.yml`
Runs on every push and PR to `main`.
- Checks out code.
- Sets up Python 3.10, 3.11, 3.12.
- Installs dependencies.
- Runs `black --check`, `ruff check`, `mypy`.
- Runs `pytest` with coverage.

### 2. `security-scan.yml`
Runs on push to `main`.
- Uses `bandit` to check for common Python security issues.
- Uses `dependabot` or `pip-audit` to check for vulnerable dependencies.

### 3. `release.yml`
Runs when a new GitHub Release is published.
- Builds the package (if applicable).
- Generates a changelog.
- Publishes to PyPI (if you decide to distribute SEAR as a pip package).
```
---
Release Strategy
```
# SEAR Release Strategy

1. **Branching**: Development happens on the `develop` branch. The `main` branch always reflects the latest stable release.
2. **Versioning**: We follow [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH).
   - **PATCH**: Bug fixes and minor performance improvements.
   - **MINOR**: New features (e.g., a new analysis module) that are backward compatible.
   - **MAJOR**: Breaking changes to the API, configuration, or core architecture.
3. **Process**:
   - Freeze the `develop` branch for a "Release Candidate" (RC) phase.
   - Run full test suites and manual QA.
   - Merge `develop` into `main` via a Pull Request.
   - Create a Git Tag (e.g., `v0.5.0`).
   - Publish a GitHub Release with auto-generated release notes and the updated `CHANGELOG.md`.
```
---
Folder Structure Recommendation
```
# Recommended Folder Structure

SEAR/
├── .github/                # GitHub templates, workflows, and labels
├── ai/                     # AI prompt generation logic
├── analysis/               # Specialized SEO analysis modules
├── competitors/            # Competitor discovery engines
├── config/                 # Constants, settings, and regex patterns
├── core/                   # Fetcher, parser, extractor, scorer
├── docs/                   # Extended documentation (MkDocs/Sphinx)
├── integrations/           # GSC, GA4, and Backlink API connectors
├── keywords/               # Keyword extraction and NLP processing
├── models/                 # Pydantic data models
├── reports/                # Export generators (TXT, JSON, CSV, PDF, HTML)
├── tests/                  # Unit and integration tests
├── utils/                  # Helper functions
├── .env.example            # Environment variable template
├── .gitignore              # Git ignore rules
├── main.py                 # CLI entry point
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
└── README.md               # Main project documentation
```
---
Documentation Structure
```
# Recommended Documentation Structure (for a `/docs` folder)

docs/
├── index.md                # Welcome and quick start
├── installation.md         # Detailed setup guide for all OS
├── usage/
│   ├── cli.md              # Command-line interface guide
│   ├── configuration.md    # How to configure sear_config.json / .env
│   └── integrations.md     # Setting up GSC, GA4, and Backlink APIs
├── features/
│   ├── technical-seo.md    # Deep dive into technical checks
│   ├── content-analysis.md # Duplicate detection and keyword extraction
│   └── ai-prompt.md        # How to use the AI Master Prompt
├── architecture.md         # For contributors (data flow, async design)
├── contributing.md         # Developer guidelines
└── faq.md                  # Frequently asked questions
```
---
Wiki Structure
```
# Recommended GitHub Wiki Structure

1. **Home**: Welcome message and link to the main README.
2. **Getting Started**: Step-by-step installation and first run guide.
3. **Understanding the Reports**: Breakdown of what each metric in the HTML/PDF reports means.
4. **Writing Custom Analysis Modules**: A tutorial for developers on how to add a new SEO check to the `analysis/` folder.
5. **Troubleshooting**: Common errors (e.g., Cloudflare blocks, SSL errors) and how to resolve them.
6. **Changelog**: Mirrored from the main `CHANGELOG.md`.
```
---
Final Suggestions for Making SEAR World-Class
Add a pyproject.toml: Migrate from requirements.txt to pyproject.toml (using Poetry or Hatch) for modern Python dependency management and metadata.
Publish to PyPI: Package SEAR so users can install it via pip install sear-seo. This dramatically increases adoption.
Add Badges to the README: Once you set up GitHub Actions, add badges for "Tests Passing", "Coverage %", and "PyPI Version".
Create a Demo Video: Record a 60-second screen capture of SEAR running in the terminal and generating the HTML dashboard, and embed it in the README using <video> or a GIF.
Pre-commit Hooks: Add a .pre-commit-config.yaml file to automatically run Black and Ruff on every commit, ensuring code quality without manual effort.
Docker Support: Add a Dockerfile and docker-compose.yml so users can run SEAR in an isolated container without installing Python locally.
