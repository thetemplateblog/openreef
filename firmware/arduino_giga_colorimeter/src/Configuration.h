/**
 * Configuration.h
 * Manages device configuration
 */

#ifndef CONFIGURATION_H
#define CONFIGURATION_H

#include <Arduino.h>
#include "Config.h"

class Configuration {
public:
  Configuration();

  // Load configuration from embedded JSON
  bool load();

  // Getters
  TSL2591_Gain getGain();
  TSL2591_IntegrationTime getIntegrationTime();
  String getStartupMode();
  int getPrecision();

  // Get integration time in milliseconds (for BLANK_DT calculation)
  int getIntegrationTimeMs();

  // Parse integration time string to enum (needed by UI_Manager for per-calibration settings)
  TSL2591_IntegrationTime parseIntegrationTime(const String& timeStr);

private:
  TSL2591_Gain _gain;
  TSL2591_IntegrationTime _integrationTime;
  String _startupMode;
  int _precision;

  bool parseJSON(const char* jsonString);
  TSL2591_Gain parseGain(int gainValue);
  TSL2591_Gain parseGainString(const String& gainStr);  // Backward compatibility
};

#endif // CONFIGURATION_H
