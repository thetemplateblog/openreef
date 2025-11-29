/**
 * UI_Manager.h
 * Manages LVGL UI for 800x480 touchscreen
 */

#ifndef UI_MANAGER_H
#define UI_MANAGER_H

#include <Arduino.h>
#include "Arduino_H7_Video.h"
#include "Arduino_GigaDisplayTouch.h"
#include "lvgl.h"
#include "Config.h"

// Forward declarations for callbacks
class UI_Manager;
class MotorController;
class Calibrations;

// UI Screens
enum Screen {
  SCREEN_MEASURE,
  SCREEN_MENU,
  SCREEN_MOTOR_SELECT,
  SCREEN_MOTOR_CONTROL,
  SCREEN_SOLENOID,
  SCREEN_SETTINGS,
  SCREEN_MESSAGE,
  SCREEN_CALIBRATE
};

class UI_Manager {
public:
  UI_Manager();

  // Initialize UI
  void begin(MotorController* motorController = nullptr, Calibrations* calibrations = nullptr);

  // Update UI (call in loop)
  void update();

  // Screen navigation
  void showMeasureScreen();
  void showMenuScreen();
  void showMotorSelectScreen();
  void showMotorControlScreen(int motorNum);
  void showSolenoidScreen(int solenoidNum);
  void showSettingsScreen();
  void showMessage(const char* title, const char* message);
  void showCalibrateScreen();

  // Measurement screen updates
  void setMeasurementValue(float value, bool blanked);
  void setMeasurementName(const char* name);
  void setMeasurementUnits(const char* units);
  void setSensorStatus(bool initialized);
  void showOverflow();

  // Callback handlers (public so they can be accessed by C callbacks)
  void handleBlankButton();
  void handleMenuButton();
  void handleBackButton();
  void handleMeasurementSelect(const char* measurement);
  void handleMotorsButton();
  void handleMotorSelect(int motorNum);
  void handleMotorForward(int motorNum);
  void handleMotorReverse(int motorNum);
  void handleMotorStop(int motorNum);
  void handleCalibrateButton();
  void handleCalibrationSelect(const char* calibrationName);
  void handleCalibrationBlank();
  void handleCalibrationMeasure();

  // Public members so callbacks can access them
  int _currentMotorNum;
  String _currentCalibrationName;

private:
  Arduino_H7_Video _display;
  Arduino_GigaDisplayTouch _touchDetector;
  Screen _currentScreen;
  MotorController* _motorController;
  Calibrations* _calibrations;

  // LVGL objects
  lv_obj_t* _screen_measure;
  lv_obj_t* _screen_menu;
  lv_obj_t* _screen_motor_select;
  lv_obj_t* _screen_motor_control;
  lv_obj_t* _screen_message;

  // Measure screen widgets
  lv_obj_t* _label_title;
  lv_obj_t* _label_value;
  lv_obj_t* _label_status;
  lv_obj_t* _btn_blank;
  lv_obj_t* _btn_menu;

  // Menu screen widgets
  lv_obj_t* _btn_absorbance;
  lv_obj_t* _btn_transmittance;
  lv_obj_t* _btn_raw;
  lv_obj_t* _btn_motors;
  lv_obj_t* _btn_back;

  // Motor select screen widgets
  lv_obj_t* _btn_motor1;
  lv_obj_t* _btn_motor2;
  lv_obj_t* _btn_motor_back;

  // Motor control screen widgets
  lv_obj_t* _label_motor_title;
  lv_obj_t* _btn_motor_forward;
  lv_obj_t* _btn_motor_reverse;
  lv_obj_t* _btn_motor_stop;
  lv_obj_t* _btn_motor_control_back;

  // Message screen widgets
  lv_obj_t* _label_msg_title;
  lv_obj_t* _label_msg_text;

  // Calibration screen widgets
  lv_obj_t* _screen_calibrate;
  lv_obj_t* _label_cal_title;
  lv_obj_t* _label_cal_instructions;
  lv_obj_t* _cal_scroll_container;
  lv_obj_t* _btn_cal_blank;
  lv_obj_t* _btn_cal_measure;
  lv_obj_t* _btn_cal_back;

  // Measurement screen state
  String _measurementName;
  String _measurementUnits;
  float _measurementValue;
  bool _isBlanked;
  bool _sensorInitialized;

  // Message screen state
  String _messageTitle;
  String _messageText;

  // Calibration state
  float _calBlankAbsorbance;
  bool _calBlanked;

  // Create screen functions
  void createMeasureScreen();
  void createMenuScreen();
  void createMotorSelectScreen();
  void createMotorControlScreen();
  void createMessageScreen();
  void createCalibrateScreen();

  // Touch input driver for LVGL
  static void touchpad_read(lv_indev_t* indev, lv_indev_data_t* data);
};

#endif // UI_MANAGER_H
