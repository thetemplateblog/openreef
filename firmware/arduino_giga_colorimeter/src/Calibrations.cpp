/**
 * Calibrations.cpp
 * Implementation of calibration management
 */

#include "Calibrations.h"
#include "Config.h"
#include <ArduinoJson.h>
#include <SD.h>

Calibrations::Calibrations() {
  // Constructor
}

bool Calibrations::load() {
  // Try to load from SD card first
  if (SD.begin()) {
    File file = SD.open(CALIBRATIONS_FILE, FILE_READ);
    if (file) {
      Serial.println("Loading calibrations from SD card...");
      // Read file into string
      String jsonString = "";
      while (file.available()) {
        jsonString += (char)file.read();
      }
      file.close();
      return loadFromString(jsonString.c_str());
    }
  }

  // No SD card or file not found - use built-in calibrations
  Serial.println("SD card not available - using built-in calibrations");
  return loadBuiltInCalibrations();
}

bool Calibrations::loadBuiltInCalibrations() {
  // Built-in calibrations - no SD card required
  const char* builtInCalibrations = R"({
    "Phosphate Hanna": {
      "units": "ppm",
      "led": "850",
      "fit_type": "polynomial",
      "fit_coef": [0.0, 18.30],
      "range": {"min": 0.0, "max": 0.50},
      "standard": 0.307
    },
    "Nitrate API": {
      "units": "ppm",
      "led": "528",
      "fit_type": "polynomial",
      "fit_coef": [0.32039213453320625, 34.032597696304, 0.0],
      "range": {"min": 0.0, "max": 10},
      "standard": 5.0
    },
    "Nitrite API": {
      "units": "ppm",
      "led": "528",
      "fit_type": "polynomial",
      "fit_coef": [0.13111937060865314, 1.2591439203550079, 0.0],
      "range": {"min": 0.0, "max": 1.4},
      "standard": 0.5
    }
  })";

  Serial.println("Loading built-in calibrations...");
  return loadFromString(builtInCalibrations);
}

bool Calibrations::loadFromString(const char* jsonString) {
  return parseJSON(jsonString);
}

bool Calibrations::parseJSON(const char* jsonString) {
  // Create JSON document (adjust size as needed)
  StaticJsonDocument<4096> doc;

  DeserializationError error = deserializeJson(doc, jsonString);
  if (error) {
    Serial.print("JSON parse error: ");
    Serial.println(error.c_str());
    return false;
  }

  _calibrations.clear();

  // Iterate through calibrations
  for (JsonPair kv : doc.as<JsonObject>()) {
    CalibrationData cal;
    cal.name = kv.key().c_str();
    cal.valid = true;

    JsonObject obj = kv.value();

    // Parse fields
    if (obj.containsKey("units")) {
      cal.units = obj["units"].as<String>();
    }

    if (obj.containsKey("led")) {
      cal.led = obj["led"].as<String>();
    }

    if (obj.containsKey("fit_type")) {
      cal.fitType = obj["fit_type"].as<String>();
    }

    // Parse coefficients
    if (obj.containsKey("fit_coef")) {
      JsonArray coefArray = obj["fit_coef"];
      for (JsonVariant v : coefArray) {
        cal.fitCoef.push_back(v.as<float>());
      }
    }

    // Parse range
    if (obj.containsKey("range")) {
      JsonObject range = obj["range"];
      cal.rangeMin = range["min"];
      cal.rangeMax = range["max"];
    }

    // Parse standard concentration
    if (obj.containsKey("standard")) {
      cal.standard = obj["standard"];
    } else {
      cal.standard = 0.0;
    }

    // Store calibration
    _calibrations[cal.name] = cal;

    Serial.print("Loaded calibration: ");
    Serial.print(cal.name);
    Serial.print(" (");
    Serial.print(cal.units);
    Serial.println(")");
  }

  return true;
}

float Calibrations::apply(String calibrationName, float absorbance) {
  if (!hasCalibration(calibrationName)) {
    Serial.print("Calibration not found: ");
    Serial.println(calibrationName);
    return absorbance;
  }

  CalibrationData& cal = _calibrations[calibrationName];

  if (cal.fitType == "polynomial") {
    return applyPolynomial(cal.fitCoef, absorbance);
  }

  // Default: return absorbance unchanged
  return absorbance;
}

float Calibrations::applyPolynomial(const std::vector<float>& coef, float x) {
  float result = 0.0;
  float xPower = 1.0;

  for (size_t i = 0; i < coef.size(); i++) {
    result += coef[i] * xPower;
    xPower *= x;
  }

  return result;
}

bool Calibrations::hasCalibration(String name) {
  return _calibrations.find(name) != _calibrations.end();
}

String Calibrations::getUnits(String name) {
  if (hasCalibration(name)) {
    return _calibrations[name].units;
  }
  return "";
}

String Calibrations::getLED(String name) {
  if (hasCalibration(name)) {
    return _calibrations[name].led;
  }
  return "";
}

int Calibrations::getCount() {
  return _calibrations.size();
}

String Calibrations::getNameByIndex(int index) {
  if (index < 0 || index >= (int)_calibrations.size()) {
    return "";
  }

  int i = 0;
  for (auto& kv : _calibrations) {
    if (i == index) {
      return kv.first;
    }
    i++;
  }
  return "";
}

std::vector<String> Calibrations::getNames() {
  std::vector<String> names;
  for (auto& kv : _calibrations) {
    names.push_back(kv.first);
  }
  return names;
}

float Calibrations::getStandard(String name) {
  if (hasCalibration(name)) {
    return _calibrations[name].standard;
  }
  return 0.0;
}

void Calibrations::updateCoefficient(String name, float newCoefficient) {
  if (hasCalibration(name)) {
    // For linear calibration: y = coef[0] + coef[1] * x
    // Update the slope (coef[1])
    if (_calibrations[name].fitCoef.size() >= 2) {
      _calibrations[name].fitCoef[1] = newCoefficient;
      Serial.print("Updated coefficient for ");
      Serial.print(name);
      Serial.print(" to: ");
      Serial.println(newCoefficient);
    }
  }
}
