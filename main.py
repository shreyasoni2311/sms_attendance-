# main.py

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from mobile_app import SmartAttendanceApp


if __name__ == "__main__":
    SmartAttendanceApp().run()

from database import (
    create_tables,
    add_student,
    get_students,
    delete_student
)

from attendance import AttendanceScreen
from sms import SMSScreen


# ==========================================================
# DASHBOARD SCREEN
# ==========================================================

class DashboardScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15
        )

        # --------------------------------------------------
        # TITLE
        # --------------------------------------------------

        root.add_widget(
            Label(
                text="SMART ATTENDANCE SMS",
                font_size=28,
                bold=True,
                size_hint_y=None,
                height=70
            )
        )

        root.add_widget(
            Label(
                text="Attendance Management System",
                font_size=18,
                size_hint_y=None,
                height=45
            )
        )

        # --------------------------------------------------
        # STUDENT MANAGEMENT
        # --------------------------------------------------

        student_btn = Button(
            text="STUDENT MANAGEMENT",
            font_size=18,
            size_hint_y=None,
            height=60
        )

        student_btn.bind(
            on_press=self.open_students
        )

        root.add_widget(student_btn)

        # --------------------------------------------------
        # DAILY ATTENDANCE
        # --------------------------------------------------

        attendance_btn = Button(
            text="DAILY ATTENDANCE",
            font_size=18,
            size_hint_y=None,
            height=60
        )

        attendance_btn.bind(
            on_press=self.open_attendance
        )

        root.add_widget(attendance_btn)

        # --------------------------------------------------
        # REPORT
        # --------------------------------------------------

        report_btn = Button(
            text="ATTENDANCE REPORT",
            font_size=18,
            size_hint_y=None,
            height=60
        )

        report_btn.bind(
            on_press=self.open_report
        )

        root.add_widget(report_btn)

        # --------------------------------------------------
        # SMS
        # --------------------------------------------------

        sms_btn = Button(
            text="SEND PARENT SMS",
            font_size=18,
            size_hint_y=None,
            height=60
        )

        sms_btn.bind(
            on_press=self.open_sms
        )

        root.add_widget(sms_btn)

        root.add_widget(
            Label(text="")
        )

        root.add_widget(
            Label(
                text="Smart Attendance SMS",
                font_size=14,
                size_hint_y=None,
                height=40
            )
        )

        self.add_widget(root)

    # ======================================================
    # OPEN STUDENTS
    # ======================================================

    def open_students(self, instance):

        self.manager.current = "students"

        screen = self.manager.get_screen("students")
        screen.load_students()

    # ======================================================
    # OPEN ATTENDANCE
    # ======================================================

    def open_attendance(self, instance):

        self.manager.current = "attendance"

        screen = self.manager.get_screen("attendance")
        screen.load_attendance()

    # ======================================================
    # OPEN REPORT
    # ======================================================

    def open_report(self, instance):

        self.manager.current = "report"

    # ======================================================
    # OPEN SMS
    # ======================================================

    def open_sms(self, instance):

        self.manager.current = "sms"

        screen = self.manager.get_screen("sms")
        screen.load_attendance()


# ==========================================================
# STUDENT MANAGEMENT SCREEN
# ==========================================================

class StudentScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.build_ui()

    # ======================================================
    # BUILD UI
    # ======================================================

    def build_ui(self):

        root = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )

        # --------------------------------------------------
        # TITLE
        # --------------------------------------------------

        root.add_widget(
            Label(
                text="STUDENT MANAGEMENT",
                font_size=25,
                bold=True,
                size_hint_y=None,
                height=55
            )
        )

        # --------------------------------------------------
        # BACK
        # --------------------------------------------------

        back_btn = Button(
            text="BACK TO DASHBOARD",
            size_hint_y=None,
            height=50
        )

        back_btn.bind(
            on_press=self.go_back
        )

        root.add_widget(back_btn)

        # --------------------------------------------------
        # ROLL NUMBER
        # --------------------------------------------------

        self.roll_input = TextInput(
            hint_text="Enter Roll No",
            multiline=False,
            font_size=17,
            size_hint_y=None,
            height=50
        )

        root.add_widget(
            self.roll_input
        )

        # --------------------------------------------------
        # STUDENT NAME
        # --------------------------------------------------

        self.name_input = TextInput(
            hint_text="Enter Student Name",
            multiline=False,
            font_size=17,
            size_hint_y=None,
            height=50
        )

        root.add_widget(
            self.name_input
        )

        # --------------------------------------------------
        # PARENT MOBILE
        # --------------------------------------------------

        self.mobile_input = TextInput(
            hint_text="Enter Parent Mobile Number",
            multiline=False,
            font_size=17,
            input_filter="int",
            size_hint_y=None,
            height=50
        )

        root.add_widget(
            self.mobile_input
        )

        # --------------------------------------------------
        # ADD STUDENT
        # --------------------------------------------------

        add_btn = Button(
            text="ADD STUDENT",
            font_size=17,
            size_hint_y=None,
            height=55
        )

        add_btn.bind(
            on_press=self.add_new_student
        )

        root.add_widget(
            add_btn
        )

        # --------------------------------------------------
        # STUDENT LIST
        # --------------------------------------------------

        scroll = ScrollView()

        self.student_list = GridLayout(
            cols=1,
            spacing=8,
            size_hint_y=None
        )

        self.student_list.bind(
            minimum_height=self.student_list.setter(
                "height"
            )
        )

        scroll.add_widget(
            self.student_list
        )

        root.add_widget(
            scroll
        )

        self.add_widget(root)

    # ======================================================
    # LOAD STUDENTS
    # ======================================================

    def load_students(self):

        self.student_list.clear_widgets()

        students = get_students()

        if not students:

            self.student_list.add_widget(
                Label(
                    text="No students added yet.",
                    font_size=17,
                    size_hint_y=None,
                    height=50
                )
            )

            return

        for student in students:

            student_id = student[0]
            roll = student[1]
            name = student[2]
            mobile = student[3] or ""

            row = BoxLayout(
                size_hint_y=None,
                height=60,
                spacing=5
            )

            info = Label(
                text=(
                    f"Roll: {roll}\n"
                    f"{name}\n"
                    f"Mobile: {mobile}"
                ),
                font_size=14
            )

            delete_btn = Button(
                text="DELETE",
                size_hint_x=0.25
            )

            delete_btn.bind(
                on_press=lambda btn, sid=student_id:
                self.remove_student(sid)
            )

            row.add_widget(info)
            row.add_widget(delete_btn)

            self.student_list.add_widget(
                row
            )

    # ======================================================
    # ADD STUDENT
    # ======================================================

    def add_new_student(self, instance):

        roll = self.roll_input.text.strip()
        name = self.name_input.text.strip()
        mobile = self.mobile_input.text.strip()

        if not roll:

            self.show_message(
                "Please enter Roll No."
            )

            return

        if not name:

            self.show_message(
                "Please enter Student Name."
            )

            return

        if mobile and len(mobile) != 10:

            self.show_message(
                "Please enter a valid 10 digit mobile number."
            )

            return

        success = add_student(
            roll,
            name,
            mobile
        )

        if success:

            self.roll_input.text = ""
            self.name_input.text = ""
            self.mobile_input.text = ""

            self.load_students()

            self.show_message(
                "Student added successfully."
            )

        else:

            self.show_message(
                "Roll No already exists."
            )

    # ======================================================
    # DELETE STUDENT
    # ======================================================

    def remove_student(self, student_id):

        delete_student(student_id)

        self.load_students()

    # ======================================================
    # MESSAGE POPUP
    # ======================================================

    def show_message(self, message):

        content = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )

        content.add_widget(
            Label(
                text=message,
                font_size=16
            )
        )

        close_btn = Button(
            text="OK",
            size_hint_y=None,
            height=50
        )

        content.add_widget(
            close_btn
        )

        popup = Popup(
            title="Smart Attendance",
            content=content,
            size_hint=(0.85, 0.35)
        )

        close_btn.bind(
            on_press=popup.dismiss
        )

        popup.open()

    # ======================================================
    # BACK
    # ======================================================

    def go_back(self, instance):

        self.manager.current = "dashboard"


# ==========================================================
# REPORT SCREEN
# ==========================================================

class ReportScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15
        )

        root.add_widget(
            Label(
                text="ATTENDANCE REPORT",
                font_size=25,
                bold=True,
                size_hint_y=None,
                height=60
            )
        )

        back_btn = Button(
            text="BACK TO DASHBOARD",
            size_hint_y=None,
            height=55
        )

        back_btn.bind(
            on_press=self.go_back
        )

        root.add_widget(back_btn)

        root.add_widget(
            Label(
                text="Attendance report coming soon.",
                font_size=17
            )
        )

        self.add_widget(root)

    def go_back(self, instance):

        self.manager.current = "dashboard"


# ==========================================================
# MAIN APP
# ==========================================================

class SmartAttendanceApp(App):

    def build(self):

        # Create SQLite tables
        create_tables()

        manager = ScreenManager()

        # --------------------------------------------------
        # DASHBOARD
        # --------------------------------------------------

        manager.add_widget(
            DashboardScreen(
                name="dashboard"
            )
        )

        # --------------------------------------------------
        # STUDENTS
        # --------------------------------------------------

        manager.add_widget(
            StudentScreen(
                name="students"
            )
        )

        # --------------------------------------------------
        # ATTENDANCE
        # --------------------------------------------------

        manager.add_widget(
            AttendanceScreen(
                name="attendance"
            )
        )

        # --------------------------------------------------
        # REPORT
        # --------------------------------------------------

        manager.add_widget(
            ReportScreen(
                name="report"
            )
        )

        # --------------------------------------------------
        # SMS
        # --------------------------------------------------

        manager.add_widget(
            SMSScreen(
                name="sms"
            )
        )

        return manager


# ==========================================================
# RUN APPLICATION
# ==========================================================

if __name__ == "__main__":

    SmartAttendanceApp().run()