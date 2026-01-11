import serial
import time
import os

# === USER SETTINGS ===
COM_PORT = 'COM12'  # << CHANGE this to your ESP32 serial port
BAUD_RATE = 115200
SAVE_PATH = r"C:/Users/ankit/OneDrive/Documents/Personal/Repls/Complete code/Random Python/NeuroMentor/Resource files/EEG_Dataset.csv" # << Set your custom save path here

def download_eeg_data():
    """
    Connects to the ESP32, requests the EEG data, and saves it to a local CSV file.
    """
    try:
        # Initialize Serial Connection with a 5-second timeout for reading lines
        ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=5)
        time.sleep(2)  # Wait for the ESP32 to boot and reset
        ser.flushInput() # Clear any garbage data in the input buffer
        print(f"[INFO] Connected to {COM_PORT}")
    except serial.SerialException as e:
        print(f"[ERROR] Could not open serial port {COM_PORT}: {e}")
        return # Exit the function

    # --- Send command to ESP32 to get the CSV file ---
    print("[INFO] Sending command: GET_CSV")
    ser.write(b'GET_CSV\n')

    # --- Wait for the start marker from the ESP32 ---
    # This makes the script robust by waiting for the ESP32 to confirm it's sending data.
    in_data_stream = False
    while not in_data_stream:
        line = ser.readline().decode('utf-8').strip()
        if line == "---BEGIN CSV DATA---":
            in_data_stream = True
            print("[INFO] Data stream started. Receiving file...")
        elif line == "":
            print("[ERROR] Timed out waiting for data stream to start. Is the ESP32 running the correct code?")
            ser.close()
            return

    # --- Read and Save the CSV lines until the end marker is found ---
    csv_lines = []
    line_count = 0
    while True:
        try:
            line = ser.readline().decode('utf-8').strip()
            # Check for the specific end marker from the Arduino code
            if line == "---END CSV DATA---":
                print(f"\n[INFO] End of stream detected. Received {line_count} lines of data.")
                break
            # Handle timeout case
            if line == "":
                print("\n[WARNING] Timed out while receiving data. File might be incomplete.")
                break
            
            # If it's a valid data line, save it
            csv_lines.append(line)
            line_count += 1
            print(f"\r[DATA] Receiving line #{line_count}", end="")

        except UnicodeDecodeError:
            # This can happen if there's electrical noise or a baud rate mismatch
            print(f"\n[WARNING] Skipped a line due to a decoding error.")


    # --- Save the collected data to the specified path ---
    if not csv_lines:
        print("[ERROR] No data was received. Nothing to save.")
    else:
        try:
            # Ensure the directory exists before trying to save
            os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
            with open(SAVE_PATH, 'w', newline='') as file:
                for row in csv_lines:
                    file.write(row + '\n')
            print(f"\n[SUCCESS] CSV data saved to {SAVE_PATH}")
        except Exception as e:
            print(f"\n[ERROR] Could not write to file: {e}")

    # --- Close the serial port ---
    ser.close()
    print("[INFO] Serial connection closed.")

if __name__ == "__main__":
    download_eeg_data()
