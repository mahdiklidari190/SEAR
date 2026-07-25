"""HTML Dashboard Generator with TailwindCSS, Chart.js, and Interactive SPA View."""
# This module generates a modern, highly interactive, and visually appealing 
# single-page HTML dashboard for SEO reports. It leverages TailwindCSS for styling, 
# Chart.js for data visualization, and vanilla JavaScript for client-side interactivity 
# (e.g., searching, filtering, and navigating between summary and detail views).
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Import core data models to ensure type safety and structured data access.
from models.page_data import PageData
from models.reports import CompetitorData
from models.integrations import SearchConsoleData, LinkGraphData


class HTMLDashboardGenerator:
    """Generate a modern, interactive, enterprise-grade HTML dashboard report."""

    @staticmethod
    def generate(
        pages: list[PageData],
        competitors: list[CompetitorData],
        site_name: str,
        search_console: SearchConsoleData = None,
        link_graph: LinkGraphData = None,
    ) -> str:
        """
        Generate the complete HTML dashboard string.
        
        Args:
            pages: List of analyzed PageData objects.
            competitors: List of CompetitorData objects for benchmarking.
            site_name: The name of the website being analyzed.
            search_console: Optional Google Search Console data.
            link_graph: Optional internal link graph data.
            
        Returns:
            A fully formed HTML string ready to be written to a file.
        """
        pages_data = []
        total_words = 0
        total_critical = 0
        
        # =========================================================================
        # 1. DATA AGGREGATION & SAFE EXTRACTION
        # Iterate through pages to extract metrics, using getattr for safety 
        # against missing or dynamically added attributes.
        # =========================================================================
        for p in pages:
            total_words += getattr(p, 'word_count', 0)
            
            # Safely extract and categorize issues, counting critical ones.
            issues_list = []
            for i in getattr(p, 'issues', []):
                severity = str(getattr(i, 'severity', 'Info'))
                if severity == 'Critical':
                    total_critical += 1
                issues_list.append({
                    "severity": severity,
                    "category": str(getattr(i, 'category', 'General')),
                    # Fallback chain to find the issue description across different possible attribute names.
                    "message": str(getattr(i, 'message', getattr(i, 'problem', getattr(i, 'description', 'No details provided'))))
                })
            
            # Safely extract competitor data associated with the page.
            page_competitors = getattr(p, 'competitors', []) or (competitors[:3] if competitors else [])
            comp_list = []
            for c in page_competitors:
                comp_list.append({
                    "rank": getattr(c, 'rank', 0),
                    "url": str(getattr(c, 'url', '')),
                    "title": str(getattr(c, 'title', ''))
                })
            
            pages_data.append({
                "url": str(getattr(p, 'url', 'Unknown')),
                "title": str(getattr(p, 'title', 'No Title'))[:80],
                "score": int(getattr(p, 'overall_score', 0)),
                "word_count": int(getattr(p, 'word_count', 0)),
                "h1": [str(x) for x in getattr(p, 'h1', [])][:3],
                "meta_desc": str(getattr(p, 'meta_description', ''))[:150],
                "internal_links": len(getattr(getattr(p, 'links', None), 'internal_urls', [])),
                "external_links": len(getattr(getattr(p, 'links', None), 'external_urls', [])),
                "issues": issues_list,
                "competitors": comp_list,
                "ai_prompt": str(getattr(p, 'ai_prompt', 'AI Prompt not generated for this page.')),
                "cwv": {} # Simplified to prevent potential JSON serialization errors with complex nested objects.
            })

        # Calculate site-wide averages and totals.
        avg_score = sum(p["score"] for p in pages_data) // max(len(pages_data), 1)
        
        # Aggregate issues by category for the bar chart.
        issue_cats: dict[str, int] = {}
        for p in pages_data:
            for i in p["issues"]:
                issue_cats[i["category"]] = issue_cats.get(i["category"], 0) + 1

        # Aggregate scores by category for the radar chart.
        score_cats = {}
        if pages and hasattr(pages[0], 'scores'):
            for key in pages[0].scores.keys():
                score_cats[key] = sum(p.scores.get(key, 0) for p in pages) // max(len(pages), 1)
        else:
            score_cats = {"Technical": avg_score, "Content": avg_score, "Performance": avg_score}

        # =========================================================================
        # 2. JSON SERIALIZATION
        # Convert Python dictionaries to JSON strings for injection into the JavaScript.
        # default=str is crucial here to handle any non-serializable objects (like Path or datetime).
        # =========================================================================
        pages_json = json.dumps(pages_data, ensure_ascii=False, indent=2, default=str)
        scores_json = json.dumps(score_cats, ensure_ascii=False, default=str)
        issues_json = json.dumps(issue_cats, ensure_ascii=False, default=str)

        # =========================================================================
        # 3. HTML TEMPLATE GENERATION
        # A comprehensive, self-contained HTML document with embedded CSS and JS.
        # =========================================================================
        html = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEAR Enterprise SEO Dashboard | {site_name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; }}
        .mono {{ font-family: 'JetBrains Mono', monospace; }}
        .glass {{ background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }}
        .glass-hover:hover {{ background: rgba(51, 65, 85, 0.8); border-color: rgba(34, 211, 238, 0.3); }}
        .glow-text {{ text-shadow: 0 0 20px rgba(34, 211, 238, 0.5); }}
        .scrollbar-hide::-webkit-scrollbar {{ display: none; }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .animate-fade-in {{ animation: fadeIn 0.4s ease-out forwards; }}
        .score-ring {{ transition: stroke-dashoffset 1s ease-in-out; }}
    </style>
    <script>
        tailwind.config = {{
            darkMode: 'class',
            theme: {{
                extend: {{
                    colors: {{
                        dark: {{ 950: '#020617', 900: '#0f172a', 800: '#1e293b', 700: '#334155' }},
                        brand: {{ 400: '#22d3ee', 500: '#06b6d4', 600: '#0891b2' }}
                    }}
                }}
            }}
        }}
    </script>
</head>
<body class="bg-dark-950 text-slate-200 min-h-screen selection:bg-brand-500 selection:text-white">

    <!-- MAIN DASHBOARD VIEW -->
    <div id="dashboard-view" class="max-w-7xl mx-auto p-6 animate-fade-in">
        <header class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 pb-6 border-b border-slate-800">
            <div>
                <h1 class="text-3xl md:text-4xl font-bold bg-gradient-to-r from-brand-400 to-purple-500 bg-clip-text text-transparent glow-text">
                    SEAR Enterprise Dashboard
                </h1>
                <p class="text-slate-400 mt-1 flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                    {site_name} &bull; {len(pages_data)} Pages Analyzed
                </p>
            </div>
            <button onclick="window.print()" class="mt-4 md:mt-0 px-4 py-2 glass rounded-lg text-sm font-medium hover:bg-slate-700 transition-colors flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                Export PDF
            </button>
        </header>

        <!-- KPI Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div class="glass rounded-2xl p-5 border-l-4 border-brand-400">
                <div class="text-slate-400 text-xs font-semibold uppercase tracking-wider mb-1">Average Score</div>
                <div class="text-4xl font-bold text-white">{avg_score}<span class="text-lg text-slate-500">/100</span></div>
            </div>
            <div class="glass rounded-2xl p-5 border-l-4 border-rose-500">
                <div class="text-slate-400 text-xs font-semibold uppercase tracking-wider mb-1">Critical Issues</div>
                <div class="text-4xl font-bold text-rose-400">{total_critical}</div>
            </div>
            <div class="glass rounded-2xl p-5 border-l-4 border-amber-500">
                <div class="text-slate-400 text-xs font-semibold uppercase tracking-wider mb-1">Total Issues</div>
                <div class="text-4xl font-bold text-amber-400">{sum(len(p['issues']) for p in pages_data)}</div>
            </div>
            <div class="glass rounded-2xl p-5 border-l-4 border-emerald-500">
                <div class="text-slate-400 text-xs font-semibold uppercase tracking-wider mb-1">Total Words</div>
                <div class="text-4xl font-bold text-emerald-400">{total_words:,}</div>
            </div>
        </div>

        <!-- Charts Section -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div class="glass rounded-2xl p-6">
                <h3 class="text-lg font-semibold text-slate-100 mb-4 flex items-center gap-2">
                    <span class="w-1.5 h-1.5 rounded-full bg-brand-400"></span> Score Breakdown
                </h3>
                <div class="h-64"><canvas id="scoreChart"></canvas></div>
            </div>
            <div class="glass rounded-2xl p-6">
                <h3 class="text-lg font-semibold text-slate-100 mb-4 flex items-center gap-2">
                    <span class="w-1.5 h-1.5 rounded-full bg-rose-400"></span> Issues by Category
                </h3>
                <div class="h-64"><canvas id="issueChart"></canvas></div>
            </div>
        </div>

        <!-- Interactive Pages Table -->
        <div class="glass rounded-2xl p-6">
            <div class="flex flex-col md:flex-row justify-between items-center mb-6 gap-4">
                <h3 class="text-lg font-semibold text-slate-100">Page Analysis Details</h3>
                <div class="relative w-full md:w-64">
                    <input type="text" id="searchInput" placeholder="Search URL or Title..." 
                        class="w-full bg-dark-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-slate-200 focus:outline-none focus:border-brand-400 transition-colors">
                    <svg class="w-4 h-4 text-slate-500 absolute right-3 top-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                </div>
            </div>
            
            <div class="overflow-x-auto rounded-lg border border-slate-800">
                <table class="w-full text-sm text-left">
                    <thead class="bg-dark-900 text-slate-400 uppercase text-xs font-semibold">
                        <tr>
                            <th class="px-6 py-4">Page / Title</th>
                            <th class="px-6 py-4 text-center">Score</th>
                            <th class="px-6 py-4 text-center">Issues</th>
                            <th class="px-6 py-4 text-center">Words</th>
                            <th class="px-6 py-4 text-right">Action</th>
                        </tr>
                    </thead>
                    <tbody id="pagesTableBody" class="divide-y divide-slate-800">
                        <!-- Populated by JS -->
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- DETAIL VIEW (Hidden by default) -->
    <div id="detail-view" class="hidden max-w-7xl mx-auto p-6 animate-fade-in">
        <button onclick="showDashboard()" class="mb-6 flex items-center gap-2 text-slate-400 hover:text-brand-400 transition-colors text-sm font-medium">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
            Back to Dashboard
        </button>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Left Column: Page Info & Metrics -->
            <div class="lg:col-span-2 space-y-6">
                <div class="glass rounded-2xl p-6 border-l-4" id="detail-header-border">
                    <div class="flex justify-between items-start mb-4">
                        <div>
                            <h2 id="detail-title" class="text-xl font-bold text-white mb-1"></h2>
                            <a id="detail-url" href="#" target="_blank" class="text-brand-400 text-sm hover:underline mono break-all"></a>
                        </div>
                        <div class="text-center">
                            <div class="relative w-20 h-20">
                                <svg class="w-full h-full transform -rotate-90">
                                    <circle cx="40" cy="40" r="36" stroke="currentColor" stroke-width="8" fill="transparent" class="text-slate-800" />
                                    <circle id="detail-score-ring" cx="40" cy="40" r="36" stroke="currentColor" stroke-width="8" fill="transparent" stroke-dasharray="226" stroke-dashoffset="226" class="score-ring" />
                                </svg>
                                <div class="absolute inset-0 flex items-center justify-center">
                                    <span id="detail-score" class="text-2xl font-bold text-white"></span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-slate-700/50">
                        <div><div class="text-xs text-slate-500 uppercase">Words</div><div id="detail-words" class="text-lg font-semibold text-slate-200"></div></div>
                        <div><div class="text-xs text-slate-500 uppercase">H1 Tags</div><div id="detail-h1" class="text-lg font-semibold text-slate-200"></div></div>
                        <div><div class="text-xs text-slate-500 uppercase">Int. Links</div><div id="detail-int" class="text-lg font-semibold text-slate-200"></div></div>
                        <div><div class="text-xs text-slate-500 uppercase">Ext. Links</div><div id="detail-ext" class="text-lg font-semibold text-slate-200"></div></div>
                    </div>
                    <div class="mt-4">
                        <div class="text-xs text-slate-500 uppercase mb-1">Meta Description</div>
                        <p id="detail-meta" class="text-sm text-slate-300 italic"></p>
                    </div>
                </div>

                <!-- Issues List -->
                <div class="glass rounded-2xl p-6">
                    <h3 class="text-lg font-semibold text-slate-100 mb-4">Identified Issues</h3>
                    <div id="detail-issues" class="space-y-3 max-h-96 overflow-y-auto pr-2 scrollbar-hide">
                        <!-- Populated by JS -->
                    </div>
                </div>
            </div>

            <!-- Right Column: Competitors & AI Prompt -->
            <div class="space-y-6">
                <!-- Competitors -->
                <div class="glass rounded-2xl p-6">
                    <h3 class="text-lg font-semibold text-slate-100 mb-4 flex items-center gap-2">
                        <svg class="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
                        Top Competitors
                    </h3>
                    <div id="detail-competitors" class="space-y-3">
                        <!-- Populated by JS -->
                    </div>
                </div>

                <!-- AI Master Prompt -->
                <div class="glass rounded-2xl p-6 border border-brand-500/30 bg-brand-900/10">
                    <div class="flex justify-between items-center mb-3">
                        <h3 class="text-lg font-semibold text-brand-400 flex items-center gap-2">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                            AI Master Prompt
                        </h3>
                        <button onclick="copyPrompt()" class="text-xs bg-brand-600 hover:bg-brand-500 text-white px-3 py-1.5 rounded-md transition-colors flex items-center gap-1">
                            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
                            Copy
                        </button>
                    </div>
                    <pre id="detail-ai-prompt" class="mono text-xs text-slate-300 bg-dark-950 p-4 rounded-lg border border-slate-800 overflow-x-auto whitespace-pre-wrap max-h-96 overflow-y-auto scrollbar-hide"></pre>
                </div>
            </div>
        </div>
    </div>

    <script>
        const ALL_PAGES = {pages_json};
        const SCORES = {scores_json};
        const ISSUES = {issues_json};
        let currentPromptText = "";

        // --- Chart Initialization ---
        const chartColors = {{ grid: 'rgba(255,255,255,0.05)', text: '#94a3b8' }};
        
        new Chart(document.getElementById('scoreChart'), {{
            type: 'radar',
            data: {{
                labels: Object.keys(SCORES),
                datasets: [{{ 
                    label: 'Average Score', 
                    data: Object.values(SCORES),
                    borderColor: '#22d3ee', 
                    backgroundColor: 'rgba(34,211,238,0.15)',
                    pointBackgroundColor: '#22d3ee',
                    borderWidth: 2
                }}]
            }},
            options: {{ 
                responsive: true, maintainAspectRatio: false,
                scales: {{ r: {{ min: 0, max: 100, ticks: {{ color: chartColors.text, backdropColor: 'transparent' }}, grid: {{ color: chartColors.grid }}, pointLabels: {{ color: '#cbd5e1', font: {{ size: 11 }} }} }} }},
                plugins: {{ legend: {{ display: false }} }} 
            }}
        }});

        new Chart(document.getElementById('issueChart'), {{
            type: 'bar',
            data: {{
                labels: Object.keys(ISSUES),
                datasets: [{{ 
                    label: 'Count', 
                    data: Object.values(ISSUES),
                    backgroundColor: ['#f43f5e', '#f59e0b', '#3b82f6', '#8b5cf6', '#10b981'],
                    borderRadius: 4
                }}]
            }},
            options: {{ 
                responsive: true, maintainAspectRatio: false,
                scales: {{ y: {{ ticks: {{ color: chartColors.text }}, grid: {{ color: chartColors.grid }} }}, x: {{ ticks: {{ color: chartColors.text, font: {{ size: 10 }} }}, grid: {{ display: false }} }} }},
                plugins: {{ legend: {{ display: false }} }} 
            }}
        }});

        // --- Table Rendering & Search ---
        function renderTable(data) {{
            const tbody = document.getElementById('pagesTableBody');
            tbody.innerHTML = '';
            data.forEach(p => {{
                const scoreColor = p.score >= 80 ? 'text-emerald-400' : p.score >= 50 ? 'text-amber-400' : 'text-rose-400';
                const scoreBg = p.score >= 80 ? 'bg-emerald-400/10' : p.score >= 50 ? 'bg-amber-400/10' : 'bg-rose-400/10';
                
                const row = document.createElement('tr');
                row.className = 'hover:bg-slate-800/50 transition-colors cursor-pointer group';
                row.onclick = () => showDetail(p.url);
                row.innerHTML = `
                    <td class="px-6 py-4">
                        <div class="font-medium text-slate-200 group-hover:text-brand-400 transition-colors truncate max-w-xs" title="${{p.title}}">${{p.title || 'No Title'}}</div>
                        <div class="text-xs text-slate-500 mono truncate max-w-xs">${{p.url}}</div>
                    </td>
                    <td class="px-6 py-4 text-center">
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${{scoreBg}} ${{scoreColor}}">${{p.score}}</span>
                    </td>
                    <td class="px-6 py-4 text-center text-slate-300">${{p.issues.length}}</td>
                    <td class="px-6 py-4 text-center text-slate-300">${{p.word_count.toLocaleString()}}</td>
                    <td class="px-6 py-4 text-right">
                        <button class="text-slate-500 hover:text-brand-400 transition-colors">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                        </button>
                    </td>
                `;
                tbody.appendChild(row);
            }});
        }}

        document.getElementById('searchInput').addEventListener('input', (e) => {{
            const term = e.target.value.toLowerCase();
            const filtered = ALL_PAGES.filter(p => p.url.toLowerCase().includes(term) || (p.title && p.title.toLowerCase().includes(term)));
            renderTable(filtered);
        }});

        // --- Detail View Logic ---
        function showDetail(url) {{
            const page = ALL_PAGES.find(p => p.url === url);
            if (!page) return;

            document.getElementById('dashboard-view').classList.add('hidden');
            document.getElementById('detail-view').classList.remove('hidden');
            window.scrollTo(0, 0);

            document.getElementById('detail-title').textContent = page.title || 'No Title';
            document.getElementById('detail-url').textContent = page.url;
            document.getElementById('detail-url').href = page.url;
            document.getElementById('detail-words').textContent = page.word_count.toLocaleString();
            document.getElementById('detail-h1').textContent = page.h1.length > 0 ? page.h1.join(', ') : 'None';
            document.getElementById('detail-int').textContent = page.internal_links;
            document.getElementById('detail-ext').textContent = page.external_links;
            document.getElementById('detail-meta').textContent = page.meta_desc || 'No meta description';

            const score = page.score;
            document.getElementById('detail-score').textContent = score;
            const offset = 226 - (226 * score / 100);
            const ring = document.getElementById('detail-score-ring');
            ring.style.strokeDashoffset = offset;
            
            const headerBorder = document.getElementById('detail-header-border');
            headerBorder.className = `glass rounded-2xl p-6 border-l-4 ${{score >= 80 ? 'border-emerald-500' : score >= 50 ? 'border-amber-500' : 'border-rose-500'}}`;
            ring.className = `score-ring ${{score >= 80 ? 'text-emerald-400' : score >= 50 ? 'text-amber-400' : 'text-rose-400'}}`;

            const issuesContainer = document.getElementById('detail-issues');
            issuesContainer.innerHTML = '';
            if (page.issues.length === 0) {{
                issuesContainer.innerHTML = '<div class="text-emerald-400 text-sm flex items-center gap-2"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg> No issues found. Great job!</div>';
            }} else {{
                page.issues.forEach(issue => {{
                    const color = issue.severity === 'Critical' ? 'border-rose-500/50 bg-rose-500/10 text-rose-300' : 
                                  issue.severity === 'Warning' ? 'border-amber-500/50 bg-amber-500/10 text-amber-300' : 'border-blue-500/50 bg-blue-500/10 text-blue-300';
                    const icon = issue.severity === 'Critical' ? '🔴' : issue.severity === 'Warning' ? '🟡' : '🔵';
                    
                    issuesContainer.innerHTML += `
                        <div class="p-3 rounded-lg border ${{color}} text-sm">
                            <div class="font-semibold mb-1 flex items-center gap-2">${{icon}} [${{issue.category}}] ${{issue.severity}}</div>
                            <div class="text-slate-300 leading-relaxed">${{issue.message}}</div>
                        </div>
                    `;
                }});
            }}

            const compContainer = document.getElementById('detail-competitors');
            compContainer.innerHTML = '';
            if (page.competitors && page.competitors.length > 0) {{
                page.competitors.forEach(c => {{
                    compContainer.innerHTML += `
                        <a href="${{c.url}}" target="_blank" class="block p-3 rounded-lg bg-dark-900 border border-slate-800 hover:border-brand-500/50 transition-colors group">
                            <div class="text-xs text-brand-400 font-semibold mb-1">Rank #${{c.rank}} Competitor</div>
                            <div class="text-sm text-slate-200 font-medium group-hover:text-brand-400 transition-colors truncate">${{c.title || c.url}}</div>
                            <div class="text-xs text-slate-500 mono truncate mt-1">${{c.url}}</div>
                        </a>
                    `;
                }});
            }} else {{
                compContainer.innerHTML = '<div class="text-slate-500 text-sm italic">No competitor data available for this page.</div>';
            }}

            currentPromptText = page.ai_prompt || "No AI prompt generated.";
            document.getElementById('detail-ai-prompt').textContent = currentPromptText;
        }}

        function showDashboard() {{
            document.getElementById('detail-view').classList.add('hidden');
            document.getElementById('dashboard-view').classList.remove('hidden');
            window.scrollTo(0, 0);
        }}

        function copyPrompt() {{
            navigator.clipboard.writeText(currentPromptText).then(() => {{
                const btn = event.currentTarget;
                const originalHTML = btn.innerHTML;
                btn.innerHTML = `<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg> Copied!`;
                btn.classList.add('bg-emerald-600');
                setTimeout(() => {{
                    btn.innerHTML = originalHTML;
                    btn.classList.remove('bg-emerald-600');
                }}, 2000);
            }});
        }}

        // Initial Render
        renderTable(ALL_PAGES);
    </script>
</body>
</html>"""
        return html