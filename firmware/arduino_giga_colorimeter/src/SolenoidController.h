/**
 * SolenoidController.h
 * Controls solenoid valves via PCA9685 PWM driver or GPIO
 */

#ifndef SOLENOID_CONTROLLER_H
#define SOLENOID_CONTROLLER_H

#include <Arduino.h>
#include <Wire.h>
#include "Config.h"

class SolenoidController {
public:
  SolenoidController(uint8_t address = PCA9685_SOLENOID_ADDRESS);

  // Initialize the controller
  bool begin();

  // Set solenoid state (true = energized/open, false = de-energized/closed)
  void setState(uint8_t solenoidNum, bool state);

  // Open solenoid
  void open(uint8_t solenoidNum);

  // Close solenoid
  void close(uint8_t solenoidNum);

  // Toggle solenoid state
  void toggle(uint8_t solenoidNum);

  // Get current state
  bool getState(uint8_t solenoidNum);

  // Close all solenoids
  void closeAll();

  // Pulse solenoid (open for duration ms, then close)
  void pulse(uint8_t solenoidNum, uint32_t duration);

  // Check if controller is in mock mode
  bool isMockMode();

private:
  uint8_t _address;
  bool _mockMode;
  bool _states[NUM_SOLENOIDS + 1]; // Index 1-4 for solenoids 1-4

  // Solenoid channel mappings on PCA9685 (or GPIO pins if not using PCA9685)
  uint8_t _solenoidChannels[NUM_SOLENOIDS + 1];

  // PCA9685 PWM functions
  void setPWM(uint8_t channel, uint16_t on, uint16_t off);
  void write8(uint8_t reg, uint8_t value);
  uint8_t read8(uint8_t reg);

  // Initialize channel mappings
  void initChannelMappings();
};

#endif // SOLENOID_CONTROLLER_H
