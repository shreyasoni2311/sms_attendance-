from datetime import date

from database import (
    get_students,
    get_attendance,
    save_attendance,
    get_attendance_count
)


# ==========================================================
# TODAY
# ==========================================================

def today():

    return str(date.today())


# ==========================================================
# LOAD ATTENDANCE
# ==========================================================

def load_attendance(attendance_date=None):

    if not attendance_date:
        attendance_date = today()

    return get_attendance(attendance_date)


# ==========================================================
# MARK ATTENDANCE
# ==========================================================

def mark_attendance(
    roll_no,
    attendance_date,
    status
):

    status = str(status).strip().title()

    if status not in ("Present", "Absent"):
        return False

    return save_attendance(
        roll_no,
        attendance_date,
        status
    )


# ==========================================================
# MARK ALL PRESENT
# ==========================================================

def mark_all_present(attendance_date):

    students = get_students()

    count = 0

    for student in students:

        roll_no = student[1]

        if save_attendance(
            roll_no,
            attendance_date,
            "Present"
        ):
            count += 1

    return count


# ==========================================================
# MARK ALL ABSENT
# ==========================================================

def mark_all_absent(attendance_date):

    students = get_students()

    count = 0

    for student in students:

        roll_no = student[1]

        if save_attendance(
            roll_no,
            attendance_date,
            "Absent"
        ):
            count += 1

    return count


# ==========================================================
# SUMMARY
# ==========================================================

def get_summary(attendance_date):

    return get_attendance_count(
        attendance_date
    )