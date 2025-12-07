/**
 * LightSensor.h
 * Interface for TSL2591 light sensor
 */

#ifndef LIGHT_SENSOR_H
#define LIGHT_SENSOR_H

#include <Arduino.h>
#include <Wire.h>
#include "Config.h"

// TSL2591 Register definitions
#define TSL2591_COMMAND_BIT       0x80
#define TSL2591_ENABLE_POWEROFF   0x00
#define TSL2591_ENABLE_POWERON    0x01
#define TSL2591_ENABLE_AEN        0x02
#define TSL2591_ENABLE_AIEN       0x10
#define TSL2591_REGISTER_ENABLE   0x00
#define TSL2591_REGISTER_CONTROL  0x01
#define TSL2591_REGISTER_DEVICE_ID 0x12
#define TSL2591_REGISTER_CHAN0_LOW 0x14
#define TSL2591_REGISTER_CHAN0_HIGH 0x15
#define TSL2591_REGISTER_CHAN1_LOW 0x16
#define TSL2591_REGISTER_CHAN1_HIGH 0x17

class LightSensor {
public:
  LightSensor();
  bool begin();

  // Get raw sensor value
  uint16_t getValue();
  uint16_t getChannel0();  // Full spectrum
  uint16_t getChannel1();  // IR only

  // Gain settings
  void setGain(TSL2591_Gain gain);
  TSL2591_Gain getGain();

  // Integration time settings
  void setIntegrationTime(TSL2591_IntegrationTime time);
  TSL2591_IntegrationTime getIntegrationTime();

  // Max counts for overflow detection
  uint16_t getMaxCounts();

  // Check if sensor reading is overflowed
  bool isOverflow();

  // Enable/disable sensor power (for power saving)
  void enable();
  void disable();

private:
  TSL2591_Gain _gain;
  TSL2591_IntegrationTime _integrationTime;

  // I2C communication
  void write8(uint8_t reg, uint8_t value);
  uint8_t read8(uint8_t reg);
  uint16_t read16(uint8_t reg);
};

#endif // LIGHT_SENSOR_H
