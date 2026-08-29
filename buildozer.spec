[app]

title = Smart Attendance
package.name = smartattendance
package.domain = org.smartattendance

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json

version = 1.0

requirements = python3,kivy,pyjnius

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,SEND_SMS

android.api = 34
android.minapi = 21
android.ndk = 28c
android.archs = arm64-v8a

android.skip_update = True
android.accept_sdk_license = True
android.sdk_path = ${ANDROID_HOME}


[buildozer]

log_level = 2
warn_on_root = 1
