from datetime import date

from kivy.app import App
from kivy.uix.screenmanager import (
    ScreenManager,
    Screen
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.utils import platform

from database import (
    create_tables,
    add_student,
    get_students,
    delete_student,
    get_attendance,
    get_attendance_report
)

from attendance import (
    mark_attendance,
    mark_all_present,
    mark_all_absent,
    get_summary
)

from sms import send_attendance_sms


# ==========================================================
# COMMON
# ==========================================================

def show_message(title, message):

    content = BoxLayout(
        orientation="vertical",
        padding=dp(15),
        spacing=dp(15)
    )

    label = Label(
        text=str(message),
        halign="center",
        valign="middle"
    )

    content.add_widget(label)

    close_button = Button(
        text="OK",
        size_hint_y=None,
        height=dp(50)
    )

    content.add_widget(close_button)

    popup = Popup(
        title=title,
        content=content,
        size_hint=(0.9, 0.4)
    )

    close_button.bind(
        on_release=popup.dismiss
    )

    popup.open()


# ==========================================================
# BASE SCREEN
# ==========================================================

class BaseScreen(Screen):

    def make_title(self, text):

        return Label(
            text=text,
            font_size=dp(24),
            bold=True,
            size_hint_y=None,
            height=dp(60)
        )


    def make_button(
        self,
        text,
        callback
    ):

        button = Button(
            text=text,
            font_size=dp(16),
            size_hint_y=None,
            height=dp(55)
        )

        button.bind(
            on_release=callback
        )

        return button


# ==========================================================
# DASHBOARD
# ==========================================================

class DashboardScreen(BaseScreen):

    def on_pre_enter(self, *args):

        self.clear_widgets()

        root = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(15)
        )

        root.add_widget(
            self.make_title(
                "📋 SMART ATTENDANCE"
            )
        )

        root.add_widget(
            self.make_button(
                "👨‍🎓 STUDENT MANAGEMENT",
                self.open_students
            )
        )

        root.add_widget(
            self.make_button(
                "📅 DAILY ATTENDANCE",
                self.open_attendance
            )
        )

        root.add_widget(
            self.make_button(
                "📊 ATTENDANCE REPORT",
                self.open_report
            )
        )

        root.add_widget(
            self.make_button(
                "📩 SEND PARENT SMS",
                self.open_sms
            )
        )

        root.add_widget(
            Label(
                text="",
                size_hint_y=1
            )
        )

        root.add_widget(
            Label(
                text="Attendance Management System",
                size_hint_y=None,
                height=dp(40)
            )
        )

        self.add_widget(root)


    def open_students(self, instance):

        self.manager.current = "students"


    def open_attendance(self, instance):

        self.manager.current = "attendance"


    def open_report(self, instance):

        self.manager.current = "report"


    def open_sms(self, instance):

        self.manager.current = "sms"


# ==========================================================
# STUDENT MANAGEMENT
# ==========================================================

class StudentScreen(BaseScreen):

    def on_pre_enter(self, *args):

        self.build_ui()

        self.load_students()


    def build_ui(self):

        self.clear_widgets()

        root = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10)
        )

        root.add_widget(
            self.make_title(
                "👨‍🎓 STUDENT MANAGEMENT"
            )
        )

        back = self.make_button(
            "← BACK TO DASHBOARD",
            self.go_back
        )

        root.add_widget(back)

        # --------------------------------------------------
        # INPUTS
        # --------------------------------------------------

        self.roll_input = TextInput(
            hint_text="Roll Number",
            multiline=False,
            size_hint_y=None,
            height=dp(50)
        )

        self.name_input = TextInput(
            hint_text="Student Name",
            multiline=False,
            size_hint_y=None,
            height=dp(50)
        )

        self.mobile_input = TextInput(
            hint_text="Parent Mobile Number",
            multiline=False,
            input_filter="int",
            size_hint_y=None,
            height=dp(50)
        )

        root.add_widget(
            self.roll_input
        )

        root.add_widget(
            self.name_input
        )

        root.add_widget(
            self.mobile_input
        )

        root.add_widget(
            self.make_button(
                "➕ ADD STUDENT",
                self.add_student_click
            )
        )

        root.add_widget(
            Label(
                text="STUDENT LIST",
                bold=True,
                size_hint_y=None,
                height=dp(40)
            )
        )

        # --------------------------------------------------
        # STUDENT LIST
        # --------------------------------------------------

        self.student_scroll = ScrollView()

        self.student_list = GridLayout(
            cols=1,
            spacing=dp(8),
            size_hint_y=None
        )

        self.student_list.bind(
            minimum_height=
            self.student_list.setter(
                "height"
            )
        )

        self.student_scroll.add_widget(
            self.student_list
        )

        root.add_widget(
            self.student_scroll
        )

        self.add_widget(root)


    def load_students(self):

        self.student_list.clear_widgets()

        students = get_students()

        if not students:

            self.student_list.add_widget(
                Label(
                    text="No students found.",
                    size_hint_y=None,
                    height=dp(50)
                )
            )

            return

        for student in students:

            student_id = student[0]
            roll = student[1]
            name = student[2]
            mobile = student[3] or "-"

            row = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(65),
                spacing=dp(5)
            )

            info = Label(
                text=(
                    f"{roll}\n"
                    f"{name}\n"
                    f"📱 {mobile}"
                ),
                halign="left",
                valign="middle"
            )

            delete_btn = Button(
                text="DELETE",
                size_hint_x=None,
                width=dp(90)
            )

            delete_btn.bind(
                on_release=lambda btn,
                sid=student_id:
                self.delete_click(sid)
            )

            row.add_widget(info)
            row.add_widget(delete_btn)

            self.student_list.add_widget(row)


    def add_student_click(self, instance):

        roll = self.roll_input.text.strip()
        name = self.name_input.text.strip()
        mobile = self.mobile_input.text.strip()

        if not roll:

            show_message(
                "Error",
                "Enter roll number."
            )

            return

        if not name:

            show_message(
                "Error",
                "Enter student name."
            )

            return

        success, message = add_student(
            roll,
            name,
            mobile
        )

        if success:

            self.roll_input.text = ""
            self.name_input.text = ""
            self.mobile_input.text = ""

            self.load_students()

            show_message(
                "Success",
                message
            )

        else:

            show_message(
                "Error",
                message
            )


    def delete_click(self, student_id):

        delete_student(student_id)

        self.load_students()


    def go_back(self, instance):

        self.manager.current = "dashboard"


# ==========================================================
# DAILY ATTENDANCE
# ==========================================================

class AttendanceScreen(BaseScreen):

    def on_pre_enter(self, *args):

        self.build_ui()

        self.load_data()


    def build_ui(self):

        self.clear_widgets()

        root = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10)
        )

        root.add_widget(
            self.make_title(
                "📅 DAILY ATTENDANCE"
            )
        )

        root.add_widget(
            self.make_button(
                "← BACK TO DASHBOARD",
                self.go_back
            )
        )

        date_row = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(5)
        )

        date_row.add_widget(
            Label(
                text="Date:",
                size_hint_x=None,
                width=dp(60)
            )
        )

        self.date_input = TextInput(
            text=str(date.today()),
            multiline=False
        )

        date_row.add_widget(
            self.date_input
        )

        load_btn = Button(
            text="LOAD",
            size_hint_x=None,
            width=dp(90)
        )

        load_btn.bind(
            on_release=lambda x:
            self.load_data()
        )

        date_row.add_widget(
            load_btn
        )

        root.add_widget(date_row)

        # --------------------------------------------------
        # QUICK BUTTONS
        # --------------------------------------------------

        quick_row = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(5)
        )

        present_btn = Button(
            text="ALL PRESENT"
        )

        present_btn.bind(
            on_release=self.all_present
        )

        absent_btn = Button(
            text="ALL ABSENT"
        )

        absent_btn.bind(
            on_release=self.all_absent
        )

        quick_row.add_widget(
            present_btn
        )

        quick_row.add_widget(
            absent_btn
        )

        root.add_widget(
            quick_row
        )

        # --------------------------------------------------
        # STUDENTS
        # --------------------------------------------------

        self.scroll = ScrollView()

        self.list_layout = GridLayout(
            cols=1,
            spacing=dp(8),
            size_hint_y=None
        )

        self.list_layout.bind(
            minimum_height=
            self.list_layout.setter(
                "height"
            )
        )

        self.scroll.add_widget(
            self.list_layout
        )

        root.add_widget(
            self.scroll
        )

        self.summary_label = Label(
            text="Present: 0    Absent: 0",
            size_hint_y=None,
            height=dp(40),
            bold=True
        )

        root.add_widget(
            self.summary_label
        )

        self.add_widget(root)


    def load_data(self):

        self.list_layout.clear_widgets()

        attendance_date = (
            self.date_input.text.strip()
        )

        if not attendance_date:
            return

        rows = get_attendance(
            attendance_date
        )

        for row in rows:

            roll = row[0]
            name = row[1]
            status = row[3]

            student_row = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(60),
                spacing=dp(5)
            )

            label = Label(
                text=f"{roll} - {name}",
                halign="left",
                valign="middle"
            )

            spinner = Spinner(
                text=status,
                values=(
                    "Present",
                    "Absent"
                ),
                size_hint_x=None,
                width=dp(110)
            )

            spinner.bind(
                text=lambda sp, value,
                r=roll:
                self.status_changed(
                    r,
                    value
                )
            )

            student_row.add_widget(
                label
            )

            student_row.add_widget(
                spinner
            )

            self.list_layout.add_widget(
                student_row
            )

        self.update_summary()


    def status_changed(
        self,
        roll_no,
        status
    ):

        attendance_date = (
            self.date_input.text.strip()
        )

        mark_attendance(
            roll_no,
            attendance_date,
            status
        )

        self.update_summary()


    def update_summary(self):

        attendance_date = (
            self.date_input.text.strip()
        )

        present, absent = get_summary(
            attendance_date
        )

        self.summary_label.text = (
            f"Present: {present}    "
            f"Absent: {absent}"
        )


    def all_present(self, instance):

        attendance_date = (
            self.date_input.text.strip()
        )

        count = mark_all_present(
            attendance_date
        )

        self.load_data()

        show_message(
            "Attendance",
            f"{count} students marked Present."
        )


    def all_absent(self, instance):

        attendance_date = (
            self.date_input.text.strip()
        )

        count = mark_all_absent(
            attendance_date
        )

        self.load_data()

        show_message(
            "Attendance",
            f"{count} students marked Absent."
        )


    def go_back(self, instance):

        self.manager.current = "dashboard"


# ==========================================================
# ATTENDANCE REPORT
# ==========================================================

class ReportScreen(BaseScreen):

    def on_pre_enter(self, *args):

        self.clear_widgets()

        root = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10)
        )

        root.add_widget(
            self.make_title(
                "📊 ATTENDANCE REPORT"
            )
        )

        root.add_widget(
            self.make_button(
                "← BACK TO DASHBOARD",
                self.go_back
            )
        )

        scroll = ScrollView()

        layout = GridLayout(
            cols=1,
            spacing=dp(5),
            size_hint_y=None
        )

        layout.bind(
            minimum_height=
            layout.setter(
                "height"
            )
        )

        rows = get_attendance_report()

        if not rows:

            layout.add_widget(
                Label(
                    text="No attendance records.",
                    size_hint_y=None,
                    height=dp(50)
                )
            )

        else:

            for row in rows:

                attendance_date = row[0]
                roll = row[1]
                name = row[2]
                status = row[3]

                layout.add_widget(
                    Label(
                        text=(
                            f"{attendance_date} | "
                            f"{roll} | "
                            f"{name} | "
                            f"{status}"
                        ),
                        size_hint_y=None,
                        height=dp(45)
                    )
                )

        scroll.add_widget(layout)

        root.add_widget(scroll)

        self.add_widget(root)


    def go_back(self, instance):

        self.manager.current = "dashboard"


# ==========================================================
# SMS SCREEN
# ==========================================================

class SMSScreen(BaseScreen):

    def on_pre_enter(self, *args):

        self.build_ui()

        self.load_data()


    def build_ui(self):

        self.clear_widgets()

        root = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10)
        )

        root.add_widget(
            self.make_title(
                "📩 SEND PARENT SMS"
            )
        )

        root.add_widget(
            self.make_button(
                "← BACK TO DASHBOARD",
                self.go_back
            )
        )

        # --------------------------------------------------
        # DATE
        # --------------------------------------------------

        date_row = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(5)
        )

        date_row.add_widget(
            Label(
                text="Date:",
                size_hint_x=None,
                width=dp(60)
            )
        )

        self.sms_date = TextInput(
            text=str(date.today()),
            multiline=False
        )

        date_row.add_widget(
            self.sms_date
        )

        load_btn = Button(
            text="LOAD",
            size_hint_x=None,
            width=dp(90)
        )

        load_btn.bind(
            on_release=lambda x:
            self.load_data()
        )

        date_row.add_widget(load_btn)

        root.add_widget(
            date_row
        )

        # --------------------------------------------------
        # SEND ALL
        # --------------------------------------------------

        root.add_widget(
            self.make_button(
                "📨 SEND ALL SMS",
                self.send_all
            )
        )

        self.scroll = ScrollView()

        self.list_layout = GridLayout(
            cols=1,
            spacing=dp(8),
            size_hint_y=None
        )

        self.list_layout.bind(
            minimum_height=
            self.list_layout.setter(
                "height"
            )
        )

        self.scroll.add_widget(
            self.list_layout
        )

        root.add_widget(
            self.scroll
        )

        self.add_widget(root)


    def load_data(self):

        self.list_layout.clear_widgets()

        attendance_date = (
            self.sms_date.text.strip()
        )

        rows = get_attendance(
            attendance_date
        )

        for row in rows:

            roll = row[0]
            name = row[1]
            mobile = row[2]
            status = row[3]

            student_row = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(105),
                spacing=dp(3)
            )

            info = Label(
                text=(
                    f"{roll} - {name}\n"
                    f"📱 {mobile or 'No mobile'}\n"
                    f"Attendance: {status}"
                ),
                halign="left",
                valign="middle"
            )

            send_btn = Button(
                text="📩 SEND SMS",
                size_hint_y=None,
                height=dp(45)
            )

            send_btn.bind(
                on_release=lambda btn,
                n=name,
                m=mobile,
                s=status:
                self.send_one(
                    n,
                    m,
                    s
                )
            )

            student_row.add_widget(info)
            student_row.add_widget(send_btn)

            self.list_layout.add_widget(
                student_row
            )


    def send_one(
        self,
        name,
        mobile,
        status
    ):

        if not mobile:

            show_message(
                "Mobile Missing",
                f"No mobile number for {name}."
            )

            return

        attendance_date = (
            self.sms_date.text.strip()
        )

        success, message = send_attendance_sms(
            mobile,
            name,
            attendance_date,
            status
        )

        if success:

            show_message(
                "SMS Sent",
                f"SMS sent to {mobile}"
            )

        else:

            show_message(
                "SMS Failed",
                message
            )


    def send_all(self, instance):

        attendance_date = (
            self.sms_date.text.strip()
        )

        rows = get_attendance(
            attendance_date
        )

        if not rows:

            show_message(
                "SMS",
                "No students found."
            )

            return

        sent = 0
        failed = 0

        for row in rows:

            name = row[1]
            mobile = row[2]
            status = row[3]

            if not mobile:

                failed += 1
                continue

            success, message = send_attendance_sms(
                mobile,
                name,
                attendance_date,
                status
            )

            if success:

                sent += 1

            else:

                failed += 1

        show_message(
            "SMS Completed",
            f"SMS Sent: {sent}\n"
            f"SMS Failed: {failed}"
        )


    def go_back(self, instance):

        self.manager.current = "dashboard"


# ==========================================================
# MAIN APP
# ==========================================================

class SmartAttendanceApp(App):

    def build(self):

        self.title = "Smart Attendance"

        create_tables()

        manager = ScreenManager()

        manager.add_widget(
            DashboardScreen(
                name="dashboard"
            )
        )

        manager.add_widget(
            StudentScreen(
                name="students"
            )
        )

        manager.add_widget(
            AttendanceScreen(
                name="attendance"
            )
        )

        manager.add_widget(
            ReportScreen(
                name="report"
            )
        )

        manager.add_widget(
            SMSScreen(
                name="sms"
            )
        )

        return manager


    def on_start(self):

        self.request_sms_permission()


    # ======================================================
    # ANDROID SMS PERMISSION
    # ======================================================

    def request_sms_permission(self):

        if platform != "android":
            return

        try:

            from android.permissions import (
                request_permissions,
                Permission
            )

            request_permissions([
                Permission.SEND_SMS
            ])

        except Exception as e:

            print(
                "Permission Error:",
                e
            )