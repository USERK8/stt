#rules.py

import random

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
PERIODS_PER_DAY = 8

# ---------------------------------------
# CLASS SORTING
# ---------------------------------------
def sort_classes(class_list):
    def sort_key(cls):
        num = ""
        sec = ""
        for ch in cls:
            if ch.isdigit():
                num += ch
            else:
                sec += ch
        try:
            return (int(num), sec)
        except:
            return (999, cls)
    return sorted(class_list, key=sort_key)


# ---------------------------------------
# APPLY SCHOOL RULES WITH BACKEND UPDATE
# ---------------------------------------
def apply_rules(timetable, msc_data, backend_data):

    actual_classes = list(timetable.keys())
    class_map = {cls.upper(): cls for cls in actual_classes}

    def exists(cls_name):
        return cls_name.upper() in class_map

    # ---------------------------------------
    # LAB TRACKERS
    # ---------------------------------------
    cs_lab = [[None]*PERIODS_PER_DAY for _ in DAYS]
    phychem_lab = [[None]*PERIODS_PER_DAY for _ in DAYS]
    bio_lab = [[None]*PERIODS_PER_DAY for _ in DAYS]

    cs_blocks = {cls:0 for cls in actual_classes}
    phychem_blocks = {cls:0 for cls in actual_classes}
    bio_blocks = {"11B":0,"12B":0}

    practical_days = {cls:set() for cls in actual_classes}
    bio_practical_days = {"11B": set(), "12B": set()}

    # ---------------------------------------
    # RULE 1 & 2: MPT & CCA
    # ---------------------------------------
    for cls in actual_classes:
        table = timetable[cls]
        table[2][0] = {"subject":"MPT","teacher":"—"}
        table[4][0] = {"subject":"CCA","teacher":"—"}
        table[4][1] = {"subject":"CCA","teacher":"—"}

    # ---------------------------------------
    # FIXED SYNC BLOCKS
    # ---------------------------------------
    SYNC_PAIRS = [
        ("11A", ["11B","11C"]),
        ("12A", ["12B","12C"])
    ]

    for main, others in SYNC_PAIRS:
        if not exists(main):
            continue
        for day in range(len(DAYS)):
            for period in range(PERIODS_PER_DAY):
                if timetable[class_map[main]][day][period] is None:
                    # MAIN CLASS
                    timetable[class_map[main]][day][period] = {
                        "subject": "Maths",
                        "teacher": "MATHS"
                    }
                    # OTHER CLASSES → COMBINED BLOCK
                    for cls in others:
                        if exists(cls):
                            timetable[class_map[cls]][day][period] = {
                                "subject": "Maths/Hindi/CS",
                                "teacher": "MATHS / KIRAN / SOJU"
                            }
                    break
            break

    # ---------------------------------------
    # PRACTICAL HELPERS
    # ---------------------------------------

    # Practicals must only start at these 0-indexed periods:
    # 0→[1,2], 2→[3,4], 4→[5,6], 6→[7,8]  (avoids crossing the break after period 4)
    ALLOWED_PRACTICAL_STARTS = {0, 2, 4, 6}

    def can_place_block(cls, day, period, lab):
        table = timetable[cls]
        if period not in ALLOWED_PRACTICAL_STARTS:
            return False
        if table[day][period] or table[day][period+1]:
            return False
        if day in practical_days[cls]:
            return False
        lab_tracker = cs_lab if lab=="CS" else phychem_lab
        if lab_tracker[day][period] or lab_tracker[day][period+1]:
            return False
        return True

    def place_block(cls,day,period,subject,lab):
        # Pick teacher(s) from msc_data if exists
        teacher_str = None
        for tname, info in msc_data.items():
            if info["subject"] == subject and cls in info.get("classes", {}):
                teacher_str = tname
                break

        if not teacher_str:
            # fallback to defaults
            if lab=="CS":
                teacher_str = "SOJU"
            elif subject=="Phy/Chem Practical":
                # assign correct multi-teachers based on class
                if cls in ["11A","12B"]:
                    teacher_str = "RAJANI & SAJIMON"
                elif cls in ["11B","12A"]:
                    teacher_str = "LIJI MATHEW & POOJA SIHAG"
                else:
                    teacher_str = "RAJANI & SAJIMON"
            elif subject=="Bio Practical":
                teacher_str = "BINDU C"

        # assign to timetable
        timetable[cls][day][period] = {"subject":subject,"teacher":teacher_str}
        timetable[cls][day][period+1] = {"subject":subject,"teacher":teacher_str}

        # mark lab slots
        lab_tracker = cs_lab if lab=="CS" else phychem_lab
        if lab=="CS":
            cs_lab[day][period] = cls
            cs_lab[day][period+1] = cls
            cs_blocks[cls] += 1
        elif subject=="Phy/Chem Practical":
            phychem_lab[day][period] = cls
            phychem_lab[day][period+1] = cls
            phychem_blocks[cls] += 1

        practical_days[cls].add(day)

        # --- handle multiple teachers correctly ---
        teachers = [t.strip() for t in teacher_str.split("&")]
        for t in teachers:
            if t in backend_data:
                backend_data[t]["grid"][day][period] = cls
                backend_data[t]["grid"][day][period+1] = cls

    # ---------------------------------------
    # BIO PRACTICAL HELPERS
    # ---------------------------------------
    def can_place_bio(cls, day, period):
        table = timetable[cls]
        if period not in ALLOWED_PRACTICAL_STARTS:
            return False
        if table[day][period] or table[day][period+1]:
            return False
        if day in bio_practical_days[cls]:
            return False
        if bio_lab[day][period] or bio_lab[day][period+1]:
            return False
        return True

    def place_bio(cls,day,period):
        teacher_str = None
        for tname, info in msc_data.items():
            if info["subject"]=="Bio Practical" and cls in info.get("classes",{}):
                teacher_str = tname
                break
        if not teacher_str:
            teacher_str = "BINDU C"

        timetable[cls][day][period] = {"subject":"Bio Practical","teacher":teacher_str}
        timetable[cls][day][period+1] = {"subject":"Bio Practical","teacher":teacher_str}

        bio_lab[day][period] = cls
        bio_lab[day][period+1] = cls
        bio_practical_days[cls].add(day)
        bio_blocks[cls] += 1

        teachers = [t.strip() for t in teacher_str.split("&")]
        for t in teachers:
            if t in backend_data:
                backend_data[t]["grid"][day][period] = cls
                backend_data[t]["grid"][day][period+1] = cls

    # ---------------------------------------
    # PLACE PRACTICALS
    # ---------------------------------------
    for cls in actual_classes:
        if cls.startswith(("11","12")):
            while cs_blocks[cls] < 2:
                placed=False
                for day in range(len(DAYS)):
                    for period in range(PERIODS_PER_DAY-1):
                        if can_place_block(cls,day,period,"CS"):
                            place_block(cls,day,period,"CS Practical","CS")
                            placed=True
                            break
                    if placed:
                        break
                if not placed:
                    break

    science_classes = ["11A","11B","12A","12B"]
    for cls in actual_classes:
        if cls in science_classes:
            while phychem_blocks[cls] < 4:
                placed=False
                for day in range(len(DAYS)):
                    for period in range(PERIODS_PER_DAY-1):
                        if can_place_block(cls,day,period,"PHY"):
                            place_block(cls,day,period,"Phy/Chem Practical","PHY")
                            placed=True
                            break
                    if placed:
                        break
                if not placed:
                    break

    for cls in ["11B","12B"]:
        if cls in actual_classes:
            while bio_blocks[cls] < 3:
                placed=False
                for day in range(len(DAYS)):
                    for period in range(PERIODS_PER_DAY-1):
                        if can_place_bio(cls,day,period):
                            place_bio(cls,day,period)
                            placed=True
                            break
                    if placed:
                        break
                if not placed:
                    break

    return timetable