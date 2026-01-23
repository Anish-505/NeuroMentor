"""
EEG Glitch Detector (1Hz Model)
================================
Inference script that loads the trained 1Hz LSTM model
and detects sensor glitches in real-time EEG readings.

Usage:
    from glitch_detector import EEGGlitchDetector
    
    detector = EEGGlitchDetector(state='Focused')
    
    # Pass 60 readings + 1 new reading to validate
    is_valid, details = detector.check_reading(last_60_readings, new_reading)
"""

import os
# Set Keras backend before importing keras
os.environ['KERAS_BACKEND'] = 'jax'

import numpy as np
import pickle
import json
from keras.models import load_model

# =============================================================================
# CONFIGURATION
# =============================================================================
MODEL_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(MODEL_DIR, 'eeg_1hz_model.keras')
SCALER_PATH = os.path.join(MODEL_DIR, 'eeg_1hz_scaler.pkl')
THRESHOLDS_PATH = os.path.join(MODEL_DIR, 'eeg_1hz_thresholds.json')

EEG_BANDS = ['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']
LOOKBACK = 60  # Must match training


# =============================================================================
# GLITCH DETECTOR CLASS
# =============================================================================
class EEGGlitchDetector:
    """
    Real-time EEG glitch detector using LSTM predictions.
    
    The detector predicts the next reading based on the previous 60 seconds
    and flags values that deviate more than 4x the Mean Absolute Error.
    
    Attributes:
        state: The EEG state for normalization (Baseline, Focused, Stressed)
        thresholds: Per-band error thresholds for glitch detection
    
    Example:
        detector = EEGGlitchDetector(state='Focused')
        
        # 60 previous readings, each is [Delta, Theta, Alpha, Beta, Gamma]
        history = [[9.6, 19.65, 23.16, 18.45, 5.44], ...]  # 60 rows
        
        # New reading to validate
        new_reading = [10.2, 18.3, 25.1, 20.0, 5.8]
        
        is_valid, details = detector.check_reading(history, new_reading)
        if not is_valid:
            print("GLITCH DETECTED!")
    """
    
    def __init__(self, state='Baseline', model_path=None, scaler_path=None, thresholds_path=None):
        """
        Initialize the glitch detector.
        
        Args:
            state: EEG state for normalization ('Baseline', 'Focused', or 'Stressed')
            model_path: Optional custom path to .keras model file
            scaler_path: Optional custom path to scaler .pkl file
            thresholds_path: Optional custom path to thresholds .json file
        """
        self.state = state
        self.lookback = LOOKBACK
        
        # Resolve paths
        model_path = model_path or MODEL_PATH
        scaler_path = scaler_path or SCALER_PATH
        thresholds_path = thresholds_path or THRESHOLDS_PATH
        
        # Load model
        print(f"Loading model: {os.path.basename(model_path)}")
        self.model = load_model(model_path)
        
        # Load scalers (dict keyed by state)
        print(f"Loading scalers: {os.path.basename(scaler_path)}")
        with open(scaler_path, 'rb') as f:
            self.scalers = pickle.load(f)
        
        if state not in self.scalers:
            available = list(self.scalers.keys())
            raise ValueError(f"State '{state}' not found. Available: {available}")
        
        self.scaler = self.scalers[state]
        
        # Load thresholds
        print(f"Loading thresholds: {os.path.basename(thresholds_path)}")
        with open(thresholds_path, 'r') as f:
            self.config = json.load(f)
        
        self.thresholds = self.config['glitch_thresholds']
        self.mae_per_band = self.config['mae_per_band']
        self.bands = self.config['bands']
        
        print(f"\n✓ Detector ready for state: {state}")
        print(f"  Lookback window: {self.lookback} seconds")
        print(f"  Glitch thresholds: {self.thresholds}")
    
    def normalize(self, data):
        """Normalize data using the state's scaler."""
        return self.scaler.transform(np.array(data))
    
    def denormalize(self, data):
        """Inverse transform normalized data back to original scale."""
        return self.scaler.inverse_transform(data)
    
    def check_reading(self, last_60_readings, actual_next_reading):
        """
        Check if a new EEG reading is valid or a glitch.
        
        Args:
            last_60_readings: List/array of shape (60, 5) containing the 
                              previous 60 seconds of EEG data.
                              Each row is [Delta, Theta, Alpha, Beta, Gamma].
            actual_next_reading: The new reading to validate, shape (5,).
                                 Format: [Delta, Theta, Alpha, Beta, Gamma].
        
        Returns:
            tuple: (is_valid, details)
                - is_valid (bool): True if reading is valid, False if glitch
                - details (dict): Prediction info, errors, and per-band analysis
        """
        # Validate inputs
        history = np.array(last_60_readings)
        actual = np.array(actual_next_reading)
        
        if history.shape != (60, 5):
            raise ValueError(
                f"Expected last_60_readings shape (60, 5), got {history.shape}"
            )
        if actual.shape != (5,):
            raise ValueError(
                f"Expected actual_next_reading shape (5,), got {actual.shape}"
            )
        
        # Normalize inputs
        history_norm = self.normalize(history)
        actual_norm = self.normalize([actual])[0]
        
        # Reshape for LSTM: (batch=1, timesteps=60, features=5)
        X = history_norm.reshape(1, 60, 5)
        
        # Predict
        predicted_norm = self.model.predict(X, verbose=0)[0]
        
        # Calculate normalized errors
        errors = np.abs(actual_norm - predicted_norm)
        
        # Analyze each band
        band_analysis = {}
        any_glitch = False
        
        for i, band in enumerate(self.bands):
            threshold = self.thresholds[band]
            is_glitch = errors[i] > threshold
            
            if is_glitch:
                any_glitch = True
            
            band_analysis[band] = {
                'error': float(errors[i]),
                'threshold': float(threshold),
                'is_glitch': bool(is_glitch)
            }
        
        # Denormalize predictions for human-readable output
        predicted_original = self.denormalize([predicted_norm])[0]
        
        details = {
            'is_valid': not any_glitch,
            'predicted': {b: float(predicted_original[i]) for i, b in enumerate(self.bands)},
            'actual': {b: float(actual[i]) for i, b in enumerate(self.bands)},
            'normalized_errors': {b: float(errors[i]) for i, b in enumerate(self.bands)},
            'band_analysis': band_analysis,
            'glitch_bands': [b for b, info in band_analysis.items() if info['is_glitch']]
        }
        
        return not any_glitch, details
    
    def is_valid_reading(self, last_60_readings, actual_next_reading):
        """
        Simplified boolean check - returns True for valid, False for glitch.
        
        This is a convenience method when you don't need detailed analysis.
        """
        is_valid, _ = self.check_reading(last_60_readings, actual_next_reading)
        return is_valid


# =============================================================================
# DEMO / TESTING
# =============================================================================
def demo():
    """Demonstrate the glitch detector with synthetic data."""
    import pandas as pd
    
    print("\n" + "=" * 60)
    print("  EEG GLITCH DETECTOR DEMO")
    print("=" * 60)
    
    # Load some real data for demo
    data_path = os.path.join(MODEL_DIR, 'data', 'Synthetic_EEG_Data.csv')
    
    if not os.path.exists(data_path):
        print(f"Demo data not found at: {data_path}")
        return
    
    df = pd.read_csv(data_path)
    baseline_data = df[df['State'] == 'Baseline'][EEG_BANDS].values
    
    # Initialize detector
    detector = EEGGlitchDetector(state='Baseline')
    
    # Test 1: Normal reading (61st value from dataset)
    print("\n" + "-" * 40)
    print("TEST 1: Normal Reading")
    print("-" * 40)
    
    history = baseline_data[0:60].tolist()  # First 60 rows
    normal_reading = baseline_data[60].tolist()  # 61st row
    
    is_valid, details = detector.check_reading(history, normal_reading)
    
    print(f"Input: 60 rows of Baseline data")
    print(f"New reading: {normal_reading}")
    print(f"Predicted:   {list(details['predicted'].values())}")
    print(f"\n→ Is Valid: {is_valid}")
    
    if not is_valid:
        print(f"  Glitch bands: {details['glitch_bands']}")
    
    # Test 2: Obvious glitch (extreme values)
    print("\n" + "-" * 40)
    print("TEST 2: Glitch Reading (Extreme Values)")
    print("-" * 40)
    
    glitch_reading = [100.0, 0.0, 200.0, -50.0, 50.0]  # Clearly wrong
    
    is_valid, details = detector.check_reading(history, glitch_reading)
    
    print(f"Input: Same 60 rows of Baseline data")
    print(f"Glitch reading: {glitch_reading}")
    print(f"Predicted:      {list(details['predicted'].values())}")
    print(f"\n→ Is Valid: {is_valid}")
    
    if not is_valid:
        print(f"  Glitch bands: {details['glitch_bands']}")
        print("\n  Per-band analysis:")
        for band, info in details['band_analysis'].items():
            status = "GLITCH!" if info['is_glitch'] else "OK"
            print(f"    {band}: error={info['error']:.4f}, "
                  f"threshold={info['threshold']:.4f} → {status}")
    
    return detector


if __name__ == '__main__':
    demo()
