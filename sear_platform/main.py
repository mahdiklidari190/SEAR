"""
SEAR Enterprise AI SEO Platform - Main Entry Point
Strict Workflow: Sitemap -> Extract URLs -> Fetch HTML -> Extract Keywords -> Chrome Competitor Search.
"""
from __future__ import annotations

import sys
import asyncio
import logging
import re
import webbrowser
import http.server
import threading
from pathlib import Path
from urllib.parse import urlparse

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.rule import Rule

from config.settings import get_settings
from config.constants import RE_LOC
from utils.dependency_manager import check_dependencies
from utils.helpers import sanitize_filename, get_domain
from core.fetcher import RobustFetcher
from core.extractor import ContentExtractor
from core.scorer import SEOScorer
from core.duplicate_detector import duplicate_detector
from core.parser import SitemapParser, RobotsParser
from core.ddg_discoverer import DDGDiscoverer
from core.competitor_extractor import CompetitorExtractor
from keywords.extractor import KeywordExtractor
from competitors.finder import CompetitorFinder
from analysis.crawl_budget import CrawlBudgetAnalyzer
from analysis.link_graph import LinkGraphAnalyzer
from analysis.orphan_pages import OrphanPageDetector
from analysis.broken_links import BrokenLinkChecker
from analysis.redirect_analysis import RedirectAnalyzer
from analysis.canonical_validation import CanonicalValidator
from analysis.content_similarity import ContentSimilarityAnalyzer
from analysis.keyword_cannibalization import KeywordCannibalizationDetector
from analysis.anchor_text import AnchorTextAnalyzer
from analysis.core_web_vitals import CoreWebVitalsAnalyzer
from analysis.technical_seo import TechnicalSEOAnalyzer
from integrations.search_console import SearchConsoleIntegration
from integrations.analytics import AnalyticsIntegration
from integrations.backlink_apis import BacklinkAPIConnector
from ai.master_prompt import AIMasterPromptGenerator
from reports.export_manager import ExportManager
from models.page_data import PageData
from models.reports import AnalysisReport

# Logging setup
settings = get_settings()
REPORTS_DIR = settings.reports_dir
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

log_file = REPORTS_DIR / "error_log.txt"
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)
console = Console()


def display_header():
    """Display application header."""
    ascii_art = """
 ███████╗███████╗ █████╗ ██████╗ 
 ██╔════╝██╔════╝██╔══██╗██╔══██╗
 ███████╗█████╗  ███████║██████╔╝
 ╚════██║██╔══╝  ██╔══██║██╔══██╗
 ███████║███████╗██║  ██║██║  ██║
 ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
"""
    header_content = (
        f"[bold cyan]{ascii_art}[/bold cyan]\n"
        f"[bold white]Enterprise AI SEO Intelligence Platform v6.0[/bold white]\n"
        f"[dim]Powered by Dark Wolf Agency[/dim]\n\n"
        f"[bold blue]🌐 Web: https://klidari.ir/[/]\n"
        f"[bold magenta]💼 LinkedIn: https://ir.linkedin.com/in/bardia-klidari-64a32a30b[/]"
    )
    console.print(Panel(
        header_content,
        title="[bold gold1]SEO ANALYZER (ENTERPRISE EDITION)[/bold gold1]",
        border_style="gold1",
        expand=False,
    ))


async def process_single_page(
    url: str,
    fetcher: RobustFetcher,
    finder: CompetitorFinder,
    comp_extractor: CompetitorExtractor,
    export_mgr: ExportManager,
    crawl_budget: CrawlBudgetAnalyzer,
    link_graph: LinkGraphAnalyzer,
    canonical_validator: CanonicalValidator,
    content_sim: ContentSimilarityAnalyzer,
    kw_cannibal: KeywordCannibalizationDetector,
    anchor_analyzer: AnchorTextAnalyzer,
) -> tuple[AnalysisReport, PageData | None, str]:
    """Process a single page: Fetch HTML -> Extract Keywords -> Chrome Competitor Search."""
    raw_filename = sanitize_filename(urlparse(url).path)
    filename = raw_filename if raw_filename else "homepage"

    try:
        # 1. Fetch HTML Content
        console.print(f"[cyan]>> Fetching HTML content...[/cyan]")
        fetch_result = await fetcher.fetch(url)

        # 2. Extract Content & Data
        console.print(f"[cyan]>> Extracting page data...[/cyan]")
        page_data = ContentExtractor.extract(fetch_result, url)

        # 3. Extract Keywords
        console.print(f"[cyan]>> Extracting Keywords & Title...[/cyan]")
        keywords = KeywordExtractor.extract(page_data)
        page_data.keywords = keywords

        # 4. Find Competitors via Google Chrome
        console.print(f"[cyan]>> Searching Google (Chrome) for competitors using keywords...[/cyan]")
        competitors = await finder.find_competitors(keywords, num_results=3)
        page_data.competitors = competitors
        
        # 5. Extract Competitor Content
        if competitors:
            console.print(f"[cyan]>> Extracting Competitor Content & Saving...[/cyan]")
            await comp_extractor.extract_and_save(url, competitors)

        console.print(f"[cyan]>> Calculating SEO Score...[/cyan]")
        page_data = SEOScorer.calculate(page_data)

        # Feed analyzers
        crawl_budget.add_url(url)
        link_graph.add_page(url)
        canonical_validator.add_page(page_data)
        content_sim.add_page(url, page_data.text_sample)
        kw_cannibal.add_page(url, keywords)
        anchor_analyzer.add_anchors(page_data.links.anchor_texts, url)

        for internal_url in page_data.links.internal_urls:
            link_graph.add_link(url, internal_url)

        if page_data.redirect_chain:
            for i, chain_url in enumerate(page_data.redirect_chain):
                crawl_budget.add_redirect(chain_url, url)

        cwv = CoreWebVitalsAnalyzer.analyze(page_data)
        tech_seo = TechnicalSEOAnalyzer.analyze_from_page(page_data)

        console.print(f"[cyan]>> Generating AI Master Prompt...[/cyan]")
        ai_prompt = AIMasterPromptGenerator.generate(
            page=page_data,
            keywords=keywords,
            competitors=competitors,
            cwv=cwv,
        )
        page_data.ai_prompt = ai_prompt

        console.print(f"[cyan]>> Fetching Robots.txt...[/cyan]")
        robots_txt = await _fetch_robots_txt(fetcher, url)

        console.print(f"[cyan]>> Generating Reports (TXT, JSON, PDF)...[/cyan]")
        export_mgr.export_page(
            page=page_data,
            filename=filename,
            competitors=competitors,
            keywords=keywords,
            robots_txt=robots_txt,
            ai_prompt=ai_prompt,
            cwv=cwv,
        )

        report = AnalysisReport(page_url=url, ai_analysis=ai_prompt, status="success")
        return report, page_data, keywords

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed: {url} | {error_msg}")
        error_path = export_mgr.txt_dir / f"{filename}.txt"
        error_path.write_text(
            f"ANALYSIS FAILED\nURL: {url}\nReason: {error_msg}\n\nAction: Check error_log.txt",
            encoding="utf-8",
        )
        return AnalysisReport(page_url=url, ai_analysis="", status="error", error_message=error_msg), None, ""


async def _fetch_robots_txt(fetcher: RobustFetcher, base_url: str) -> str:
    parsed = urlparse(base_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        result = await fetcher.fetch(robots_url)
        return result.content.decode("utf-8", errors="ignore")
    except Exception:
        return ""


def _serve_dashboard(directory: Path, port: int = 8765) -> None:
    import os
    os.chdir(directory)
    handler = http.server.SimpleHTTPRequestHandler
    handler.log_message = lambda *args: None

    try:
        server = http.server.HTTPServer(("127.0.0.1", port), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        webbrowser.open(f"http://127.0.0.1:{port}/report.html")
        console.print(f"[green]📊 Dashboard: http://127.0.0.1:{port}/report.html[/green]")
    except OSError:
        report_path = directory / "report.html"
        if report_path.exists():
            webbrowser.open(report_path.as_uri())


async def main_flow(input_url: str):
    """Main analysis workflow - STRICT SITEMAP PARSING."""
    settings = get_settings()
    fetcher = RobustFetcher(
        timeout=settings.request_timeout,
        max_concurrent=settings.max_concurrent_requests,
    )
    finder = CompetitorFinder(fetcher)
    comp_extractor = CompetitorExtractor(fetcher)

    domain = get_domain(input_url).replace(".", "_")
    site_name = get_domain(input_url)
    target_dir = REPORTS_DIR / domain
    export_mgr = ExportManager(target_dir)

    duplicate_detector.reset()

    crawl_budget = CrawlBudgetAnalyzer()
    link_graph = LinkGraphAnalyzer()
    canonical_validator = CanonicalValidator()
    content_sim = ContentSimilarityAnalyzer()
    kw_cannibal = KeywordCannibalizationDetector()
    anchor_analyzer = AnchorTextAnalyzer()

    console.print("\n[bold cyan]Initializing discovery engine...[/bold cyan]")
    urls: list[str] = []
    parsed_input = urlparse(input_url)

    # ✅ منطق سخت‌گیرانه: اگر ورودی سایت‌مپ است، فقط از سایت‌مپ استفاده کن
    is_sitemap_input = "sitemap" in parsed_input.path.lower() or parsed_input.path.endswith(".xml")

    if is_sitemap_input:
        console.print(f"[bold yellow][!] Direct Sitemap URL detected. Extracting ALL URLs from it...[/bold yellow]")
        try:
            seen = {input_url}
            urls = await SitemapParser.parse_recursive(fetcher, input_url, seen)
            if not urls:
                console.print("[red][ERROR] Sitemap parsing returned 0 URLs. Please check if the URL is a valid sitemap.[/red]")
        except Exception as e:
            console.print(f"[red][ERROR] Failed to parse sitemap: {e}[/red]")
    else:
        # فقط اگر ورودی سایت‌مپ نبود، سراغ DDG می‌رود
        console.print("[dim]Not a sitemap URL. Searching DuckDuckGo for sitemaps...[/dim]")
        ddg_sitemaps = DDGDiscoverer.find_sitemaps(site_name)
        
        if ddg_sitemaps:
            console.print(f"[yellow][!] Found {len(ddg_sitemaps)} sitemap(s) via DuckDuckGo. Crawling recursively...[/yellow]")
            seen = set()
            for sm_url in ddg_sitemaps:
                urls.extend(await SitemapParser.parse_recursive(fetcher, sm_url, seen))
        
        if not urls:
            console.print("[yellow][!] No sitemaps found. Discovering indexed pages via DuckDuckGo...[/yellow]")
            urls = DDGDiscoverer.find_all_pages(site_name)

    # ✅ فال‌بک نهایی فقط در صورتی که همه چیز شکست خورد
    if not urls:
        console.print("[red][ERROR] Could not extract any URLs. Falling back to root domain.[/red]")
        urls = [f"{parsed_input.scheme}://{parsed_input.netloc}/"]

    console.print(Rule())
    console.print(f"[bold green]{len(urls)} page(s) extracted and queued for analysis.[/bold green]")
    console.print(Rule())

    sc_integration = SearchConsoleIntegration()
    an_integration = AnalyticsIntegration()
    bl_connector = BacklinkAPIConnector()

    search_console_data = sc_integration.fetch_data() if sc_integration.is_available else None
    analytics_data = an_integration.fetch_data() if an_integration.is_available else None
    backlink_data = bl_connector.fetch_backlinks(site_name)

    all_pages: list[PageData] = []
    all_competitors: list = []
    success_count = 0

    for idx, url in enumerate(urls, 1):
        console.print(f"\n[bold magenta]>>> PROCESSING PAGE {idx}/{len(urls)} <<<[/bold magenta]")
        console.print(f"[bold white]Target: {url}[/bold white]")

        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
            BarColumn(), console=console
        ) as progress:
            task = progress.add_task("Analyzing...", total=None)
            report, page_data, keywords = await process_single_page(
                url, fetcher, finder, comp_extractor, export_mgr,
                crawl_budget, link_graph, canonical_validator,
                content_sim, kw_cannibal, anchor_analyzer,
            )
            progress.update(task, completed=True)

        if report.status == "success" and page_data:
            success_count += 1
            all_pages.append(page_data)
            if hasattr(page_data, 'competitors') and page_data.competitors:
                all_competitors.extend(page_data.competitors)
                
            console.print(Panel(
                f"[green]SUCCESS[/green]\nReports: [bold cyan]{target_dir}[/bold cyan]",
                border_style="green",
            ))
        else:
            console.print(Panel(
                f"[red]FAILED[/red]\nReason: {(report.error_message or 'Unknown')[:150]}",
                border_style="red",
            ))

        console.print(Rule())

    # === SITE-LEVEL ANALYSIS ===
    console.print("\n[bold cyan]Running site-level analysis...[/bold cyan]")

    cb_report = crawl_budget.analyze()
    console.print(f"  Crawl Budget Waste: {cb_report.wasted_budget_pct}%")

    lg_data = link_graph.analyze()
    console.print(f"  Orphan Pages: {len(lg_data.orphan_pages)} | Hub Pages: {len(lg_data.hub_pages)}")

    canon_issues = canonical_validator.analyze()
    if canon_issues:
        console.print(f"  Canonical Issues: {len(canon_issues)}")

    near_dupes = content_sim.find_near_duplicates()
    if near_dupes:
        console.print(f"  Near-Duplicate Pages: {len(near_dupes)}")

    cannibal = kw_cannibal.detect()
    if cannibal:
        console.print(f"  Keyword Cannibalization: {len(cannibal)} keywords")

    anchor_analyzer.analyze()

    console.print("[cyan]>> Generating site dashboard and CSV reports...[/cyan]")
    export_mgr.export_site_summary(
        pages=all_pages,
        competitors=all_competitors,
        site_name=site_name,
        search_console=search_console_data,
        link_graph=lg_data,
    )

    console.print(f"\n[bold green]✅ OPERATION COMPLETED. {success_count}/{len(urls)} pages analyzed.[/bold green]")
    console.print(f"[dim]Reports: {target_dir.absolute()}[/dim]")
    console.print(f"[dim]Dashboard: {target_dir / 'report.html'}[/dim]\n")

    _serve_dashboard(target_dir)
    await fetcher.close()


def main():
    check_dependencies()

    while True:
        console.clear()
        display_header()

        input_url = console.input("\n[bold yellow]Enter Sitemap URL (e.g., https://site.com/sitemap.xml) or Domain: [/bold yellow]").strip()

        if not input_url:
            console.print("[red]Error: No URL provided. Exiting.[/red]")
            sys.exit(1)

        if not input_url.startswith("http"):
            input_url = "https://" + input_url

        try:
            asyncio.run(main_flow(input_url))
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠️ Analysis interrupted. Shutting down gracefully...[/yellow]")
            sys.exit(0)
        except Exception as e:
            console.print(f"\n[bold red]Unexpected error: {e}[/bold red]")
            logger.exception("Unexpected error in main loop")

        console.input("\n[bold cyan]Press Enter to analyze another site (or Ctrl+C to exit)...[/bold cyan]")


if __name__ == "__main__":
    main()