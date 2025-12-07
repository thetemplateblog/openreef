/**
 * Calibrations.cpp
 * Implementation of calibration management
 */

#include "Calibrations.h"
#include "Config.h"
#include <ArduinoJson.h>
#include "QSPIFBlockDevice.h"
#include "SlicingBlockDevice.h"
#include "LittleFileSystem.h"

// QSPI flash and filesystem instances (shared with Configuration)
static QSPIFBlockDevice* qspi_bd = nullptr;
static mbed::SlicingBlockDevice* cal_data = nullptr;
mbed::LittleFileSystem* fs = nullptr;
bool fs_mounted = false;

// Use last 1MB of QSPI flash for calibration data (starts at 15MB)
#define CAL_STORAGE_OFFSET (15 * 1024 * 1024)
#define CAL_STORAGE_SIZE   (1 * 1024 * 1024)

Calibrations::Calibrations() {
  // Constructor - keep it minimal, no QSPI initialization here
  // QSPI will be initialized in load() after Serial is ready
}

bool Calibrations::load() {
  // Initialize QSPI flash filesystem on first call
  if (!fs_mounted) {
    Serial.println("Initializing persistent storage on QSPI flash...");

    // Create QSPI block device
    qspi_bd = new QSPIFBlockDevice(QSPI_SO0, QSPI_SO1, QSPI_SO2, QSPI_SO3,
                                   QSPI_SCK, QSPI_CS, QSPIF_POLARITY_MODE_1, 40000000);

    // Initialize the block device
    int err = qspi_bd->init();
    if (err) {
      Serial.print("ERROR: QSPI init failed (error ");
      Serial.print(err);
      Serial.println(")");
      delete qspi_bd;
      qspi_bd = nullptr;
      Serial.println("Calibrations will be RAM-only (lost on power cycle)");
    } else {
      Serial.print("QSPI flash size: ");
      Serial.print(qspi_bd->size() / (1024 * 1024));
      Serial.println(" MB");

      // Create a slice of QSPI flash for calibration data (last 1MB)
      Serial.print("Carving out ");
      Serial.print(CAL_STORAGE_SIZE / 1024);
      Serial.print(" KB at offset ");
      Serial.print(CAL_STORAGE_OFFSET / (1024 * 1024));
      Serial.println(" MB for calibrations");

      cal_data = new mbed::SlicingBlockDevice(qspi_bd, CAL_STORAGE_OFFSET, CAL_STORAGE_OFFSET + CAL_STORAGE_SIZE);
      err = cal_data->init();

      if (err) {
        Serial.print("ERROR: Storage slice init failed (error ");
        Serial.print(err);
        Serial.println(")");
        delete cal_data;
        delete qspi_bd;
        cal_data = nullptr;
        qspi_bd = nullptr;
        Serial.println("Calibrations will be RAM-only (lost on power cycle)");
      } else {
        // Create LittleFS instance
        fs = new mbed::LittleFileSystem("fs");

        // Try to mount the filesystem
        err = fs->mount(cal_data);
        if (err) {
          Serial.print("LittleFS mount failed (error ");
          Serial.print(err);
          Serial.println(") - formatting storage...");

          // Try to format it
          err = fs->reformat(cal_data);
          if (err) {
            Serial.print("ERROR: Format failed (error ");
            Serial.print(err);
            Serial.println(")");
            delete fs;
            delete cal_data;
            delete qspi_bd;
            fs = nullptr;
            cal_data = nullptr;
            qspi_bd = nullptr;
            Serial.println("Calibrations will be RAM-only (lost on power cycle)");
          } else {
            Serial.println("SUCCESS: LittleFS formatted on QSPI flash");
            Serial.println("Calibrations will persist across firmware uploads & power cycles!");
            fs_mounted = true;
          }
        } else {
          Serial.println("SUCCESS: LittleFS mounted on QSPI flash");
          Serial.println("Calibrations will persist across firmware uploads & power cycles!");
          fs_mounted = true;
        }
      }
    }
  }

  // Clean up old calibrations.json file if it exists (one-time cleanup)
  if (fs_mounted) {
    if (remove("/fs/calibrations.json") == 0) {
      Serial.println("Cleaned up old /fs/calibrations.json");
    }
  }

  // Load built-in calibrations
  Serial.println("Loading built-in calibrations");
  loadBuiltInCalibrations();

  // Try to load saved coefficient overrides from LittleFS
  if (fs_mounted && _calibrations.size() > 0) {
    Serial.println("Checking for saved coefficient overrides...");
    int loaded_count = 0;
    for (auto& kv : _calibrations) {
      float saved_intercept, saved_slope;
      if (loadCoefficients(kv.first, saved_intercept, saved_slope)) {
        if (kv.second.fitCoef.size() >= 2) {
          kv.second.fitCoef[0] = saved_intercept;
          kv.second.fitCoef[1] = saved_slope;
          Serial.print("  ");
          Serial.print(kv.first);
          Serial.print(" coefficients: intercept=");
          Serial.print(saved_intercept, 4);
          Serial.print(", slope=");
          Serial.println(saved_slope, 4);
          loaded_count++;
        }
      }
    }
    if (loaded_count > 0) {
      Serial.print("Applied ");
      Serial.print(loaded_count);
      Serial.println(" coefficient override(s)");
    }
  }

  return true;
}

bool Calibrations::loadBuiltInCalibrations() {
  // Built-in calibrations - no SD card required
  const char* builtInCalibrations = R"({
    "Phosphate Hanna": {
      "units": "ppm",
      "led": "880",
      "gain": 25,
      "integration_time": "100ms",
      "fit_type": "polynomial",
      "range": {"min": 0.0, "max": 0.50},
      "standard": 0.2882
    },
    "Nitrate API": {
      "units": "ppm",
      "led": "528",
      "gain": 1,
      "integration_time": "100ms",
      "fit_type": "polynomial",
      "range": {"min": 0.0, "max": 10},
      "standard": 5.0
    },
    "Nitrite API": {
      "units": "ppm",
      "led": "528",
      "gain": 1,
      "integration_time": "100ms",
      "fit_type": "polynomial",
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

    if (obj.containsKey("gain")) {
      cal.gain = obj["gain"].as<int>();
    } else {
      cal.gain = 1;  // Default to 1x gain if not specified
    }

    if (obj.containsKey("integration_time")) {
      cal.integration_time = obj["integration_time"].as<String>();
    } else {
      cal.integration_time = "100ms";  // Default to 100ms if not specified
    }

    if (obj.containsKey("fit_type")) {
      cal.fitType = obj["fit_type"].as<String>();
    }

    // Initialize fit_coef with default [0.0, 1.0]
    // Real coefficients come from LittleFS only
    cal.fitCoef.push_back(0.0);  // Intercept (always forced to 0)
    cal.fitCoef.push_back(1.0);  // Default slope (will be overridden from LittleFS if exists)

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

int Calibrations::getGain(String name) {
  if (hasCalibration(name)) {
    return _calibrations[name].gain;
  }
  return 1;  // Default to 1x gain
}

String Calibrations::getIntegrationTime(String name) {
  if (hasCalibration(name)) {
    return _calibrations[name].integration_time;
  }
  return "100ms";  // Default to 100ms
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

void Calibrations::updateCoefficients(String name, float intercept, float slope) {
  if (hasCalibration(name)) {
    // For linear calibration: y = intercept + slope * x
    if (_calibrations[name].fitCoef.size() >= 2) {
      _calibrations[name].fitCoef[0] = intercept;
      _calibrations[name].fitCoef[1] = slope;

      Serial.print("Updated calibration for ");
      Serial.print(name);
      Serial.print(": intercept=");
      Serial.print(intercept, 4);
      Serial.print(", slope=");
      Serial.println(slope, 4);

      // Save to LittleFS
      if (saveCoefficients(name, intercept, slope)) {
        Serial.println("Calibration saved to QSPI flash - will persist across uploads");
      } else {
        Serial.println("WARNING: Failed to save calibration to QSPI flash");
      }
    }
  }
}

String Calibrations::getCalibrationFilename(const String& name) {
  // Create filename (replace spaces with underscores)
  String filename = "/fs/cal_" + name;
  filename.replace(" ", "_");
  filename += ".dat";
  return filename;
}

bool Calibrations::saveCoefficients(String name, float intercept, float slope) {
  if (!fs_mounted) {
    return false;
  }

  String filename = getCalibrationFilename(name);

  Serial.print("Saving to LittleFS: file='");
  Serial.print(filename);
  Serial.print("', intercept=");
  Serial.print(intercept, 4);
  Serial.print(", slope=");
  Serial.println(slope, 4);

  // Open file for writing
  FILE* file = fopen(filename.c_str(), "wb");
  if (!file) {
    Serial.print("ERROR: Could not open file for writing: ");
    Serial.println(filename);
    return false;
  }

  // Write both coefficients
  float coeffs[2] = {intercept, slope};
  size_t written = fwrite(coeffs, sizeof(float), 2, file);
  fclose(file);

  if (written != 2) {
    Serial.println("ERROR: Failed to write coefficients");
    return false;
  }

  Serial.println("Successfully saved to LittleFS!");
  return true;
}

bool Calibrations::loadCoefficients(String name, float& intercept, float& slope) {
  if (!fs_mounted) {
    return false;
  }

  String filename = getCalibrationFilename(name);

  // Open file for reading
  FILE* file = fopen(filename.c_str(), "rb");
  if (!file) {
    return false;  // File doesn't exist
  }

  // Read both coefficients
  float coeffs[2];
  size_t read = fread(coeffs, sizeof(float), 2, file);
  fclose(file);

  if (read != 2) {
    return false;
  }

  intercept = coeffs[0];
  slope = coeffs[1];
  return true;
}
