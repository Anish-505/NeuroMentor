import serial
import time
import os
import pandas as pd

# =================================================================
# User Configuration
# =================================================================
# Set the COM port your ESP32 is connected to.
COM_PORT = 'COM12'
# Set the baud rate (must match the ESP32 code).
BAUD_RATE = 115200
# IMPORTANT: This script REQUIRES a calibration file to exist.
# Set the path to the 'eeg_dataset.csv' file that was created by the full calibration script.
CALIBRATION_FILE = r"C:\Users\ankit\OneDrive\Documents\Personal\Repls\Complete code\Random Python\NeuroMentor\Resource files\EEG_Dataset_Faizan.csv"
# Define the file path for logging all live readings.
LIVE_READINGS_FILE = r"C:\Users\ankit\OneDrive\Documents\Personal\Repls\Complete code\Random Python\NeuroMentor\Resource files\EEG_Readings_Faizan.csv"

# --- Alerting Thresholds ---
# These values determine the sensitivity of the real-time alerts.
STRESS_RATIO_THRESHOLD = 1.2
STRESS_POWER_THRESHOLD = 1.1
FOCUS_RATIO_THRESHOLD = 0.8
FOCUS_POWER_THRESHOLD = 0.9

# ================================================================= 
# Global Variables
# =================================================================
# These will be populated by loading the existing calibration file.
baseline_psd = None
baseline_ratios = None

# =================================================================
# Core Functions
# =================================================================

def get_serial_connection():
    """Establishes and returns a serial connection object."""
    try:
        ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=2)
        time.sleep(2)
        ser.flushInput()
        print(f"[INFO] Successfully connected to {COM_PORT}")
        return ser
    except serial.SerialException as e:
        print(f"[FATAL] Could not open serial port {COM_PORT}: {e}")
        return None

def load_and_analyze_calibration():
    """
    Loads the pre-existing calibration file and calculates the necessary
    baseline values for live monitoring.
    """
    global baseline_psd, baseline_ratios
    print("="*60)
    print("      Loading Personal Calibration Profile      ")
    print("="*60)

    # Check if the required calibration file actually exists.
    if not os.path.exists(CALIBRATION_FILE):
        print(f"[FATAL ERROR] Calibration file not found at: {CALIBRATION_FILE}")
        print("[FATAL ERROR] Please run the full 'NeuroCalibrator_Streaming.py' script at least once to generate your personal baseline.")
        return False

    try:
        # Load the calibration data from the CSV file.
        df = pd.read_csv(CALIBRATION_FILE)
        
        # 1. Calculate and store the average Power Spectral Density (PSD).
        baseline_psd = df.groupby('State')[['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']].mean()
        
        # 2. Calculate and store the key heuristic Ratios from the PSD data.
        epsilon = 1e-9
        baseline_ratios = {
            'stress': baseline_psd.loc['Stressed', 'Beta'] / (baseline_psd.loc['Stressed', 'Alpha'] + epsilon),
            'focus': baseline_psd.loc['Focused', 'Alpha'] / (baseline_psd.loc['Focused', 'Theta'] + epsilon)
        }
        
        # Print the loaded baseline values for user confirmation.
        print("[SUCCESS] Calibration profile loaded successfully.")
        print("\n--- Loaded Baseline PSD Values ---")
        print(baseline_psd)
        print("\n--- Loaded Baseline Ratio Values ---")
        print(f"  Calibrated Stress Index (Beta/Alpha): {baseline_ratios['stress']:.2f}")
        print(f"  Calibrated Focus Index (Alpha/Theta): {baseline_ratios['focus']:.2f}")
        print("------------------------------------")
        return True # Return True to indicate success.
    except Exception as e:
        print(f"[ERROR] Could not analyze the calibration file: {e}")
        return False

def run_live_monitoring(ser):
    """
    Manages the live monitoring phase using the pre-loaded calibration data.
    """
    print("\n" + "="*60)
    print("      Starting Live Monitoring Session      ")
    print("="*60)
    
    # Command the ESP32 to start streaming live data.
    ser.write(b'start_live_monitoring\n')
    ser.readline() # Discard the "OK" confirmation message.

    print("[INFO] Now receiving live data. Press Ctrl+C to stop.")
    header_written = os.path.exists(LIVE_READINGS_FILE)

    # The main infinite loop for monitoring.
    while True:
        try:
            line = ser.readline().decode('utf-8').strip()
            if line and line.startswith("Live"):
                # Log the raw reading to the live readings file.
                with open(LIVE_READINGS_FILE, 'a', newline='') as f:
                    if not header_written:
                        f.write("State,Delta,Theta,Alpha,Beta,Gamma\n")
                        header_written = True
                    f.write(line + '\n')
                
                # --- Perform the multi-criteria analysis ---
                parts = line.split(',')
                live_data = {'Alpha': float(parts[3]), 'Beta': float(parts[4]), 'Theta': float(parts[2])}
                epsilon = 1e-9
                live_stress_index = live_data['Beta'] / (live_data['Alpha'] + epsilon)
                live_focus_index = live_data['Alpha'] / (live_data['Theta'] + epsilon)

                status = "State: CALM" # Default state.

                # -- Check for STRESS --
                ratio_stress_cond = live_stress_index > (baseline_ratios['stress'] * STRESS_RATIO_THRESHOLD)
                power_stress_cond = live_data['Beta'] > (baseline_psd.loc['Stressed', 'Beta'] * STRESS_POWER_THRESHOLD)
                
                if ratio_stress_cond and power_stress_cond:
                    status = "State: STRESSED! (High Beta Power & Ratio)"

                # -- Check for FOCUS LOSS --
                ratio_focus_loss_cond = live_focus_index < (baseline_ratios['focus'] * FOCUS_RATIO_THRESHOLD)
                power_focus_loss_cond = live_data['Alpha'] < (baseline_psd.loc['Focused', 'Alpha'] * FOCUS_POWER_THRESHOLD)

                if ratio_focus_loss_cond and power_focus_loss_cond:
                    status = "State: LOSING FOCUS (Low Alpha Power & Ratio)"
                
                elif live_focus_index > (baseline_ratios['focus'] * 1.1):
                    status = "State: FOCUSED (High Alpha/Theta Ratio)"

                # Print the live status, updating on a single line.
                print(f"\r{status.ljust(50)}", end="")

        except KeyboardInterrupt:
            ser.write(b'stop\n')
            print("\n[INFO] Stopping live monitor...")
            break
        except:
            pass

# =================================================================
# Main Execution Block
# =================================================================
if __name__ == "__main__":
    # The script now starts by loading the calibration data first.
    if load_and_analyze_calibration():
        # If the calibration data is loaded successfully, then connect to the device.
        ser = get_serial_connection()
        if ser:
            # If the connection is successful, start the live monitoring loop.
            run_live_monitoring(ser)
            ser.close() # Close the connection when done.
            print("\n[INFO] Session ended. Serial connection closed.")
