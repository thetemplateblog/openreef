/**
 * UI_Manager.cpp
 * LVGL Implementation for Giga Display
 */

#include "UI_Manager.h"
#include "MotorController.h"
#include "Calibrations.h"
#include "LightSensor.h"

// External flags and data from main sketch
extern bool blankRequested;
extern String currentMeasurement;
extern float blankValue;
extern bool isBlanked;
extern LightSensor lightSensor;

// Global pointer to UI manager instance for callbacks
static UI_Manager* ui_instance = nullptr;

// Touch detector global for LVGL driver
static Arduino_GigaDisplayTouch* touchDetector_ptr = nullptr;

// LVGL event callbacks (C-style functions that call class methods)
static void blank_btn_event_cb(lv_event_t* e) {
  if (ui_instance) ui_instance->handleBlankButton();
}

static void menu_btn_event_cb(lv_event_t* e) {
  if (ui_instance) ui_instance->handleMenuButton();
}

static void back_btn_event_cb(lv_event_t* e) {
  if (ui_instance) ui_instance->handleBackButton();
}

static void absorbance_btn_event_cb(lv_event_t* e) {
  if (ui_instance) ui_instance->handleMeasurementSelect("Absorbance");
}

static void transmittance_btn_event_cb(lv_event_t* e) {
  if (ui_instance) ui_instance->handleMeasurementSelect("Transmittance");
}

static void raw_btn_event_cb(lv_event_t* e) {
  if (ui_instance) ui_instance->handleMeasurementSelect("Raw Sensor");
}

static void calibration_btn_event_cb(lv_event_t* e) {
  if (ui_instance) {
    // Get the button that was clicked
    lv_obj_t* btn = (lv_obj_t*)lv_event_get_target(e);
    // Get the label (first child of button)
    lv_obj_t* label = lv_obj_get_child(btn, 0);
    // Get the label text (calibration name)
    const char* calName = lv_label_get_text(label);
    ui_instance->handleMeasurementSelect(calName);
  }
}

static void motors_btn_event_cb(lv_event_t* e) {
  if (ui_instance) ui_instance->handleMotorsButton();
}

static void motor1_btn_event_cb(lv_event_t* e) {
  if (ui_instance) ui_instance->handleMotorSelect(1);
}

static void motor2_btn_event_cb(lv_event_t* e) {
  if (ui_instance) ui_instance->handleMotorSelect(2);
}

static void motor_forward_btn_event_cb(lv_event_t* e) {
  if (ui_instance) {
    ui_instance->handleMotorForward(ui_instance->_currentMotorNum);
  }
}

static void motor_reverse_btn_event_cb(lv_event_t* e) {
  if (ui_instance) {
    ui_instance->handleMotorReverse(ui_instance->_currentMotorNum);
  }
}

static void motor_stop_btn_event_cb(lv_event_t* e) {
  if (ui_instance) {
    ui_instance->handleMotorStop(ui_instance->_currentMotorNum);
  }
}

static void calibrate_btn_event_cb(lv_event_t* e) {
  if (ui_instance) ui_instance->handleCalibrateButton();
}

static void calibration_select_btn_event_cb(lv_event_t* e) {
  if (ui_instance) {
    lv_obj_t* btn = (lv_obj_t*)lv_event_get_target(e);
    lv_obj_t* label = lv_obj_get_child(btn, 0);
    const char* calName = lv_label_get_text(label);
    ui_instance->handleCalibrationSelect(calName);
  }
}

static void cal_blank_btn_event_cb(lv_event_t* e) {
  if (ui_instance) ui_instance->handleCalibrationBlank();
}

static void cal_measure_btn_event_cb(lv_event_t* e) {
  if (ui_instance) ui_instance->handleCalibrationMeasure();
}

UI_Manager::UI_Manager() : _display(800, 480, GigaDisplayShield) {
  _currentScreen = SCREEN_MEASURE;
  _measurementName = "Absorbance";
  _measurementUnits = "";
  _measurementValue = 0.0;
  _isBlanked = false;
  _sensorInitialized = false;
  _motorController = nullptr;
  _calibrations = nullptr;
  _currentMotorNum = 1;
  _calBlanked = false;
  _calBlankAbsorbance = 0.0;
  _currentCalibrationName = "";

  ui_instance = this;
}

void UI_Manager::begin(MotorController* motorController, Calibrations* calibrations) {
  _motorController = motorController;
  _calibrations = calibrations;

  Serial.println("UI_Manager: Starting initialization...");

  // Initialize display
  Serial.println("UI_Manager: Initializing display...");
  _display.begin();
  Serial.println("UI_Manager: Display initialized OK");

  // Initialize touch
  Serial.println("UI_Manager: Initializing touch...");
  if (!_touchDetector.begin()) {
    Serial.println("UI_Manager: WARNING - Touch init failed!");
  } else {
    Serial.println("UI_Manager: Touch initialized OK");
  }
  touchDetector_ptr = &_touchDetector;

  // Register touch input device with LVGL (v9 API)
  Serial.println("UI_Manager: Registering touch with LVGL...");
  lv_indev_t* indev = lv_indev_create();
  lv_indev_set_type(indev, LV_INDEV_TYPE_POINTER);
  lv_indev_set_read_cb(indev, touchpad_read);
  Serial.println("UI_Manager: Touch driver registered");

  // Create all screens
  Serial.println("UI_Manager: Creating screens...");
  createMeasureScreen();
  Serial.println("UI_Manager: Measure screen created");

  createMenuScreen();
  Serial.println("UI_Manager: Menu screen created");

  createMotorSelectScreen();
  Serial.println("UI_Manager: Motor select screen created");

  createMotorControlScreen();
  Serial.println("UI_Manager: Motor control screen created");

  createMessageScreen();
  Serial.println("UI_Manager: Message screen created");

  createCalibrateScreen();
  Serial.println("UI_Manager: Calibrate screen created");

  // Show measure screen by default
  Serial.println("UI_Manager: Loading measure screen...");
  showMeasureScreen();
  Serial.println("UI_Manager: Initialization complete!");
}

void UI_Manager::update() {
  // Update LVGL timer
  lv_timer_handler();

  // Update measurement display if on measure screen
  if (_currentScreen == SCREEN_MEASURE && _label_value != nullptr) {
    char buf[64];
    if (_measurementUnits.length() > 0) {
      snprintf(buf, sizeof(buf), "%.2f %s", _measurementValue, _measurementUnits.c_str());
    } else {
      snprintf(buf, sizeof(buf), "%.2f", _measurementValue);
    }
    lv_label_set_text(_label_value, buf);

    // Update status label
    if (!_sensorInitialized) {
      lv_label_set_text(_label_status, "SENSOR NOT CONNECTED");
    } else if (_isBlanked) {
      lv_label_set_text(_label_status, "BLANKED");
    } else {
      lv_label_set_text(_label_status, "NOT BLANKED");
    }
  }
}

void UI_Manager::createMeasureScreen() {
  _screen_measure = lv_obj_create(nullptr);

  // Title header in right 2/3 area
  _label_title = lv_label_create(_screen_measure);
  lv_label_set_text(_label_title, _measurementName.c_str());
  lv_obj_set_pos(_label_title, 300, 20);

  // Large value display in right 2/3 area
  _label_value = lv_label_create(_screen_measure);
  lv_label_set_text(_label_value, "0.00");
  lv_obj_set_pos(_label_value, 300, 180);

  // Make text 3x larger with proper pivot point
  lv_obj_set_style_transform_pivot_x(_label_value, 0, 0);
  lv_obj_set_style_transform_pivot_y(_label_value, 0, 0);
  lv_obj_set_style_transform_scale(_label_value, 768, 0); // 768 = 3x (256 * 3)

  // Status label in right area
  _label_status = lv_label_create(_screen_measure);
  lv_label_set_text(_label_status, "NOT BLANKED");
  lv_obj_set_pos(_label_status, 300, 350);

  // BLANK button in left column
  _btn_blank = lv_btn_create(_screen_measure);
  lv_obj_set_size(_btn_blank, 240, 50);
  lv_obj_set_pos(_btn_blank, 20, 60);
  lv_obj_add_event_cb(_btn_blank, blank_btn_event_cb, LV_EVENT_CLICKED, nullptr);

  lv_obj_t* label = lv_label_create(_btn_blank);
  lv_label_set_text(label, "BLANK");
  lv_obj_align(label, LV_ALIGN_LEFT_MID, 10, 0);

  // MENU button in left column below BLANK
  _btn_menu = lv_btn_create(_screen_measure);
  lv_obj_set_size(_btn_menu, 240, 50);
  lv_obj_set_pos(_btn_menu, 20, 120);
  lv_obj_add_event_cb(_btn_menu, menu_btn_event_cb, LV_EVENT_CLICKED, nullptr);

  label = lv_label_create(_btn_menu);
  lv_label_set_text(label, "MENU");
  lv_obj_align(label, LV_ALIGN_LEFT_MID, 10, 0);
}

void UI_Manager::createMenuScreen() {
  _screen_menu = lv_obj_create(nullptr);

  // Title at top (fixed)
  lv_obj_t* title = lv_label_create(_screen_menu);
  lv_label_set_text(title, "Menu");
  lv_obj_set_pos(title, 20, 20);

  // Create scrollable container for menu items
  lv_obj_t* scroll_container = lv_obj_create(_screen_menu);
  lv_obj_set_size(scroll_container, 280, 340); // Width x Height (leave room for title and BACK)
  lv_obj_set_pos(scroll_container, 10, 60); // Start below title
  lv_obj_set_flex_flow(scroll_container, LV_FLEX_FLOW_COLUMN); // Stack items vertically
  lv_obj_set_flex_align(scroll_container, LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_START);
  lv_obj_set_scroll_dir(scroll_container, LV_DIR_VER); // Vertical scrolling only
  lv_obj_set_scrollbar_mode(scroll_container, LV_SCROLLBAR_MODE_AUTO); // Show scrollbar when needed

  int btn_width = 240;
  int btn_height = 50;

  // Absorbance button
  _btn_absorbance = lv_btn_create(scroll_container);
  lv_obj_set_size(_btn_absorbance, btn_width, btn_height);
  lv_obj_add_event_cb(_btn_absorbance, absorbance_btn_event_cb, LV_EVENT_CLICKED, nullptr);

  lv_obj_t* label = lv_label_create(_btn_absorbance);
  lv_label_set_text(label, "Absorbance");
  lv_obj_align(label, LV_ALIGN_LEFT_MID, 10, 0);

  // Transmittance button
  _btn_transmittance = lv_btn_create(scroll_container);
  lv_obj_set_size(_btn_transmittance, btn_width, btn_height);
  lv_obj_add_event_cb(_btn_transmittance, transmittance_btn_event_cb, LV_EVENT_CLICKED, nullptr);

  label = lv_label_create(_btn_transmittance);
  lv_label_set_text(label, "Transmittance");
  lv_obj_align(label, LV_ALIGN_LEFT_MID, 10, 0);

  // Raw Sensor button
  _btn_raw = lv_btn_create(scroll_container);
  lv_obj_set_size(_btn_raw, btn_width, btn_height);
  lv_obj_add_event_cb(_btn_raw, raw_btn_event_cb, LV_EVENT_CLICKED, nullptr);

  label = lv_label_create(_btn_raw);
  lv_label_set_text(label, "Raw Sensor");
  lv_obj_align(label, LV_ALIGN_LEFT_MID, 10, 0);

  // Add calibration buttons dynamically
  if (_calibrations != nullptr) {
    std::vector<String> calNames = _calibrations->getNames();
    for (const String& calName : calNames) {
      lv_obj_t* btn = lv_btn_create(scroll_container);
      lv_obj_set_size(btn, btn_width, btn_height);
      lv_obj_add_event_cb(btn, calibration_btn_event_cb, LV_EVENT_CLICKED, nullptr);

      label = lv_label_create(btn);
      lv_label_set_text(label, calName.c_str());
      lv_obj_align(label, LV_ALIGN_LEFT_MID, 10, 0);
    }
  }

  // Motors button
  _btn_motors = lv_btn_create(scroll_container);
  lv_obj_set_size(_btn_motors, btn_width, btn_height);
  lv_obj_add_event_cb(_btn_motors, motors_btn_event_cb, LV_EVENT_CLICKED, nullptr);

  label = lv_label_create(_btn_motors);
  lv_label_set_text(label, "Motors");
  lv_obj_align(label, LV_ALIGN_LEFT_MID, 10, 0);

  // Calibrate button
  lv_obj_t* _btn_calibrate = lv_btn_create(scroll_container);
  lv_obj_set_size(_btn_calibrate, btn_width, btn_height);
  lv_obj_add_event_cb(_btn_calibrate, calibrate_btn_event_cb, LV_EVENT_CLICKED, nullptr);

  label = lv_label_create(_btn_calibrate);
  lv_label_set_text(label, "Calibrate");
  lv_obj_align(label, LV_ALIGN_LEFT_MID, 10, 0);

  // BACK button at bottom (fixed, outside scroll area)
  _btn_back = lv_btn_create(_screen_menu);
  lv_obj_set_size(_btn_back, btn_width, btn_height);
  lv_obj_align(_btn_back, LV_ALIGN_BOTTOM_LEFT, 20, -20);
  lv_obj_add_event_cb(_btn_back, back_btn_event_cb, LV_EVENT_CLICKED, nullptr);

  label = lv_label_create(_btn_back);
  lv_label_set_text(label, "BACK");
  lv_obj_align(label, LV_ALIGN_LEFT_MID, 10, 0);
}

void UI_Manager::createMessageScreen() {
  _screen_message = lv_obj_create(nullptr);

  _label_msg_title = lv_label_create(_screen_message);
  lv_obj_align(_label_msg_title, LV_ALIGN_TOP_MID, 0, 20);

  _label_msg_text = lv_label_create(_screen_message);
  lv_obj_align(_label_msg_text, LV_ALIGN_CENTER, 0, 0);
}

void UI_Manager::createCalibrateScreen() {
  _screen_calibrate = lv_obj_create(nullptr);

  // Title
  _label_cal_title = lv_label_create(_screen_calibrate);
  lv_label_set_text(_label_cal_title, "Calibrate");
  lv_obj_set_pos(_label_cal_title, 20, 20);

  // Instructions label (large, centered)
  _label_cal_instructions = lv_label_create(_screen_calibrate);
  lv_label_set_text(_label_cal_instructions, "Select test to calibrate:");
  lv_obj_set_pos(_label_cal_instructions, 40, 100);
  lv_obj_set_width(_label_cal_instructions, 720);
  lv_label_set_long_mode(_label_cal_instructions, LV_LABEL_LONG_WRAP);

  // Scrollable container for calibration selection
  _cal_scroll_container = lv_obj_create(_screen_calibrate);
  lv_obj_set_size(_cal_scroll_container, 760, 250);
  lv_obj_set_pos(_cal_scroll_container, 20, 140);
  lv_obj_set_flex_flow(_cal_scroll_container, LV_FLEX_FLOW_COLUMN);
  lv_obj_set_scroll_dir(_cal_scroll_container, LV_DIR_VER);
  lv_obj_set_scrollbar_mode(_cal_scroll_container, LV_SCROLLBAR_MODE_AUTO);

  // Add buttons for each calibration (compact)
  if (_calibrations != nullptr) {
    std::vector<String> calNames = _calibrations->getNames();
    for (const String& calName : calNames) {
      lv_obj_t* btn = lv_btn_create(_cal_scroll_container);
      lv_obj_set_size(btn, 720, 45);  // Reduced from 60 to 45
      lv_obj_add_event_cb(btn, calibration_select_btn_event_cb, LV_EVENT_CLICKED, nullptr);

      lv_obj_t* label = lv_label_create(btn);
      lv_label_set_text(label, calName.c_str());
      lv_obj_align(label, LV_ALIGN_LEFT_MID, 10, 0);
    }
  }

  // BLANK button (hidden initially)
  _btn_cal_blank = lv_btn_create(_screen_calibrate);
  lv_obj_set_size(_btn_cal_blank, 300, 80);
  lv_obj_align(_btn_cal_blank, LV_ALIGN_CENTER, -160, 100);
  lv_obj_add_event_cb(_btn_cal_blank, cal_blank_btn_event_cb, LV_EVENT_CLICKED, nullptr);
  lv_obj_add_flag(_btn_cal_blank, LV_OBJ_FLAG_HIDDEN);

  lv_obj_t* label = lv_label_create(_btn_cal_blank);
  lv_label_set_text(label, "BLANK");
  lv_obj_center(label);

  // MEASURE button (hidden initially)
  _btn_cal_measure = lv_btn_create(_screen_calibrate);
  lv_obj_set_size(_btn_cal_measure, 300, 80);
  lv_obj_align(_btn_cal_measure, LV_ALIGN_CENTER, 160, 100);
  lv_obj_add_event_cb(_btn_cal_measure, cal_measure_btn_event_cb, LV_EVENT_CLICKED, nullptr);
  lv_obj_add_flag(_btn_cal_measure, LV_OBJ_FLAG_HIDDEN);

  label = lv_label_create(_btn_cal_measure);
  lv_label_set_text(label, "MEASURE");
  lv_obj_center(label);

  // BACK button at bottom
  _btn_cal_back = lv_btn_create(_screen_calibrate);
  lv_obj_set_size(_btn_cal_back, 240, 50);
  lv_obj_align(_btn_cal_back, LV_ALIGN_BOTTOM_LEFT, 20, -20);
  lv_obj_add_event_cb(_btn_cal_back, back_btn_event_cb, LV_EVENT_CLICKED, nullptr);

  label = lv_label_create(_btn_cal_back);
  lv_label_set_text(label, "BACK");
  lv_obj_align(label, LV_ALIGN_LEFT_MID, 10, 0);
}

void UI_Manager::showMeasureScreen() {
  _currentScreen = SCREEN_MEASURE;
  lv_scr_load(_screen_measure);
}

void UI_Manager::showMenuScreen() {
  _currentScreen = SCREEN_MENU;
  lv_scr_load(_screen_menu);
}

void UI_Manager::showMotorSelectScreen() {
  _currentScreen = SCREEN_MOTOR_SELECT;
  lv_scr_load(_screen_motor_select);
}

void UI_Manager::showMotorControlScreen(int motorNum) {
  _currentMotorNum = motorNum;
  _currentScreen = SCREEN_MOTOR_CONTROL;

  // Update motor title
  char title[32];
  snprintf(title, sizeof(title), "Motor %d Control", motorNum);
  lv_label_set_text(_label_motor_title, title);

  lv_scr_load(_screen_motor_control);
}

void UI_Manager::showSolenoidScreen(int solenoidNum) {
  _currentScreen = SCREEN_SOLENOID;
  // TODO: Implement solenoid screen
}

void UI_Manager::showSettingsScreen() {
  _currentScreen = SCREEN_SETTINGS;
  // TODO: Implement settings screen
}

void UI_Manager::showMessage(const char* title, const char* message) {
  _messageTitle = title;
  _messageText = message;

  lv_label_set_text(_label_msg_title, title);
  lv_label_set_text(_label_msg_text, message);

  _currentScreen = SCREEN_MESSAGE;
  lv_scr_load(_screen_message);
}

void UI_Manager::showCalibrateScreen() {
  _currentScreen = SCREEN_CALIBRATE;

  // Reset calibration screen to selection mode
  lv_label_set_text(_label_cal_instructions, "Select test to calibrate:");
  _calBlanked = false;

  // Show selection list, hide buttons
  lv_obj_clear_flag(_cal_scroll_container, LV_OBJ_FLAG_HIDDEN);
  lv_obj_add_flag(_btn_cal_blank, LV_OBJ_FLAG_HIDDEN);
  lv_obj_add_flag(_btn_cal_measure, LV_OBJ_FLAG_HIDDEN);

  lv_scr_load(_screen_calibrate);
}

void UI_Manager::setMeasurementValue(float value, bool blanked) {
  _measurementValue = value;
  _isBlanked = blanked;
}

void UI_Manager::setMeasurementName(const char* name) {
  _measurementName = name;
  if (_label_title != nullptr) {
    lv_label_set_text(_label_title, name);
  }
}

void UI_Manager::setMeasurementUnits(const char* units) {
  _measurementUnits = units;
}

void UI_Manager::setSensorStatus(bool initialized) {
  _sensorInitialized = initialized;
}

void UI_Manager::showOverflow() {
  setMeasurementValue(99.99, _isBlanked);
}

// Touch input driver for LVGL (v9 API)
void UI_Manager::touchpad_read(lv_indev_t* indev, lv_indev_data_t* data) {
  if (touchDetector_ptr == nullptr) {
    data->state = LV_INDEV_STATE_RELEASED;
    return;
  }

  GDTpoint_t points[5];
  uint8_t contacts = touchDetector_ptr->getTouchPoints(points);

  if (contacts > 0) {
    data->state = LV_INDEV_STATE_PRESSED;
    data->point.x = points[0].x;
    data->point.y = points[0].y;
  } else {
    data->state = LV_INDEV_STATE_RELEASED;
  }
}

// Callback handlers
void UI_Manager::handleBlankButton() {
  Serial.println("BLANK button pressed via LVGL");
  blankRequested = true;
}

void UI_Manager::handleMenuButton() {
  Serial.println("MENU button pressed via LVGL");
  showMenuScreen();
}

void UI_Manager::handleBackButton() {
  Serial.println("BACK button pressed via LVGL");

  // Navigate to previous screen based on current screen
  switch(_currentScreen) {
    case SCREEN_MENU:
      showMeasureScreen();
      break;
    case SCREEN_MOTOR_SELECT:
      showMenuScreen();
      break;
    case SCREEN_MOTOR_CONTROL:
      showMotorSelectScreen();
      break;
    default:
      showMeasureScreen();
      break;
  }
}

void UI_Manager::handleMeasurementSelect(const char* measurement) {
  Serial.print("Measurement selected: ");
  Serial.println(measurement);
  currentMeasurement = String(measurement);
  setMeasurementName(measurement);

  // Set units based on measurement type
  if (_calibrations != nullptr && _calibrations->hasCalibration(measurement)) {
    String units = _calibrations->getUnits(measurement);
    Serial.print("Units for ");
    Serial.print(measurement);
    Serial.print(": ");
    Serial.println(units);
    setMeasurementUnits(units.c_str());
  } else {
    setMeasurementUnits("");
  }

  showMeasureScreen();
}

void UI_Manager::handleMotorsButton() {
  Serial.println("MOTORS button pressed via LVGL");
  showMotorSelectScreen();
}

void UI_Manager::handleMotorSelect(int motorNum) {
  Serial.print("Motor ");
  Serial.print(motorNum);
  Serial.println(" selected");
  showMotorControlScreen(motorNum);
}

void UI_Manager::handleMotorForward(int motorNum) {
  Serial.print("Motor ");
  Serial.print(motorNum);
  Serial.println(" FORWARD");
  if (_motorController != nullptr) {
    _motorController->runForward(motorNum, 0.5);
  }
}

void UI_Manager::handleMotorReverse(int motorNum) {
  Serial.print("Motor ");
  Serial.print(motorNum);
  Serial.println(" REVERSE");
  if (_motorController != nullptr) {
    _motorController->runReverse(motorNum, 0.5);
  }
}

void UI_Manager::handleMotorStop(int motorNum) {
  Serial.print("Motor ");
  Serial.print(motorNum);
  Serial.println(" STOP");
  if (_motorController != nullptr) {
    _motorController->stop(motorNum);
  }
}

void UI_Manager::createMotorSelectScreen() {
  _screen_motor_select = lv_obj_create(nullptr);

  // Title in left column
  lv_obj_t* title = lv_label_create(_screen_motor_select);
  lv_label_set_text(title, "Select Motor");
  lv_obj_set_pos(title, 20, 20);

  int x = 20;
  int y = 60;
  int btn_width = 240;
  int btn_height = 50;
  int spacing = 10;

  // Motor 1 button
  _btn_motor1 = lv_btn_create(_screen_motor_select);
  lv_obj_set_size(_btn_motor1, btn_width, btn_height);
  lv_obj_set_pos(_btn_motor1, x, y);
  lv_obj_add_event_cb(_btn_motor1, motor1_btn_event_cb, LV_EVENT_CLICKED, nullptr);

  lv_obj_t* label = lv_label_create(_btn_motor1);
  lv_label_set_text(label, "Motor 1");
  lv_obj_align(label, LV_ALIGN_LEFT_MID, 10, 0);
  y += btn_height + spacing;

  // Motor 2 button
  _btn_motor2 = lv_btn_create(_screen_motor_select);
  lv_obj_set_size(_btn_motor2, btn_width, btn_height);
  lv_obj_set_pos(_btn_motor2, x, y);
  lv_obj_add_event_cb(_btn_motor2, motor2_btn_event_cb, LV_EVENT_CLICKED, nullptr);

  label = lv_label_create(_btn_motor2);
  lv_label_set_text(label, "Motor 2");
  lv_obj_align(label, LV_ALIGN_LEFT_MID, 10, 0);

  // BACK button at bottom left
  _btn_motor_back = lv_btn_create(_screen_motor_select);
  lv_obj_set_size(_btn_motor_back, btn_width, btn_height);
  lv_obj_align(_btn_motor_back, LV_ALIGN_BOTTOM_LEFT, 20, -20);
  lv_obj_add_event_cb(_btn_motor_back, back_btn_event_cb, LV_EVENT_CLICKED, nullptr);

  label = lv_label_create(_btn_motor_back);
  lv_label_set_text(label, "BACK");
  lv_obj_align(label, LV_ALIGN_LEFT_MID, 10, 0);
}

void UI_Manager::createMotorControlScreen() {
  _screen_motor_control = lv_obj_create(nullptr);

  // Title
  _label_motor_title = lv_label_create(_screen_motor_control);
  lv_label_set_text(_label_motor_title, "Motor 1 Control");
  lv_obj_align(_label_motor_title, LV_ALIGN_TOP_MID, 0, 20);

  // FORWARD button
  _btn_motor_forward = lv_btn_create(_screen_motor_control);
  lv_obj_set_size(_btn_motor_forward, 300, 80);
  lv_obj_align(_btn_motor_forward, LV_ALIGN_CENTER, 0, -100);
  lv_obj_add_event_cb(_btn_motor_forward, motor_forward_btn_event_cb, LV_EVENT_CLICKED, nullptr);

  lv_obj_t* label = lv_label_create(_btn_motor_forward);
  lv_label_set_text(label, "FORWARD");
  lv_obj_center(label);

  // STOP button
  _btn_motor_stop = lv_btn_create(_screen_motor_control);
  lv_obj_set_size(_btn_motor_stop, 300, 80);
  lv_obj_align(_btn_motor_stop, LV_ALIGN_CENTER, 0, 0);
  lv_obj_add_event_cb(_btn_motor_stop, motor_stop_btn_event_cb, LV_EVENT_CLICKED, nullptr);

  label = lv_label_create(_btn_motor_stop);
  lv_label_set_text(label, "STOP");
  lv_obj_center(label);

  // REVERSE button
  _btn_motor_reverse = lv_btn_create(_screen_motor_control);
  lv_obj_set_size(_btn_motor_reverse, 300, 80);
  lv_obj_align(_btn_motor_reverse, LV_ALIGN_CENTER, 0, 100);
  lv_obj_add_event_cb(_btn_motor_reverse, motor_reverse_btn_event_cb, LV_EVENT_CLICKED, nullptr);

  label = lv_label_create(_btn_motor_reverse);
  lv_label_set_text(label, "REVERSE");
  lv_obj_center(label);

  // BACK button
  _btn_motor_control_back = lv_btn_create(_screen_motor_control);
  lv_obj_set_size(_btn_motor_control_back, 200, 60);
  lv_obj_align(_btn_motor_control_back, LV_ALIGN_BOTTOM_LEFT, 50, -20);
  lv_obj_add_event_cb(_btn_motor_control_back, back_btn_event_cb, LV_EVENT_CLICKED, nullptr);

  label = lv_label_create(_btn_motor_control_back);
  lv_label_set_text(label, "BACK");
  lv_obj_center(label);
}

// Calibration handlers
void UI_Manager::handleCalibrateButton() {
  Serial.println("CALIBRATE button pressed");
  showCalibrateScreen();
}

void UI_Manager::handleCalibrationSelect(const char* calibrationName) {
  Serial.print("Calibration selected: ");
  Serial.println(calibrationName);

  _currentCalibrationName = String(calibrationName);
  _calBlanked = false;

  // Update instructions for blank step
  char instruction[128];
  snprintf(instruction, sizeof(instruction), "Step 1: Insert reagent blank\nPress BLANK when ready");
  lv_label_set_text(_label_cal_instructions, instruction);

  // Hide selection buttons, show BLANK button
  lv_obj_add_flag(_cal_scroll_container, LV_OBJ_FLAG_HIDDEN);
  lv_obj_clear_flag(_btn_cal_blank, LV_OBJ_FLAG_HIDDEN);
  lv_obj_add_flag(_btn_cal_measure, LV_OBJ_FLAG_HIDDEN);
}

void UI_Manager::handleCalibrationBlank() {
  Serial.println("Calibration blank: Taking readings...");

  // Show progress
  lv_label_set_text(_label_cal_instructions, "Blanking...\nPlease wait...");

  // Perform blank directly (same as performBlank() in main sketch)
  float sum = 0.0;
  for (int i = 0; i < NUM_BLANK_SAMPLES; i++) {
    sum += lightSensor.getValue();
    lv_timer_handler(); // Keep UI responsive
    delay(BLANK_DT);
  }

  blankValue = sum / NUM_BLANK_SAMPLES;
  isBlanked = true;
  _calBlanked = true;

  Serial.print("Blank value set to: ");
  Serial.println(blankValue, 4);

  // Update instructions for measurement step
  if (_calibrations == nullptr) return;

  float standard = _calibrations->getStandard(_currentCalibrationName);
  char instruction[128];
  snprintf(instruction, sizeof(instruction), "Step 2: Insert %.3f %s standard\nPress MEASURE when ready",
           standard, _calibrations->getUnits(_currentCalibrationName).c_str());
  lv_label_set_text(_label_cal_instructions, instruction);

  // Hide BLANK button, show MEASURE button
  lv_obj_add_flag(_btn_cal_blank, LV_OBJ_FLAG_HIDDEN);
  lv_obj_clear_flag(_btn_cal_measure, LV_OBJ_FLAG_HIDDEN);

  Serial.println("Ready for standard measurement");
}

void UI_Manager::handleCalibrationMeasure() {
  if (!_calBlanked) {
    lv_label_set_text(_label_cal_instructions, "ERROR: Please blank first!");
    Serial.println("Error: Blank first!");
    return;
  }

  if (_calibrations == nullptr) {
    lv_label_set_text(_label_cal_instructions, "ERROR: No calibrations available");
    Serial.println("Error: No calibrations");
    return;
  }

  // Get standard concentration from calibration
  float standard = _calibrations->getStandard(_currentCalibrationName);
  if (standard == 0.0) {
    lv_label_set_text(_label_cal_instructions, "ERROR: No standard defined");
    Serial.println("Error: No standard");
    return;
  }

  // Measure current absorbance
  float raw = lightSensor.getValue();
  float transmittance = raw / blankValue;
  float absorbance = -log10(transmittance);
  if (absorbance < 0.0) absorbance = 0.0;

  Serial.print("Calibration measurement: raw=");
  Serial.print(raw);
  Serial.print(" trans=");
  Serial.print(transmittance);
  Serial.print(" abs=");
  Serial.println(absorbance);

  // Calculate new coefficient: standard / absorbance
  if (absorbance > 0.001) {
    float newCoefficient = standard / absorbance;

    Serial.print("Updating coefficient to: ");
    Serial.println(newCoefficient);

    // Update the calibration
    _calibrations->updateCoefficient(_currentCalibrationName, newCoefficient);

    // Show success on calibration screen
    char successMsg[200];
    snprintf(successMsg, sizeof(successMsg),
             "SUCCESS!\n\nCalibration: %s\nStandard: %.3f %s\nAbsorbance: %.4f\nNew coefficient: %.2f\n\nPress BACK to return to menu",
             _currentCalibrationName.c_str(), standard, _calibrations->getUnits(_currentCalibrationName).c_str(), absorbance, newCoefficient);
    lv_label_set_text(_label_cal_instructions, successMsg);

    // Hide both buttons
    lv_obj_add_flag(_btn_cal_blank, LV_OBJ_FLAG_HIDDEN);
    lv_obj_add_flag(_btn_cal_measure, LV_OBJ_FLAG_HIDDEN);
  } else {
    lv_label_set_text(_label_cal_instructions, "ERROR: Absorbance too low!\nCheck sample and blank\nPress BACK to retry");
    Serial.println("Error: Absorbance too low");
  }
}
