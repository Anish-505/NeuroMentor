# NeuroMentor — Android APK Build Guide

Complete step-by-step instructions for building the NeuroMentor Kivy app
into a debug APK installable on any Android device (Android 8.0 / API 26+).

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Environment Setup](#environment-setup)
3. [First Time Build](#first-time-build)
4. [Installing on Device](#installing-on-device)
5. [Common Errors and Fixes](#common-errors-and-fixes)
6. [Subsequent Builds](#subsequent-builds)
7. [Project-Specific Notes](#project-specific-notes)

---

## System Requirements

### Operating System

- **Ubuntu 20.04 or 22.04** (recommended)
- **WSL2 on Windows** (Ubuntu 22.04 from Microsoft Store)
- macOS is NOT supported by Buildozer for Android builds

### Software Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.10+ | System python or pyenv-managed |
| Java JDK | 17 | OpenJDK recommended |
| Git | 2.x+ | For cloning p4a and SDK repos |
| pip | 23+ | Latest stable |

### System Packages (Ubuntu/Debian)

Install all required system dependencies in one command:

```bash
sudo apt update && sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    git \
    zip \
    unzip \
    openjdk-17-jdk \
    autoconf \
    libtool \
    pkg-config \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libtinfo5 \
    cmake \
    libffi-dev \
    libssl-dev \
    automake \
    ccache \
    lld
```

### For WSL2 on Windows

1. Open PowerShell as Administrator:
   ```powershell
   wsl --install -d Ubuntu-22.04
   ```
2. Launch Ubuntu from Start Menu
3. Run the `apt install` command above inside WSL2
4. Navigate to the project: `cd /mnt/c/Users/anish/Desktop/work/nm-git/NeuroMentor/flutter/Kivy_Section/neuro_mentor_kivy`

---

## Environment Setup

### 1. Install Buildozer

```bash
pip install --upgrade buildozer
```

Verify installation:

```bash
buildozer version
```

### 2. Install python-for-android (optional, buildozer downloads automatically)

```bash
pip install --upgrade python-for-android
```

### 3. Set Environment Variables (optional)

If you already have the Android SDK/NDK installed, set these environment variables.
If not, **buildozer will download them automatically** during the first build.

```bash
# Add to ~/.bashrc or ~/.profile
export ANDROID_SDK_ROOT=$HOME/.buildozer/android/platform/android-sdk
export ANDROID_NDK_ROOT=$HOME/.buildozer/android/platform/android-ndk-r25b
export PATH=$PATH:$ANDROID_SDK_ROOT/platform-tools
```

Reload:

```bash
source ~/.bashrc
```

### 4. Accept Android SDK Licenses

This is handled automatically by `buildozer.spec` with:

```
android.accept_sdk_license = True
```

If you need to accept manually:

```bash
$ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager --licenses
```

---

## First Time Build

### What the First Build Does

The first build will:

1. Download the Android SDK (~2 GB)
2. Download the Android NDK r25b (~1.5 GB)
3. Download and compile python-for-android
4. Build all Python dependencies (numpy, scikit-learn, etc.) from source for ARM64
5. Package everything into an APK

### Expected Disk Space

**Approximately 8–12 GB** for the full build toolchain and intermediate files.

### Expected Build Time

| Hardware | First Build | Subsequent Builds |
|----------|------------|-------------------|
| 4-core CPU, 8 GB RAM | 30–60 minutes | 5–10 minutes |
| 8-core CPU, 16 GB RAM | 15–30 minutes | 2–5 minutes |
| CI/CD (GitHub Actions) | 20–40 minutes | 5–15 minutes |

### Run the Build

#### Option A: Using the build script

```bash
chmod +x build_apk.sh
./build_apk.sh
```

#### Option B: Manual commands

```bash
# Clean previous build
buildozer android clean

# Build debug APK
buildozer android debug
```

### Build Output

The APK will be created at:

```
bin/neuromentor-1.0.0-arm64-v8a_armeabi-v7a-debug.apk
```

(Exact filename may vary based on version and target architectures.)

---

## Installing on Device

### 1. Enable Developer Options on Android

1. Open **Settings** → **About Phone**
2. Tap **Build Number** 7 times
3. A toast will say "You are now a developer!"

### 2. Enable USB Debugging

1. Open **Settings** → **Developer Options**
2. Enable **USB Debugging**
3. When prompted on the phone, tap **Allow** for your computer

### 3. Connect Device and Install

```bash
# Check device is connected
adb devices

# Install the APK (-r replaces existing installation)
adb install -r bin/neuromentor-*-debug.apk
```

### 4. If adb Does Not Detect the Device

1. **Try a different USB cable** — some cables are charge-only
2. **Check USB mode** — pull down the notification shade and ensure "File Transfer" or "MTP" is selected
3. **Install USB drivers** (Windows only) — download from your phone manufacturer's website
4. **Restart adb server**:
   ```bash
   adb kill-server
   adb start-server
   adb devices
   ```
5. **Authorize the computer** — check the phone for a USB debugging authorization prompt

---

## Common Errors and Fixes

### Build Fails on scikit-learn

**Symptom**: Build error during scikit-learn compilation, errors about missing headers or failed C extensions.

**Fix**: The project includes a custom p4a recipe at `p4a_recipes/scikit_learn/__init__.py` that handles cross-compilation. If it fails:

1. Ensure `scipy` and `cython` are in requirements (they are dependencies)
2. Try pinning a specific scikit-learn version in the recipe
3. As a last resort, build without scikit-learn and use a pre-trained model:
   - Remove `scikit-learn` from `requirements` in `buildozer.spec`
   - The app will still load models via `joblib` but cannot retrain

### jnius Import Error on Desktop

**Symptom**: `ImportError: No module named 'jnius'` when running on desktop.

**This is expected.** The `from jnius import autoclass` call in `main.py` is wrapped in a `try/except ImportError` block. It silently skips on desktop. No fix needed.

### Bluetooth Permission Denied on Device

**Symptom**: App crashes or BLE scanning fails with permission error.

**Fix**:
1. Go to **Settings** → **Apps** → **NeuroMentor** → **Permissions**
2. Grant **Location** (required for BLE scanning on Android 6+)
3. Grant **Nearby devices** (Android 12+)
4. On Android 12+, ensure `BLUETOOTH_SCAN` and `BLUETOOTH_CONNECT` are granted

### App Crashes on Launch

**Symptom**: App installs but immediately closes.

**Fix**: Read the logcat output to find the Python traceback:

```bash
# Full python-related logs
adb logcat | grep python

# More verbose (shows all Kivy logs)
adb logcat *:S python:D

# Save to file for analysis
adb logcat -d > logcat.txt
grep -A 20 "Traceback" logcat.txt
```

Common crash causes:
- Missing dependency — add it to `requirements` in `buildozer.spec`
- File not found — ensure file extensions are in `source.include_exts`
- Import error — check that all custom modules have `__init__.py` files

### numpy Version Conflict

**Symptom**: `ImportError` or `RuntimeError` about numpy version mismatch.

**Fix**: Pin the numpy version in `requirements`:

```
requirements = python3,kivy==2.3.0,pyjnius,numpy==1.24.4,joblib,scikit-learn
```

Use the same numpy version that was used to train the model. Check with:

```python
import numpy; print(numpy.__version__)
```

### Build Hangs at "Compiling..."

**Symptom**: Build process appears stuck during compilation of numpy or scikit-learn.

**Fix**: These packages take a long time to compile from source for ARM. Be patient (15-30 minutes). Ensure:
- At least 4 GB of free RAM
- Stable internet connection (for downloading sources)
- Check disk space: `df -h`

---

## Subsequent Builds

### Incremental Build (fastest)

When you've only changed Python source files:

```bash
buildozer android debug
```

This repackages the APK without recompiling native dependencies. Takes 2–5 minutes.

### Full Rebuild

When you've changed `requirements`, `buildozer.spec` settings, or p4a recipes:

```bash
buildozer android clean
buildozer android debug
```

### When a Full Rebuild Is Necessary

You **must** do a clean build when:

- Adding or removing a package from `requirements`
- Changing `android.api`, `android.minapi`, or `android.ndk`
- Changing `android.archs`
- Modifying any file in `p4a_recipes/`
- Upgrading buildozer or python-for-android

You **do not** need a clean build when:

- Editing Python source files (`.py`)
- Adding new `.py`, `.json`, `.kv`, or `.pkl` files
- Changing `android.permissions`
- Changing `title`, `version`, or `orientation`

---

## Project-Specific Notes

### Data Directory on Android

The app stores user data (profiles, RF models) in `neuromentor_data/` using paths
derived from `os.path.dirname(os.path.abspath(__file__))`. On Android, this resolves
to the app's private storage directory, which is correct for debug builds.

For production releases, consider updating `app_state.py` to use Kivy's
`App.get_running_app().user_data_dir` for proper Android-friendly persistent storage:

```python
# In app_state.py, replace:
#   self.users_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'users.json')
# With:
#   from kivy.app import App
#   data_dir = App.get_running_app().user_data_dir
#   self.users_file = os.path.join(data_dir, 'users.json')
```

### Icon and Presplash

The project does **not** currently include `icon.png` or `presplash.png`.

Before building, add these files to the project root:

- **icon.png** — 512×512 PNG, the app launcher icon
- **presplash.png** — 1080×1920 PNG, shown during app startup

Then uncomment these lines in `buildozer.spec`:

```ini
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png
```

### Model Files

Pre-trained RF model files (`rf_eeg_model.pkl`, `rf_scaler.pkl`, `rf_encoder.pkl`)
are bundled from the `neuromentor_data/` directory. Ensure `.pkl` is included in
`source.include_exts` (it is by default in this buildozer.spec).

### Scikit-learn on Android

Scikit-learn requires cross-compilation for Android ARM. This project includes a
custom p4a recipe at `p4a_recipes/scikit_learn/__init__.py` that:

1. Downloads scikit-learn 1.3.2 source
2. Disables OpenMP (not available on Android NDK)
3. Builds with `--no-build-isolation` to use p4a's numpy/scipy
4. Installs into the APK's Python environment

If scikit-learn compilation fails, the app can still run in inference-only mode
using pre-trained model files loaded via joblib.
