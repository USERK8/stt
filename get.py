# get.py

import json, os, random, copy
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from rules import apply_rules, sort_classes

MSC_FILE = "msc.json"
DAYS = ["Mon","Tue","Wed","Thu","Fri","Sat"]
PERIODS_PER_DAY = 8
DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")
BACKEND_FILE = os.path.join(os.path.dirname(__file__), "backend_details.json")

def generate_timetable_pdfs():
    if not os.path.exists(MSC_FILE):
        return "msc.json not found!"

    with open(MSC_FILE, "r") as f:
        msc_data = json.load(f)

    # Collect all classes
    classes = set()
    for t_info in msc_data.values():
        for cls in t_info.get("classes", {}).keys():
            classes.add(cls)

    classes = sort_classes(list(classes))
    best_timetable = None
    best_empty = 999999

    for attempt in range(40):
        # Initialize timetable
        timetable = {cls: [[None]*PERIODS_PER_DAY for _ in DAYS] for cls in classes}
        teacher_avail_global = {teacher: [[True]*PERIODS_PER_DAY for _ in DAYS] for teacher in msc_data.keys()}

        # Apply rules from rules.py
        timetable = apply_rules(timetable, msc_data)

        # Build tasks from MSC
        tasks = []
        for teacher, info in msc_data.items():
            subject = info["subject"]
            for cls, count in info["classes"].items():
                for _ in range(count):
                    tasks.append({"teacher": teacher, "class": cls, "subject": subject})

        random.shuffle(tasks)

        # Distribute tasks
        for task in tasks:
            cls = task["class"]
            teacher = task["teacher"]
            subject = task["subject"]

            days = list(range(len(DAYS)))
            random.shuffle(days)
            placed = False
            for day in days:
                count_today = sum(1 for p in range(PERIODS_PER_DAY)
                                  if timetable[cls][day][p] and timetable[cls][day][p]["subject"] == subject)
                if count_today >= 2:
                    continue
                for period in range(PERIODS_PER_DAY):
                    if timetable[cls][day][period] is None and teacher_avail_global[teacher][day][period]:
                        timetable[cls][day][period] = {"subject": subject, "teacher": teacher}
                        teacher_avail_global[teacher][day][period] = False
                        placed = True
                        break
                if placed: break

        # Fill empty cells
        for cls in classes:
            table = timetable[cls]
            if cls.startswith(("11","12")):
                allowed = [t["subject"] for t in msc_data.values() if cls in t.get("classes", {}) and t["subject"] not in ["PET","English"]]
            else:
                allowed = [t["subject"] for t in msc_data.values() if cls in t.get("classes", {}) and t["subject"] not in ["DL","ART","VE","PET"]]
            allowed = list(set(allowed))

            for day_idx, day in enumerate(table):
                daily_count = {}
                for p in range(PERIODS_PER_DAY):
                    cell = day[p]
                    if cell and cell["subject"] in allowed:
                        daily_count[cell["subject"]] = daily_count.get(cell["subject"], 0) + 1

                for period in range(PERIODS_PER_DAY):
                    if day[period] is None:
                        random.shuffle(allowed)
                        placed = False
                        for sub in allowed:
                            teacher = None
                            for tname, info in msc_data.items():
                                if info["subject"] == sub and cls in info.get("classes", {}):
                                    teacher = tname
                                    break
                            if not teacher:
                                continue
                            if teacher_avail_global[teacher][day_idx][period] and daily_count.get(sub,0) < 3:
                                day[period] = {"subject": sub, "teacher": teacher}
                                daily_count[sub] = daily_count.get(sub,0) + 1
                                teacher_avail_global[teacher][day_idx][period] = False
                                placed = True
                                break

        # Count empty slots
        empty_count = sum(
            1 for cls in classes for d in range(len(DAYS)) for p in range(PERIODS_PER_DAY)
            if timetable[cls][d][p] is None
        )
        if empty_count < best_empty:
            best_empty = empty_count
            best_timetable = copy.deepcopy(timetable)
        if best_empty == 0:
            break

    timetable = best_timetable

    # -----------------------------
    # Build backend details for teachers
    # -----------------------------
    backend_data = {}
    for teacher, info in msc_data.items():
        grid = [[None]*PERIODS_PER_DAY for _ in DAYS]
        for cls in timetable:
            for day_idx in range(len(DAYS)):
                for period_idx in range(PERIODS_PER_DAY):
                    cell = timetable[cls][day_idx][period_idx]
                    if cell and cell["teacher"] == teacher:
                        grid[day_idx][period_idx] = cls
        backend_data[teacher] = {
            "subject": info["subject"],
            "grid": grid
        }

    with open(BACKEND_FILE, "w") as f:
        json.dump(backend_data, f, indent=4)

    # -----------------------------
    # Generate timetable PDF
    # -----------------------------
    pdf_path = os.path.join(DOWNLOADS, "timetable.pdf")
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    content = []
    cell_style = ParagraphStyle("CellStyle", fontSize=8, alignment=1, leading=10)
    col_widths = [2*cm] + [2.5*cm]*PERIODS_PER_DAY

    for cls in classes:
        title = Paragraph(f"Class {cls} Timetable", styles["Title"])
        content.append(title)
        content.append(Spacer(1, 12))
        header = ["Day"] + [f"P{p+1}" for p in range(PERIODS_PER_DAY)]
        data = [header]

        for day_index, day_name in enumerate(DAYS):
            row = [day_name]
            for period in range(PERIODS_PER_DAY):
                cell = timetable[cls][day_index][period]
                if cell:
                    p = Paragraph(f"<b>{cell['subject']}</b><br/>{cell['teacher']}", cell_style)
                    row.append(p)
                else:
                    row.append("")
            data.append(row)

        tbl = Table(data, colWidths=col_widths, repeatRows=1)
        tbl.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 0.5, colors.black),
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE")
        ]))
        content.append(tbl)
        content.append(PageBreak())

    doc.build(content)
    return f"Timetable generated.\nEmpty slots: {best_empty}\nExported to {pdf_path}.\nBackend file saved as backend_details.json"
