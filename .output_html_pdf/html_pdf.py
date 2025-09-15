from weasyprint import HTML
import os

# Get the directory of this script
base_dir = os.path.dirname(os.path.abspath(__file__))

# HTML files
html1 = os.path.join(base_dir, "weekly_report_assessment_report_14072025_21072025.html")
pdf1 = os.path.join(base_dir, "weekly_report_assessment_report_14072025_21072025.pdf")

html2 = os.path.join(base_dir, "weekly_report_video_report_05-09-2025_12-09-2025.html")
pdf2 = os.path.join(base_dir, "weekly_report_video_report_05-09-2025_12-09-2025.pdf")

# Convert
HTML(html1).write_pdf(pdf1)
HTML(html2).write_pdf(pdf2)
