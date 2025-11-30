/**
 * LightSensor.cpp
 * Implementation of TSL2591 light sensor interface
 */

#include "LightSensor.h"

LightSensor::LightSensor() {
  _gain = DEFAULT_GAIN;
  _integrationTime = DEFAULT_INTEGRATION_TIME;
  _channel = 0; // Default to full spectrum (channel 0)
}

bool LightSensor::begin() {
  Wire.begin();

  // Check if device is present on I2C bus
  Serial.print("Checking for TSL2591 at address 0x");
  Serial.println(TSL2591_I2C_ADDRESS, HEX);

  Wire.beginTransmission(TSL2591_I2C_ADDRESS);
  if (Wire.endTransmission() != 0) {
    Serial.println("ERROR: TSL2591 not found on I2C bus!");
    Serial.print("Expected address: 0x");
    Serial.println(TSL2591_I2C_ADDRESS, HEX);
    return false;
  }
  Serial.println("TSL2591 found on I2C bus");

  // Verify device ID
  Serial.print("Reading device ID register 0x");
  Serial.println(TSL2591_REGISTER_DEVICE_ID, HEX);
  uint8_t id = read8(TSL2591_REGISTER_DEVICE_ID);
  Serial.print("Device ID: 0x");
  Serial.print(id, HEX);
  Serial.print(" (expected 0x50)");

  if (id != 0x50) {
    Serial.println(" - MISMATCH!");
    Serial.println("ERROR: Wrong device ID");
    return false;
  }
  Serial.println(" - OK!");

  // Enable the device
  Serial.println("Enabling sensor...");
  enable();
  delay(100); // Give sensor time to power up

  // Set gain and integration time
  Serial.print("Setting gain: 0x");
  Serial.print(_gain, HEX);
  Serial.print(" integration time: 0x");
  Serial.println(_integrationTime, HEX);
  write8(TSL2591_REGISTER_CONTROL, _gain | _integrationTime);
  delay(120); // Wait for integration to complete

  // Verify settings were applied
  uint8_t control = read8(TSL2591_REGISTER_CONTROL);
  Serial.print("Control register readback: 0x");
  Serial.print(control, HEX);
  Serial.print(" (gain=0x");
  Serial.print(control & 0x30, HEX);
  Serial.print(", itime=0x");
  Serial.print(control & 0x07, HEX);
  Serial.println(")");

  Serial.println("TSL2591 initialized successfully");
  return true;
}

void LightSensor::enable() {
  write8(TSL2591_REGISTER_ENABLE, TSL2591_ENABLE_POWERON | TSL2591_ENABLE_AEN);
}

void LightSensor::disable() {
  write8(TSL2591_REGISTER_ENABLE, TSL2591_ENABLE_POWEROFF);
}

uint16_t LightSensor::getValue() {
  if (_channel == 0) {
    return getChannel0();
  } else {
    return getChannel1();
  }
}

uint16_t LightSensor::getChannel0() {
  // Read full spectrum (visible + IR)
  uint8_t low = read8(TSL2591_REGISTER_CHAN0_LOW);
  uint8_t high = read8(TSL2591_REGISTER_CHAN0_HIGH);
  return (high << 8) | low;
}

uint16_t LightSensor::getChannel1() {
  // Read IR only
  uint8_t low = read8(TSL2591_REGISTER_CHAN1_LOW);
  uint8_t high = read8(TSL2591_REGISTER_CHAN1_HIGH);
  return (high << 8) | low;
}

void LightSensor::setGain(TSL2591_Gain gain) {
  _gain = gain;
  write8(TSL2591_REGISTER_CONTROL, _gain | _integrationTime);
  delay(120); // Wait for integration to complete
}

TSL2591_Gain LightSensor::getGain() {
  return _gain;
}

void LightSensor::setIntegrationTime(TSL2591_IntegrationTime time) {
  _integrationTime = time;
  write8(TSL2591_REGISTER_CONTROL, _gain | _integrationTime);
  delay(120); // Wait for integration to complete
}

TSL2591_IntegrationTime LightSensor::getIntegrationTime() {
  return _integrationTime;
}

uint16_t LightSensor::getMaxCounts() {
  if (_integrationTime == TSL2591_INTEGRATIONTIME_100MS) {
    return TSL2591_MAX_COUNT_100MS;
  }
  return TSL2591_MAX_COUNT;
}

bool LightSensor::isOverflow() {
  uint16_t value = getValue();
  return (value >= getMaxCounts());
}

// I2C communication functions
void LightSensor::write8(uint8_t reg, uint8_t value) {
  Wire.beginTransmission(TSL2591_I2C_ADDRESS);
  Wire.write(TSL2591_COMMAND_BIT | reg);
  Wire.write(value);
  Wire.endTransmission();
}

uint8_t LightSensor::read8(uint8_t reg) {
  Wire.beginTransmission(TSL2591_I2C_ADDRESS);
  Wire.write(TSL2591_COMMAND_BIT | reg);
  Wire.endTransmission();

  Wire.requestFrom(TSL2591_I2C_ADDRESS, 1);
  return Wire.read();
}

uint16_t LightSensor::read16(uint8_t reg) {
  Wire.beginTransmission(TSL2591_I2C_ADDRESS);
  Wire.write(TSL2591_COMMAND_BIT | reg);
  Wire.endTransmission();

  Wire.requestFrom(TSL2591_I2C_ADDRESS, 2);
  uint8_t low = Wire.read();
  uint8_t high = Wire.read();
  return (high << 8) | low;
}
