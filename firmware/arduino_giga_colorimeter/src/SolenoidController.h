/**
 * SolenoidController.h
 * Solenoid controller stub - to be implemented with new hardware
 */

#ifndef SOLENOID_CONTROLLER_H
#define SOLENOID_CONTROLLER_H

#include <Arduino.h>
#include "Config.h"

class SolenoidController {
public:
  SolenoidController();

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
  bool _mockMode;
  bool _states[NUM_SOLENOIDS + 1]; // Index 1-4 for solenoids 1-4
};

#endif // SOLENOID_CONTROLLER_H
