/**
 * Open Colorimeter for Arduino Giga R1 WiFi + Display Shield
 *
 * Ported from CircuitPython PyBadge version
 * Uses LVGL for 800x480 touchscreen display
 *
 * Hardware:
 * - Arduino Giga R1 WiFi
 * - Arduino Giga Display Shield (800x480)
 * - TSL2591 Light Sensor (I2C)
 * - PCA9685 Motor Driver (I2C, optional)
 * - Solenoid Driver (optional)
 *
 * Author: Ported to Arduino C++
 * Version: 1.0.0
 */

#include <Wire.h>
#include "src/Config.h"
#include "src/LightSensor.h"
#include "src/Calibrations.h"
#include "src/UI_Manager.h"
#include "src/MotorController.h"

// Forward declarations
void performBlank();
void scanI2C();

// Global objects
LightSensor lightSensor;
Calibrations calibrations;
UI_Manager uiManager;
MotorController motorController;

// System state
float blankValue = 1.0;
bool sensorInitialized = false;
bool isBlanked = false;
String currentMeasurement = "Absorbance";
bool blankRequested = false;

void setup() {
  Serial.begin(115200);
  delay(2000); // Give time for Serial to stabilize

  Serial.println("\n\n========================================");
  Serial.println("Open Colorimeter for Arduino Giga R1");
  Serial.println("Version 1.0.0 - LVGL Edition");
  Serial.println("========================================\n");

  // Initialize I2C
  Serial.println("Step 1: Initializing I2C...");
  Wire.begin();
  Serial.println("I2C initialized OK");

  // Scan I2C bus for devices
  Serial.println("\nScanning I2C bus...");
  scanI2C();
  Serial.println();

  // Initialize light sensor
  Serial.println("Step 2: Initializing light sensor...");
  sensorInitialized = lightSensor.begin();
  if (!sensorInitialized) {
    Serial.println("WARNING: TSL2591 sensor initialization failed!");
    Serial.println("System will continue but readings will show 'SENSOR ERROR'");
  } else {
    Serial.println("Light sensor initialized OK");
  }
  Serial.println();

  // Load calibrations from SD card or internal storage
  Serial.println("Step 3: Loading calibrations...");
  if (!calibrations.load()) {
    Serial.println("WARNING: No calibrations loaded");
  }
  Serial.println();

  // Initialize motor controller (stub)
  Serial.println("Step 4: Initializing motor controller...");
  motorController.begin();
  Serial.println();

  // Initialize LVGL UI (includes display and touch)
  Serial.println("Step 5: Initializing LVGL UI...");
  Serial.println("This may take a moment...\n");
  uiManager.begin(&motorController, &calibrations);

  // Set sensor status in UI
  uiManager.setSensorStatus(sensorInitialized);

  Serial.println("\n========================================");
  Serial.println("Initialization complete!");
  Serial.println("LVGL UI active with touch support");
  Serial.println("========================================\n");
}

void loop() {
  static unsigned long lastPrint = 0;
  static unsigned long lastDebug = 0;

  // Update LVGL UI (handles touch internally)
  uiManager.update();

  // Handle blank button press
  if (blankRequested) {
    blankRequested = false;
    performBlank();
  }

  // Update measurement display
  updateMeasurement();

  // Debug sensor readings every 2 seconds
  if (sensorInitialized && millis() - lastDebug > 2000) {
    uint16_t raw = lightSensor.getValue();
    Serial.print("Sensor reading: ");
    Serial.print(raw);
    Serial.print(" (0x");
    Serial.print(raw, HEX);
    Serial.println(")");
    lastDebug = millis();
  }

  // Heartbeat - print every 5 seconds to show loop is running
  if (millis() - lastPrint > 5000) {
    Serial.println("Loop running OK");
    lastPrint = millis();
  }

  delay(10); // LVGL needs frequent updates
}

void updateMeasurement() {
  static unsigned long lastDebugCalc = 0;
  float value = 0.0;

  // Check if sensor is initialized
  if (!sensorInitialized) {
    uiManager.setMeasurementValue(0.0, false);
    return;
  }

  try {
    if (currentMeasurement == "Raw Sensor") {
      value = lightSensor.getValue();
    }
    else if (currentMeasurement == "Transmittance") {
      float raw = lightSensor.getValue();
      value = raw / blankValue;
    }
    else if (currentMeasurement == "Absorbance") {
      float raw = lightSensor.getValue();
      float transmittance = raw / blankValue;
      value = -log10(transmittance);

      // Debug output every 3 seconds
      if (millis() - lastDebugCalc > 3000) {
        Serial.print("Absorbance calc: raw=");
        Serial.print(raw);
        Serial.print(" blank=");
        Serial.print(blankValue);
        Serial.print(" trans=");
        Serial.print(transmittance);
        Serial.print(" abs=");
        Serial.print(value);
        Serial.print(" (before clamp)");
        lastDebugCalc = millis();
      }

      if (value < 0.0) value = 0.0;

      if (millis() - lastDebugCalc < 100) {
        Serial.print(" final=");
        Serial.println(value);
      }
    }
    else {
      // Check if it's a calibration
      float raw = lightSensor.getValue();
      float transmittance = raw / blankValue;
      float absorbance = -log10(transmittance);
      if (absorbance < 0.0) absorbance = 0.0;

      value = calibrations.apply(currentMeasurement, absorbance);

      // Debug output every 3 seconds
      if (millis() - lastDebugCalc > 3000) {
        Serial.print("Calibration: ");
        Serial.print(currentMeasurement);
        Serial.print(" abs=");
        Serial.print(absorbance);
        Serial.print(" value=");
        Serial.println(value);
        lastDebugCalc = millis();
      }
    }

    uiManager.setMeasurementValue(value, isBlanked);
  }
  catch (...) {
    uiManager.showOverflow();
  }
}

void performBlank() {
  Serial.println("Performing blank...");

  // Check if sensor is initialized
  if (!sensorInitialized) {
    Serial.println("ERROR: Cannot blank - sensor not initialized!");
    return;
  }

  // Take multiple readings and average
  float sum = 0.0;
  for (int i = 0; i < NUM_BLANK_SAMPLES; i++) {
    sum += lightSensor.getValue();
    delay(BLANK_DT);
  }

  blankValue = sum / NUM_BLANK_SAMPLES;
  isBlanked = true;

  Serial.print("Blank value set to: ");
  Serial.println(blankValue, 4);

  // Show confirmation message briefly
  uiManager.showMessage("Blanked", "Reference value set");
  delay(1000);
  uiManager.showMeasureScreen();
}

void scanI2C() {
  byte error, address;
  int deviceCount = 0;

  Serial.println("Scanning for I2C devices...");

  for (address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    error = Wire.endTransmission();

    if (error == 0) {
      Serial.print("I2C device found at address 0x");
      if (address < 16) Serial.print("0");
      Serial.print(address, HEX);
      Serial.print(" (");
      Serial.print(address);
      Serial.print(")");

      // Identify known devices
      if (address == 0x29) {
        Serial.print(" - TSL2591 Light Sensor");
      }
      Serial.println();
      deviceCount++;
    }
  }

  if (deviceCount == 0) {
    Serial.println("No I2C devices found!");
    Serial.println("Check wiring: SDA->Pin 20, SCL->Pin 21, VCC->3.3V, GND->GND");
  } else {
    Serial.print("Found ");
    Serial.print(deviceCount);
    Serial.println(" device(s)");
  }
}
