# get.py

import json, os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

from rules import apply_rules, sort_classes

MSC_FILE = "msc.json"
DAYS = ["Mon","Tue","Wed","Thu","Fri","Sat"]
PERIODS_PER_DAY = 8
TOTAL_SLOTS = len(DAYS) * PERIODS_PER_DAY
DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")


def generate_timetable_pdfs():

    if not os.path.exists(MSC_FILE):
        return "msc.json not found!"

    with open(MSC_FILE,"r") as f:
        msc_data = json.load(f)

    # -------- Collect Classes --------
    classes = set()
    for t_info in msc_data.values():
        classes.update(t_info.get("classes",{}).keys())

    classes = sort_classes(list(classes))

    # -------- Initialize Timetable --------
    timetable = {cls: [[None]*PERIODS_PER_DAY for _ in range(len(DAYS))] for cls in classes}
    teacher_avail = {
        teacher: [[True]*PERIODS_PER_DAY for _ in range(len(DAYS))]
        for teacher in msc_data.keys()
    }

    # -------- Apply Fixed Rules --------
    temp_tt = {cls: [[None]*PERIODS_PER_DAY for _ in range(len(DAYS))] for cls in classes}
    temp_tt = apply_rules(temp_tt, msc_data)

    for cls in classes:
        for d in range(len(DAYS)):
            for p in range(PERIODS_PER_DAY):
                if temp_tt[cls][d][p] is not None:
                    timetable[cls][d][p] = temp_tt[cls][d][p]

    # -------- Build Subject Pool --------
    class_subjects = {}

    for cls in classes:
        subject_pool = []

        for teacher, info in msc_data.items():
            subject = info["subject"]
            if cls in info["classes"]:
                count = info["classes"][cls]
                subject_pool.append({
                    "subject": subject,
                    "teacher": teacher,
                    "remaining": count
                })

        class_subjects[cls] = subject_pool

    # -------- Adaptive Smart Allocation --------
    for cls in classes:

        subjects = class_subjects[cls]

        for day in range(len(DAYS)):
            for period in range(PERIODS_PER_DAY):

                if timetable[cls][day][period] is not None:
                    continue

                # Sort subjects by highest remaining demand
                subjects_sorted = sorted(
                    subjects,
                    key=lambda x: x["remaining"],
                    reverse=True
                )

                placed = False

                for subj_data in subjects_sorted:

                    if subj_data["remaining"] <= 0:
                        continue

                    teacher = subj_data["teacher"]

                    if teacher_avail[teacher][day][period]:

                        timetable[cls][day][period] = {
                            "subject": subj_data["subject"],
                            "teacher": teacher
                        }

                        teacher_avail[teacher][day][period] = False
                        subj_data["remaining"] -= 1
                        placed = True
                        break

                # If nothing fits, leave empty (soft constraint)
                if not placed:
                    pass

    # -------- Warning Report --------
    warnings = []

    for cls in classes:
        empty_slots = 0

        for d in range(len(DAYS)):
            for p in range(PERIODS_PER_DAY):
                if timetable[cls][d][p] is None:
                    empty_slots += 1

        if empty_slots > 0:
            warnings.append(f"{cls}: {empty_slots} empty slots")

        for subj in class_subjects[cls]:
            if subj["remaining"] > 0:
                warnings.append(
                    f"{cls}: {subj['remaining']} periods of {subj['subject']} unallocated"
                )

    if warnings:
        print("\n⚠ TIMETABLE WARNINGS:")
        for w in warnings:
            print(" -", w)

    # -------- Export PDF (CLASS-WISE ORDERED) --------
    pdf_path = os.path.join(DOWNLOADS, "All_Classes_Timetable.pdf")
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    content = []

    cell_style = ParagraphStyle(
        "CellStyle",
        fontSize=8,
        alignment=1,
        leading=10,
    )

    col_widths = [2*cm] + [2.5*cm]*PERIODS_PER_DAY

    for cls in classes:

        table_data = timetable[cls]

        title = Paragraph(f"Class {cls} Timetable", styles["Title"])
        content.append(title)
        content.append(Spacer(1, 12))

        header = ["Day"] + [f"P{p+1}" for p in range(PERIODS_PER_DAY)]
        data = [header]

        for day_index, day_name in enumerate(DAYS):
            row = [day_name]
            for period in range(PERIODS_PER_DAY):
                cell = table_data[day_index][period]
                if cell:
                    p = Paragraph(
                        f"<b>{cell['subject']}</b><br/>{cell['teacher']}",
                        cell_style
                    )
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
        ]))

        content.append(tbl)
        content.append(PageBreak())

    doc.build(content)

    return f"Timetable generated with adaptive fitting.\nExported to {pdf_path}"
