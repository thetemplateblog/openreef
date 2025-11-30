/**
 * MotorController.cpp
 * Motor controller stub - to be implemented with new motor driver
 */

#include "MotorController.h"

MotorController::MotorController() {
  _mockMode = true;
}

bool MotorController::begin() {
  Serial.println("MotorController: Stub implementation - no hardware");
  _mockMode = true;
  return false;
}

void MotorController::setThrottle(uint8_t motorNum, float throttle) {
  Serial.print("Motor ");
  Serial.print(motorNum);
  Serial.print(" throttle: ");
  Serial.println(throttle);
}

void MotorController::stop(uint8_t motorNum) {
  Serial.print("Motor ");
  Serial.print(motorNum);
  Serial.println(" stopped");
}

void MotorController::stopAll() {
  Serial.println("All motors stopped");
}

void MotorController::runForward(uint8_t motorNum, float speed) {
  Serial.print("Motor ");
  Serial.print(motorNum);
  Serial.print(" forward at speed: ");
  Serial.println(speed);
}

void MotorController::runReverse(uint8_t motorNum, float speed) {
  Serial.print("Motor ");
  Serial.print(motorNum);
  Serial.print(" reverse at speed: ");
  Serial.println(speed);
}

bool MotorController::isMockMode() {
  return _mockMode;
}
