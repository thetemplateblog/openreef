/**
 * MotorController.h
 * Motor controller stub - to be implemented with new motor driver
 */

#ifndef MOTOR_CONTROLLER_H
#define MOTOR_CONTROLLER_H

#include <Arduino.h>

class MotorController {
public:
  MotorController();

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
  bool _mockMode;
};

#endif // MOTOR_CONTROLLER_H
