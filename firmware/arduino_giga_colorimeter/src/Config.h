/**
 * Config.h
 * Configuration constants for Open Colorimeter
 */

#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>

// Version
#define FIRMWARE_VERSION "1.0.0"

// File paths
#define CALIBRATIONS_FILE "/sd/calibrations.json"
#define CONFIGURATION_FILE "/sd/configuration.json"

// Timing constants
#define LOOP_DT 100              // Loop delay in ms
#define BLANK_DT 50              // Blanking sample delay in ms
#define DEBOUNCE_DT 600          // Button debounce in ms
#define NUM_BLANK_SAMPLES 50     // Number of samples for blanking

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

// Color definitions (RGB565 for display)
#define COLOR_BLACK   0x0000
#define COLOR_GRAY    0x8410
#define COLOR_RED     0xF800
#define COLOR_GREEN   0x07E0
#define COLOR_BLUE    0x001F
#define COLOR_WHITE   0xFFFF
#define COLOR_ORANGE  0xFDA0
#define COLOR_YELLOW  0xFFE0

// Display dimensions (Giga Display Shield - rotated 90 degrees)
#define SCREEN_WIDTH  800
#define SCREEN_HEIGHT 480

// Number of motors/solenoids
#define NUM_MOTORS 4
#define NUM_SOLENOIDS 4

// Default sensor settings (LOW gain for always-on LED, 100MS integration)
#define DEFAULT_GAIN TSL2591_GAIN_LOW
#define DEFAULT_INTEGRATION_TIME TSL2591_INTEGRATIONTIME_100MS
#define DEFAULT_PRECISION 2

// I2C Addresses
#define TSL2591_I2C_ADDRESS 0x29

#endif // CONFIG_H
