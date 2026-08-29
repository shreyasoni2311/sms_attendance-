import sqlite3
import os

try:
    from kivy.app import App
except ImportError:
    App = None


# ==========================================================
# DATABASE PATH
# ==========================================================

def get_db_path():

    # Android / Kivy
    if App is not None:
        try:
            app = App.get_running_app()

            if app is not None:
                return os.path.join(
                    app.user_data_dir,
                    "attendance.db"
                )
        except Exception:
            pass

    # Desktop testing
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "attendance.db"
    )


# ==========================================================
# CONNECTION
# ==========================================================

def get_connection():

    db_path = get_db_path()

    folder = os.path.dirname(db_path)

    if folder:
        os.makedirs(folder, exist_ok=True)

    con = sqlite3.connect(db_path)

    return con


# ==========================================================
# CREATE TABLES
# ==========================================================

def create_tables():

    con = get_connection()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            parent_mobile TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            UNIQUE(roll_no, date)
        )
    """)

    con.commit()
    con.close()


# ==========================================================
# ADD STUDENT
# ==========================================================

def add_student(roll_no, name, parent_mobile=""):

    roll_no = str(roll_no).strip()
    name = str(name).strip()
    parent_mobile = str(parent_mobile).strip()

    if not roll_no or not name:
        return False, "Roll number and name are required."

    con = get_connection()

    try:

        con.execute("""
            INSERT INTO students
            (roll_no, name, parent_mobile)
            VALUES (?, ?, ?)
        """, (
            roll_no,
            name,
            parent_mobile
        ))

        con.commit()

        return True, "Student added successfully."

    except sqlite3.IntegrityError:

        return False, "Roll number already exists."

    except Exception as e:

        return False, str(e)

    finally:

        con.close()


# ==========================================================
# GET STUDENTS
# ==========================================================

def get_students():

    con = get_connection()

    try:

        rows = con.execute("""
            SELECT
                id,
                roll_no,
                name,
                parent_mobile
            FROM students
            ORDER BY roll_no
        """).fetchall()

        return rows

    finally:

        con.close()


# ==========================================================
# GET ONE STUDENT
# ==========================================================

def get_student_by_roll(roll_no):

    con = get_connection()

    try:

        row = con.execute("""
            SELECT
                id,
                roll_no,
                name,
                parent_mobile
            FROM students
            WHERE roll_no = ?
        """, (str(roll_no).strip(),)).fetchone()

        return row

    finally:

        con.close()


# ==========================================================
# DELETE STUDENT
# ==========================================================

def delete_student(student_id):

    con = get_connection()

    try:

        con.execute(
            "DELETE FROM students WHERE id = ?",
            (student_id,)
        )

        con.execute(
            "DELETE FROM attendance WHERE roll_no NOT IN "
            "(SELECT roll_no FROM students)"
        )

        con.commit()

        return True

    except Exception:

        return False

    finally:

        con.close()


# ==========================================================
# SAVE ATTENDANCE
# ==========================================================

def save_attendance(roll_no, attendance_date, status):

    con = get_connection()

    try:

        con.execute("""
            INSERT INTO attendance
            (roll_no, date, status)
            VALUES (?, ?, ?)

            ON CONFLICT(roll_no, date)
            DO UPDATE SET
                status = excluded.status
        """, (
            str(roll_no).strip(),
            str(attendance_date).strip(),
            str(status).strip()
        ))

        con.commit()

        return True

    except Exception as e:

        print("Attendance Error:", e)

        return False

    finally:

        con.close()


# ==========================================================
# GET ATTENDANCE
# ==========================================================

def get_attendance(attendance_date):

    con = get_connection()

    try:

        rows = con.execute("""
            SELECT
                s.roll_no,
                s.name,
                s.parent_mobile,
                COALESCE(a.status, 'Absent')
            FROM students s

            LEFT JOIN attendance a
                ON s.roll_no = a.roll_no
                AND a.date = ?

            ORDER BY s.roll_no
        """, (
            str(attendance_date).strip(),
        )).fetchall()

        return rows

    finally:

        con.close()


# ==========================================================
# GET ATTENDANCE REPORT
# ==========================================================

def get_attendance_report():

    con = get_connection()

    try:

        rows = con.execute("""
            SELECT
                a.date,
                s.roll_no,
                s.name,
                a.status
            FROM attendance a

            INNER JOIN students s
                ON s.roll_no = a.roll_no

            ORDER BY
                a.date DESC,
                s.roll_no
        """).fetchall()

        return rows

    finally:

        con.close()


# ==========================================================
# ATTENDANCE COUNT
# ==========================================================

def get_attendance_count(attendance_date):

    con = get_connection()

    try:

        present = con.execute("""
            SELECT COUNT(*)
            FROM attendance
            WHERE date = ?
            AND status = 'Present'
        """, (
            attendance_date,
        )).fetchone()[0]

        absent = con.execute("""
            SELECT COUNT(*)
            FROM attendance
            WHERE date = ?
            AND status = 'Absent'
        """, (
            attendance_date,
        )).fetchone()[0]

        return present, absent

    finally:

        con.close()