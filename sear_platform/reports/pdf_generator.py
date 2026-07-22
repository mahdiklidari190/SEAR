"""PDF Report Generator."""
from __future__ import annotations

import logging
from pathlib import Path

from models.page_data import PageData

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """Generate PDF reports using ReportLab."""

    @staticmethod
    def generate(page: PageData, keywords: str, output_path: Path) -> bool:
        """Generate a PDF report for a single page."""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib import colors
            from reportlab.lib.units import mm

            doc = SimpleDocTemplate(str(output_path), pagesize=A4)
            styles = getSampleStyleSheet()
            story = []

            # Title
            title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=16)
            story.append(Paragraph(f"SEO Report: {page.url[:60]}", title_style))
            story.append(Spacer(1, 10 * mm))

            # Score
            story.append(Paragraph(f"Overall Score: {page.overall_score}/100", styles['Heading2']))
            story.append(Paragraph(f"Keywords: {keywords}", styles['Normal']))
            story.append(Spacer(1, 5 * mm))

            # Scores table
            score_data = [["Category", "Score"]] + [[k, str(v)] for k, v in page.scores.items()]
            t = Table(score_data, colWidths=[100 * mm, 40 * mm])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a3e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
            ]))
            story.append(t)
            story.append(Spacer(1, 5 * mm))

            # Issues
            story.append(Paragraph("Issues", styles['Heading2']))
            for issue in page.issues[:15]:
                story.append(Paragraph(
                    f"[{issue.severity}] {issue.category}: {issue.problem}",
                    styles['Normal']
                ))
                story.append(Paragraph(f"  → {issue.solution}", styles['Normal']))

            doc.build(story)
            return True

        except ImportError:
            logger.warning("ReportLab not installed. PDF generation skipped.")
            return False
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            return False