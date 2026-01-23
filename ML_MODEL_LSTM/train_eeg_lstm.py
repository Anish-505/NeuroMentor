"""
EEG LSTM Model Training Script
==============================
Trains an LSTM model to predict the next EEG reading based on the previous 10.
Used for real-time glitch detection in homemade EEG hardware.
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
from keras.layers import LSTM, Dense
from keras.callbacks import EarlyStopping

# Configuration
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'Synthetic_EEG_Data.csv')
OUTPUT_DIR = os.path.dirname(__file__)
LOOKBACK = 45
PREDICTION_HORIZON = 1
LSTM_UNITS = 50
EPOCHS = 50
BATCH_SIZE = 64
TEST_SPLIT = 0.2
GLITCH_MULTIPLIER = 4  # MAE * this = glitch threshold

# EEG Band columns
EEG_BANDS = ['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']


def load_and_group_data(csv_path):
    """Load CSV and group by State."""
    print("Loading data...")
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows with states: {df['State'].unique()}")
    
    grouped = {state: df[df['State'] == state][EEG_BANDS].values 
               for state in df['State'].unique()}
    
    return grouped


def normalize_data(grouped_data):
    """Apply MinMaxScaler per state, return normalized data and scalers."""
    print("Normalizing data per state...")
    scalers = {}
    normalized_data = {}
    
    for state, data in grouped_data.items():
        scaler = MinMaxScaler(feature_range=(0, 1))
        normalized_data[state] = scaler.fit_transform(data)
        scalers[state] = scaler
        print(f"  {state}: {len(data)} samples normalized")
    
    return normalized_data, scalers


def create_sequences(data, lookback=10):
    """Create sliding window sequences for LSTM.
    
    X: shape (samples, lookback, features)
    y: shape (samples, features) - next timestep prediction
    """
    X, y = [], []
    for i in range(len(data) - lookback):
        X.append(data[i:i + lookback])
        y.append(data[i + lookback])
    return np.array(X), np.array(y)


def prepare_all_sequences(normalized_data, lookback=10, test_split=0.2):
    """Create sequences for all states and combine."""
    all_X_train, all_y_train = [], []
    all_X_test, all_y_test = [], []
    test_data_by_state = {}  # For visualization
    
    for state, data in normalized_data.items():
        X, y = create_sequences(data, lookback)
        
        # Split into train/test
        split_idx = int(len(X) * (1 - test_split))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        all_X_train.append(X_train)
        all_y_train.append(y_train)
        all_X_test.append(X_test)
        all_y_test.append(y_test)
        
        test_data_by_state[state] = (X_test, y_test)
        
        print(f"  {state}: Train={len(X_train)}, Test={len(X_test)}")
    
    # Combine all states
    X_train = np.concatenate(all_X_train, axis=0)
    y_train = np.concatenate(all_y_train, axis=0)
    X_test = np.concatenate(all_X_test, axis=0)
    y_test = np.concatenate(all_y_test, axis=0)
    
    # Shuffle training data
    shuffle_idx = np.random.permutation(len(X_train))
    X_train, y_train = X_train[shuffle_idx], y_train[shuffle_idx]
    
    return X_train, y_train, X_test, y_test, test_data_by_state


def build_lstm_model(input_shape, output_shape):
    """Build LSTM model for next-step prediction."""
    print(f"Building LSTM model: input_shape={input_shape}, output_shape={output_shape}")
    
    model = Sequential([
        LSTM(LSTM_UNITS, input_shape=input_shape, return_sequences=False),
        Dense(output_shape)
    ])
    
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    model.summary()
    
    return model


def calculate_thresholds(model, X_test, y_test, multiplier=4):
    """Calculate MAE per band and glitch thresholds."""
    print("Calculating glitch thresholds...")
    
    predictions = model.predict(X_test, verbose=0)
    
    # Calculate MAE per band
    mae_per_band = {}
    thresholds = {}
    
    for i, band in enumerate(EEG_BANDS):
        abs_errors = np.abs(y_test[:, i] - predictions[:, i])
        mae = np.mean(abs_errors)
        mae_per_band[band] = float(mae)
        thresholds[band] = float(mae * multiplier)
        print(f"  {band}: MAE={mae:.6f}, Threshold={mae * multiplier:.6f}")
    
    return mae_per_band, thresholds, predictions


def visualize_predictions(y_actual, y_pred, state_name, band_idx=3, num_samples=100):
    """Plot Actual vs Predicted for a band (default: Beta)."""
    band_name = EEG_BANDS[band_idx]
    
    plt.figure(figsize=(14, 5))
    plt.plot(y_actual[:num_samples, band_idx], label='Actual', linewidth=2, marker='o', markersize=3)
    plt.plot(y_pred[:num_samples, band_idx], label='Predicted', linewidth=2, linestyle='--', marker='x', markersize=3)
    
    plt.title(f'{band_name} Wave: Actual vs Predicted ({state_name} State)', fontsize=14)
    plt.xlabel('Sample Index', fontsize=12)
    plt.ylabel(f'{band_name} (Normalized)', fontsize=12)
    plt.legend(loc='upper right', fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    save_path = os.path.join(OUTPUT_DIR, 'visualize_predictions.png')
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Visualization saved to: {save_path}")


def main():
    print("=" * 60)
    print("EEG LSTM Model Training for Glitch Detection")
    print("=" * 60)
    
    # Step 1: Load and group data
    grouped_data = load_and_group_data(DATA_PATH)
    
    # Step 2: Normalize per state
    normalized_data, scalers = normalize_data(grouped_data)
    
    # Step 3: Create sequences
    print("\nCreating sliding window sequences...")
    X_train, y_train, X_test, y_test, test_by_state = prepare_all_sequences(
        normalized_data, lookback=LOOKBACK, test_split=TEST_SPLIT
    )
    print(f"\nTotal: X_train={X_train.shape}, y_train={y_train.shape}")
    print(f"Total: X_test={X_test.shape}, y_test={y_test.shape}")
    
    # Step 4: Build and train model
    print("\n" + "=" * 60)
    model = build_lstm_model(
        input_shape=(LOOKBACK, len(EEG_BANDS)),
        output_shape=len(EEG_BANDS)
    )
    
    early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    
    print("\nTraining model...")
    history = model.fit(
        X_train, y_train,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_split=0.1,
        callbacks=[early_stop],
        verbose=1
    )
    
    # Step 5: Calculate thresholds
    print("\n" + "=" * 60)
    mae_per_band, thresholds, predictions = calculate_thresholds(
        model, X_test, y_test, multiplier=GLITCH_MULTIPLIER
    )
    
    # Step 6: Visualize on Focused state Beta wave
    print("\n" + "=" * 60)
    if 'Focused' in test_by_state:
        X_focused, y_focused = test_by_state['Focused']
        preds_focused = model.predict(X_focused, verbose=0)
        visualize_predictions(y_focused, preds_focused, 'Focused', band_idx=3, num_samples=100)
    else:
        # Fallback to first available state
        first_state = list(test_by_state.keys())[0]
        X_first, y_first = test_by_state[first_state]
        preds_first = model.predict(X_first, verbose=0)
        visualize_predictions(y_first, preds_first, first_state, band_idx=3, num_samples=100)
    
    # Step 7: Save artifacts
    print("\n" + "=" * 60)
    print("Saving artifacts...")
    
    # Save model
    model_path = os.path.join(OUTPUT_DIR, 'eeg_lstm_model.keras')
    model.save(model_path)
    print(f"  Model saved: {model_path}")
    
    # Save scalers (dictionary of scalers per state)
    scaler_path = os.path.join(OUTPUT_DIR, 'eeg_scaler.pkl')
    with open(scaler_path, 'wb') as f:
        pickle.dump(scalers, f)
    print(f"  Scalers saved: {scaler_path}")
    
    # Save thresholds
    thresholds_path = os.path.join(OUTPUT_DIR, 'eeg_thresholds.json')
    thresholds_data = {
        'mae_per_band': mae_per_band,
        'glitch_thresholds': thresholds,
        'glitch_multiplier': GLITCH_MULTIPLIER,
        'bands': EEG_BANDS
    }
    with open(thresholds_path, 'w') as f:
        json.dump(thresholds_data, f, indent=2)
    print(f"  Thresholds saved: {thresholds_path}")
    
    print("\n" + "=" * 60)
    print("Training complete!")
    print("=" * 60)
    
    return model, scalers, thresholds


if __name__ == '__main__':
    main()
