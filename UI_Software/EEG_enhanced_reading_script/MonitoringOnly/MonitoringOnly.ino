#include "arduinoFFT.h"

// =================================================================
// Configuration Constants
// =================================================================
// Define the analog pin connected to your EEG sensor's output.
const int EEG_PIN = 34;
// Define the sampling frequency in Hz.
const int SAMPLING_FREQUENCY = 256;
// Define the number of samples for each FFT window.
const int SAMPLES = 256;

// =================================================================
// Global State Machine Variables
// =================================================================
// For this simplified script, we only need two states.
enum State {
  IDLE,             // Waiting for the Python script to connect and send a command.
  LIVE_MONITORING   // Continuously streaming live data.
};

// The state machine starts in the IDLE state.
State currentState = IDLE;

// --- FFT variables ---
// These are required for the signal processing.
double vReal[SAMPLES];
double vImag[SAMPLES];
ArduinoFFT<double> FFT = ArduinoFFT<double>(vReal, vImag, SAMPLES, SAMPLING_FREQUENCY);

// =================================================================
// HELPER FUNCTION: Performs one reading and returns a formatted string
// (This function is unchanged as it's the core processing engine).
// =================================================================
String acquireAndProcessReading(const char* stateLabel) {
  // --- Step 1: Acquire Raw EEG Samples ---
  for (int i = 0; i < SAMPLES; i++) {
    vReal[i] = analogRead(EEG_PIN);
    vImag[i] = 0;
    delayMicroseconds(1000000 / SAMPLING_FREQUENCY);
  }

  // --- Step 2: Perform Fast Fourier Transform (FFT) ---
  FFT.windowing(FFT_WIN_TYP_HAMMING, FFT_FORWARD);
  FFT.compute(FFT_FORWARD);
  FFT.complexToMagnitude();

  // --- Step 3: Calculate Power in Each Brainwave Band ---
  double delta = 0, theta = 0, alpha = 0, beta = 0, gamma = 0;
  for (int i = 2; i < SAMPLES / 2; i++) {
    double freq = i * 1.0 * SAMPLING_FREQUENCY / SAMPLES;
    double mag = vReal[i];
    if (freq >= 0.5 && freq < 4)   delta += mag;
    else if (freq >= 4 && freq < 8)   theta += mag;
    else if (freq >= 8 && freq < 13)  alpha += mag;
    else if (freq >= 13 && freq < 30) beta  += mag;
    else if (freq >= 30 && freq < 100) gamma += mag;
  }

  // --- Step 4: Format the Output String ---
  char buffer[100];
  snprintf(buffer, sizeof(buffer), "%s,%.2f,%.2f,%.2f,%.2f,%.2f", stateLabel, delta, theta, alpha, beta, gamma);
  return String(buffer);
}

// =================================================================
// SETUP: Runs once when the ESP32 boots up.
// =================================================================
void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Live EEG Monitor Initialized. Ready for commands.");
}

// =================================================================
// MAIN LOOP: This code runs repeatedly forever.
// =================================================================
void loop() {
  // --- Handle Incoming Commands from Python ---
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    // The only command this sketch needs to listen for is "start_live_monitoring".
    if (command == "start_live_monitoring" && currentState == IDLE) {
      currentState = LIVE_MONITORING;
      Serial.println("OK: Starting Live Monitoring Stream...");
    }
    // The "stop" command is still useful to return the device to a low-power idle state.
    else if (command == "stop") {
      currentState = IDLE;
      Serial.println("OK: Stopped. Returning to IDLE state.");
    }
  }

  // --- Main State Machine Logic ---
  // This logic is now much simpler with only two states.
  switch (currentState) {
    case LIVE_MONITORING: {
      // In this state, continuously take readings and stream them over the serial port.
      String reading = acquireAndProcessReading("Live");
      Serial.println(reading);
      break;
    }
    case IDLE:
      // In the IDLE state, do nothing but wait for a command.
      break;
  }
}
