#!/usr/bin/env bash
#
# build_apk.sh — NeuroMentor Android Debug APK Build Script
# ==========================================================
# Runs the full clean-build sequence and outputs the APK path.
#
# Usage:
#   chmod +x build_apk.sh
#   ./build_apk.sh
#
set -euo pipefail

echo "═══════════════════════════════════════════════════════════"
echo "  NeuroMentor — Android Debug APK Builder"
echo "═══════════════════════════════════════════════════════════"
echo ""

# ─── Step 1: Check that buildozer is installed ───────────────────
echo "[1/7] Checking buildozer installation..."
if ! command -v buildozer &> /dev/null; then
    echo "  buildozer not found. Installing via pip..."
    pip install --upgrade buildozer
    if ! command -v buildozer &> /dev/null; then
        echo "  ERROR: Failed to install buildozer."
        echo "  Install manually: pip install buildozer"
        exit 1
    fi
fi
BUILDOZER_VERSION=$(buildozer version 2>/dev/null || echo "unknown")
echo "  ✓ buildozer found (${BUILDOZER_VERSION})"

# ─── Step 2: Check Android SDK/NDK availability ─────────────────
echo ""
echo "[2/7] Checking Android SDK/NDK..."
if [ -n "${ANDROID_SDK_ROOT:-}" ]; then
    echo "  ✓ ANDROID_SDK_ROOT = ${ANDROID_SDK_ROOT}"
elif [ -n "${ANDROID_HOME:-}" ]; then
    echo "  ✓ ANDROID_HOME = ${ANDROID_HOME}"
    export ANDROID_SDK_ROOT="${ANDROID_HOME}"
else
    echo "  ⚠ ANDROID_SDK_ROOT not set."
    echo "    Buildozer will download the SDK automatically on first build."
    echo "    This requires ~8 GB of disk space and a stable internet connection."
fi

if [ -n "${ANDROID_NDK_ROOT:-}" ]; then
    echo "  ✓ ANDROID_NDK_ROOT = ${ANDROID_NDK_ROOT}"
else
    echo "  ⚠ ANDROID_NDK_ROOT not set."
    echo "    Buildozer will download the NDK automatically on first build."
fi

# ─── Step 3: Clean previous build ───────────────────────────────
echo ""
echo "[3/7] Cleaning previous build artifacts..."
buildozer android clean
echo "  ✓ Clean complete."

# ─── Step 4: Build debug APK ────────────────────────────────────
echo ""
echo "[4/7] Building debug APK... (this may take 10-30 minutes on first build)"
echo "  Running: buildozer android debug"
echo ""
buildozer android debug

# ─── Step 5: Find the output APK ────────────────────────────────
echo ""
echo "[5/7] Locating output APK..."
APK_PATH=$(find bin/ -name "*.apk" -type f 2>/dev/null | head -1)

if [ -z "${APK_PATH}" ]; then
    echo "  ERROR: No APK found in bin/ directory."
    echo "  Check the build output above for errors."
    exit 1
fi
echo "  ✓ APK found."

# ─── Step 6: Print APK info ─────────────────────────────────────
echo ""
echo "[6/7] APK Details:"
APK_SIZE=$(du -h "${APK_PATH}" | cut -f1)
APK_FULL=$(realpath "${APK_PATH}")
echo "  Path : ${APK_FULL}"
echo "  Size : ${APK_SIZE}"

# ─── Step 7: Installation instructions ──────────────────────────
echo ""
echo "[7/7] Installation Instructions:"
echo ""
echo "  Connect your Android device via USB with USB Debugging enabled, then run:"
echo ""
echo "    adb install -r ${APK_FULL}"
echo ""
echo "  If adb is not in your PATH, try:"
echo "    \${ANDROID_SDK_ROOT}/platform-tools/adb install -r ${APK_FULL}"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  BUILD COMPLETE ✓"
echo "═══════════════════════════════════════════════════════════"
