import serial
import time
import os
import pandas as pd

# =================================================================
# User Configuration
# =================================================================
# Set the COM port your ESP32 is connected to.
COM_PORT = 'COM3'
# Set the baud rate. This must match the rate in the ESP32 code (115200).
BAUD_RATE = 115200
# Define the file path to save the one-time calibration dataset.
CALIBRATION_FILE = r"C:\Users\ankit\OneDrive\Documents\Personal\Repls\Complete code\Random Python\NeuroMentor\Resource files\EEG_Dataset.csv"
# Define the file path for logging all live readings during monitoring.
LIVE_READINGS_FILE = r"C:\Users\ankit\OneDrive\Documents\Personal\Repls\Complete code\Random Python\NeuroMentor\Resource files\EEG_Readings.csv"
# Set a timeout for the entire calibration process to prevent the script from hanging indefinitely.
CALIBRATION_TIMEOUT_S = (20 * 3 * 60) + 300 # 60 minutes for sessions + 5 min buffer

# --- Alerting Thresholds ---
# These values determine the sensitivity of the real-time alerts.
# Trigger a stress alert if the live Stress Index is 20% higher than your calibrated stressed state.
STRESS_THRESHOLD = 1.2
# Trigger a focus loss alert if the live Relaxed Focus index is 20% lower than your calibrated focused state.
FOCUS_THRESHOLD = 0.8

# =================================================================
# Global Variables
# =================================================================
# This global variable will hold the calculated PSD values from the calibration phase.
# It acts as the system's "memory" of your personal brainwave patterns.
baseline_psd = None

# =================================================================
# Core Functions
# =================================================================

def get_serial_connection():
    """
    Establishes and returns a serial connection object to the ESP32.
    Handles potential connection errors gracefully.
    """
    try:
        # Initialize the serial connection. The timeout is important for readline() not to block forever.
        ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=2)
        # A short pause to allow the ESP32 to reset after connection is established.
        time.sleep(2)
        # Flush any garbage data that might be in the input buffer from previous runs.
        ser.flushInput()
        print(f"[INFO] Successfully connected to {COM_PORT}")
        return ser
    except serial.SerialException as e:
        print(f"[FATAL] Could not open serial port {COM_PORT}: {e}")
        return None

def run_calibration_stream(ser):
    """
    Manages the entire calibration phase by listening to the real-time data stream from the ESP32.
    It saves the streamed data to a local CSV file and then analyzes it.
    """
    global baseline_psd # Declare that we intend to modify the global baseline_psd variable.
    print("\n" + "="*60)
    print("      PHASE 1: Starting Device Calibration (via Real-time Stream)      ")
    print("="*60)
    
    # --- Step 1: Command the ESP32 to start streaming calibration data ---
    ser.write(b'start_calibration\n')
    
    try:
        # --- Step 2: Open a local file to save the incoming data ---
        # The 'with' statement ensures the file is properly closed even if errors occur.
        with open(CALIBRATION_FILE, 'w', newline='') as f:
            # Write the CSV header row to our new file.
            f.write("State,Delta,Theta,Alpha,Beta,Gamma\n")
            
            print("[INFO] Listening for calibration data stream... This will take ~61 minutes.")
            
            # --- Step 3: Enter a loop to listen for the data stream ---
            # This loop will continue until the ESP32 signals that calibration is complete.
            while True:
                # Read one line from the serial port.
                line = ser.readline().decode('utf-8').strip()

                # If the line is empty (due to timeout), just continue and wait for the next one.
                if not line:
                    continue

                # Check if the line is an event marker sent by the ESP32.
                if line.startswith("EVENT:"):
                    print(f"[DEVICE STATUS] {line}")
                    # If the ESP32 says calibration is done, we can exit the listening loop.
                    if "Calibration Complete" in line:
                        break
                
                # Check if the line is a valid data line (contains 5 commas).
                elif line.count(',') == 5:
                    f.write(line + '\n') # Write the received data line to our local CSV file.
                    # Provide continuous feedback to the user without spamming the console.
                    print(f"\r[DATA] Receiving and saving calibration reading...", end="")
        
        print(f"\n[SUCCESS] Calibration stream finished. Data saved to {CALIBRATION_FILE}")

    except Exception as e:
        print(f"\n[ERROR] An error occurred during the calibration stream: {e}")
        return False

    # --- Step 4: Analyze the saved data to establish the baseline ---
    try:
        df = pd.read_csv(CALIBRATION_FILE)
        # This is the core analysis step: group the data by state and calculate the mean for each band.
        baseline_psd = df.groupby('State')[['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']].mean()
        print("\n--- Calculated Baseline PSD Values ---")
        print(baseline_psd)
        print("--------------------------------------")
        return True # Return True to indicate calibration was successful.
    except Exception as e:
        print(f"[ERROR] Could not analyze the saved calibration file: {e}")
        return False

def run_live_monitoring(ser):
    """
    Manages the live monitoring phase. It reads live data, compares it to the
    calibrated baseline, and provides real-time feedback to the user.
    """
    print("\n" + "="*60)
    print("      PHASE 2: Starting Live Monitoring      ")
    print("="*60)
    
    # --- Step 1: Command the ESP32 to start streaming live data ---
    ser.write(b'start_live_monitoring\n')
    ser.readline() # Read and discard the "OK" confirmation from the ESP32.

    print("[INFO] Now receiving live data. Press Ctrl+C to stop.")
    
    # Check if the live log file already has a header.
    header_written = os.path.exists(LIVE_READINGS_FILE)

    # --- Step 2: Enter the infinite monitoring loop ---
    while True:
        try:
            # Read a line of live data from the ESP32.
            line = ser.readline().decode('utf-8').strip()
            
            # Process the line only if it's a valid "Live" data line.
            if line and line.startswith("Live"):
                # --- Step 3: Log the live reading ---
                with open(LIVE_READINGS_FILE, 'a', newline='') as f:
                    # Write the header only if it's the first time writing to the file.
                    if not header_written:
                        f.write("State,Delta,Theta,Alpha,Beta,Gamma\n")
                        header_written = True
                    f.write(line + '\n')
                
                # --- Step 4: Parse and Analyze the live data ---
                parts = line.split(',')
                live_data = {'Alpha': float(parts[3]), 'Beta': float(parts[4]), 'Theta': float(parts[2])}
                
                epsilon = 1e-9 # A small number to prevent division by zero errors.
                # Calculate the heuristic ratios for the current live reading.
                live_stress_index = live_data['Beta'] / (live_data['Alpha'] + epsilon)
                live_focus_index = live_data['Alpha'] / (live_data['Theta'] + epsilon)

                # --- Step 5: Compare live data to the calibrated baseline ---
                # Retrieve the specific values from our stored baseline_psd DataFrame.
                calibrated_stress_index = baseline_psd.loc['Stressed', 'Beta'] / (baseline_psd.loc['Stressed', 'Alpha'] + epsilon)
                calibrated_focus_index = baseline_psd.loc['Focused', 'Alpha'] / (baseline_psd.loc['Focused', 'Theta'] + epsilon)

                # --- Step 6: Issue Alerts based on the comparison ---
                status = "State: CALM" # Default state.
                if live_stress_index > calibrated_stress_index * STRESS_THRESHOLD:
                    status = "State: STRESSED! (High Beta/Alpha Ratio)"
                elif live_focus_index < calibrated_focus_index * FOCUS_THRESHOLD:
                    status = "State: LOSING FOCUS (Low Alpha/Theta Ratio)"
                elif live_focus_index > calibrated_focus_index * 1.1: # If focus is 10% higher than calibrated
                    status = "State: FOCUSED (High Alpha/Theta Ratio)"
                
                # Print the status to the console. The '\r' and 'end=""' make it update on a single line.
                print(f"\r{status.ljust(50)}", end="")

        # Gracefully handle the user pressing Ctrl+C to stop the script.
        except KeyboardInterrupt:
            ser.write(b'stop\n') # Tell the ESP32 to stop streaming.
            print("\n[INFO] Stopping live monitor...")
            break
        # Catch any other potential errors (like bad data from the ESP32) and continue.
        except:
            pass

# =================================================================
# Main Execution Block
# =================================================================
if __name__ == "__main__":
    # This is the entry point of the script.
    ser = get_serial_connection() # First, establish the connection.
    
    # Proceed only if the connection was successful.
    if ser:
        # First, run the calibration process.
        if run_calibration_stream(ser):
            # If calibration completes successfully, then proceed to live monitoring.
            run_live_monitoring(ser)
        
        # Close the serial connection when the script is finished.
        ser.close()
        print("\n[INFO] Session ended. Serial connection closed.")