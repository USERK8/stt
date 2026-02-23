# rules.py

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

def apply_rules(timetable, msc_data):
    """
    Apply school rules to the timetable:
    1. MPT on Wednesday first period for every class
    2. CCA on Friday first two periods for every class

    timetable: dict[class_name] -> list of 6 days x 8 periods
               cells = {"subject": str, "teacher": str} or None
    msc_data: loaded msc.json
    """

    for cls, table in timetable.items():
        # ---------------- Rule 1: MPT on Wednesday first period ----------------
        # day_idx=2 (Wed), period_idx=0
        table[2][0] = {"subject": "MPT", "teacher": "—"}

        # ---------------- Rule 2: CCA on Friday first two periods ----------------
        # day_idx=4 (Fri), period_idx=0 and 1
        table[4][0] = {"subject": "CCA", "teacher": "—"}
        table[4][1] = {"subject": "CCA", "teacher": "—"}

    return timetable
