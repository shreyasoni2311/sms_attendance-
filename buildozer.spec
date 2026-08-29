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

android.api = 35
android.minapi = 21

android.archs = arm64-v8a, armeabi-v7a

[buildozer]

log_level = 2
warn_on_root = 1