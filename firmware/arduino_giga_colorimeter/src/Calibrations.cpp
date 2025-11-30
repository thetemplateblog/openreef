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

// QSPI flash and filesystem instances
static QSPIFBlockDevice* qspi_bd = nullptr;
static mbed::SlicingBlockDevice* cal_data = nullptr;
static mbed::LittleFileSystem* fs = nullptr;
static bool fs_mounted = false;

// Use last 1MB of QSPI flash for calibration data (starts at 15MB)
#define CAL_STORAGE_OFFSET (15 * 1024 * 1024)
#define CAL_STORAGE_SIZE   (1 * 1024 * 1024)

Calibrations::Calibrations() {
  // Constructor - keep it minimal, no QSPI initialization here
  // QSPI will be initialized in load() after Serial is ready
}

bool Calibrations::load() {
  // Load built-in calibrations
  Serial.println("Loading built-in calibrations");
  loadBuiltInCalibrations();

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

  // Try to load saved coefficients from LittleFS
  if (fs_mounted) {
    Serial.println("Loading saved coefficients from LittleFS...");
    Serial.println("Checking storage for each calibration:");
    int loaded_count = 0;
    for (auto& kv : _calibrations) {
      Serial.print("  ");
      Serial.print(kv.first);
      Serial.print(" ... ");

      float saved_coefficient;
      if (loadCoefficient(kv.first, saved_coefficient)) {
        if (kv.second.fitCoef.size() >= 2) {
          kv.second.fitCoef[1] = saved_coefficient;
          Serial.print("FOUND: ");
          Serial.println(saved_coefficient, 4);
          loaded_count++;
        }
      } else {
        Serial.println("NOT FOUND");
      }
    }
    if (loaded_count > 0) {
      Serial.print("Successfully loaded ");
      Serial.print(loaded_count);
      Serial.println(" saved calibration(s) from QSPI flash");
    } else {
      Serial.println("No saved calibrations found in QSPI flash");
    }
  } else {
    Serial.println("LittleFS not mounted - calibrations will be in RAM only");
  }

  return true;
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

      // Save to LittleFS
      if (saveCoefficient(name, newCoefficient)) {
        Serial.println("Calibration saved to QSPI flash - will persist across uploads");
      } else {
        Serial.println("WARNING: Failed to save calibration to QSPI flash");
      }
    }
  }
}

bool Calibrations::saveCoefficient(String name, float coefficient) {
  if (!fs_mounted) {
    return false;
  }

  // Create filename (replace spaces with underscores)
  String filename = "/fs/cal_" + name;
  filename.replace(" ", "_");
  filename += ".dat";

  Serial.print("Saving to LittleFS: file='");
  Serial.print(filename);
  Serial.print("', value=");
  Serial.println(coefficient, 4);

  // Open file for writing
  FILE* file = fopen(filename.c_str(), "wb");
  if (!file) {
    Serial.print("ERROR: Could not open file for writing: ");
    Serial.println(filename);
    return false;
  }

  // Write coefficient
  size_t written = fwrite(&coefficient, sizeof(float), 1, file);
  fclose(file);

  if (written != 1) {
    Serial.println("ERROR: Failed to write coefficient");
    return false;
  }

  Serial.println("Successfully saved to LittleFS!");
  return true;
}

bool Calibrations::loadCoefficient(String name, float& coefficient) {
  if (!fs_mounted) {
    return false;
  }

  // Create filename (replace spaces with underscores)
  String filename = "/fs/cal_" + name;
  filename.replace(" ", "_");
  filename += ".dat";

  // Open file for reading
  FILE* file = fopen(filename.c_str(), "rb");
  if (!file) {
    return false;  // File doesn't exist
  }

  // Read coefficient
  size_t read = fread(&coefficient, sizeof(float), 1, file);
  fclose(file);

  if (read != 1) {
    return false;
  }

  return true;
}
