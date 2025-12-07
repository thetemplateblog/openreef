/**
 * Calibrations.h
 * Manages calibration data for various tests
 */

#ifndef CALIBRATIONS_H
#define CALIBRATIONS_H

#include <Arduino.h>
#include <vector>
#include <map>
#include <LittleFileSystem.h>
#include <BlockDevice.h>
#include "Config.h"  // For TSL2591_Gain enum

#define MAX_CALIBRATIONS 10
#define MAX_COEF 10

struct CalibrationData {
  String name;
  String units;
  String led;  // LED wavelength (e.g., "625nm")
  int gain;    // Sensor gain (1, 25, 428, or 9876)
  String integration_time;  // Integration time (e.g., "100ms", "200ms")
  String fitType;  // "polynomial"
  std::vector<float> fitCoef;
  float rangeMin;
  float rangeMax;
  float standard;  // Standard concentration for calibration
  bool valid;
};

class Calibrations {
public:
  Calibrations();

  // Load calibrations from JSON file (SD card or internal storage)
  bool load();
  bool loadFromString(const char* jsonString);

  // Apply calibration to absorbance value
  float apply(String calibrationName, float absorbance);

  // Get calibration info
  bool hasCalibration(String name);
  String getUnits(String name);
  String getLED(String name);
  int getGain(String name);
  String getIntegrationTime(String name);
  float getStandard(String name);
  int getCount();
  String getNameByIndex(int index);

  // Get all calibration names
  std::vector<String> getNames();

  // Update calibration coefficients (intercept and slope)
  void updateCoefficients(String name, float intercept, float slope);

private:
  std::map<String, CalibrationData> _calibrations;

  // Load built-in calibrations
  bool loadBuiltInCalibrations();

  // Persistent storage helpers (using LittleFS)
  bool saveCoefficients(String name, float intercept, float slope);
  bool loadCoefficients(String name, float& intercept, float& slope);
  String getCalibrationFilename(const String& name);

  // Parse JSON and populate calibrations
  bool parseJSON(const char* jsonString);

  // Apply polynomial fit
  float applyPolynomial(const std::vector<float>& coef, float x);
};

#endif // CALIBRATIONS_H
