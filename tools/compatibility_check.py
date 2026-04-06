"""
NeuroMentor — Pipeline × Model Compatibility Diagnostic
========================================================
Standalone tool that verifies the EXG sensor data pipeline
is fully aligned with the saved Random Forest model.

Run standalone:
    python -m tools.compatibility_check

Or call from app code:
    from tools.compatibility_check import run_compatibility_check
    output_text = run_compatibility_check()
"""
import os
import sys
import math
import glob
import traceback
from io import StringIO

# ---------------------------------------------------------------------------
# Ensure project root is on path so we can import services/
# ---------------------------------------------------------------------------
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# ---------------------------------------------------------------------------
# Import project modules (read-only — never modify them)
# ---------------------------------------------------------------------------
from services.rf_classifier import EegBands, RFClassifier, FEATURE_NAMES

try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False

try:
    import joblib
    _HAS_JOBLIB = True
except ImportError:
    _HAS_JOBLIB = False

# ═══════════════════════════════════════════════════════════════════════════
# DSP PIPELINE CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════
# These mirror the standard NeuroMentor EXG pipeline.  Because
# dsp_pipeline.py does not yet exist in the Kivy codebase, we define
# the canonical values here so every check is self-contained.
# When dsp_pipeline.py is eventually added these MUST be kept in sync.
# ═══════════════════════════════════════════════════════════════════════════

# ADC conversion — ADS1299 defaults
ADC_BITS       = 24
VREF           = 4.5         # Volts
PGA_GAIN       = 24
ADC_RESOLUTION = (2 ** (ADC_BITS - 1)) - 1  # 8388607

# Sampling & windowing
SAMPLE_RATE    = 250         # Hz
WINDOW_SIZE    = 256         # samples
OVERLAP        = 128         # samples

# Standard clinical EEG bands (Hz)
BAND_BOUNDARIES = {
    'delta': (0.5,  4.0),
    'theta': (4.0,  8.0),
    'alpha': (8.0, 13.0),
    'beta':  (13.0, 30.0),
    'gamma': (30.0, 45.0),
}

# Expected classifier labels
EXPECTED_LABELS = ['Baseline', 'Focused', 'Stressed']

# ---------------------------------------------------------------------------
# Counters
# ---------------------------------------------------------------------------
_pass = 0
_fail = 0
_warn = 0
_fail_details: list = []
_buf = StringIO()


def _p(msg: str = ''):
    """Print to both stdout and buffer."""
    print(msg)
    _buf.write(msg + '\n')


def _PASS(msg: str):
    global _pass
    _pass += 1
    _p(f'  ✓ PASS   {msg}')


def _FAIL(msg: str):
    global _fail
    _fail += 1
    _fail_details.append(msg)
    _p(f'  ✗ FAIL   {msg}')


def _WARN(msg: str):
    global _warn
    _warn += 1
    _p(f'  ⚠ WARN   {msg}')


def _header(title: str):
    _p('')
    _p('─' * 60)
    _p(f'  {title}')
    _p('─' * 60)


# ═══════════════════════════════════════════════════════════════════════════
# CHECK GROUP 1: ADC CONVERSION
# ═══════════════════════════════════════════════════════════════════════════

def _check_adc_conversion():
    _header('CHECK 1 — ADC CONVERSION')

    scale = (VREF / ADC_RESOLUTION / PGA_GAIN) * 1e6  # µV per count

    full_scale_uv = ADC_RESOLUTION * scale
    mid_scale_uv  = (ADC_RESOLUTION // 2) * scale

    _p(f'  ADC bits          : {ADC_BITS}')
    _p(f'  VREF              : {VREF} V')
    _p(f'  PGA gain          : {PGA_GAIN}')
    _p(f'  ADC resolution    : {ADC_RESOLUTION}')
    _p(f'  µV per count      : {scale:.6f}')
    _p(f'  Full-scale output : {full_scale_uv:.2f} µV')
    _p(f'  Mid-scale output  : {mid_scale_uv:.2f} µV')

    # Full-scale must be within absolute EEG range (1 – 500 µV is generous;
    # the ADC full-scale will be much larger — that is expected because the
    # ADC can represent larger signals.  What matters is that the *scale
    # factor* is correct, i.e. a typical 50 µV scalp signal uses a
    # meaningful portion of the ADC range.)
    if 100 < full_scale_uv < 300_000:
        _PASS(f'Full-scale {full_scale_uv:.2f} µV is within sensor range')
    else:
        _FAIL(f'Full-scale {full_scale_uv:.2f} µV is outside expected sensor range')

    # Mid-scale should be within a broadly reasonable range
    if 50 < mid_scale_uv < 150_000:
        _PASS(f'Mid-scale {mid_scale_uv:.2f} µV is within reasonable range')
    else:
        _FAIL(f'Mid-scale {mid_scale_uv:.2f} µV is outside expected range')

    # Check that 50 µV (typical scalp EEG) maps to a sensible ADC count
    counts_for_50uv = 50.0 / scale
    if counts_for_50uv >= 1:
        _PASS(f'50 µV signal → {counts_for_50uv:.1f} ADC counts (resolvable)')
    else:
        _FAIL(f'50 µV signal → {counts_for_50uv:.4f} ADC counts (too few — cannot resolve)')


# ═══════════════════════════════════════════════════════════════════════════
# CHECK GROUP 2: SAMPLE RATE AND WINDOW
# ═══════════════════════════════════════════════════════════════════════════

def _check_sample_rate_and_window():
    _header('CHECK 2 — SAMPLE RATE & WINDOW')

    nyquist = SAMPLE_RATE / 2.0
    freq_res = SAMPLE_RATE / WINDOW_SIZE  # Hz per bin
    highest_band = max(hi for _, hi in BAND_BOUNDARIES.values())

    _p(f'  Sample rate       : {SAMPLE_RATE} Hz')
    _p(f'  Window size       : {WINDOW_SIZE} samples')
    _p(f'  Overlap           : {OVERLAP} samples')
    _p(f'  Nyquist frequency : {nyquist} Hz')
    _p(f'  FFT resolution    : {freq_res:.4f} Hz/bin')
    _p(f'  Highest band edge : {highest_band} Hz')

    # Nyquist covers highest band
    if nyquist >= highest_band:
        _PASS(f'Nyquist {nyquist} Hz ≥ highest band edge {highest_band} Hz')
    else:
        _FAIL(f'Nyquist {nyquist} Hz < highest band edge {highest_band} Hz — aliasing!')

    # Frequency resolution fine enough to separate adjacent boundaries
    all_edges = sorted(set(
        edge for lo, hi in BAND_BOUNDARIES.values() for edge in (lo, hi)
    ))
    min_gap = min(b - a for a, b in zip(all_edges, all_edges[1:]))
    if freq_res <= min_gap:
        _PASS(f'Freq resolution {freq_res:.4f} Hz ≤ min band gap {min_gap} Hz')
    else:
        _FAIL(f'Freq resolution {freq_res:.4f} Hz > min band gap {min_gap} Hz — bins fall between bands')

    # Overlap < window
    if OVERLAP < WINDOW_SIZE:
        _PASS(f'Overlap {OVERLAP} < window size {WINDOW_SIZE}')
    else:
        _FAIL(f'Overlap {OVERLAP} ≥ window size {WINDOW_SIZE}')


# ═══════════════════════════════════════════════════════════════════════════
# CHECK GROUP 3: BAND BOUNDARY ALIGNMENT
# ═══════════════════════════════════════════════════════════════════════════

def _check_band_boundaries():
    _header('CHECK 3 — BAND BOUNDARY ALIGNMENT')

    freq_res = SAMPLE_RATE / WINDOW_SIZE
    freqs = [i * freq_res for i in range(WINDOW_SIZE // 2 + 1)]

    for name, (lo, hi) in BAND_BOUNDARIES.items():
        bins_in_band = [f for f in freqs if lo <= f < hi]
        n_bins = len(bins_in_band)

        # Check if lo and hi land on (or very near) an FFT bin edge
        lo_snap = min(freqs, key=lambda f: abs(f - lo))
        hi_snap = min(freqs, key=lambda f: abs(f - hi))
        lo_err = abs(lo_snap - lo)
        hi_err = abs(hi_snap - hi)

        aligned = lo_err < freq_res / 2 and hi_err < freq_res / 2

        if aligned:
            _PASS(f'{name:6s}  {lo:5.1f}–{hi:5.1f} Hz  bins={n_bins}  (aligned)')
        else:
            _WARN(f'{name:6s}  {lo:5.1f}–{hi:5.1f} Hz  bins={n_bins}  (lo_err={lo_err:.3f}, hi_err={hi_err:.3f})')

        if n_bins < 4:
            _WARN(f'{name:6s}  only {n_bins} bins — power estimate unreliable')


# ═══════════════════════════════════════════════════════════════════════════
# CHECK GROUP 4: SYNTHETIC SIGNAL END-TO-END
# ═══════════════════════════════════════════════════════════════════════════

def _compute_band_powers_fft(signal, sample_rate, window_size):
    """Compute band powers from a signal using the same FFT approach the
    live pipeline will use.  Returns dict of band→power."""
    if not _HAS_NUMPY:
        return {}

    # Hann window + FFT
    window = np.hanning(window_size)
    windowed = signal[:window_size] * window
    spectrum = np.fft.rfft(windowed)
    psd = (np.abs(spectrum) ** 2) / window_size
    freqs = np.fft.rfftfreq(window_size, d=1.0 / sample_rate)

    powers = {}
    for name, (lo, hi) in BAND_BOUNDARIES.items():
        mask = (freqs >= lo) & (freqs < hi)
        powers[name] = float(np.sum(psd[mask]))

    return powers


def _check_synthetic_signals():
    _header('CHECK 4 — SYNTHETIC SIGNAL END-TO-END')

    if not _HAS_NUMPY:
        _FAIL('numpy not available — cannot run synthetic signal tests')
        return

    test_cases = [
        (2,  'delta'),
        (6,  'theta'),
        (10, 'alpha'),
        (20, 'beta'),
        (40, 'gamma'),
    ]

    t = np.arange(WINDOW_SIZE) / SAMPLE_RATE
    all_ok = True

    for freq_hz, expected_band in test_cases:
        signal = np.sin(2 * np.pi * freq_hz * t)
        powers = _compute_band_powers_fft(signal, SAMPLE_RATE, WINDOW_SIZE)

        dominant = max(powers, key=powers.get)
        vals = '  '.join(f'{k}={v:.4f}' for k, v in powers.items())

        if dominant == expected_band:
            _PASS(f'{freq_hz:2d} Hz → dominates {dominant:6s}   [{vals}]')
        else:
            _FAIL(f'{freq_hz:2d} Hz → expected {expected_band}, got {dominant}   [{vals}]')
            all_ok = False

    return all_ok


# ═══════════════════════════════════════════════════════════════════════════
# CHECK GROUP 5: FEATURE VECTOR CONSISTENCY
# ═══════════════════════════════════════════════════════════════════════════

def _check_feature_vector():
    _header('CHECK 5 — FEATURE VECTOR CONSISTENCY')

    if not _HAS_NUMPY:
        _FAIL('numpy not available — cannot build feature vector')
        return None

    # Use 10 Hz alpha sine → compute band powers
    t = np.arange(WINDOW_SIZE) / SAMPLE_RATE
    signal = np.sin(2 * np.pi * 10 * t)
    powers = _compute_band_powers_fft(signal, SAMPLE_RATE, WINDOW_SIZE)

    bands = EegBands(
        delta=powers.get('delta', 0.0),
        theta=powers.get('theta', 0.0),
        alpha=powers.get('alpha', 0.0),
        beta=powers.get('beta', 0.0),
        gamma=powers.get('gamma', 0.0),
    )

    clf = RFClassifier()
    fv = clf.build_feature_vector(bands)

    expected_len = len(FEATURE_NAMES)

    _p(f'  Expected feature count : {expected_len}')
    _p(f'  Actual feature count   : {len(fv)}')

    if len(fv) == expected_len:
        _PASS(f'Feature vector length {len(fv)} matches FEATURE_NAMES ({expected_len})')
    else:
        _FAIL(f'Feature vector length {len(fv)} ≠ FEATURE_NAMES ({expected_len})')

    has_nan = any(math.isnan(v) for v in fv)
    has_inf = any(math.isinf(v) for v in fv)
    all_finite = all(math.isfinite(v) for v in fv)
    all_nonneg = all(v >= 0 or not math.isfinite(v) for v in fv)  # ratios can be 0

    if not has_nan:
        _PASS('No NaN values in feature vector')
    else:
        _FAIL('Feature vector contains NaN values')

    if not has_inf:
        _PASS('No Inf values in feature vector')
    else:
        _FAIL('Feature vector contains Inf values')

    if all_finite:
        _PASS('All values are finite')
    else:
        _FAIL('Feature vector contains non-finite values')

    # Report feature values
    _p('')
    _p('  Feature vector values:')
    for name, val in zip(FEATURE_NAMES, fv):
        sign = '  ' if val >= 0 else ''
        _p(f'    {name:20s} = {sign}{val:.8f}')

    return fv


# ═══════════════════════════════════════════════════════════════════════════
# CHECK GROUP 6: SAVED MODEL FILE
# ═══════════════════════════════════════════════════════════════════════════

def _find_model_directories():
    """Find all model directories (user-specific and bundled)."""
    data_dir = os.path.join(_PROJECT_ROOT, 'neuromentor_data')
    bundled_dir = os.path.normpath(os.path.join(_PROJECT_ROOT, '..', 'rf_model', 'rf_model'))

    dirs = []

    # User-specific model dirs
    if os.path.isdir(data_dir):
        for entry in os.listdir(data_dir):
            full = os.path.join(data_dir, entry)
            if os.path.isdir(full) and entry.endswith('_rf_model'):
                model_file = os.path.join(full, 'rf_eeg_model.pkl')
                if os.path.exists(model_file):
                    dirs.append(('user', entry, full))

    # Bundled model
    bundled_model = os.path.join(bundled_dir, 'rf_eeg_model.pkl')
    if os.path.exists(bundled_model):
        dirs.append(('bundled', 'rf_model', bundled_dir))

    return dirs


def _check_saved_model(feature_vector):
    _header('CHECK 6 — SAVED MODEL FILES')

    if not _HAS_NUMPY or not _HAS_JOBLIB:
        _FAIL('numpy/joblib not available — cannot inspect model files')
        return

    model_dirs = _find_model_directories()

    if not model_dirs:
        _WARN('No model files found.')
        _p('  → Complete a calibration session, then re-run this check.')
        _p('  → Expected locations:')
        _p(f'     neuromentor_data/<user>_rf_model/rf_eeg_model.pkl')
        _p(f'     ../rf_model/rf_model/rf_eeg_model.pkl')
        return

    expected_n_features = len(FEATURE_NAMES)

    for source, label, dirpath in model_dirs:
        _p('')
        _p(f'  ── Model: {label} ({source}) ──')
        _p(f'  Path: {dirpath}')

        model_path   = os.path.join(dirpath, 'rf_eeg_model.pkl')
        scaler_path  = os.path.join(dirpath, 'rf_scaler.pkl')
        encoder_path = os.path.join(dirpath, 'rf_encoder.pkl')

        # Load model
        try:
            clf = joblib.load(model_path)
            _PASS(f'rf_eeg_model.pkl loads without error')
        except Exception as e:
            _FAIL(f'rf_eeg_model.pkl failed to load: {e}')
            continue

        # Load scaler
        try:
            scaler = joblib.load(scaler_path)
            _PASS(f'rf_scaler.pkl loads without error')
        except Exception as e:
            _FAIL(f'rf_scaler.pkl failed to load: {e}')
            continue

        # Load encoder (optional but expected)
        encoder = None
        if os.path.exists(encoder_path):
            try:
                encoder = joblib.load(encoder_path)
                _PASS(f'rf_encoder.pkl loads without error')
            except Exception as e:
                _WARN(f'rf_encoder.pkl failed to load: {e}')

        # Check clf.n_features_in_
        clf_n = getattr(clf, 'n_features_in_', None)
        if clf_n is not None:
            if clf_n == expected_n_features:
                _PASS(f'clf.n_features_in_ = {clf_n} matches feature vector ({expected_n_features})')
            else:
                _FAIL(f'clf.n_features_in_ = {clf_n} ≠ feature vector ({expected_n_features})')
        else:
            _WARN('clf.n_features_in_ not available')

        # Check scaler.n_features_in_
        scaler_n = getattr(scaler, 'n_features_in_', None)
        if scaler_n is not None:
            if scaler_n == expected_n_features:
                _PASS(f'scaler.n_features_in_ = {scaler_n} matches feature vector ({expected_n_features})')
            else:
                _FAIL(f'scaler.n_features_in_ = {scaler_n} ≠ feature vector ({expected_n_features})')
        else:
            _WARN('scaler.n_features_in_ not available')

        # Check classes
        clf_classes = getattr(clf, 'classes_', None)
        n_classes = getattr(clf, 'n_classes_', None)

        if encoder is not None:
            # The trained model uses integer labels; encoder maps them back
            decoded_classes = sorted(encoder.inverse_transform(clf_classes).tolist()) if clf_classes is not None else []
            expected_sorted = sorted(EXPECTED_LABELS)

            if n_classes is not None:
                if n_classes == len(EXPECTED_LABELS):
                    _PASS(f'clf.n_classes_ = {n_classes} matches expected ({len(EXPECTED_LABELS)})')
                else:
                    _FAIL(f'clf.n_classes_ = {n_classes} ≠ expected ({len(EXPECTED_LABELS)})')

            if decoded_classes == expected_sorted:
                _PASS(f'clf.classes_ (decoded) = {decoded_classes}')
            else:
                _FAIL(f'clf.classes_ (decoded) = {decoded_classes}, expected {expected_sorted}')
        else:
            # No encoder — classes are raw
            if clf_classes is not None:
                _p(f'  clf.classes_ (raw) = {list(clf_classes)}')
            if n_classes is not None:
                if n_classes == len(EXPECTED_LABELS):
                    _PASS(f'clf.n_classes_ = {n_classes}')
                else:
                    _FAIL(f'clf.n_classes_ = {n_classes} ≠ expected {len(EXPECTED_LABELS)}')

        # Scaler transform
        if feature_vector is not None:
            try:
                X = np.array([feature_vector])
                X_scaled = scaler.transform(X)
                _PASS('scaler.transform() succeeded')

                max_abs = float(np.max(np.abs(X_scaled)))
                _p(f'  Max |scaled value| : {max_abs:.4f}')
                if max_abs <= 10.0:
                    _PASS(f'Max |scaled value| {max_abs:.4f} ≤ 10 — amplitude scale consistent')
                else:
                    _WARN(f'Max |scaled value| {max_abs:.4f} > 10 — possible amplitude scale mismatch')

                # Predict
                try:
                    pred = clf.predict(X_scaled)
                    pred_label = pred[0]
                    if encoder is not None:
                        pred_label = encoder.inverse_transform(pred)[0]
                    pred_label = str(pred_label)

                    if pred_label in EXPECTED_LABELS:
                        _PASS(f'clf.predict() → "{pred_label}" (valid label)')
                    else:
                        _FAIL(f'clf.predict() → "{pred_label}" (not in expected labels)')
                except Exception as e:
                    _FAIL(f'clf.predict() failed: {e}')

                # Predict proba
                try:
                    proba = clf.predict_proba(X_scaled)[0]
                    prob_sum = float(np.sum(proba))
                    if abs(prob_sum - 1.0) < 1e-6:
                        _PASS(f'predict_proba() sums to {prob_sum:.6f} (≈1.0)')
                    else:
                        _FAIL(f'predict_proba() sums to {prob_sum:.6f} (≠1.0)')
                except Exception as e:
                    _FAIL(f'clf.predict_proba() failed: {e}')

            except Exception as e:
                _FAIL(f'scaler.transform() failed: {e}')

        # Report scaler means
        scaler_mean = getattr(scaler, 'mean_', None)
        if scaler_mean is not None:
            _p('')
            _p('  Scaler mean per feature position:')
            for i, m in enumerate(scaler_mean):
                name = FEATURE_NAMES[i] if i < len(FEATURE_NAMES) else f'idx_{i}'
                _p(f'    [{i:2d}] {name:20s} = {m:.8f}')


# ═══════════════════════════════════════════════════════════════════════════
# CHECK GROUP 7: VERSION DRIFT DETECTION
# ═══════════════════════════════════════════════════════════════════════════

def _check_version_drift():
    _header('CHECK 7 — VERSION DRIFT DETECTION')

    model_dirs = _find_model_directories()

    if not model_dirs:
        _WARN('No model files to check for version drift.')
        return

    if not _HAS_JOBLIB:
        _FAIL('joblib not available — cannot inspect models')
        return

    current_names = list(FEATURE_NAMES)

    for source, label, dirpath in model_dirs:
        _p(f'  ── Model: {label} ({source}) ──')

        # The RFClassifier stores _feature_names on the instance, but
        # it is NOT persisted inside the pkl files.  We check for a
        # feature_names.txt sidecar or any attribute on the saved clf.
        model_path = os.path.join(dirpath, 'rf_eeg_model.pkl')
        try:
            clf = joblib.load(model_path)
        except Exception:
            _WARN(f'Cannot load model at {model_path}')
            continue

        saved_names = getattr(clf, 'feature_names_in_', None)
        if saved_names is None:
            # Try sidecar file
            sidecar = os.path.join(dirpath, 'feature_names.txt')
            if os.path.exists(sidecar):
                with open(sidecar) as f:
                    saved_names = [line.strip() for line in f if line.strip()]

        if saved_names is not None:
            saved_list = list(saved_names)
            if saved_list == current_names:
                _PASS(f'Feature names match current FEATURE_NAMES')
            else:
                _FAIL('Feature name mismatch detected:')
                for i, (s, c) in enumerate(zip(saved_list, current_names)):
                    if s != c:
                        _p(f'    [{i}] model="{s}"  current="{c}"')
                if len(saved_list) != len(current_names):
                    _p(f'    Length mismatch: model={len(saved_list)} current={len(current_names)}')
        else:
            _WARN(f'Model does not store feature names — version drift cannot be auto-detected.')
            _p('  → Recommend adding feature name storage to RFClassifier.save()')
            _p(f'  → Current FEATURE_NAMES: {current_names}')


# ═══════════════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════════════

def _print_summary():
    _p('')
    _p('═' * 60)
    _p('  COMPATIBILITY CHECK SUMMARY')
    _p('═' * 60)
    total = _pass + _fail + _warn
    _p(f'  Total checks  : {total}')
    _p(f'  Passed        : {_pass}')
    _p(f'  Failed        : {_fail}')
    _p(f'  Warnings      : {_warn}')

    if _fail_details:
        _p('')
        _p('  ── FAILED CHECKS ──')
        for i, detail in enumerate(_fail_details, 1):
            _p(f'  {i}. {detail}')

    _p('')
    if _fail == 0:
        _p('  ╔══════════════════════════════════════════════════╗')
        _p('  ║   VERDICT: COMPATIBLE                           ║')
        _p('  ║   Safe to run live classification.               ║')
        _p('  ╚══════════════════════════════════════════════════╝')
    else:
        _p('  ╔══════════════════════════════════════════════════╗')
        _p('  ║   VERDICT: INCOMPATIBLE                         ║')
        _p('  ║   Fix issues above before connecting hardware.   ║')
        _p('  ╚══════════════════════════════════════════════════╝')
    _p('')


# ═══════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════

def run_compatibility_check() -> str:
    """Run all checks and return the full output as a string.

    This is the entry point for both standalone use and in-app integration.
    """
    global _pass, _fail, _warn, _fail_details, _buf
    _pass = 0
    _fail = 0
    _warn = 0
    _fail_details = []
    _buf = StringIO()

    _p('╔════════════════════════════════════════════════════════╗')
    _p('║  NEUROMENTOR PIPELINE × MODEL COMPATIBILITY DIAGNOSTIC ║')
    _p('╚════════════════════════════════════════════════════════╝')

    try:
        _check_adc_conversion()
    except Exception as e:
        _FAIL(f'ADC conversion check crashed: {e}')

    try:
        _check_sample_rate_and_window()
    except Exception as e:
        _FAIL(f'Sample rate check crashed: {e}')

    try:
        _check_band_boundaries()
    except Exception as e:
        _FAIL(f'Band boundary check crashed: {e}')

    try:
        _check_synthetic_signals()
    except Exception as e:
        _FAIL(f'Synthetic signal check crashed: {e}')

    fv = None
    try:
        fv = _check_feature_vector()
    except Exception as e:
        _FAIL(f'Feature vector check crashed: {e}')

    try:
        _check_saved_model(fv)
    except Exception as e:
        _FAIL(f'Saved model check crashed: {e}')

    try:
        _check_version_drift()
    except Exception as e:
        _FAIL(f'Version drift check crashed: {e}')

    _print_summary()

    return _buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
# STANDALONE ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    run_compatibility_check()
