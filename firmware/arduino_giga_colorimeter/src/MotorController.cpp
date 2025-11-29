/**
 * MotorController.cpp
 * Implementation of DC motor control via PCA9685
 */

#include "MotorController.h"

MotorController::MotorController(uint8_t address) {
  _address = address;
  _mockMode = false;
  initChannelMappings();
}

void MotorController::initChannelMappings() {
  // Motor channel mappings for Adafruit Motor FeatherWing
  _motorChannels[1] = {8, 9, 10};   // Motor 1
  _motorChannels[2] = {13, 12, 11}; // Motor 2
  _motorChannels[3] = {2, 3, 4};    // Motor 3
  _motorChannels[4] = {7, 6, 5};    // Motor 4
}

bool MotorController::begin() {
  Wire.begin();

  // Try to communicate with PCA9685
  Wire.beginTransmission(_address);
  if (Wire.endTransmission() != 0) {
    Serial.println("PCA9685 not found - running in mock mode");
    _mockMode = true;
    return false;
  }

  // Reset PCA9685
  write8(PCA9685_MODE1, 0x00);

  // Set PWM frequency
  setPWMFreq(PCA9685_FREQUENCY);

  // Stop all motors
  stopAll();

  Serial.println("Motor controller initialized");
  return true;
}

void MotorController::setThrottle(uint8_t motorNum, float throttle) {
  if (motorNum < 1 || motorNum > 4) {
    Serial.println("Invalid motor number");
    return;
  }

  if (_mockMode) {
    Serial.print("[MOCK] Motor ");
    Serial.print(motorNum);
    Serial.print(" throttle: ");
    Serial.println(throttle);
    return;
  }

  // Clamp throttle to valid range
  throttle = constrain(throttle, -1.0, 1.0);

  MotorChannels& ch = _motorChannels[motorNum];

  if (throttle > 0.01) {
    // Forward
    uint16_t pwmValue = (uint16_t)(throttle * 4095);
    setPWM(ch.in1, 4096, 0);    // Full on
    setPWM(ch.in2, 0, 4096);     // Full off
    setPWM(ch.pwm, 0, pwmValue); // Speed control
  }
  else if (throttle < -0.01) {
    // Reverse
    uint16_t pwmValue = (uint16_t)(-throttle * 4095);
    setPWM(ch.in1, 0, 4096);     // Full off
    setPWM(ch.in2, 4096, 0);     // Full on
    setPWM(ch.pwm, 0, pwmValue); // Speed control
  }
  else {
    // Stop
    setPWM(ch.in1, 0, 4096);
    setPWM(ch.in2, 0, 4096);
    setPWM(ch.pwm, 0, 4096);
  }
}

void MotorController::stop(uint8_t motorNum) {
  setThrottle(motorNum, 0.0);
}

void MotorController::stopAll() {
  for (uint8_t i = 1; i <= 4; i++) {
    stop(i);
  }
}

void MotorController::runForward(uint8_t motorNum, float speed) {
  speed = constrain(abs(speed), 0.0, 1.0);
  setThrottle(motorNum, speed);
}

void MotorController::runReverse(uint8_t motorNum, float speed) {
  speed = constrain(abs(speed), 0.0, 1.0);
  setThrottle(motorNum, -speed);
}

bool MotorController::isMockMode() {
  return _mockMode;
}

// PCA9685 low-level functions
void MotorController::setPWM(uint8_t channel, uint16_t on, uint16_t off) {
  Wire.beginTransmission(_address);
  Wire.write(PCA9685_LED0_ON_L + 4 * channel);
  Wire.write(on & 0xFF);
  Wire.write(on >> 8);
  Wire.write(off & 0xFF);
  Wire.write(off >> 8);
  Wire.endTransmission();
}

void MotorController::setPWMFreq(float freq) {
  // Calculate prescale value
  float prescaleval = 25000000.0; // 25MHz oscillator
  prescaleval /= 4096.0;          // 12-bit resolution
  prescaleval /= freq;
  prescaleval -= 1.0;

  uint8_t prescale = (uint8_t)(prescaleval + 0.5);

  uint8_t oldmode = read8(PCA9685_MODE1);
  uint8_t newmode = (oldmode & 0x7F) | 0x10; // Sleep
  write8(PCA9685_MODE1, newmode);
  write8(PCA9685_PRESCALE, prescale);
  write8(PCA9685_MODE1, oldmode);
  delay(5);
  write8(PCA9685_MODE1, oldmode | 0xA0); // Auto-increment
}

void MotorController::write8(uint8_t reg, uint8_t value) {
  Wire.beginTransmission(_address);
  Wire.write(reg);
  Wire.write(value);
  Wire.endTransmission();
}

uint8_t MotorController::read8(uint8_t reg) {
  Wire.beginTransmission(_address);
  Wire.write(reg);
  Wire.endTransmission();

  Wire.requestFrom(_address, (uint8_t)1);
  return Wire.read();
}
