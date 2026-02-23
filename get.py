# get.py

import json, os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from rules import apply_rules  # rules.py must have apply_rules function

MSC_FILE = "msc.json"
DAYS = ["Mon","Tue","Wed","Thu","Fri","Sat"]
PERIODS_PER_DAY = 8
DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")


def generate_timetable_pdfs():
    # Load data
    if not os.path.exists(MSC_FILE):
        return "msc.json not found!"
    with open(MSC_FILE,"r") as f:
        msc_data = json.load(f)

    # Build timetables
    classes = set()
    for t_info in msc_data.values():
        classes.update(t_info.get("classes",{}).keys())
    timetable = {}
    teacher_avail = {}
    for cls in classes:
        timetable[cls] = [[None]*PERIODS_PER_DAY for _ in range(len(DAYS))]
    for teacher in msc_data.keys():
        teacher_avail[teacher] = [[True]*PERIODS_PER_DAY for _ in range(len(DAYS))]

    # Collect subjects per class
    class_subjects = {cls: [] for cls in classes}
    for teacher, info in sorted(msc_data.items()):
        sub = info["subject"]
        for cls, periods in sorted(info["classes"].items()):
            class_subjects[cls].append((sub, teacher, periods))

    # Assign subjects evenly
    for cls, subs in class_subjects.items():
        for sub, teacher, periods in subs:
            placed = 0
            day_idx, period_idx = 0, 0
            while placed < periods:
                if timetable[cls][day_idx][period_idx] is None and teacher_avail[teacher][day_idx][period_idx]:
                    timetable[cls][day_idx][period_idx] = {"subject": sub, "teacher": teacher}
                    teacher_avail[teacher][day_idx][period_idx] = False
                    placed += 1
                period_idx += 1
                if period_idx >= PERIODS_PER_DAY:
                    period_idx = 0
                    day_idx += 1
                    if day_idx >= len(DAYS):
                        day_idx = 0

    # Apply rules from rules.py
    timetable = apply_rules(timetable, msc_data)

    # Export all classes in a single PDF
    pdf_path = os.path.join(DOWNLOADS, "All_Classes_Timetable.pdf")
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    content = []

    # Paragraph style for cell: subject on top, teacher below
    cell_style = ParagraphStyle(
        "CellStyle",
        fontSize=8,
        alignment=1,  # center horizontally
        leading=10,
    )

    col_widths = [1.5*cm] + [3*cm]*len(DAYS)  # first column narrower, day columns wider

    for cls, table_data in timetable.items():
        title = Paragraph(f"Class {cls} Timetable", styles["Title"])
        content.append(title)
        content.append(Spacer(1, 12))

        # Table header
        data = [["Period"] + DAYS]

        for period in range(PERIODS_PER_DAY):
            row = [str(period+1)]
            for day in range(len(DAYS)):
                cell = table_data[day][period]
                if cell:
                    # Use Paragraph with subject on top, teacher below
                    subj = cell["subject"]
                    teach = cell["teacher"]
                    p = Paragraph(f"<b>{subj}</b><br/>{teach}", cell_style)
                    row.append(p)
                else:
                    row.append("")
            data.append(row)

        tbl = Table(data, colWidths=col_widths, repeatRows=1)
        tbl.setStyle(TableStyle([
            ("GRID",(0,0),(-1,-1),0.5,colors.black),
            ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
            ("ALIGN",(0,0),(-1,-1),"CENTER"),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("FONTSIZE",(0,0),(-1,-1),8),
        ]))
        content.append(tbl)
        content.append(PageBreak())

    doc.build(content)
    return f"All class timetables exported to {pdf_path}"
