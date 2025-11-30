/**
 * SolenoidController.cpp
 * Solenoid controller stub - to be implemented with new hardware
 */

#include "SolenoidController.h"

SolenoidController::SolenoidController() {
  _mockMode = true;

  // Initialize states to closed
  for (int i = 0; i <= NUM_SOLENOIDS; i++) {
    _states[i] = false;
  }
}

bool SolenoidController::begin() {
  Serial.println("SolenoidController: Stub implementation - no hardware");
  _mockMode = true;
  return false;
}

void SolenoidController::setState(uint8_t solenoidNum, bool state) {
  if (solenoidNum < 1 || solenoidNum > NUM_SOLENOIDS) {
    Serial.println("Invalid solenoid number");
    return;
  }

  _states[solenoidNum] = state;

  Serial.print("Solenoid ");
  Serial.print(solenoidNum);
  Serial.print(state ? " OPEN" : " CLOSED");
  Serial.println();
}

void SolenoidController::open(uint8_t solenoidNum) {
  setState(solenoidNum, true);
}

void SolenoidController::close(uint8_t solenoidNum) {
  setState(solenoidNum, false);
}

void SolenoidController::toggle(uint8_t solenoidNum) {
  if (solenoidNum < 1 || solenoidNum > NUM_SOLENOIDS) {
    return;
  }
  setState(solenoidNum, !_states[solenoidNum]);
}

bool SolenoidController::getState(uint8_t solenoidNum) {
  if (solenoidNum < 1 || solenoidNum > NUM_SOLENOIDS) {
    return false;
  }
  return _states[solenoidNum];
}

void SolenoidController::closeAll() {
  for (uint8_t i = 1; i <= NUM_SOLENOIDS; i++) {
    close(i);
  }
}

void SolenoidController::pulse(uint8_t solenoidNum, uint32_t duration) {
  open(solenoidNum);
  delay(duration);
  close(solenoidNum);
}

bool SolenoidController::isMockMode() {
  return _mockMode;
}
