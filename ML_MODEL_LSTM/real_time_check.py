"""
Real-Time EEG Glitch Detection Script
======================================
Loads the trained LSTM model and checks if incoming EEG readings are valid
or represent sensor glitches.
"""

import os
# Set Keras backend to JAX before importing keras
os.environ['KERAS_BACKEND'] = 'jax'

import numpy as np
import pickle
import json
from keras.models import load_model

# Configuration
MODEL_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(MODEL_DIR, 'eeg_lstm_model.keras')
SCALER_PATH = os.path.join(MODEL_DIR, 'eeg_scaler.pkl')
THRESHOLDS_PATH = os.path.join(MODEL_DIR, 'eeg_thresholds.json')

# EEG Band columns (must match training)
EEG_BANDS = ['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']


class EEGGlitchDetector:
    """
    Real-time EEG glitch detector using LSTM predictions.
    
    Usage:
        detector = EEGGlitchDetector(state='Focused')
        
        # Last 45 readings (each reading is [Delta, Theta, Alpha, Beta, Gamma])
        last_45_readings = [...]
        
        # The actual 46th reading to validate
        new_reading = [delta, theta, alpha, beta, gamma]
        
        is_valid, details = detector.check_reading(last_45_readings, new_reading)
    """
    
    def __init__(self, state='Baseline', model_path=None, scaler_path=None, thresholds_path=None):
        """
        Initialize the detector.
        
        Args:
            state: The EEG state (Baseline, Focused, or Stressed)
            model_path: Path to the Keras model file
            scaler_path: Path to the scaler pickle file
            thresholds_path: Path to the thresholds JSON file
        """
        self.state = state
        
        # Use defaults if not specified
        model_path = model_path or MODEL_PATH
        scaler_path = scaler_path or SCALER_PATH
        thresholds_path = thresholds_path or THRESHOLDS_PATH
        
        # Load model
        print(f"Loading model from: {model_path}")
        self.model = load_model(model_path)
        
        # Load scalers (dictionary keyed by state)
        print(f"Loading scalers from: {scaler_path}")
        with open(scaler_path, 'rb') as f:
            self.scalers = pickle.load(f)
        
        if state not in self.scalers:
            available_states = list(self.scalers.keys())
            raise ValueError(f"State '{state}' not found. Available: {available_states}")
        
        self.scaler = self.scalers[state]
        
        # Load thresholds
        print(f"Loading thresholds from: {thresholds_path}")
        with open(thresholds_path, 'r') as f:
            self.thresholds_data = json.load(f)
        
        self.thresholds = self.thresholds_data['glitch_thresholds']
        self.mae_per_band = self.thresholds_data['mae_per_band']
        self.bands = self.thresholds_data['bands']
        
        print(f"Detector initialized for state: {state}")
        print(f"Glitch thresholds: {self.thresholds}")
    
    def normalize(self, readings):
        """Normalize readings using the state's scaler."""
        return self.scaler.transform(np.array(readings))
    
    def denormalize(self, normalized_readings):
        """Inverse transform normalized readings."""
        return self.scaler.inverse_transform(normalized_readings)
    
    def check_reading(self, last_45_readings, actual_next_reading):
        """
        Check if the actual next reading is valid or a glitch.
        
        Args:
            last_45_readings: List of 45 readings, each is [Delta, Theta, Alpha, Beta, Gamma]
            actual_next_reading: The actual 46th reading to validate [Delta, Theta, Alpha, Beta, Gamma]
        
        Returns:
            tuple: (is_valid: bool, details: dict)
                - is_valid: True if reading is valid, False if glitch
                - details: Dictionary with prediction, errors, and per-band glitch status
        """
        # Validate input shapes
        last_45 = np.array(last_45_readings)
        actual = np.array(actual_next_reading)
        
        if last_45.shape != (45, 5):
            raise ValueError(f"last_45_readings must be shape (45, 5), got {last_45.shape}")
        if actual.shape != (5,):
            raise ValueError(f"actual_next_reading must be shape (5,), got {actual.shape}")
        
        # Normalize the input
        normalized_input = self.normalize(last_45)
        normalized_actual = self.normalize([actual])[0]
        
        # Reshape for LSTM: (1, 45, 5)
        X = normalized_input.reshape(1, 45, 5)
        
        # Predict
        predicted_normalized = self.model.predict(X, verbose=0)[0]
        
        # Calculate errors (in normalized space)
        errors = np.abs(normalized_actual - predicted_normalized)
        
        # Check each band for glitch
        glitch_bands = {}
        for i, band in enumerate(self.bands):
            threshold = self.thresholds[band]
            is_glitch = errors[i] > threshold
            glitch_bands[band] = {
                'error': float(errors[i]),
                'threshold': threshold,
                'is_glitch': bool(is_glitch)
            }
        
        # Overall validity: no band should be a glitch
        is_valid = not any(band_info['is_glitch'] for band_info in glitch_bands.values())
        
        # Denormalize predictions for display
        predicted_original = self.denormalize([predicted_normalized])[0]
        
        details = {
            'is_valid': is_valid,
            'predicted': {band: float(predicted_original[i]) for i, band in enumerate(self.bands)},
            'actual': {band: float(actual[i]) for i, band in enumerate(self.bands)},
            'errors_normalized': {band: float(errors[i]) for i, band in enumerate(self.bands)},
            'band_analysis': glitch_bands
        }
        
        return is_valid, details


def demo():
    """Demonstrate the glitch detector with sample data."""
    print("\n" + "=" * 60)
    print("EEG Glitch Detector Demo")
    print("=" * 60)
    
    # Initialize detector
    detector = EEGGlitchDetector(state='Baseline')
    
    # Sample data: 45 "normal" baseline readings (first 45 from dataset)
    # Format: [Delta, Theta, Alpha, Beta, Gamma]
    sample_readings = [
        [9.6, 19.65, 23.16, 18.45, 5.44], [7.1, 9.68, 34.98, 15.03, 4.07],
        [7.65, 16.76, 33.38, 16.59, 4.63], [10.18, 14.32, 38.28, 24.46, 6.95],
        [8.52, 15.96, 29.56, 14.31, 3.94], [9.79, 11.57, 35.4, 13.42, 5.56],
        [8.42, 17.53, 32.93, 9.13, 5.75], [8.34, 22.41, 29.09, 25.14, 4.12],
        [9.31, 19.22, 42.4, 16.4, 5.63], [10.26, 13.58, 32.15, 24.85, 5.49],
        [9.83, 13.27, 34.88, 19.87, 5.14], [11.51, 8.8, 28.62, 25.86, 5.16],
        [7.78, 15.57, 34.21, 19.02, 5.63], [11.86, 18.14, 41.94, 17.36, 6.61],
        [15.55, 12.01, 42.66, 19.63, 3.45], [5.96, 13.21, 26.37, 16.29, 6.27],
        [10.87, 10.58, 42.91, 22.43, 5.49], [11.1, 16.95, 36.22, 16.42, 4.39],
        [9.93, 16.17, 32.24, 15.57, 4.77], [10.77, 10.08, 18.89, 12.41, 3.46],
        [12.68, 12.48, 30.91, 21.38, 3.03], [9.46, 17.59, 26.62, 21.24, 6.53],
        [11.01, 12.16, 24.47, 15.21, 5.01], [12.14, 21.01, 26.72, 27.34, 6.63],
        [9.96, 16.45, 34.63, 14.11, 5.82], [13.34, 15.45, 37.16, 20.17, 5.87],
        [10.93, 21.08, 31.41, 11.17, 6.72], [9.98, 19.44, 32.89, 24.83, 3.82],
        [11.05, 15.28, 31.07, 17.56, 4.71], [10.12, 14.54, 45.78, 13.73, 4.5],
        [10.29, 16.49, 38.07, 18.49, 4.87], [6.8, 17.95, 41.54, 23.08, 2.75],
        [8.79, 15.22, 36.89, 11.83, 3.26], [7.86, 16.81, 29.63, 17.06, 5.3],
        [10.02, 18.03, 30.55, 25.17, 5.92], [9.37, 13.94, 35.0, 19.42, 4.1],
        [10.73, 13.33, 39.14, 23.44, 3.59], [11.85, 16.33, 30.36, 13.27, 3.27],
        [11.76, 11.29, 26.31, 18.5, 4.18], [9.66, 11.01, 41.05, 24.42, 5.47],
        [12.34, 16.45, 29.51, 20.78, 5.1], [9.19, 15.19, 39.04, 12.08, 5.24],
        [8.32, 15.73, 37.25, 10.07, 7.02], [10.36, 15.09, 43.24, 14.23, 4.57],
        [10.97, 11.19, 41.26, 29.13, 6.33],
    ]
    
    # Test 1: Normal reading (likely valid)
    print("\n--- Test 1: Normal reading ---")
    normal_reading = [9.32, 14.46, 31.44, 16.29, 5.6]  # 46th value from dataset
    is_valid, details = detector.check_reading(sample_readings, normal_reading)
    print(f"Reading: {normal_reading}")
    print(f"Is Valid: {is_valid}")
    print(f"Predicted: {details['predicted']}")
    
    # Test 2: Glitch reading (extreme values)
    print("\n--- Test 2: Glitch reading (extreme values) ---")
    glitch_reading = [50.0, 5.0, 100.0, 0.0, 20.0]  # Unrealistic values
    is_valid, details = detector.check_reading(sample_readings, glitch_reading)
    print(f"Reading: {glitch_reading}")
    print(f"Is Valid: {is_valid}")
    print("Glitch Analysis:")
    for band, info in details['band_analysis'].items():
        if info['is_glitch']:
            print(f"  {band}: GLITCH! (error={info['error']:.4f} > threshold={info['threshold']:.4f})")
    
    return detector


if __name__ == '__main__':
    demo()
