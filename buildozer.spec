[app]

# (str) Title of your application
title = NeuroMentor

# (str) Package name
package.name = neuromentor

# (str) Package domain (needed for android/ios packaging)
package.domain = org.neuromentor

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,pkl,ttf

# (list) List of inclusions using pattern matching
source.include_patterns = neuromentor_data/**/*.pkl,neuromentor_data/**/*.json,tools/**/*.py

# (list) Source files to exclude (let empty to not exclude anything)
source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = .venv,__pycache__,.git,.github,tests,bin

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
# ──────────────────────────────────────────────────────────────────
# Derived from reading every import across every .py file:
#   kivy          — core framework (Config, App, Window, uix.*, graphics.*, etc.)
#   pyjnius       — jnius autoclass in main.py for Android orientation lock
#   numpy         — numpy in rf_classifier.py and compatibility_check.py
#   joblib        — joblib in rf_classifier.py for model persistence
#   scikit-learn  — sklearn.ensemble, sklearn.preprocessing, sklearn.model_selection
#
# NOT used (confirmed by reading all source):
#   kivymd, pillow, requests, plyer, scipy
# ──────────────────────────────────────────────────────────────────
requirements = python3,kivy==2.3.0,pyjnius,numpy,joblib

# (str) Custom source folders for requirements
# p4a.source_dir =

# (str) Presplash of the application
# presplash.filename = %(source.dir)s/presplash.png

# (str) Icon of the application
# icon.filename = %(source.dir)s/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
# 0 = not fullscreen (show status bar)
fullscreen = 0

# (string) Presplash background color (for Android dark theme)
android.presplash_color = #332e3c

# (string) Presplash animation using Lottie
# android.presplash_lottie =

#
# ─── ANDROID SETTINGS ────────────────────────────────────────────
#

# (int) Target Android API, should be as high as possible
android.api = 33

# (int) Minimum API your APK / AAB will support
android.minapi = 26

# (str) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android NDK API to use. This is the minimum API your app will support.
android.ndk_api = 21

# (list) The Android archs to build for
android.archs = arm64-v8a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (bool) If True, then skip trying to update the Android sdk
# android.skip_update = False

# (bool) If True, then automatically accept SDK license
android.accept_sdk_license = True

# (list) Permissions
# ──────────────────────────────────────────────────────────────────
# Derived from:
#   INTERNET                 — future network features / general connectivity
#   BLUETOOTH*               — BLE EXG device communication (future)
#   ACCESS_*_LOCATION        — required for BLE scanning on Android 6+
#   ACCESS_WIFI_STATE        — future WiFi UDP data streaming
#   CHANGE_WIFI_STATE        — future WiFi UDP data streaming
#   READ/WRITE_EXTERNAL_STORAGE — model pkl file persistence
# ──────────────────────────────────────────────────────────────────
android.permissions = INTERNET,BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_SCAN,BLUETOOTH_CONNECT,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,ACCESS_WIFI_STATE,CHANGE_WIFI_STATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# (list) features (adds uses-feature to manifest)
android.features = android.hardware.bluetooth_le,android.hardware.wifi

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (str) The Android entry point, default is ok for Kivy-based app
# android.entrypoint = org.kivy.android.PythonActivity

# (str) Full name including package path of the Java class that implements Android Activity
# android.activity_class_name = org.kivy.android.PythonActivity

# (list) Pattern to whitelist for the whole project
# android.whitelist =

# ─── DATA DIRECTORY NOTE ─────────────────────────────────────────
# The app currently stores user data (users.json, neuromentor_data/)
# via os.path.dirname(os.path.abspath(__file__)) in app_state.py.
# This resolves to the app's private storage on Android, which works
# for debug builds. For production, consider migrating to
# App.get_running_app().user_data_dir for proper Android-friendly
# persistent storage.
# ──────────────────────────────────────────────────────────────────

# (str) python-for-android branch to use
p4a.branch = master

# (str) The directory in which python-for-android should look for local recipes
p4a.local_recipes = ./p4a_recipes

# (str) Bootstrap to use for android builds
# p4a.bootstrap = sdl2

# (str) Extra build arguments for python-for-android
# p4a.extra_args =

#
# ─── iOS SETTINGS (not used) ─────────────────────────────────────
#

# (str) Path to a custom kivy-ios folder
# ios.kivy_ios_dir = ../kivy-ios
# ios.kivy_ios_branch = master

#
# ─── BUILDOZER SETTINGS ──────────────────────────────────────────
#

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
