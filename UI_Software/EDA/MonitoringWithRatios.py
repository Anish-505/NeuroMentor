# Import necessary libraries:
# - serial: for communicating with the ESP32 over the USB port.
# - time: for handling delays and pauses.
# - os: for checking if files exist.
# - pandas: for powerful and easy data analysis.
import serial
import time
import os
import pandas as pd

# =================================================================
# User Configuration
# =================================================================
# Set the COM port your ESP32 is connected to.
# On Windows, this looks like 'COM12'. On macOS/Linux, it might be '/dev/tty.usbserial-XXXX'.
COM_PORT = 'COM12'
# Set the baud rate for serial communication. This must match the rate in the ESP32 code.
BAUD_RATE = 115200
# Define the file path where the one-time calibration dataset will be saved.
CALIBRATION_FILE = r"C:\Users\ankit\OneDrive\Documents\Personal\Repls\Complete code\Random Python\NeuroMentor\Resource files\EEG_Dataset_Faizan.csv"
# Define the file path for logging all live readings during the monitoring phase.
LIVE_READINGS_FILE = r"C:\Users\ankit\OneDrive\Documents\Personal\Repls\Complete code\Random Python\NeuroMentor\Resource files\EEG_Readings_Faizan.csv"
# Set a timeout for the entire calibration process to prevent the script from hanging.
CALIBRATION_TIMEOUT_S = (20 * 3 * 60) + 300 # 61 minutes for sessions + 4 min buffer

# --- Multi-Criteria Alerting Thresholds for Higher Reliability ---
# An alert is triggered only if BOTH the power and ratio conditions are met. 

# -- For STRESS detection --
# 1. The live Beta/Alpha ratio must be 20% higher than the calibrated "Stressed" ratio.
STRESS_RATIO_THRESHOLD = 1.2
# 2. The live Beta power must ALSO be 10% higher than the calibrated "Stressed" Beta power.
STRESS_POWER_THRESHOLD = 1.1

# -- For FOCUS LOSS detection --
# 1. The live Alpha/Theta ratio must be 20% lower than the calibrated "Focused" ratio.
FOCUS_RATIO_THRESHOLD = 0.8
# 2. The live Alpha power must ALSO be 10% lower than the calibrated "Focused" Alpha power.
FOCUS_POWER_THRESHOLD = 0.9

# =================================================================
# Global Variables
# =================================================================
# This global variable will hold the calculated average PSD power values from the calibration phase.
# It acts as the system's "memory" of your personal brainwave patterns.
baseline_psd = None
# This global variable will hold the calculated heuristic ratios from the calibration phase.
baseline_ratios = None

# =================================================================
# Core Functions
# =================================================================

def get_serial_connection():
    """Establishes and returns a serial connection object."""
    try:
        # Initialize the serial connection. The timeout is important for readline() not to block forever.
        ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=2)
        # A short pause to allow the ESP32 to reset after the connection is established.
        time.sleep(2)
        # Flush any garbage data that might be in the input buffer from a previous run.
        ser.flushInput()
        print(f"[INFO] Successfully connected to {COM_PORT}")
        return ser
    except serial.SerialException as e:
        # If the connection fails, print a fatal error message and return None.
        print(f"[FATAL] Could not open serial port {COM_PORT}: {e}")
        return None

def run_calibration_stream(ser):
    """
    Manages the calibration phase by listening to the real-time data stream,
    saving it, and then calculating the baseline PSD and Ratio values.
    """
    # Declare that we intend to modify the global variables from within this function.
    global baseline_psd, baseline_ratios
    print("\n" + "="*60)
    print("      PHASE 1: Starting Device Calibration (via Real-time Stream)      ")
    print("="*60)
    
    # Command the ESP32 to start the calibration process. `\n` is crucial.
    ser.write(b'start_calibration\n')
    
    try:
        # Open the local CSV file in write mode. The 'with' statement ensures it's closed properly.
        with open(CALIBRATION_FILE, 'w', newline='') as f:
            # Manually write the header row for our CSV file.
            f.write("State,Delta,Theta,Alpha,Beta,Gamma\n")
            print("[INFO] Listening for calibration data stream... This will take ~61 minutes.")
            
            # This is the main listening loop for the calibration phase.
            while True:
                # Read one line from the serial port. `decode` converts bytes to a string.
                line = ser.readline().decode('utf-8').strip()
                # If the line is empty (due to a timeout), skip and try again.
                if not line: continue
                
                # Check if the line is a special message (an "event marker") from the ESP32.
                if line.startswith("EVENT:"):
                    print(f"[DEVICE STATUS] {line}")
                    # The "Calibration Complete" event is our signal to stop listening.
                    if "Calibration Complete" in line: break
                # Check if the line is a valid data line (it should contain 5 commas).
                elif line.count(',') == 5:
                    # If it's data, write it to our local file.
                    f.write(line + '\n')
                    # Update the user's console on a single line to show that data is flowing.
                    print(f"\r[DATA] Receiving and saving calibration reading...", end="")
        
        print(f"\n[SUCCESS] Calibration stream finished. Data saved to {CALIBRATION_FILE}")
    except Exception as e:
        print(f"\n[ERROR] An error occurred during the calibration stream: {e}")
        return False # Return False to indicate that calibration failed.

    # --- Analyze the saved data to establish the baseline PSD and Ratios ---
    try:
        # Use pandas to read the CSV file we just created.
        df = pd.read_csv(CALIBRATION_FILE)
        
        # 1. Calculate and store the average Power Spectral Density (PSD).
        # This groups the dataframe by "State" and calculates the mean for each brainwave column.
        baseline_psd = df.groupby('State')[['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']].mean()
        
        # 2. Calculate and store the key heuristic Ratios from the PSD data.
        epsilon = 1e-9 # A small number to prevent division by zero errors.
        baseline_ratios = {
            'stress': baseline_psd.loc['Stressed', 'Beta'] / (baseline_psd.loc['Stressed', 'Alpha'] + epsilon),
            'focus': baseline_psd.loc['Focused', 'Alpha'] / (baseline_psd.loc['Focused', 'Theta'] + epsilon)
        }
        
        # Print the results of the analysis for the user to see.
        print("\n--- Calculated Baseline PSD Values ---")
        print(baseline_psd)
        print("\n--- Calculated Baseline Ratio Values ---")
        print(f"  Calibrated Stress Index (Beta/Alpha): {baseline_ratios['stress']:.2f}")
        print(f"  Calibrated Focus Index (Alpha/Theta): {baseline_ratios['focus']:.2f}")
        print("----------------------------------------")
        return True # Return True to indicate calibration was successful.
    except Exception as e:
        print(f"[ERROR] Could not analyze the saved calibration file: {e}")
        return False

def run_live_monitoring(ser):
    """
    Manages the live monitoring phase with multi-criteria alerting.
    This function runs an infinite loop until the user stops it.
    """
    print("\n" + "="*60)
    print("      PHASE 2: Starting Live Monitoring      ")
    print("="*60)
    
    # Command the ESP32 to start streaming live, unlabeled data.
    ser.write(b'start_live_monitoring\n')
    # Read and discard the "OK" confirmation message from the ESP32.
    ser.readline()

    print("[INFO] Now receiving live data. Press Ctrl+C to stop.")
    # Check if the live log file already exists to decide whether to write a header.
    header_written = os.path.exists(LIVE_READINGS_FILE)

    # This is the main infinite loop for live monitoring.
    while True:
        try:
            # Read a line of live data from the ESP32.
            line = ser.readline().decode('utf-8').strip()
            
            # Only process the line if it's a valid "Live" data line.
            if line and line.startswith("Live"):
                # Log the raw reading to the live readings file for later review.
                with open(LIVE_READINGS_FILE, 'a', newline='') as f:
                    if not header_written:
                        f.write("State,Delta,Theta,Alpha,Beta,Gamma\n")
                        header_written = True
                    f.write(line + '\n')
                
                # --- Step 1: Parse live data and calculate live ratios ---
                parts = line.split(',')
                live_data = {'Alpha': float(parts[3]), 'Beta': float(parts[4]), 'Theta': float(parts[2])}
                epsilon = 1e-9
                live_stress_index = live_data['Beta'] / (live_data['Alpha'] + epsilon)
                live_focus_index = live_data['Alpha'] / (live_data['Theta'] + epsilon)

                # --- Step 2: Perform Multi-Criteria Alerting Logic ---
                status = "State: CALM" # Assume the default state is calm.

                # -- Check for STRESS --
                # Condition 1: Is the live Beta/Alpha ratio significantly higher than the calibrated value?
                ratio_stress_cond = live_stress_index > (baseline_ratios['stress'] * STRESS_RATIO_THRESHOLD)
                # Condition 2: Is the live Beta power ALSO significantly higher than the calibrated value?
                power_stress_cond = live_data['Beta'] > (baseline_psd.loc['Stressed', 'Beta'] * STRESS_POWER_THRESHOLD)
                
                # An alert is only triggered if BOTH conditions are true.
                if ratio_stress_cond and power_stress_cond:
                    status = "State: STRESSED! (High Beta Power & Ratio)"

                # -- Check for FOCUS LOSS --
                # Condition 1: Is the live Alpha/Theta ratio significantly lower than the calibrated value?
                ratio_focus_loss_cond = live_focus_index < (baseline_ratios['focus'] * FOCUS_RATIO_THRESHOLD)
                # Condition 2: Is the live Alpha power ALSO significantly lower than the calibrated value?
                power_focus_loss_cond = live_data['Alpha'] < (baseline_psd.loc['Focused', 'Alpha'] * FOCUS_POWER_THRESHOLD)

                # An alert is only triggered if BOTH conditions are true.
                if ratio_focus_loss_cond and power_focus_loss_cond:
                    status = "State: LOSING FOCUS (Low Alpha Power & Ratio)"
                
                # A simple check for a positive focused state.
                elif live_focus_index > (baseline_ratios['focus'] * 1.1):
                    status = "State: FOCUSED (High Alpha/Theta Ratio)"

                # Print the determined status to the console, updating on a single line.
                print(f"\r{status.ljust(50)}", end="")

        # This `except` block handles the user pressing Ctrl+C to stop the script.
        except KeyboardInterrupt:
            ser.write(b'stop\n') # Command the ESP32 to stop streaming and go idle.
            print("\n[INFO] Stopping live monitor...")
            break # Exit the infinite `while` loop.
        # This `except` block catches any other minor errors (e.g., a corrupted serial line)
        # and simply ignores them, preventing the script from crashing.
        except:
            pass

# =================================================================
# Main Execution Block
# =================================================================
# This code only runs when the script is executed directly (not imported as a module).
if __name__ == "__main__":
    # First, establish the serial connection.
    ser = get_serial_connection()
    
    # Proceed only if the connection was successful.
    if ser:
        # First, run the calibration process. This must succeed to proceed.
        if run_calibration_stream(ser):
            # If calibration is successful, then proceed to the live monitoring phase.
            run_live_monitoring(ser)
        
        # After everything is finished (or failed), close the serial connection.
        ser.close()
        print("\n[INFO] Session ended. Serial connection closed.")