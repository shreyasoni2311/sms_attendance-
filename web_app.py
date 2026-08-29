# web_app.py

from flask import (
    Flask,
    render_template_string,
    request,
    redirect,
    url_for,
    flash
)

from datetime import date

from database import (
    create_tables,
    get_connection,
    add_student,
    get_students,
    delete_student,
    save_attendance
)

from sms import send_sms


# ==========================================================
# FLASK APP
# ==========================================================

app = Flask(__name__)

app.secret_key = "smart-attendance-secret-key"

# SMS Gateway
# તમારું SMS Gateway phone/device નું IP અહીં મૂકો.
SMS_URL = "http://192.168.0.186:8080/send-sms"


# ==========================================================
# CREATE DATABASE
# ==========================================================

create_tables()


# ==========================================================
# COMMON HTML
# ==========================================================

HTML_START = """
<!DOCTYPE html>

<html>

<head>

<meta name="viewport"
      content="width=device-width, initial-scale=1">

<title>Smart Attendance SMS</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f4f6f8;
    color: #222;
}

.header {
    background: #1f2937;
    color: white;
    padding: 18px;
    text-align: center;
}

.header h1 {
    margin: 0;
    font-size: 24px;
}

.container {
    width: 95%;
    max-width: 900px;
    margin: 20px auto;
}

.card {
    background: white;
    padding: 18px;
    margin-bottom: 15px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

button,
.btn {
    border: none;
    padding: 13px 18px;
    border-radius: 8px;
    font-size: 15px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
    margin: 5px 3px;
    background: #2563eb;
    color: white;
}

.btn-danger {
    background: #dc2626;
}

.btn-success {
    background: #16a34a;
}

.btn-warning {
    background: #d97706;
}

.btn-dark {
    background: #374151;
}

input,
select {
    width: 100%;
    padding: 13px;
    margin: 7px 0 14px;
    border: 1px solid #ccc;
    border-radius: 8px;
    font-size: 16px;
}

label {
    font-weight: bold;
}

table {
    width: 100%;
    border-collapse: collapse;
    background: white;
}

th,
td {
    padding: 11px 7px;
    border-bottom: 1px solid #ddd;
    text-align: left;
}

th {
    background: #e5e7eb;
}

.present {
    color: green;
    font-weight: bold;
}

.absent {
    color: red;
    font-weight: bold;
}

.dashboard-btn {
    display: block;
    width: 100%;
    padding: 18px;
    margin: 10px 0;
    border-radius: 10px;
    text-align: center;
    background: #2563eb;
    color: white;
    text-decoration: none;
    font-size: 18px;
}

.flash {
    padding: 13px;
    background: #fff3cd;
    border-radius: 8px;
    margin-bottom: 10px;
}

@media(max-width: 600px) {

    table {
        font-size: 13px;
    }

    th,
    td {
        padding: 8px 4px;
    }

    .container {
        width: 96%;
    }

    .hide-mobile {
        display: none;
    }

}

</style>

</head>

<body>

<div class="header">

<h1>SMART ATTENDANCE SMS</h1>

</div>

<div class="container">

{% with messages = get_flashed_messages() %}

{% if messages %}

{% for message in messages %}

<div class="flash">
{{ message }}
</div>

{% endfor %}

{% endif %}

{% endwith %}
"""


HTML_END = """

</div>

</body>

</html>
"""


# ==========================================================
# DASHBOARD
# ==========================================================

@app.route("/")
def dashboard():

    students = get_students()

    html = HTML_START + """

<div class="card">

<h2>Dashboard</h2>

<p>
Total Students:
<b>{{ students|length }}</b>
</p>

</div>

<a class="dashboard-btn"
   href="{{ url_for('students') }}">

👨‍🎓 Student Management

</a>

<a class="dashboard-btn"
   href="{{ url_for('attendance') }}">

📋 Daily Attendance

</a>

<a class="dashboard-btn"
   href="{{ url_for('report') }}">

📊 Attendance Report

</a>

<a class="dashboard-btn"
   href="{{ url_for('sms_page') }}">

📩 Send Parent SMS

</a>

""" + HTML_END

    return render_template_string(
        html,
        students=students
    )


# ==========================================================
# STUDENT MANAGEMENT
# ==========================================================

@app.route("/students")
def students():

    data = get_students()

    html = HTML_START + """

<div class="card">

<h2>👨‍🎓 Student Management</h2>

<form method="POST"
      action="{{ url_for('add_student_web') }}">

<label>Roll No</label>

<input type="text"
       name="roll_no"
       placeholder="Enter Roll No"
       required>

<label>Student Name</label>

<input type="text"
       name="name"
       placeholder="Enter Student Name"
       required>

<label>Parent Mobile</label>

<input type="tel"
       name="parent_mobile"
       placeholder="10 digit mobile number"
       maxlength="10">

<button class="btn-success"
        type="submit">

ADD STUDENT

</button>

</form>

</div>

<div class="card">

<h3>Student List</h3>

{% if data %}

<table>

<tr>

<th>Roll</th>
<th>Name</th>
<th>Mobile</th>
<th>Action</th>

</tr>

{% for student in data %}

<tr>

<td>{{ student[1] }}</td>

<td>{{ student[2] }}</td>

<td>{{ student[3] or "-" }}</td>

<td>

<a class="btn btn-danger"
   href="{{ url_for('delete_student_web',
                   student_id=student[0]) }}"
   onclick="return confirm('Delete student?');">

DELETE

</a>

</td>

</tr>

{% endfor %}

</table>

{% else %}

<p>No students added yet.</p>

{% endif %}

</div>

<a class="btn btn-dark"
   href="{{ url_for('dashboard') }}">

⬅ Dashboard

</a>

""" + HTML_END

    return render_template_string(
        html,
        data=data
    )


# ==========================================================
# ADD STUDENT
# ==========================================================

@app.route(
    "/students/add",
    methods=["POST"]
)
def add_student_web():

    roll_no = request.form.get(
        "roll_no",
        ""
    ).strip()

    name = request.form.get(
        "name",
        ""
    ).strip()

    parent_mobile = request.form.get(
        "parent_mobile",
        ""
    ).strip()

    if not roll_no or not name:

        flash(
            "Roll No and Student Name are required."
        )

        return redirect(
            url_for("students")
        )

    if parent_mobile:

        if not parent_mobile.isdigit() or len(parent_mobile) != 10:

            flash(
                "Please enter valid 10 digit mobile number."
            )

            return redirect(
                url_for("students")
            )

    success = add_student(
        roll_no,
        name,
        parent_mobile
    )

    if success:

        flash(
            "Student added successfully."
        )

    else:

        flash(
            "Roll No already exists."
        )

    return redirect(
        url_for("students")
    )


# ==========================================================
# DELETE STUDENT
# ==========================================================

@app.route(
    "/students/delete/<int:student_id>"
)
def delete_student_web(student_id):

    delete_student(student_id)

    flash(
        "Student deleted successfully."
    )

    return redirect(
        url_for("students")
    )


# ==========================================================
# DAILY ATTENDANCE
# ==========================================================

@app.route("/attendance")
def attendance():

    selected_date = request.args.get(
        "date",
        str(date.today())
    )

    con = get_connection()

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
        selected_date,
    )).fetchall()

    con.close()

    html = HTML_START + """

<div class="card">

<h2>📋 Daily Attendance</h2>

<form method="GET">

<label>Date</label>

<input type="date"
       name="date"
       value="{{ selected_date }}">

<button type="submit">

LOAD

</button>

</form>

</div>

<form method="POST"
      action="{{ url_for('save_attendance_web') }}">

<input type="hidden"
       name="attendance_date"
       value="{{ selected_date }}">

<div class="card">

<table>

<tr>

<th>Roll</th>
<th>Student</th>
<th>Mobile</th>
<th>Status</th>

</tr>

{% for row in rows %}

<tr>

<td>{{ row[0] }}</td>

<td>{{ row[1] }}</td>

<td>{{ row[2] or "-" }}</td>

<td>

<select name="status_{{ row[0] }}">

<option value="Present"
{% if row[3] == "Present" %}
selected
{% endif %}>

Present

</option>

<option value="Absent"
{% if row[3] == "Absent" %}
selected
{% endif %}>

Absent

</option>

</select>

</td>

</tr>

{% endfor %}

</table>

</div>

{% if rows %}

<button class="btn-success"
        type="submit">

💾 SAVE ATTENDANCE

</button>

{% endif %}

</form>

<a class="btn btn-dark"
   href="{{ url_for('dashboard') }}">

⬅ Dashboard

</a>

""" + HTML_END

    return render_template_string(
        html,
        rows=rows,
        selected_date=selected_date
    )


# ==========================================================
# SAVE ATTENDANCE
# ==========================================================

@app.route(
    "/attendance/save",
    methods=["POST"]
)
def save_attendance_web():

    selected_date = request.form.get(
        "attendance_date",
        ""
    ).strip()

    students = get_students()

    saved = 0

    for student in students:

        roll_no = student[1]

        status = request.form.get(
            f"status_{roll_no}",
            "Absent"
        )

        if status not in (
            "Present",
            "Absent"
        ):
            status = "Absent"

        save_attendance(
            roll_no,
            selected_date,
            status
        )

        saved += 1

    flash(
        f"Attendance saved successfully. Students: {saved}"
    )

    return redirect(
        url_for(
            "attendance",
            date=selected_date
        )
    )


# ==========================================================
# REPORT
# ==========================================================

@app.route("/report")
def report():

    selected_date = request.args.get(
        "date",
        str(date.today())
    )

    con = get_connection()

    rows = con.execute("""
        SELECT
            s.roll_no,
            s.name,
            a.status

        FROM students s

        LEFT JOIN attendance a

        ON s.roll_no = a.roll_no

        AND a.date = ?

        ORDER BY s.roll_no

    """, (
        selected_date,
    )).fetchall()

    con.close()

    total = len(rows)

    present = sum(
        1
        for row in rows
        if row[2] == "Present"
    )

    absent = sum(
        1
        for row in rows
        if row[2] == "Absent"
        or row[2] is None
    )

    html = HTML_START + """

<div class="card">

<h2>📊 Attendance Report</h2>

<form method="GET">

<label>Date</label>

<input type="date"
       name="date"
       value="{{ selected_date }}">

<button type="submit">

LOAD REPORT

</button>

</form>

</div>

<div class="card">

<p>
Total Students:
<b>{{ total }}</b>
</p>

<p class="present">
Present:
<b>{{ present }}</b>
</p>

<p class="absent">
Absent:
<b>{{ absent }}</b>
</p>

</div>

<div class="card">

<table>

<tr>

<th>Roll</th>
<th>Student</th>
<th>Status</th>

</tr>

{% for row in rows %}

<tr>

<td>{{ row[0] }}</td>

<td>{{ row[1] }}</td>

<td>

{% if row[2] == "Present" %}

<span class="present">
Present
</span>

{% else %}

<span class="absent">
Absent
</span>

{% endif %}

</td>

</tr>

{% endfor %}

</table>

</div>

<a class="btn btn-dark"
   href="{{ url_for('dashboard') }}">

⬅ Dashboard

</a>

""" + HTML_END

    return render_template_string(
        html,
        rows=rows,
        selected_date=selected_date,
        total=total,
        present=present,
        absent=absent
    )


# ==========================================================
# SMS PAGE
# ==========================================================

@app.route("/sms")
def sms_page():

    selected_date = request.args.get(
        "date",
        str(date.today())
    )

    con = get_connection()

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
        selected_date,
    )).fetchall()

    con.close()

    html = HTML_START + """

<div class="card">

<h2>📩 Send Parent SMS</h2>

<form method="GET">

<label>Date</label>

<input type="date"
       name="date"
       value="{{ selected_date }}">

<button type="submit">

LOAD

</button>

</form>

</div>

<div class="card">

<table>

<tr>

<th>Roll</th>
<th>Student</th>
<th>Mobile</th>
<th>Status</th>

</tr>

{% for row in rows %}

<tr>

<td>{{ row[0] }}</td>

<td>{{ row[1] }}</td>

<td>{{ row[2] or "-" }}</td>

<td>

{% if row[3] == "Present" %}

<span class="present">
Present
</span>

{% else %}

<span class="absent">
Absent
</span>

{% endif %}

</td>

</tr>

{% endfor %}

</table>

</div>

<div class="card">

<h3>Send SMS</h3>

<form method="POST"
      action="{{ url_for('send_all_sms_web') }}">

<input type="hidden"
       name="attendance_date"
       value="{{ selected_date }}">

<button class="btn-success"
        type="submit"
        onclick="return confirm('Send SMS to all parents?');">

📨 SEND ALL SMS

</button>

</form>

</div>

<a class="btn btn-dark"
   href="{{ url_for('dashboard') }}">

⬅ Dashboard

</a>

""" + HTML_END

    return render_template_string(
        html,
        rows=rows,
        selected_date=selected_date
    )


# ==========================================================
# SEND ALL SMS
# ==========================================================

@app.route(
    "/sms/send-all",
    methods=["POST"]
)
def send_all_sms_web():

    selected_date = request.form.get(
        "attendance_date",
        str(date.today())
    ).strip()

    con = get_connection()

    rows = con.execute("""
        SELECT
            s.name,
            s.parent_mobile,
            COALESCE(a.status, 'Absent')

        FROM students s

        LEFT JOIN attendance a

        ON s.roll_no = a.roll_no

        AND a.date = ?

        ORDER BY s.roll_no

    """, (
        selected_date,
    )).fetchall()

    con.close()

    sent = 0
    failed = 0

    for row in rows:

        name = row[0]
        mobile = row[1]
        status = row[2]

        if not mobile:

            failed += 1
            continue

        message = (
            "Respected Parent,\n\n"
            f"Date: {selected_date}\n\n"
            f"Your child {name}'s attendance today "
            f"is: {status}.\n\n"
            "Please take care of regular attendance.\n\n"
            "Regards,\n"
            "Class Teacher"
        )

        success, response = send_sms(
            mobile,
            message
        )

        if success:

            sent += 1

        else:

            failed += 1

    flash(
        f"SMS Completed - Sent: {sent}, Failed: {failed}"
    )

    return redirect(
        url_for(
            "sms_page",
            date=selected_date
        )
    )


# ==========================================================
# RUN FLASK
# ==========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )