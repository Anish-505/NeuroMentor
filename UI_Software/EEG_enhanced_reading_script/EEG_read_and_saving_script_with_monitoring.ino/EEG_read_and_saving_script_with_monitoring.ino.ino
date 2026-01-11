#include "arduinoFFT.h"

// =================================================================
// Configuration Constants
// =================================================================
// Define the analog pin connected to your EEG sensor's output.
const int EEG_PIN = 34;
// Define the sampling frequency in Hz. 256Hz is common for EEG applications.
const int SAMPLING_FREQUENCY = 256;
// Define the number of samples for each FFT window. Must be a power of 2.
const int SAMPLES = 256;

// --- Experiment timing ---
// Set the duration for each calibration phase (Baseline, Stressed, Focused).
const int RECORDING_DURATION_MINS = 20;
// Calculate the total number of readings to take in each 20-minute session (1 reading/sec).
const int READINGS_PER_SESSION = RECORDING_DURATION_MINS * 60;
// The short pause duration between calibration phases.
const int PAUSE_DURATION_S = 10;
// The longer 2-minute pause after the entire calibration is complete before idling.
const int POST_CALIBRATION_PAUSE_S = 120;

// =================================================================
// Global State Machine Variables
// =================================================================
// An enumeration defines a set of named integer constants. This creates our "state machine".
// The ESP32 can only be in one of these states at any given time.
enum State {
  IDLE,             // Waiting for a command from the Python script.
  CAL_BASELINE,     // Streaming "Baseline" calibration data.
  CAL_PAUSE_1,      // Pausing between Baseline and Stressed phases.
  CAL_STRESSED,     // Streaming "Stressed" calibration data.
  CAL_PAUSE_2,      // Pausing between Stressed and Focused phases.
  CAL_FOCUSED,      // Streaming "Focused" calibration data.
  CAL_DONE,         // The calibration process is finished.
  LIVE_MONITORING   // Continuously streaming live data for real-time analysis.
};

// This variable holds the current state of our state machine. It starts in IDLE.
State currentState = IDLE;
// A counter to keep track of readings within a single calibration session.
int sessionReadingCounter = 0;
// A timer variable to manage the duration of pauses.
unsigned long pauseStartTime = 0;

// --- FFT variables ---
// These arrays will hold the real and imaginary parts of the signal for the FFT calculation.
// They live in RAM, but are small and their memory is reused for each reading.
double vReal[SAMPLES];
double vImag[SAMPLES];
// Create an instance of the arduinoFFT library.
ArduinoFFT<double> FFT = ArduinoFFT<double>(vReal, vImag, SAMPLES, SAMPLING_FREQUENCY);

// =================================================================
// HELPER FUNCTION: Performs one reading, processes it, and returns the result.
// =================================================================
String acquireAndProcessReading(const char* stateLabel) {
  // --- Step 1: Acquire Raw EEG Samples ---
  // This loop reads the specified number of samples from the EEG pin.
  for (int i = 0; i < SAMPLES; i++) {
    vReal[i] = analogRead(EEG_PIN); // Read the analog voltage.
    vImag[i] = 0;                   // Imaginary part is 0 for a real-world signal.
    // Wait for the correct amount of time to maintain the sampling frequency.
    delayMicroseconds(1000000 / SAMPLING_FREQUENCY);
  }

  // --- Step 2: Perform Fast Fourier Transform (FFT) ---
  // Apply a Hamming window to reduce spectral leakage.
  FFT.windowing(FFT_WIN_TYP_HAMMING, FFT_FORWARD);
  // Compute the FFT. This transforms the signal from the time domain to the frequency domain.
  FFT.compute(FFT_FORWARD);
  // Convert the complex FFT output into magnitude, which represents the power at each frequency.
  FFT.complexToMagnitude();

  // --- Step 3: Calculate Power in Each Brainwave Band ---
  // Initialize variables for the 5 primary EEG bands.
  double delta = 0, theta = 0, alpha = 0, beta = 0, gamma = 0;
  // Iterate through the FFT results to sum the power in each band.
  // We start at i=2 to ignore the DC offset.
  for (int i = 2; i < SAMPLES / 2; i++) {
    // Calculate the frequency corresponding to the current FFT bin.
    double freq = i * 1.0 * SAMPLING_FREQUENCY / SAMPLES;
    double mag = vReal[i]; // Get the magnitude for that frequency.
    // Add the magnitude to the corresponding band's total power.
    if (freq >= 0.5 && freq < 4)   delta += mag;
    else if (freq >= 4 && freq < 8)   theta += mag;
    else if (freq >= 8 && freq < 13)  alpha += mag;
    else if (freq >= 13 && freq < 30) beta  += mag;
    else if (freq >= 30 && freq < 100) gamma += mag;
  }

  // --- Step 4: Format the Output String ---
  char buffer[100];
  // Use snprintf to create a clean, comma-separated string of the results.
  snprintf(buffer, sizeof(buffer), "%s,%.2f,%.2f,%.2f,%.2f,%.2f", stateLabel, delta, theta, alpha, beta, gamma);
  return String(buffer); // Return the final string (e.g., "Baseline,123.4,567.8,...").
}

// =================================================================
// SETUP: Runs once when the ESP32 boots up.
// =================================================================
void setup() {
  // Start serial communication at the specified baud rate.
  Serial.begin(115200);
  // A small delay to allow the serial monitor to connect.
  delay(1000);
  // ADD THIS LINE FOR VERIFICATION:
  Serial.printf("DEBUG: This device is configured for %d readings per session.\n", READINGS_PER_SESSION);
  // Print a ready message to the serial port. The Python script can see this.
  Serial.println("NeuroMonitor Initialized. Ready for commands.");
}

// =================================================================
// MAIN LOOP: This code runs repeatedly forever.
// =================================================================
void loop() {
  // --- Part 1: Handle Incoming Commands from Python ---
  // Check if there is any data waiting in the serial input buffer.
  if (Serial.available()) {
    // Read the incoming command until a newline character is received.
    String command = Serial.readStringUntil('\n');
    command.trim(); // Remove any leading/trailing whitespace.

    // If the command is "start_calibration" and we are in the IDLE state...
    if (command == "start_calibration" && currentState == IDLE) {
      currentState = CAL_BASELINE; // ...change the state to begin calibration.
      sessionReadingCounter = 0;   // Reset the reading counter.
      Serial.println("OK: Starting Calibration Stream..."); // Send confirmation to Python.
    } 
    // If the command is "start_live_monitoring" and we are in the IDLE state...
    else if (command == "start_live_monitoring" && currentState == IDLE) {
      currentState = LIVE_MONITORING; // ...change the state to begin live monitoring.
      Serial.println("OK: Starting Live Monitoring Stream..."); // Send confirmation.
    }
    // If the command is "stop"...
    else if (command == "stop") {
      currentState = IDLE; // ...return to the IDLE state.
      Serial.println("OK: Stopped. Returning to IDLE state."); // Send confirmation.
    }
  }

  // --- Part 2: Main State Machine Logic ---
  // This switch statement executes different code based on the value of 'currentState'.
  switch (currentState) {
    case CAL_BASELINE: {
      String reading = acquireAndProcessReading("Baseline");
      // REAL-TIME STREAMING: Send the processed data directly over the serial port.
      // This avoids using any Flash storage and respects the memory limits.
      Serial.println(reading);
      sessionReadingCounter++;
      // Check if we have completed the 20-minute session.
      if (sessionReadingCounter >= READINGS_PER_SESSION) {
        currentState = CAL_PAUSE_1; // Transition to the first pause state.
        pauseStartTime = millis();  // Record the start time of the pause.
        Serial.println("EVENT: Baseline Complete"); // Send an event marker to Python.
      }
      break;
    }
    case CAL_PAUSE_1:
      // Wait for the 10-second pause to elapse.
      if (millis() - pauseStartTime >= (PAUSE_DURATION_S * 1000)) {
        currentState = CAL_STRESSED; // Transition to the "Stressed" phase.
        sessionReadingCounter = 0;   // Reset counter for the new session.
        Serial.println("EVENT: Starting Stressed"); // Send an event marker to Python.
      }
      break;

    case CAL_STRESSED: {
      String reading = acquireAndProcessReading("Stressed");
      Serial.println(reading); // STREAM the data.
      sessionReadingCounter++;
      if (sessionReadingCounter >= READINGS_PER_SESSION) {
        currentState = CAL_PAUSE_2; // Transition to the second pause.
        pauseStartTime = millis();
        Serial.println("EVENT: Stressed Complete"); // Send event marker.
      }
      break;
    }
    case CAL_PAUSE_2:
      // Wait for the 10-second pause to elapse.
      if (millis() - pauseStartTime >= (PAUSE_DURATION_S * 1000)) {
        currentState = CAL_FOCUSED; // Transition to the "Focused" phase.
        sessionReadingCounter = 0;  // Reset counter.
        Serial.println("EVENT: Starting Focused"); // Send event marker.
      }
      break;

    case CAL_FOCUSED: {
      String reading = acquireAndProcessReading("Focused");
      Serial.println(reading); // STREAM the data.
      sessionReadingCounter++;
      if (sessionReadingCounter >= READINGS_PER_SESSION) {
        currentState = CAL_DONE; // Transition to the "Done" state.
      }
      break;
    }
    case CAL_DONE:
      // Send the final completion signal to the Python script.
      Serial.println("EVENT: Calibration Complete");
      // Begin the 2-minute post-calibration pause.
      pauseStartTime = millis();
      while(millis() - pauseStartTime < (POST_CALIBRATION_PAUSE_S * 1000)) {
        delay(100); // A small delay to prevent this loop from hogging the processor.
      }
      currentState = IDLE; // Return to the IDLE state, ready for new commands.
      break;

    case LIVE_MONITORING: {
      String reading = acquireAndProcessReading("Live");
      Serial.println(reading); // Continuously stream live data.
      break;
    }
    
    case IDLE:
      // In the IDLE state, do nothing but wait for a command.
      break;
  }
}