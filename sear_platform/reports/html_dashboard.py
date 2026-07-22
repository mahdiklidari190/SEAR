"""HTML Dashboard Generator with TailwindCSS and Chart.js."""
from __future__ import annotations

import json
from pathlib import Path

from models.page_data import PageData
from models.reports import CompetitorData
from models.integrations import SearchConsoleData, LinkGraphData


class HTMLDashboardGenerator:
    """Generate a modern HTML dashboard report."""

    @staticmethod
    def generate(
        pages: list[PageData],
        competitors: list[CompetitorData],
        site_name: str,
        search_console: SearchConsoleData = None,
        link_graph: LinkGraphData = None,
    ) -> str:
        sc = search_console or SearchConsoleData()
        lg = link_graph or LinkGraphData()

        avg_score = sum(p.overall_score for p in pages) // max(len(pages), 1)
        total_issues = sum(len(p.issues) for p in pages)
        critical_count = sum(1 for p in pages for i in p.issues if i.severity == "Critical")

        # Score distribution for chart
        score_categories = {}
        if pages:
            for key in pages[0].scores:
                score_categories[key] = sum(p.scores.get(key, 0) for p in pages) // len(pages)

        # Issues by category
        issue_cats: dict[str, int] = {}
        for p in pages:
            for i in p.issues:
                issue_cats[i.category] = issue_cats.get(i.category, 0) + 1

        pages_json = json.dumps([{
            "url": p.url,
            "score": p.overall_score,
            "title": p.title[:60],
            "issues": len(p.issues),
            "words": p.word_count,
        } for p in pages[:100]], ensure_ascii=False)

        scores_json = json.dumps(score_categories)
        issues_json = json.dumps(issue_cats)

        html = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO Dashboard - {site_name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .glass {{ background: rgba(255,255,255,0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); }}
        .progress-ring {{ transition: stroke-dashoffset 0.5s ease; }}
        @keyframes fadeIn {{ from {{ opacity:0; transform:translateY(20px); }} to {{ opacity:1; transform:translateY(0); }} }}
        .card {{ animation: fadeIn 0.5s ease forwards; }}
        .gauge {{ position: relative; width: 120px; height: 120px; }}
    </style>
    <script>
        tailwind.config = {{ darkMode: 'class', theme: {{ extend: {{ colors: {{ dark: {{ 900: '#0f0f23', 800: '#1a1a3e', 700: '#252552' }} }} }} }} }}
    </script>
</head>
<body class="bg-dark-900 text-gray-100 min-h-screen p-6">
    <div class="max-w-7xl mx-auto">
        <!-- Header -->
        <div class="text-center mb-8 card">
            <h1 class="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent">
                 SEAR Enterprise SEO Dashboard
            </h1>
            <p class="text-gray-400 mt-2">{site_name} | {len(pages)} pages analyzed</p>
        </div>

        <!-- Score Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div class="glass rounded-xl p-6 card text-center">
                <div class="text-3xl font-bold text-cyan-400">{avg_score}/100</div>
                <div class="text-sm text-gray-400">Average Score</div>
            </div>
            <div class="glass rounded-xl p-6 card text-center">
                <div class="text-3xl font-bold text-red-400">{critical_count}</div>
                <div class="text-sm text-gray-400">Critical Issues</div>
            </div>
            <div class="glass rounded-xl p-6 card text-center">
                <div class="text-3xl font-bold text-yellow-400">{total_issues}</div>
                <div class="text-sm text-gray-400">Total Issues</div>
            </div>
            <div class="glass rounded-xl p-6 card text-center">
                <div class="text-3xl font-bold text-green-400">{len(pages)}</div>
                <div class="text-sm text-gray-400">Pages Analyzed</div>
            </div>
        </div>

        <!-- Charts -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div class="glass rounded-xl p-6 card">
                <h3 class="text-lg font-semibold mb-4">Score Breakdown</h3>
                <canvas id="scoreChart"></canvas>
            </div>
            <div class="glass rounded-xl p-6 card">
                <h3 class="text-lg font-semibold mb-4">Issues by Category</h3>
                <canvas id="issueChart"></canvas>
            </div>
        </div>

        <!-- Pages Table -->
        <div class="glass rounded-xl p-6 card mb-8">
            <h3 class="text-lg font-semibold mb-4">Page Scores</h3>
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead><tr class="text-left text-gray-400 border-b border-gray-700">
                        <th class="p-2">URL</th><th class="p-2">Score</th><th class="p-2">Issues</th><th class="p-2">Words</th>
                    </tr></thead>
                    <tbody id="pagesTable"></tbody>
                </table>
            </div>
        </div>

                <!-- Competitors -->
        <div class="glass rounded-xl p-6 card">
            <h3 class="text-lg font-semibold mb-4">Competitors</h3>
            {"".join([f'<div class="mb-2 text-sm text-gray-300">#{c.rank} <a href="{c.url}" class="text-cyan-400 hover:underline">{c.url[:60]}</a> - {c.title[:50]}</div>' for c in competitors]) or '<p class="text-gray-500">No competitor data</p>'}
        </div>
    </div>

    <script>
        const pages = {pages_json};
        const scores = {scores_json};
        const issues = {issues_json};

        // Score Radar Chart
        new Chart(document.getElementById('scoreChart'), {{
            type: 'radar',
            data: {{
                labels: Object.keys(scores),
                datasets: [{{ label: 'Score', data: Object.values(scores),
                    borderColor: '#22d3ee', backgroundColor: 'rgba(34,211,238,0.1)' }}]
            }},
            options: {{ scales: {{ r: {{ min: 0, max: 100, ticks: {{ color: '#9ca3af' }}, grid: {{ color: '#374151' }} }} }},
                plugins: {{ legend: {{ labels: {{ color: '#9ca3af' }} }} }} }}
        }});

        // Issues Bar Chart
        new Chart(document.getElementById('issueChart'), {{
            type: 'bar',
            data: {{
                labels: Object.keys(issues),
                datasets: [{{ label: 'Issues', data: Object.values(issues),
                    backgroundColor: ['#ef4444','#f59e0b','#22d3ee','#8b5cf6','#10b981','#ec4899','#6366f1'] }}]
            }},
            options: {{ scales: {{ y: {{ ticks: {{ color: '#9ca3af' }}, grid: {{ color: '#374151' }} }},
                x: {{ ticks: {{ color: '#9ca3af' }}, grid: {{ color: '#374151' }} }} }},
                plugins: {{ legend: {{ labels: {{ color: '#9ca3af' }} }} }} }}
        }});

        // Pages Table
        const tbody = document.getElementById('pagesTable');
        pages.forEach(p => {{
            const color = p.score >= 80 ? 'text-green-400' : p.score >= 50 ? 'text-yellow-400' : 'text-red-400';
            tbody.innerHTML += `<tr class="border-b border-gray-800">
                <td class="p-2 max-w-xs truncate">${{p.title || p.url}}</td>
                <td class="p-2 ${{color}} font-bold">${{p.score}}</td>
                <td class="p-2">${{p.issues}}</td>
                <td class="p-2">${{p.words}}</td>
            </tr>`;
        }});
    </script>
</body>
</html>"""
        return html