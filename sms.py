from kivy.utils import platform


# ==========================================================
# NORMALIZE PHONE NUMBER
# ==========================================================

def normalize_phone(phone):

    phone = str(phone).strip()

    # Remove spaces
    phone = phone.replace(" ", "")

    # Remove -
    phone = phone.replace("-", "")

    # Remove brackets
    phone = phone.replace("(", "")
    phone = phone.replace(")", "")

    # Indian 10 digit number
    if len(phone) == 10 and phone.isdigit():

        phone = "+91" + phone

    return phone


# ==========================================================
# SEND SMS
# ==========================================================

def send_sms(phone_number, message):

    if platform != "android":

        print("SMS works only on Android.")

        return False, "SMS works only on Android."

    phone_number = normalize_phone(
        phone_number
    )

    if not phone_number:

        return False, "Phone number is empty."

    if not message:

        return False, "SMS message is empty."

    try:

        from jnius import autoclass

        # Android Activity
        PythonActivity = autoclass(
            "org.kivy.android.PythonActivity"
        )

        # Android SmsManager
        SmsManager = autoclass(
            "android.telephony.SmsManager"
        )

        activity = PythonActivity.mActivity

        sms_manager = SmsManager.getDefault()

        # Split long SMS if necessary
        parts = sms_manager.divideMessage(
            str(message)
        )

        if parts.size() == 1:

            sms_manager.sendTextMessage(
                phone_number,
                None,
                str(message),
                None,
                None
            )

        else:

            sms_manager.sendMultipartTextMessage(
                phone_number,
                None,
                parts,
                None,
                None
            )

        print(
            "SMS SENT TO:",
            phone_number
        )

        return True, "SMS sent successfully."

    except Exception as e:

        print(
            "SMS ERROR:",
            str(e)
        )

        return False, str(e)


# ==========================================================
# ATTENDANCE SMS
# ==========================================================

def create_attendance_message(
    student_name,
    attendance_date,
    status
):

    if status == "Present":

        message = (
            "Respected Parent,\n\n"
            f"Your child {student_name} "
            f"was marked PRESENT today.\n\n"
            f"Date: {attendance_date}\n\n"
            "Regards,\n"
            "Class Teacher"
        )

    else:

        message = (
            "Respected Parent,\n\n"
            f"Your child {student_name} "
            f"was marked ABSENT today.\n\n"
            f"Date: {attendance_date}\n\n"
            "Please take care of regular attendance.\n\n"
            "Regards,\n"
            "Class Teacher"
        )

    return message


# ==========================================================
# SEND ATTENDANCE SMS
# ==========================================================

def send_attendance_sms(
    phone_number,
    student_name,
    attendance_date,
    status
):

    message = create_attendance_message(
        student_name,
        attendance_date,
        status
    )

    return send_sms(
        phone_number,
        message
    )