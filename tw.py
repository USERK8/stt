# tw.py

import json
import os
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm

# Constants
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
PERIODS_PER_DAY = 8
DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")
BACKEND_FILE = os.path.join(os.path.dirname(__file__), "backend_details.json")

def generate_teacherwise_pdf():
    # Check if backend file exists
    if not os.path.exists(BACKEND_FILE):
        return "No backend details found! Please generate the class-wise timetable first."

    # Load backend data
    with open(BACKEND_FILE, "r") as f:
        backend_data = json.load(f)

    # Create PDF
    pdf_path = os.path.join(DOWNLOADS, "teacherwise_timetable.pdf")
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    content = []

    cell_style = ParagraphStyle("CellStyle", fontSize=8, alignment=1, leading=10)
    col_widths = [2*cm] + [2.5*cm]*PERIODS_PER_DAY  # Day + 8 periods

    for teacher, info in backend_data.items():
        # Teacher title
        title = Paragraph(f"Teacher: {teacher} ({info['subject']})", styles["Title"])
        content.append(title)
        content.append(Spacer(1, 12))

        # Table header
        header = ["Day"] + [f"P{p+1}" for p in range(PERIODS_PER_DAY)]
        table_data = [header]

        # Fill table with classes from grid
        grid = info.get("grid", [])
        for day_idx, day_name in enumerate(DAYS):
            row = [day_name]
            for period in range(PERIODS_PER_DAY):
                cls = None
                try:
                    cls = grid[day_idx][period]
                except IndexError:
                    cls = None
                row.append(cls if cls else "")
            table_data.append(row)

        # Create Table
        tbl = Table(table_data, colWidths=col_widths, repeatRows=1)
        tbl.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 0.5, colors.black),
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE")
        ]))

        content.append(tbl)
        content.append(PageBreak())

    # Build PDF
    doc.build(content)

    return f"Teacher-wise PDF generated successfully at:\n{pdf_path}"
