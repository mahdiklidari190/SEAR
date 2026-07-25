# ==============================================================================
# REPORT GENERATION & EXPORT MODULES
# This package centralizes all output formatting capabilities for the SEO engine.
# It allows the system to transform raw analysis data into various standardized 
# formats, catering to different use cases ranging from automated data pipelines 
# to formal client deliverables.
# ==============================================================================

# The central orchestrator that manages the export workflow, routing the analysis 
# data to the appropriate format generator based on user or system requirements.
from .export_manager import ExportManager

# Generates plain text (.txt) reports. Ideal for simple, lightweight summaries, 
# system logs, or environments where rich formatting is not required.
from .txt_generator import TXTReportGenerator

# Generates structured JSON (.json) reports. This is the primary format for 
# programmatic consumption, API responses, and seamless frontend integration.
from .json_generator import JSONReportGenerator

# Generates Comma-Separated Values (.csv) files. Perfect for exporting tabular 
# data (like issue lists or keyword metrics) for further analysis in Excel or Google Sheets.
from .csv_generator import CSVReportGenerator

# Generates an interactive HTML (.html) dashboard. Provides a rich, visual, 
# and browser-native experience for exploring the SEO metrics and recommendations.
from .html_dashboard import HTMLDashboardGenerator

# Generates portable document format (.pdf) reports. Designed for creating formal, 
# highly polished, and printable deliverables to share directly with clients or stakeholders.
from .pdf_generator import PDFReportGenerator