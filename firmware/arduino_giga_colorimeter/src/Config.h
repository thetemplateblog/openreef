/**
 * Config.h
 * Configuration constants for Open Colorimeter
 */

#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>

// Version
#define FIRMWARE_VERSION "1.0.0"

// Timing constants
#define BLANK_DT 50              // Blanking sample delay in ms (match v0.1.1 firmware)
#define NUM_BLANK_SAMPLES 50     // Number of samples for blanking (median calculation, match v0.1.1)

// TSL2591 Sensor constants
#define TSL2591_MAX_COUNT_100MS 36863  // 0x8FFF
#define TSL2591_MAX_COUNT 65535        // 0xFFFF

// TSL2591 Gain settings
enum TSL2591_Gain {
  TSL2591_GAIN_LOW = 0x00,   // 1x gain
  TSL2591_GAIN_MED = 0x10,   // 25x gain
  TSL2591_GAIN_HIGH = 0x20,  // 428x gain
  TSL2591_GAIN_MAX = 0x30    // 9876x gain
};

// TSL2591 Integration time settings
enum TSL2591_IntegrationTime {
  TSL2591_INTEGRATIONTIME_100MS = 0x00,
  TSL2591_INTEGRATIONTIME_200MS = 0x01,
  TSL2591_INTEGRATIONTIME_300MS = 0x02,
  TSL2591_INTEGRATIONTIME_400MS = 0x03,
  TSL2591_INTEGRATIONTIME_500MS = 0x04,
  TSL2591_INTEGRATIONTIME_600MS = 0x05
};

// Display dimensions (Giga Display Shield)
#define SCREEN_WIDTH  800
#define SCREEN_HEIGHT 480

// Default sensor settings (LOW gain for very bright LED)
#define DEFAULT_GAIN TSL2591_GAIN_LOW
#define DEFAULT_INTEGRATION_TIME TSL2591_INTEGRATIONTIME_100MS
#define DEFAULT_PRECISION 2

// I2C Addresses
#define TSL2591_I2C_ADDRESS 0x29

// Measurement constants
#define SENSOR_STABILIZATION_DELAY_MS 10000  // LED thermal stabilization - critical for accuracy
#define MIN_BLANK_VALUE 0.001
#define MIN_ABSORBANCE_THRESHOLD 0.001

#endif // CONFIG_H
