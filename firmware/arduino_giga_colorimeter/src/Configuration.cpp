/**
 * Configuration.cpp
 * Implementation of configuration management
 */

#include "Configuration.h"
#include <ArduinoJson.h>

Configuration::Configuration() {
  // Defaults (will be overridden by JSON)
  _gain = DEFAULT_GAIN;
  _integrationTime = DEFAULT_INTEGRATION_TIME;
  _startupMode = "Absorbance";
  _precision = 2;
}

bool Configuration::load() {
  // Embedded configuration from data/configuration.json
  const char* configJson = R"({
  "gain" : 1,
  "integration_time" : "100ms",
  "startup" : "Absorbance",
  "precision" : 2
})";

  Serial.println("Loading configuration...");
  return parseJSON(configJson);
}

bool Configuration::parseJSON(const char* jsonString) {
  StaticJsonDocument<512> doc;

  DeserializationError error = deserializeJson(doc, jsonString);
  if (error) {
    Serial.print("Configuration JSON parse error: ");
    Serial.println(error.c_str());
    return false;
  }

  // Parse gain (numeric: 1, 25, 428, or 9876)
  if (doc.containsKey("gain")) {
    if (doc["gain"].is<int>()) {
      _gain = parseGain(doc["gain"].as<int>());
    } else {
      // Fallback for old string format
      _gain = parseGainString(doc["gain"].as<String>());
    }
  }

  // Parse integration time
  if (doc.containsKey("integration_time")) {
    _integrationTime = parseIntegrationTime(doc["integration_time"].as<String>());
  }

  // Parse startup mode
  if (doc.containsKey("startup")) {
    _startupMode = doc["startup"].as<String>();
  }

  // Parse precision
  if (doc.containsKey("precision")) {
    _precision = doc["precision"].as<int>();
  }

  Serial.println("Configuration loaded:");
  Serial.print("  Gain: ");
  if (doc["gain"].is<int>()) {
    Serial.print(doc["gain"].as<int>());
    Serial.println("x");
  } else {
    Serial.println(doc["gain"].as<String>());
  }
  Serial.print("  Integration time: ");
  Serial.println(doc["integration_time"].as<String>());
  Serial.print("  Startup: ");
  Serial.println(_startupMode);
  Serial.print("  Precision: ");
  Serial.println(_precision);

  return true;
}

TSL2591_Gain Configuration::parseGain(int gainValue) {
  switch (gainValue) {
    case 1:    return TSL2591_GAIN_LOW;   // 1x
    case 25:   return TSL2591_GAIN_MED;   // 25x
    case 428:  return TSL2591_GAIN_HIGH;  // 428x
    case 9876: return TSL2591_GAIN_MAX;   // 9876x
    default:
      Serial.print("Unknown gain value: ");
      Serial.print(gainValue);
      Serial.println(" - using 1x");
      return TSL2591_GAIN_LOW;
  }
}

TSL2591_Gain Configuration::parseGainString(const String& gainStr) {
  // Backward compatibility with old string format
  if (gainStr == "low") return TSL2591_GAIN_LOW;
  if (gainStr == "medium") return TSL2591_GAIN_MED;
  if (gainStr == "high") return TSL2591_GAIN_HIGH;
  if (gainStr == "max") return TSL2591_GAIN_MAX;

  Serial.print("Unknown gain: ");
  Serial.print(gainStr);
  Serial.println(" - using 1x");
  return TSL2591_GAIN_LOW;
}

TSL2591_IntegrationTime Configuration::parseIntegrationTime(const String& timeStr) {
  if (timeStr == "100ms") return TSL2591_INTEGRATIONTIME_100MS;
  if (timeStr == "200ms") return TSL2591_INTEGRATIONTIME_200MS;
  if (timeStr == "300ms") return TSL2591_INTEGRATIONTIME_300MS;
  if (timeStr == "400ms") return TSL2591_INTEGRATIONTIME_400MS;
  if (timeStr == "500ms") return TSL2591_INTEGRATIONTIME_500MS;
  if (timeStr == "600ms") return TSL2591_INTEGRATIONTIME_600MS;

  Serial.print("Unknown integration time: ");
  Serial.print(timeStr);
  Serial.println(" - using 100ms");
  return TSL2591_INTEGRATIONTIME_100MS;
}

TSL2591_Gain Configuration::getGain() {
  return _gain;
}

TSL2591_IntegrationTime Configuration::getIntegrationTime() {
  return _integrationTime;
}

String Configuration::getStartupMode() {
  return _startupMode;
}

int Configuration::getPrecision() {
  return _precision;
}

int Configuration::getIntegrationTimeMs() {
  switch (_integrationTime) {
    case TSL2591_INTEGRATIONTIME_100MS: return 100;
    case TSL2591_INTEGRATIONTIME_200MS: return 200;
    case TSL2591_INTEGRATIONTIME_300MS: return 300;
    case TSL2591_INTEGRATIONTIME_400MS: return 400;
    case TSL2591_INTEGRATIONTIME_500MS: return 500;
    case TSL2591_INTEGRATIONTIME_600MS: return 600;
    default: return 100;
  }
}
