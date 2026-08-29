[app]

# Application title
title = Smart Attendance

# Package name
package.name = smartattendance

# Package domain
package.domain = org.smartattendance

# Source directory
source.dir = .

# Files to include in the APK
source.include_exts = py,png,jpg,jpeg,kv,atlas,json

# Application version
version = 1.0

# Python and Kivy dependencies
requirements = python3,kivy,pyjnius

# Screen orientation
orientation = portrait

# Fullscreen
fullscreen = 0

# Android permissions
android.permissions = INTERNET,SEND_SMS

# Android API settings
android.api = 34
android.minapi = 21

# Android architecture
android.archs = arm64-v8a


[buildozer]

# Buildozer log level
log_level = 2

# Don't run Buildozer as root warning
warn_on_root = 1
