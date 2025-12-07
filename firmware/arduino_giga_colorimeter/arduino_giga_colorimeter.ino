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
 *
 * Author: Ported to Arduino C++
 * Version: 1.0.0
 */

#include <Wire.h>
#include <algorithm>
#include "src/Config.h"
#include "src/Configuration.h"
#include "src/LightSensor.h"
#include "src/Calibrations.h"
#include "src/UI_Manager.h"

// Forward declarations
float takeSensorMeasurement();
void performBlank();
void scanI2C();

// Global objects
Configuration config;
LightSensor lightSensor;
Calibrations calibrations;
UI_Manager uiManager;

// System state
float blankValue = 1.0;
bool sensorInitialized = false;
bool isBlanked = false;
String currentMeasurement = "Absorbance";
bool blankRequested = false;
TSL2591_Gain currentGain = TSL2591_GAIN_LOW;  // Track current gain for measurements

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

  // Load configuration
  Serial.println("Step 2: Loading configuration...");
  if (!config.load()) {
    Serial.println("WARNING: Failed to load configuration - using defaults");
  }
  Serial.println();

  // Initialize light sensor
  Serial.println("Step 3: Initializing light sensor...");
  sensorInitialized = lightSensor.begin();
  if (!sensorInitialized) {
    Serial.println("WARNING: TSL2591 sensor initialization failed!");
    Serial.println("System will continue but readings will show 'SENSOR ERROR'");
  } else {
    Serial.println("Light sensor initialized OK");

    // Apply configuration settings to sensor
    Serial.println("Applying configuration to sensor...");

    // Use config default gain
    TSL2591_Gain gainSetting = config.getGain();
    Serial.print("  Setting gain to: 0x");
    Serial.print(gainSetting, HEX);
    Serial.print(" (");
    if (gainSetting == TSL2591_GAIN_LOW) Serial.print("1x");
    else if (gainSetting == TSL2591_GAIN_MED) Serial.print("25x");
    else if (gainSetting == TSL2591_GAIN_HIGH) Serial.print("428x");
    else if (gainSetting == TSL2591_GAIN_MAX) Serial.print("9876x");
    Serial.println(")");
    lightSensor.setGain(gainSetting);

    lightSensor.setIntegrationTime(config.getIntegrationTime());
    Serial.print("  Integration time set to ");
    Serial.print(config.getIntegrationTimeMs());
    Serial.println("ms");
  }
  Serial.println();

  // Load calibrations from SD card or internal storage
  Serial.println("Step 4: Loading calibrations...");
  if (!calibrations.load()) {
    Serial.println("WARNING: No calibrations loaded");
  }
  Serial.println();

  // Initialize LVGL UI (includes display and touch)
  Serial.println("Step 5: Initializing LVGL UI...");
  Serial.println("This may take a moment...\n");
  uiManager.begin(&calibrations);

  // Set sensor status in UI
  uiManager.setSensorStatus(sensorInitialized);

  Serial.println("\n========================================");
  Serial.println("Initialization complete!");
  Serial.println("LVGL UI active with touch support");
  Serial.println("========================================\n");
}

void loop() {
  // Update LVGL UI (handles touch internally)
  uiManager.update();

  // Handle blank button press
  if (blankRequested) {
    blankRequested = false;
    performBlank();
  }

  delay(10); // LVGL needs frequent updates
}

/**
 * Takes a sensor measurement with consistent procedure:
 * 1. Reset sensor (power cycle)
 * 2. Restore gain setting
 * 3. Wait for stabilization
 * 4. Collect 50 samples
 * 5. Return median value
 *
 * Returns: Median sensor value, or -1.0 on error
 */
float takeSensorMeasurement() {
  if (!sensorInitialized) {
    Serial.println("ERROR: Sensor not initialized");
    return -1.0;
  }

  // Reset sensor before measurement for fresh state
  Serial.println("Resetting sensor...");
  lightSensor.disable();
  delay(100);  // Wait for sensor to power down
  lightSensor.enable();
  delay(SENSOR_STABILIZATION_DELAY_MS);  // 10 second stabilization

  // Restore gain setting after reset
  lightSensor.setGain(currentGain);
  Serial.println("Sensor reset and stabilized");

  // Collect 50 samples for measurement
  Serial.print("Collecting ");
  Serial.print(NUM_BLANK_SAMPLES);
  Serial.println(" samples (using median)...");

  float samples[NUM_BLANK_SAMPLES];
  for (int i = 0; i < NUM_BLANK_SAMPLES; i++) {
    uint16_t reading = lightSensor.getValue();
    samples[i] = reading;

    // Check for overflow
    if (reading >= lightSensor.getMaxCounts()) {
      Serial.println("ERROR: Sensor overflow during measurement");
      return -1.0;
    }

    delay(BLANK_DT);  // 50ms delay between samples
  }

  // Calculate median
  std::sort(samples, samples + NUM_BLANK_SAMPLES);
  float median = samples[NUM_BLANK_SAMPLES / 2];

  Serial.print("Measurement median from ");
  Serial.print(NUM_BLANK_SAMPLES);
  Serial.print(" samples: ");
  Serial.println(median, 2);

  return median;
}

void performBlank() {
  Serial.println("Performing blank...");

  // Set gain for current measurement type
  currentGain = TSL2591_GAIN_LOW;  // Default
  if (calibrations.hasCalibration(currentMeasurement)) {
    int measurementGain = calibrations.getGain(currentMeasurement);
    if (measurementGain == 1) currentGain = TSL2591_GAIN_LOW;
    else if (measurementGain == 25) currentGain = TSL2591_GAIN_MED;
    else if (measurementGain == 428) currentGain = TSL2591_GAIN_HIGH;
    else if (measurementGain == 9876) currentGain = TSL2591_GAIN_MAX;

    Serial.print("Setting gain for ");
    Serial.print(currentMeasurement);
    Serial.print(": ");
    Serial.print(measurementGain);
    Serial.println("x");
  }

  // Take measurement using standard procedure
  float measurement = takeSensorMeasurement();

  if (measurement < 0.0) {
    uiManager.showMessage("Blank Failed", "Sensor error - check serial");
    delay(2000);
    uiManager.showMeasureScreen();
    isBlanked = false;
    blankValue = 1.0;
    return;
  }

  blankValue = measurement;

  // Validate blank value
  if (blankValue < MIN_BLANK_VALUE) {
    Serial.print("ERROR: Blank value too low: ");
    Serial.println(blankValue, 4);
    uiManager.showMessage("Blank Failed", "Value too low - check sensor");
    delay(2000);
    uiManager.showMeasureScreen();
    isBlanked = false;
    blankValue = 1.0; // Reset to safe value
    return;
  }

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
