#include <Arduino.h>
#include <SPIFFS.h>
#include <arduinoFFT.h>

// === EEG and FFT Settings ===
#define EEG_PIN 8
#define SAMPLES 128
#define SAMPLING_FREQUENCY 256.0
double vReal[SAMPLES];
double vImag[SAMPLES];

ArduinoFFT FFT = ArduinoFFT(vReal, vImag, SAMPLES, SAMPLING_FREQUENCY);
File dataFile;

// === Control flags ===
bool isRecording = false;
unsigned long startTime = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Initialize SPIFFS
  if (!SPIFFS.begin(true)) {
    Serial.println("SPIFFS Mount Failed");
    return;
  }

  // Open or create the CSV file
  dataFile = SPIFFS.open("/eeg_bandpower.csv", FILE_APPEND);
  if (!dataFile) {
    Serial.println("Failed to open CSV file!");
  } else {
    if (dataFile.size() == 0) {
      dataFile.println("Delta,Theta,Alpha,Beta,Gamma");
    }
    dataFile.close();
  }

  Serial.println(">> Type 'start' to begin recording for 30 seconds");
  Serial.println(">> Type 'stop' to cancel recording");
  Serial.println(">> Type 'GET_CSV' to download CSV");
}

void loop() {
  // === Handle Serial Commands ===
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();  // Remove newline/space

    if (command == "start" && !isRecording) {
      isRecording = true;
      startTime = millis();
      Serial.println("✅ Recording started for 30 seconds...");
    }

    else if (command == "stop") {
      if (isRecording) {
        Serial.println("⛔ Recording stopped by user.");
      } else {
        Serial.println("⚠ Not recording.");
      }
      isRecording = false;
    }

    else if (command == "GET_CSV") {
      File readFile = SPIFFS.open("/eeg_bandpower.csv", "r");
      if (readFile) {
        while (readFile.available()) {
          String line = readFile.readStringUntil('\n');
          Serial.println(line);
          delay(10);
        }
        Serial.println("EOF");
        readFile.close();
      } else {
        Serial.println("Failed to open CSV");
      }
    }
  }

  // === Perform Recording if Flag is True ===
  if (isRecording) {
    if (millis() - startTime >= 30000) {
      Serial.println("✅ 30 seconds complete. Stopping recording.");
      isRecording = false;
      return;
    }

    // === Sample EEG Signal ===
    for (int i = 0; i < SAMPLES; i++) {
      vReal[i] = analogRead(EEG_PIN);
      vImag[i] = 0;
      delayMicroseconds(1000000 / SAMPLING_FREQUENCY);
    }

    FFT.windowing(FFT_WIN_TYP_HAMMING, FFT_FORWARD);
    FFT.compute(FFT_FORWARD);
    FFT.complexToMagnitude();

    double delta = 0, theta = 0, alpha = 0, beta = 0, gamma = 0;
    for (int i = 1; i < SAMPLES / 2; i++) {
      double freq = i * (SAMPLING_FREQUENCY / SAMPLES);
      double mag = vReal[i];

      if (freq >= 0.5 && freq < 4)      delta += mag;
      else if (freq >= 4 && freq < 8)   theta += mag;
      else if (freq >= 8 && freq < 13)  alpha += mag;
      else if (freq >= 13 && freq < 30) beta += mag;
      else if (freq >= 30 && freq < 100) gamma += mag;
    }

    // === Show on Serial ===
    Serial.print("Delta: "); Serial.print(delta, 2); Serial.print(" | ");
    Serial.print("Theta: "); Serial.print(theta, 2); Serial.print(" | ");
    Serial.print("Alpha: "); Serial.print(alpha, 2); Serial.print(" | ");
    Serial.print("Beta: ");  Serial.print(beta, 2);  Serial.print(" | ");
    Serial.print("Gamma: "); Serial.println(gamma, 2);

    // === Save to CSV ===
    dataFile = SPIFFS.open("/eeg_bandpower.csv", FILE_APPEND);
    if (dataFile) {
      dataFile.printf("%.2f,%.2f,%.2f,%.2f,%.2f\n", delta, theta, alpha, beta, gamma);
      dataFile.close();
    } else {
      Serial.println("Failed to write to CSV");
    }

    delay(10);  // Wait 0.01 second before next entry
  }
}