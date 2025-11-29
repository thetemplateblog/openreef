/**
 * MotorController.h
 * Controls DC motors via PCA9685 PWM driver
 */

#ifndef MOTOR_CONTROLLER_H
#define MOTOR_CONTROLLER_H

#include <Arduino.h>
#include <Wire.h>
#include "Config.h"

// PCA9685 Register definitions
#define PCA9685_MODE1 0x00
#define PCA9685_PRESCALE 0xFE
#define PCA9685_LED0_ON_L 0x06

class MotorController {
public:
  MotorController(uint8_t address = PCA9685_I2C_ADDRESS);

  // Initialize the controller
  bool begin();

  // Set motor throttle (-1.0 to 1.0)
  // Negative = reverse, Positive = forward, 0 = stop
  void setThrottle(uint8_t motorNum, float throttle);

  // Stop specific motor
  void stop(uint8_t motorNum);

  // Stop all motors
  void stopAll();

  // Run motor forward at specified speed (0.0 to 1.0)
  void runForward(uint8_t motorNum, float speed = 0.5);

  // Run motor in reverse at specified speed (0.0 to 1.0)
  void runReverse(uint8_t motorNum, float speed = 0.5);

  // Check if controller is in mock mode (hardware not found)
  bool isMockMode();

private:
  uint8_t _address;
  bool _mockMode;

  // Motor channel mappings on PCA9685
  struct MotorChannels {
    uint8_t pwm;
    uint8_t in1;
    uint8_t in2;
  };

  MotorChannels _motorChannels[5]; // Index 1-4 for motors 1-4

  // PCA9685 PWM functions
  void setPWM(uint8_t channel, uint16_t on, uint16_t off);
  void setPWMFreq(float freq);
  void write8(uint8_t reg, uint8_t value);
  uint8_t read8(uint8_t reg);

  // Initialize channel mappings
  void initChannelMappings();
};

#endif // MOTOR_CONTROLLER_H
