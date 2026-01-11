#include <SPIFFS.h>
#include "arduinoFFT.h"

// =================================================================
// Configuration Constants
// =================================================================
const int EEG_PIN = 34; // << SET YOUR EEG ANALOG PIN HERE
const int SAMPLING_FREQUENCY = 256; // Hz
const int SAMPLES = 256; // RENAMED for clarity from "Window"

// Experiment timing
const int RECORDING_DURATION_MINS = 20  ;
const int READINGS_PER_SESSION = RECORDING_DURATION_MINS * 60; // 1 reading per second
const int PAUSE_DURATION_S = 10;

const char* dataFileName = "/eeg_experiment.csv";

// =================================================================
// Global Variables for State Machine
// =================================================================

// Define the states of our experiment
enum State {
  IDLE,
  RECORDING_BASELINE,
  PAUSE_1,
  RECORDING_STRESSED,
  PAUSE_2,
  RECORDING_FOCUSED,
  DONE
};

State currentState = IDLE; // The current state of the experiment
File dataFile; // Global file object

// Counters and timers
int sessionReadingCounter = 0;
unsigned long pauseStartTime = 0;

// FFT variables
// CORRECTED: Declarations for vReal and vImag moved before they are used.
double vReal[SAMPLES];
double vImag[SAMPLES];
ArduinoFFT<double> FFT = ArduinoFFT<double>(vReal, vImag, SAMPLES, SAMPLING_FREQUENCY);


// =================================================================
// HELPER FUNCTION: Performs one reading, FFT, and saves data
// =================================================================
void acquireAndSaveReading(const char* stateLabel) {
  // 1. Acquire samples for one FFT window
  for (int i = 0; i < SAMPLES; i++) {
    vReal[i] = analogRead(EEG_PIN);
    vImag[i] = 0;
    delayMicroseconds(1000000 / SAMPLING_FREQUENCY);
  }

  // 2. Perform FFT
  FFT.windowing(FFT_WIN_TYP_HAMMING, FFT_FORWARD);
  FFT.compute(FFT_FORWARD);
  FFT.complexToMagnitude();

  // 3. Calculate band powers
  double delta = 0, theta = 0, alpha = 0, beta = 0, gamma = 0;
  for (int i = 2; i < SAMPLES / 2; i++) { // Start from i=2 to ignore DC offset
    double freq = i * 1.0 * SAMPLING_FREQUENCY / SAMPLES;
    double mag = vReal[i];
    if (freq >= 0.5 && freq < 4)   delta += mag;
    else if (freq >= 4 && freq < 8)   theta += mag;
    else if (freq >= 8 && freq < 13)  alpha += mag;
    else if (freq >= 13 && freq < 30) beta  += mag;
    else if (freq >= 30 && freq < 100) gamma += mag;
  }

  // 4. Save to CSV file
  if (dataFile) {
    dataFile.printf("%s,%.2f,%.2f,%.2f,%.2f,%.2f\n", stateLabel, delta, theta, alpha, beta, gamma);
  }

  // 5. Print status to Serial Monitor
  sessionReadingCounter++;
  Serial.printf("[%s] Saved reading #%d/%d. D:%.2f|T:%.2f|A:%.2f|B:%.2f|G:%.2f\n",
                stateLabel, sessionReadingCounter, READINGS_PER_SESSION, delta, theta, alpha, beta, gamma);
}


// =================================================================
// SETUP: Runs once on boot
// =================================================================
void setup() {
  Serial.begin(115200);
  delay(1000);

  if (!SPIFFS.begin(true)) {
    Serial.println("SPIFFS Mount Failed");
    return;
  }

  Serial.println("\n✅ System Initialized.");
  Serial.println("=================================================");
  Serial.println(">> Type 'start' to begin the 3-stage experiment.");
  Serial.println("   (15min Baseline -> 15min Stressed -> 15min Focused)");
  Serial.println(">> Type 'stop' to cancel the experiment.");
  Serial.println(">> Type 'GET_CSV' to download the last experiment's data.");
  Serial.println("=================================================");
}


// =================================================================
// LOOP: Main program logic, runs repeatedly
// =================================================================
void loop() {
  // === Handle Serial Commands ===
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "start" && currentState == IDLE) {
      // Open file in write mode to erase previous data and start fresh
      dataFile = SPIFFS.open(dataFileName, "w");
      if (dataFile) {
        // Write the new header with the "State" column
        dataFile.println("State,Delta,Theta,Alpha,Beta,Gamma");
        currentState = RECORDING_BASELINE;
        sessionReadingCounter = 0;
        Serial.println("\n🔥 Starting new experiment! Erased previous data.");
        Serial.println("--> Stage 1: Recording BASELINE for 15 minutes...");
      } else {
        Serial.println("Failed to create file!");
      }
    }
    else if (command == "stop") {
      if (currentState != IDLE && currentState != DONE) {
        currentState = DONE;
        Serial.println("\n🛑 Experiment stopped by user.");
      }
    }
    else if (command == "GET_CSV") {
      File readFile = SPIFFS.open(dataFileName, "r");
      if (readFile) {
        Serial.println("\n---BEGIN CSV DATA---");
        while (readFile.available()) {
          Serial.print(readFile.readStringUntil('\n'));
        }
        Serial.println("\n---END CSV DATA---");
        readFile.close();
      } else {
        Serial.println("Failed to open CSV for reading. Did you run an experiment yet?");
      }
    }
  }

  // === Main Experiment State Machine ===
  switch (currentState) {

    case RECORDING_BASELINE:
      acquireAndSaveReading("Baseline");
      if (sessionReadingCounter >= READINGS_PER_SESSION) {
        currentState = PAUSE_1;
        pauseStartTime = millis(); // Get the current time in milliseconds
        Serial.println("\n⏸️ Baseline recording complete. Pausing for 10 seconds...");
      }
      break;

    case PAUSE_1:
      if (millis() - pauseStartTime >= (PAUSE_DURATION_S * 1000)) {
        currentState = RECORDING_STRESSED;
        sessionReadingCounter = 0; // Reset counter for the new session
        Serial.println("--> Stage 2: Recording STRESSED for 15 minutes...");
      }
      break;

    case RECORDING_STRESSED:
      acquireAndSaveReading("Stressed");
      if (sessionReadingCounter >= READINGS_PER_SESSION) {
        currentState = PAUSE_2;
        pauseStartTime = millis();
        Serial.println("\n⏸️ Stressed recording complete. Pausing for 10 seconds...");
      }
      break;

    case PAUSE_2:
      if (millis() - pauseStartTime >= (PAUSE_DURATION_S * 1000)) {
        currentState = RECORDING_FOCUSED;
        sessionReadingCounter = 0; // Reset counter
        Serial.println("--> Stage 3: Recording FOCUSED for 15 minutes...");
      }
      break;

    case RECORDING_FOCUSED:
      acquireAndSaveReading("Focused");
      if (sessionReadingCounter >= READINGS_PER_SESSION) {
        currentState = DONE;
      }
      break;

    case DONE:
      if (dataFile) {
        dataFile.close();
      }
      Serial.println("\n✅ Experiment complete! File saved successfully.");
      Serial.println("Ready for new 'start' command.");
      currentState = IDLE; // Reset for the next experiment
      break;

    case IDLE:
      // Do nothing, wait for 'start' command
      break;
  }
}
