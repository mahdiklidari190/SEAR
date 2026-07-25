"""PDF Report Generator - Enhanced with Site-Wide Summary."""
# This module is responsible for generating professional, printable PDF reports 
# using the ReportLab library. It provides two main outputs:
# 1. A comprehensive, site-wide executive summary for stakeholders.
# 2. A detailed, page-specific technical report for developers and content creators.
from __future__ import annotations

import logging
from pathlib import Path
from datetime import datetime
from collections import Counter

# Import core data models containing the extracted SEO metrics and analysis results.
from models.page_data import PageData
from models.reports import CompetitorData

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """Generate professional PDF reports using ReportLab."""

    @staticmethod
    def generate_site_summary(
        site_name: str,
        pages: list[PageData],
        competitors: list[CompetitorData],
        output_path: Path
    ) -> bool:
        """
        Generate a comprehensive, site-wide PDF summary report.
        This is designed as an "Executive Summary" to provide high-level insights, 
        KPIs, and prioritized action items for stakeholders and management.
        
        Args:
            site_name: The name of the analyzed website.
            pages: A list of all analyzed PageData objects.
            competitors: A list of discovered CompetitorData objects.
            output_path: The destination Path for the generated PDF file.
            
        Returns:
            True if the PDF was generated successfully, False otherwise.
        """
        try:
            # Dynamically import ReportLab components to keep it as an optional dependency.
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib import colors
            from reportlab.lib.units import mm

            # Initialize the PDF document with A4 size and professional margins.
            doc = SimpleDocTemplate(
                str(output_path), 
                pagesize=A4, 
                rightMargin=20*mm, leftMargin=20*mm, 
                topMargin=20*mm, bottomMargin=20*mm
            )
            styles = getSampleStyleSheet()
            story = [] # The 'story' list holds all the elements (text, tables, spacers) to be rendered.

            # =========================================================================
            # 1. CUSTOM STYLES
            # Define consistent, branded typography for the report.
            # =========================================================================
            title_style = ParagraphStyle(
                'CustomTitle', parent=styles['Title'], 
                fontSize=20, textColor=colors.HexColor('#1a1a3e'), spaceAfter=10
            )
            subtitle_style = ParagraphStyle(
                'CustomSubtitle', parent=styles['Normal'], 
                fontSize=12, textColor=colors.grey, spaceAfter=20
            )
            heading_style = ParagraphStyle(
                'CustomHeading', parent=styles['Heading2'], 
                fontSize=14, textColor=colors.HexColor('#0891b2'), spaceBefore=15, spaceAfter=10
            )
            
            # =========================================================================
            # 2. HEADER
            # =========================================================================
            story.append(Paragraph(f"Enterprise SEO Analysis Report", title_style))
            story.append(Paragraph(
                f"Target: {site_name} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                subtitle_style
            ))
            story.append(Spacer(1, 10 * mm))

            if not pages:
                story.append(Paragraph("No data available for analysis.", styles['Normal']))
                doc.build(story)
                return True

            # =========================================================================
            # 3. KPI CALCULATIONS & TABLE
            # =========================================================================
            total_pages = len(pages)
            avg_score = sum(p.overall_score for p in pages) // total_pages
            total_issues = sum(len(p.issues) for p in pages)
            critical_issues = sum(1 for p in pages for i in p.issues if i.severity == "Critical")

            story.append(Paragraph("1. Executive Summary", heading_style))
            kpi_data = [
                ["Metric", "Value"],
                ["Total Pages Analyzed", str(total_pages)],
                ["Average SEO Score", f"{avg_score} / 100"],
                ["Total Issues Found", str(total_issues)],
                ["Critical Issues", str(critical_issues)]
            ]
            t_kpi = Table(kpi_data, colWidths=[80 * mm, 60 * mm])
            t_kpi.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a3e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(t_kpi)
            story.append(Spacer(1, 10 * mm))

            # =========================================================================
            # 4. TOP COMPETITORS
            # =========================================================================
            story.append(Paragraph("2. Top Identified Competitors", heading_style))
            if competitors:
                comp_data = [["Rank", "Competitor URL", "Title"]]
                # Limit to the top 5 unique competitors to keep the summary concise.
                for c in competitors[:5]: 
                    comp_data.append([str(c.rank), c.url[:50], c.title[:40] if c.title else "No Title"])
                
                t_comp = Table(comp_data, colWidths=[20 * mm, 70 * mm, 50 * mm])
                t_comp.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0891b2')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                story.append(t_comp)
            else:
                story.append(Paragraph("No competitor data was captured during the analysis.", styles['Normal']))
            story.append(Spacer(1, 10 * mm))

            # =========================================================================
            # 5. ISSUE CATEGORIES AGGREGATION
            # =========================================================================
            story.append(Paragraph("3. Most Frequent Issue Categories", heading_style))
            issue_counts = Counter()
            for p in pages:
                for issue in p.issues:
                    # Group by both severity and category for better prioritization (e.g., "Critical - Metadata").
                    issue_counts[f"{issue.severity} - {issue.category}"] += 1
            
            if issue_counts:
                top_issues = issue_counts.most_common(10)
                issue_data = [["Issue Category & Severity", "Occurrences"]] + [[k, str(v)] for k, v in top_issues]
                t_issues = Table(issue_data, colWidths=[100 * mm, 40 * mm])
                t_issues.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a3e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                ]))
                story.append(t_issues)
            story.append(Spacer(1, 10 * mm))

            # =========================================================================
            # 6. WORST PERFORMING PAGES
            # Highlight the pages that need immediate attention based on lowest scores.
            # =========================================================================
            story.append(Paragraph("4. Pages Requiring Immediate Attention (Lowest Scores)", heading_style))
            sorted_pages = sorted(pages, key=lambda x: x.overall_score)
            worst_pages_data = [["Score", "URL", "Critical Issues"]]
            for p in sorted_pages[:5]:
                crit_count = sum(1 for i in p.issues if i.severity == "Critical")
                worst_pages_data.append([str(p.overall_score), p.url[:60], str(crit_count)])
            
            t_worst = Table(worst_pages_data, colWidths=[20 * mm, 90 * mm, 30 * mm])
            t_worst.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')), # Red background for urgency
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ]))
            story.append(t_worst)

            # =========================================================================
            # 7. BUILD PDF
            # =========================================================================
            doc.build(story)
            logger.info(f"Site-wide PDF summary generated successfully: {output_path}")
            return True

        except ImportError:
            logger.warning("ReportLab not installed. PDF generation skipped. Run: pip install reportlab")
            return False
        except Exception as e:
            logger.error(f"Site-wide PDF generation failed: {e}")
            return False


    @staticmethod
    def generate(page: PageData, keywords: str, output_path: Path) -> bool:
        """
        Generate a detailed PDF report for a SINGLE page.
        This is designed as a "Technical Detail" view for developers and content creators 
        to see specific, actionable fixes for a particular URL.
        
        Args:
            page: The specific PageData object to report on.
            keywords: The target keywords analyzed for this page.
            output_path: The destination Path for the generated PDF file.
            
        Returns:
            True if the PDF was generated successfully, False otherwise.
        """
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib import colors
            from reportlab.lib.units import mm

            doc = SimpleDocTemplate(str(output_path), pagesize=A4)
            styles = getSampleStyleSheet()
            story = []

            # =========================================================================
            # 1. HEADER & BASIC METRICS
            # =========================================================================
            title_style = ParagraphStyle(
                'CustomTitle', parent=styles['Title'], 
                fontSize=16, textColor=colors.HexColor('#1a1a3e')
            )
            story.append(Paragraph(f"SEO Report: {page.url[:60]}", title_style))
            story.append(Spacer(1, 10 * mm))

            story.append(Paragraph(f"Overall Score: {page.overall_score}/100", styles['Heading2']))
            story.append(Paragraph(f"Target Keywords: {keywords}", styles['Normal']))
            story.append(Spacer(1, 5 * mm))

            # =========================================================================
            # 2. CATEGORY SCORES TABLE
            # =========================================================================
            if hasattr(page, 'scores') and page.scores:
                score_data = [["Category", "Score"]] + [[k, str(v)] for k, v in page.scores.items()]
                t = Table(score_data, colWidths=[100 * mm, 40 * mm])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a3e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                ]))
                story.append(t)
                story.append(Spacer(1, 10 * mm))

            # =========================================================================
            # 3. DETAILED ISSUES LIST
            # =========================================================================
            story.append(Paragraph("Identified Issues", styles['Heading2']))
            # Limit to the first 20 issues to prevent the PDF from becoming excessively long.
            for issue in page.issues[:20]: 
                # Color-code the severity badge for quick visual scanning.
                severity_color = colors.red if issue.severity == "Critical" else (colors.orange if issue.severity == "Warning" else colors.blue)
                
                story.append(Paragraph(
                    f"<font color='{severity_color.hexval()}'>[{issue.severity}]</font> <b>{issue.category}</b>: {issue.problem}",
                    styles['Normal']
                ))
                story.append(Paragraph(f"  → <i>Solution:</i> {issue.solution}", styles['Normal']))
                story.append(Spacer(1, 3 * mm))

            # =========================================================================
            # 4. BUILD PDF
            # =========================================================================
            doc.build(story)
            return True

        except ImportError:
            logger.warning("ReportLab not installed. PDF generation skipped.")
            return False
        except Exception as e:
            logger.error(f"Single-page PDF generation failed: {e}")
            return False