/**
 * SolenoidController.cpp
 * Implementation of solenoid valve control
 */

#include "SolenoidController.h"

#define PCA9685_MODE1 0x00
#define PCA9685_LED0_ON_L 0x06

SolenoidController::SolenoidController(uint8_t address) {
  _address = address;
  _mockMode = false;

  // Initialize states to closed
  for (int i = 0; i <= NUM_SOLENOIDS; i++) {
    _states[i] = false;
  }

  initChannelMappings();
}

void SolenoidController::initChannelMappings() {
  // Map solenoids to PCA9685 channels or GPIO pins
  // Using channels 0-3 on PCA9685
  _solenoidChannels[1] = 0;  // Solenoid 1
  _solenoidChannels[2] = 1;  // Solenoid 2
  _solenoidChannels[3] = 2;  // Solenoid 3
  _solenoidChannels[4] = 3;  // Solenoid 4
}

bool SolenoidController::begin() {
  Wire.begin();

  // Try to communicate with PCA9685
  Wire.beginTransmission(_address);
  if (Wire.endTransmission() != 0) {
    Serial.println("Solenoid PCA9685 not found - running in mock mode");
    _mockMode = true;
    return false;
  }

  // Reset PCA9685
  write8(PCA9685_MODE1, 0x00);

  // Close all solenoids
  closeAll();

  Serial.println("Solenoid controller initialized");
  return true;
}

void SolenoidController::setState(uint8_t solenoidNum, bool state) {
  if (solenoidNum < 1 || solenoidNum > NUM_SOLENOIDS) {
    Serial.println("Invalid solenoid number");
    return;
  }

  _states[solenoidNum] = state;

  if (_mockMode) {
    Serial.print("[MOCK] Solenoid ");
    Serial.print(solenoidNum);
    Serial.print(state ? " OPEN" : " CLOSED");
    Serial.println();
    return;
  }

  uint8_t channel = _solenoidChannels[solenoidNum];

  if (state) {
    // Open (energize) - full on
    setPWM(channel, 4096, 0);
  } else {
    // Close (de-energize) - full off
    setPWM(channel, 0, 4096);
  }
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

// PCA9685 low-level functions
void SolenoidController::setPWM(uint8_t channel, uint16_t on, uint16_t off) {
  Wire.beginTransmission(_address);
  Wire.write(PCA9685_LED0_ON_L + 4 * channel);
  Wire.write(on & 0xFF);
  Wire.write(on >> 8);
  Wire.write(off & 0xFF);
  Wire.write(off >> 8);
  Wire.endTransmission();
}

void SolenoidController::write8(uint8_t reg, uint8_t value) {
  Wire.beginTransmission(_address);
  Wire.write(reg);
  Wire.write(value);
  Wire.endTransmission();
}

uint8_t SolenoidController::read8(uint8_t reg) {
  Wire.beginTransmission(_address);
  Wire.write(reg);
  Wire.endTransmission();

  Wire.requestFrom(_address, (uint8_t)1);
  return Wire.read();
}
