"""
1Hz EEG LSTM Model Training Script
===================================
Trains an LSTM model on FFT-processed EEG data (1 sample/second).
Uses 60-second lookback to predict the next second's values.
Optimized for large datasets (~300k rows per state).
"""

import os
# Set Keras backend to JAX before importing keras
os.environ['KERAS_BACKEND'] = 'jax'

import numpy as np
import pandas as pd
import pickle
import json
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense, BatchNormalization
from keras.callbacks import EarlyStopping, ReduceLROnPlateau

# =============================================================================
# CONFIGURATION
# =============================================================================
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'Synthetic_EEG_Data.csv')
OUTPUT_DIR = os.path.dirname(__file__)

# Model Hyperparameters
LOOKBACK = 60          # 60 seconds of history (optimal for 1Hz data)
LSTM_UNITS = 64        # LSTM layer units
DENSE_UNITS = 32       # Hidden dense layer units
EPOCHS = 50            # Max epochs (early stopping will likely trigger before)
BATCH_SIZE = 2048      # Large batch for 300k+ rows dataset
TEST_SPLIT = 0.2       # 20% held out for validation
GLITCH_MULTIPLIER = 4  # Threshold = MAE * this value

# EEG Band columns
EEG_BANDS = ['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']


# =============================================================================
# DATA LOADING & PREPROCESSING
# =============================================================================
def load_and_group_data(csv_path):
    """Load CSV and group by State."""
    print("=" * 60)
    print("Loading data...")
    df = pd.read_csv(csv_path)
    
    states = df['State'].unique()
    print(f"Dataset: {len(df):,} total rows")
    print(f"States found: {list(states)}")
    
    grouped = {}
    for state in states:
        state_data = df[df['State'] == state][EEG_BANDS].values
        grouped[state] = state_data
        print(f"  {state}: {len(state_data):,} rows")
    
    return grouped


def normalize_data(grouped_data):
    """Apply MinMaxScaler per state. Returns normalized data and scalers."""
    print("\n" + "=" * 60)
    print("Normalizing data per state (0-1 range)...")
    
    scalers = {}
    normalized_data = {}
    
    for state, data in grouped_data.items():
        scaler = MinMaxScaler(feature_range=(0, 1))
        normalized_data[state] = scaler.fit_transform(data)
        scalers[state] = scaler
        
        # Show min/max per band for verification
        print(f"\n  {state}:")
        for i, band in enumerate(EEG_BANDS):
            print(f"    {band}: min={data[:, i].min():.2f}, max={data[:, i].max():.2f}")
    
    return normalized_data, scalers


def create_sequences(data, lookback=60):
    """
    Create sliding window sequences.
    
    Input: (samples, lookback, 5 features)
    Target: (samples, 5 features) - next timestep
    """
    X, y = [], []
    for i in range(len(data) - lookback):
        X.append(data[i:i + lookback])
        y.append(data[i + lookback])
    return np.array(X), np.array(y)


def prepare_all_sequences(normalized_data, lookback=60, test_split=0.2):
    """Create sequences for all states and combine into train/test sets."""
    print("\n" + "=" * 60)
    print(f"Creating sliding window sequences (lookback={lookback})...")
    
    all_X_train, all_y_train = [], []
    all_X_test, all_y_test = [], []
    test_data_by_state = {}
    
    for state, data in normalized_data.items():
        X, y = create_sequences(data, lookback)
        
        # Split: first 80% train, last 20% test (preserving temporal order)
        split_idx = int(len(X) * (1 - test_split))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        all_X_train.append(X_train)
        all_y_train.append(y_train)
        all_X_test.append(X_test)
        all_y_test.append(y_test)
        
        test_data_by_state[state] = (X_test, y_test)
        
        print(f"  {state}: Train={len(X_train):,}, Test={len(X_test):,}")
    
    # Combine all states
    X_train = np.concatenate(all_X_train, axis=0)
    y_train = np.concatenate(all_y_train, axis=0)
    X_test = np.concatenate(all_X_test, axis=0)
    y_test = np.concatenate(all_y_test, axis=0)
    
    # Shuffle training data (important for mixed-state batches)
    shuffle_idx = np.random.permutation(len(X_train))
    X_train, y_train = X_train[shuffle_idx], y_train[shuffle_idx]
    
    print(f"\nTotal Training: {X_train.shape[0]:,} sequences")
    print(f"Total Testing:  {X_test.shape[0]:,} sequences")
    print(f"Input shape:    {X_train.shape[1:]} (lookback, features)")
    print(f"Output shape:   {y_train.shape[1:]} (features)")
    
    return X_train, y_train, X_test, y_test, test_data_by_state


# =============================================================================
# MODEL BUILDING
# =============================================================================
def build_model(input_shape, output_units):
    """
    Build LSTM model with BatchNormalization for FFT-processed data.
    
    Architecture:
        LSTM(64) -> BatchNormalization -> Dense(32, ReLU) -> Dense(5)
    """
    print("\n" + "=" * 60)
    print("Building LSTM model...")
    print(f"  Input shape:  {input_shape}")
    print(f"  Output units: {output_units}")
    
    model = Sequential([
        LSTM(LSTM_UNITS, input_shape=input_shape, return_sequences=False),
        BatchNormalization(),
        Dense(DENSE_UNITS, activation='relu'),
        Dense(output_units)
    ])
    
    model.compile(
        optimizer='adam',
        loss='mse',
        metrics=['mae']
    )
    
    print("\nModel Summary:")
    model.summary()
    
    return model


# =============================================================================
# THRESHOLD CALCULATION
# =============================================================================
def calculate_thresholds(model, X_test, y_test, multiplier=4):
    """Calculate MAE per band and derive glitch thresholds."""
    print("\n" + "=" * 60)
    print("Calculating glitch thresholds...")
    
    predictions = model.predict(X_test, verbose=0, batch_size=BATCH_SIZE)
    
    mae_per_band = {}
    thresholds = {}
    
    print(f"\n  {'Band':<8} {'MAE':>10} {'Threshold (MAE×{})':>20}".format(multiplier))
    print("  " + "-" * 40)
    
    for i, band in enumerate(EEG_BANDS):
        abs_errors = np.abs(y_test[:, i] - predictions[:, i])
        mae = float(np.mean(abs_errors))
        threshold = float(mae * multiplier)
        
        mae_per_band[band] = mae
        thresholds[band] = threshold
        
        print(f"  {band:<8} {mae:>10.6f} {threshold:>20.6f}")
    
    return mae_per_band, thresholds, predictions


# =============================================================================
# VISUALIZATION
# =============================================================================
def visualize_predictions(y_actual, y_pred, state_name, band_idx=3, num_samples=200):
    """Plot Actual vs Predicted for a specific band."""
    band_name = EEG_BANDS[band_idx]
    
    plt.figure(figsize=(16, 5))
    
    x = np.arange(num_samples)
    plt.plot(x, y_actual[:num_samples, band_idx], 
             label='Actual', linewidth=1.5, alpha=0.8)
    plt.plot(x, y_pred[:num_samples, band_idx], 
             label='Predicted', linewidth=1.5, linestyle='--', alpha=0.8)
    
    plt.fill_between(x, 
                     y_actual[:num_samples, band_idx], 
                     y_pred[:num_samples, band_idx],
                     alpha=0.2, color='red', label='Error')
    
    plt.title(f'{band_name} Wave: Actual vs Predicted ({state_name} State) - 60s Lookback Model', 
              fontsize=14, fontweight='bold')
    plt.xlabel('Sample Index (seconds)', fontsize=12)
    plt.ylabel(f'{band_name} (Normalized 0-1)', fontsize=12)
    plt.legend(loc='upper right', fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    save_path = os.path.join(OUTPUT_DIR, 'predictions_1hz.png')
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\nVisualization saved: {save_path}")


# =============================================================================
# MAIN TRAINING FUNCTION
# =============================================================================
def main():
    print("\n" + "=" * 60)
    print("  1Hz EEG LSTM MODEL TRAINING")
    print("  Lookback: 60 seconds | Batch Size: 2048")
    print("=" * 60)
    
    # Step 1: Load and group data by state
    grouped_data = load_and_group_data(DATA_PATH)
    
    # Step 2: Normalize per state
    normalized_data, scalers = normalize_data(grouped_data)
    
    # Step 3: Create sequences
    X_train, y_train, X_test, y_test, test_by_state = prepare_all_sequences(
        normalized_data, 
        lookback=LOOKBACK, 
        test_split=TEST_SPLIT
    )
    
    # Step 4: Build model
    model = build_model(
        input_shape=(LOOKBACK, len(EEG_BANDS)),
        output_units=len(EEG_BANDS)
    )
    
    # Step 5: Train with callbacks
    print("\n" + "=" * 60)
    print("Training model...")
    
    callbacks = [
        EarlyStopping(
            monitor='val_loss', 
            patience=5, 
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
            min_lr=1e-6,
            verbose=1
        )
    ]
    
    history = model.fit(
        X_train, y_train,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_split=0.1,
        callbacks=callbacks,
        verbose=1
    )
    
    # Step 6: Calculate thresholds
    mae_per_band, thresholds, predictions = calculate_thresholds(
        model, X_test, y_test, multiplier=GLITCH_MULTIPLIER
    )
    
    # Step 7: Visualize (Beta wave on Focused state)
    print("\n" + "=" * 60)
    print("Generating visualization...")
    
    if 'Focused' in test_by_state:
        X_vis, y_vis = test_by_state['Focused']
        preds_vis = model.predict(X_vis, verbose=0, batch_size=BATCH_SIZE)
        visualize_predictions(y_vis, preds_vis, 'Focused', band_idx=3, num_samples=200)
    else:
        first_state = list(test_by_state.keys())[0]
        X_vis, y_vis = test_by_state[first_state]
        preds_vis = model.predict(X_vis, verbose=0, batch_size=BATCH_SIZE)
        visualize_predictions(y_vis, preds_vis, first_state, band_idx=3, num_samples=200)
    
    # Step 8: Save artifacts
    print("\n" + "=" * 60)
    print("Saving artifacts...")
    
    # Save model
    model_path = os.path.join(OUTPUT_DIR, 'eeg_1hz_model.keras')
    model.save(model_path)
    print(f"  ✓ Model: {model_path}")
    
    # Save scalers
    scaler_path = os.path.join(OUTPUT_DIR, 'eeg_1hz_scaler.pkl')
    with open(scaler_path, 'wb') as f:
        pickle.dump(scalers, f)
    print(f"  ✓ Scalers: {scaler_path}")
    
    # Save thresholds
    thresholds_path = os.path.join(OUTPUT_DIR, 'eeg_1hz_thresholds.json')
    thresholds_data = {
        'lookback': LOOKBACK,
        'mae_per_band': mae_per_band,
        'glitch_thresholds': thresholds,
        'glitch_multiplier': GLITCH_MULTIPLIER,
        'bands': EEG_BANDS
    }
    with open(thresholds_path, 'w') as f:
        json.dump(thresholds_data, f, indent=2)
    print(f"  ✓ Thresholds: {thresholds_path}")
    
    print("\n" + "=" * 60)
    print("  TRAINING COMPLETE!")
    print("=" * 60)
    
    # Summary
    print(f"\nFinal Validation Loss: {history.history['val_loss'][-1]:.6f}")
    print(f"Final Validation MAE:  {history.history['val_mae'][-1]:.6f}")
    print(f"\nGlitch Detection Thresholds (MAE × {GLITCH_MULTIPLIER}):")
    for band, thresh in thresholds.items():
        print(f"  {band}: {thresh:.6f}")
    
    return model, scalers, thresholds


if __name__ == '__main__':
    main()
