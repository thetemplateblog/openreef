/**
 * UI_Manager.cpp
 * LVGL Implementation for Giga Display
 */

#include "UI_Manager.h"
#include "Configuration.h"
#include "Calibrations.h"
#include "LightSensor.h"

// External flags and data from main sketch
extern bool blankRequested;
extern String currentMeasurement;
extern float blankValue;
extern bool isBlanked;
extern LightSensor lightSensor;
extern Configuration config;
extern TSL2591_Gain currentGain;

// External functions
extern float takeSensorMeasurement();

// Global pointer to UI manager instance for callbacks
static UI_Manager* ui_instance = nullptr;

// Touch detector global for LVGL driver
static Arduino_GigaDisplayTouch* touchDetector_ptr = nullptr;

// LVGL event callbacks (C-style functions that call class methods)
static void blank_btn_event_cb(lv_event_t* e) {
  if (ui_instance) ui_instance->handleBlankButton();
}

static void measure_btn_event_cb(lv_event_t* e) {
  if (ui_instance) ui_instance->handleMeasureButton();
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
  _rawValue = 0.0;
  _isBlanked = false;
  _sensorInitialized = false;
  _calibrations = nullptr;
  _calBlanked = false;
  _calBlankAbsorbance = 0.0;
  _currentCalibrationName = "";
  _lastCalMeasureTime = 0;

  ui_instance = this;
}

void UI_Manager::begin(Calibrations* calibrations) {
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
    char buf[128];
    if (_measurementUnits.length() > 0) {
      snprintf(buf, sizeof(buf), "%.2f %s\nRaw: %.0f", _measurementValue, _measurementUnits.c_str(), _rawValue);
    } else {
      snprintf(buf, sizeof(buf), "%.2f\nRaw: %.0f", _measurementValue, _rawValue);
    }
    lv_label_set_text(_label_value, buf);

    // Update status label - use GLOBAL isBlanked
    if (!_sensorInitialized) {
      lv_label_set_text(_label_status, "SENSOR NOT CONNECTED");
    } else if (isBlanked) {
      lv_label_set_text(_label_status, "BLANKED");
    } else {
      lv_label_set_text(_label_status, "NOT BLANKED");
    }

    // Show/hide MEASURE button based on GLOBAL blank status
    if (isBlanked) {
      lv_obj_clear_flag(_btn_measure, LV_OBJ_FLAG_HIDDEN);
    } else {
      lv_obj_add_flag(_btn_measure, LV_OBJ_FLAG_HIDDEN);
    }
  }
}

/**
 * Helper function to create a button with label - reduces code duplication
 * @param parent Parent object for the button
 * @param text Button label text
 * @param width Button width
 * @param height Button height
 * @param callback Event callback function
 * @param x X position (-1 to skip positioning, for flex containers)
 * @param y Y position (-1 to skip positioning, for flex containers)
 * @return Pointer to created button object
 */
lv_obj_t* UI_Manager::createButton(lv_obj_t* parent, const char* text, int width, int height,
                                   lv_event_cb_t callback, int x, int y) {
  // Create button
  lv_obj_t* btn = lv_btn_create(parent);
  lv_obj_set_size(btn, width, height);

  // Set position if coordinates provided
  if (x >= 0 && y >= 0) {
    lv_obj_set_pos(btn, x, y);
  }

  // Add event callback
  lv_obj_add_event_cb(btn, callback, LV_EVENT_CLICKED, nullptr);

  // Create and configure label
  lv_obj_t* label = lv_label_create(btn);
  lv_label_set_text(label, text);
  lv_obj_align(label, LV_ALIGN_LEFT_MID, 10, 0);

  return btn;
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
  _btn_blank = createButton(_screen_measure, "BLANK", 240, 50, blank_btn_event_cb, 20, 60);

  // MEASURE button in left column below BLANK (hidden initially)
  _btn_measure = createButton(_screen_measure, "MEASURE", 240, 50, measure_btn_event_cb, 20, 120);
  lv_obj_add_flag(_btn_measure, LV_OBJ_FLAG_HIDDEN); // Hide until blanked

  // MENU button in left column below MEASURE
  _btn_menu = createButton(_screen_measure, "MENU", 240, 50, menu_btn_event_cb, 20, 180);
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
  _btn_absorbance = createButton(scroll_container, "Absorbance", btn_width, btn_height, absorbance_btn_event_cb);

  // Transmittance button
  _btn_transmittance = createButton(scroll_container, "Transmittance", btn_width, btn_height, transmittance_btn_event_cb);

  // Raw Sensor button
  _btn_raw = createButton(scroll_container, "Raw Sensor", btn_width, btn_height, raw_btn_event_cb);

  // Add calibration buttons dynamically
  if (_calibrations != nullptr) {
    std::vector<String> calNames = _calibrations->getNames();
    for (const String& calName : calNames) {
      createButton(scroll_container, calName.c_str(), btn_width, btn_height, calibration_btn_event_cb);
    }
  }

  // Calibrate button
  createButton(scroll_container, "Calibrate", btn_width, btn_height, calibrate_btn_event_cb);

  // BACK button at bottom (fixed, outside scroll area)
  _btn_back = createButton(_screen_menu, "BACK", btn_width, btn_height, back_btn_event_cb);
  lv_obj_align(_btn_back, LV_ALIGN_BOTTOM_LEFT, 20, -20);
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
      createButton(_cal_scroll_container, calName.c_str(), 720, 45, calibration_select_btn_event_cb);
    }
  }

  // BLANK button (hidden initially) - needs centered label
  _btn_cal_blank = createButton(_screen_calibrate, "BLANK", 300, 80, cal_blank_btn_event_cb);
  lv_obj_align(_btn_cal_blank, LV_ALIGN_CENTER, -160, 100);
  lv_obj_add_flag(_btn_cal_blank, LV_OBJ_FLAG_HIDDEN);
  // Re-center the label
  lv_obj_t* label = lv_obj_get_child(_btn_cal_blank, 0);
  lv_obj_center(label);

  // MEASURE button (hidden initially) - needs centered label
  _btn_cal_measure = createButton(_screen_calibrate, "MEASURE", 300, 80, cal_measure_btn_event_cb);
  lv_obj_align(_btn_cal_measure, LV_ALIGN_CENTER, 160, 100);
  lv_obj_add_flag(_btn_cal_measure, LV_OBJ_FLAG_HIDDEN);
  // Re-center the label
  label = lv_obj_get_child(_btn_cal_measure, 0);
  lv_obj_center(label);

  // BACK button at bottom
  _btn_cal_back = createButton(_screen_calibrate, "BACK", 240, 50, back_btn_event_cb);
  lv_obj_align(_btn_cal_back, LV_ALIGN_BOTTOM_LEFT, 20, -20);
}

void UI_Manager::showMeasureScreen() {
  _currentScreen = SCREEN_MEASURE;
  lv_scr_load(_screen_measure);
}

void UI_Manager::showMenuScreen() {
  _currentScreen = SCREEN_MENU;
  lv_scr_load(_screen_menu);
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

void UI_Manager::setMeasurementValue(float value, float raw, bool blanked) {
  _measurementValue = value;
  _rawValue = raw;
  Serial.print("UI updated: value=");
  Serial.print(value);
  Serial.print(" raw=");
  Serial.println(raw);
  // Note: blanked parameter is ignored - we use global isBlanked instead
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
  setMeasurementValue(99.99, 65535, _isBlanked);
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

void UI_Manager::handleMeasureButton() {
  Serial.println("MEASURE button pressed via LVGL");

  // Check if sensor is initialized
  if (!_sensorInitialized) {
    Serial.println("ERROR: Cannot measure - sensor not initialized!");
    return;
  }

  // Validate blank value
  if (blankValue < MIN_BLANK_VALUE) {
    Serial.println("ERROR: Invalid blank value!");
    showMessage("Error", "Invalid blank - please re-blank");
    delay(1500);
    showMeasureScreen();
    return;
  }

  // Take measurement using standard procedure
  float raw = takeSensorMeasurement();

  if (raw < 0.0) {
    // Error occurred (logged by takeSensorMeasurement)
    showMessage("Measure Failed", "Sensor error - check serial");
    delay(1500);
    showMeasureScreen();
    return;
  }

  // Calculate value based on current measurement type
  float value = 0.0;

  if (currentMeasurement == "Raw Sensor") {
    value = raw;
  }
  else if (currentMeasurement == "Transmittance") {
    value = raw / blankValue;
  }
  else if (currentMeasurement == "Absorbance") {
    float transmittance = raw / blankValue;
    value = -log10(transmittance);
    if (value < 0.0) value = 0.0;

    Serial.print("Measurement: raw=");
    Serial.print(raw);
    Serial.print(" blank=");
    Serial.print(blankValue);
    Serial.print(" trans=");
    Serial.print(transmittance);
    Serial.print(" abs=");
    Serial.println(value);
  }
  else {
    // Check if it's a calibration
    float transmittance = raw / blankValue;
    float absorbance = -log10(transmittance);
    if (absorbance < 0.0) absorbance = 0.0;

    if (_calibrations != nullptr) {
      value = _calibrations->apply(currentMeasurement, absorbance);

      Serial.print("Calibration measurement: ");
      Serial.print(currentMeasurement);
      Serial.print(" abs=");
      Serial.print(absorbance);
      Serial.print(" value=");
      Serial.println(value);
    }
  }

  // Update display with new measurement
  setMeasurementValue(value, raw, isBlanked);
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
    default:
      showMeasureScreen();
      break;
  }
}

void UI_Manager::handleMeasurementSelect(const char* measurement) {
  Serial.print("Measurement selected: ");
  Serial.println(measurement);

  // Reset blank status when changing measurements
  if (currentMeasurement != String(measurement)) {
    isBlanked = false;
    _measurementValue = 0.0;
  }

  currentMeasurement = String(measurement);
  setMeasurementName(measurement);

  // Set units and apply per-calibration settings
  if (_calibrations != nullptr && _calibrations->hasCalibration(measurement)) {
    String units = _calibrations->getUnits(measurement);
    Serial.print("Units for ");
    Serial.print(measurement);
    Serial.print(": ");
    Serial.println(units);
    setMeasurementUnits(units.c_str());

    // Apply per-calibration gain setting
    int calibrationGain = _calibrations->getGain(measurement);
    TSL2591_Gain gainSetting;
    if (calibrationGain == 1) gainSetting = TSL2591_GAIN_LOW;
    else if (calibrationGain == 25) gainSetting = TSL2591_GAIN_MED;
    else if (calibrationGain == 428) gainSetting = TSL2591_GAIN_HIGH;
    else if (calibrationGain == 9876) gainSetting = TSL2591_GAIN_MAX;
    else gainSetting = TSL2591_GAIN_LOW;

    Serial.print("Applying gain for ");
    Serial.print(measurement);
    Serial.print(": ");
    Serial.print(calibrationGain);
    Serial.println("x");
    lightSensor.setGain(gainSetting);

    // Apply per-calibration integration time setting
    String integrationTimeStr = _calibrations->getIntegrationTime(measurement);
    TSL2591_IntegrationTime integrationTime = config.parseIntegrationTime(integrationTimeStr);
    Serial.print("Applying integration time for ");
    Serial.print(measurement);
    Serial.print(": ");
    Serial.println(integrationTimeStr);
    lightSensor.setIntegrationTime(integrationTime);
  } else {
    setMeasurementUnits("");
  }

  showMeasureScreen();
}

// Calibration handlers
void UI_Manager::handleCalibrateButton() {
  Serial.println("CALIBRATE button pressed");
  showCalibrateScreen();
}

void UI_Manager::handleCalibrationSelect(const char* calibrationName) {
  Serial.print("Calibration selected: ");
  Serial.println(calibrationName);

  // Reset blank status when changing calibrations
  if (_currentCalibrationName != String(calibrationName)) {
    _calBlanked = false;
  }

  _currentCalibrationName = String(calibrationName);
  _lastCalMeasureTime = 0;  // Reset debounce timer for new calibration

  // Update instructions for blank step
  char instruction[128];
  snprintf(instruction, sizeof(instruction), "Step 1: Insert plain water\n(no reagent)\nPress BLANK when ready");
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

  // Set current measurement to this calibration so performBlank uses correct gain
  currentMeasurement = _currentCalibrationName;

  // Set gain for this calibration
  if (_calibrations != nullptr) {
    int calibrationGain = _calibrations->getGain(_currentCalibrationName);
    if (calibrationGain == 1) currentGain = TSL2591_GAIN_LOW;
    else if (calibrationGain == 25) currentGain = TSL2591_GAIN_MED;
    else if (calibrationGain == 428) currentGain = TSL2591_GAIN_HIGH;
    else if (calibrationGain == 9876) currentGain = TSL2591_GAIN_MAX;
    else currentGain = TSL2591_GAIN_LOW;

    Serial.print("Setting gain for ");
    Serial.print(_currentCalibrationName);
    Serial.print(": ");
    Serial.print(calibrationGain);
    Serial.println("x");

    // Apply per-calibration integration time setting
    String integrationTimeStr = _calibrations->getIntegrationTime(_currentCalibrationName);
    TSL2591_IntegrationTime integrationTime = config.parseIntegrationTime(integrationTimeStr);
    Serial.print("Setting integration time for ");
    Serial.print(_currentCalibrationName);
    Serial.print(": ");
    Serial.println(integrationTimeStr);
    lightSensor.setIntegrationTime(integrationTime);
  }

  // Use standard measurement procedure
  blankValue = takeSensorMeasurement();

  if (blankValue < 0.0) {
    lv_label_set_text(_label_cal_instructions, "ERROR: Blank failed!\nCheck serial output\nPress BACK to retry");
    isBlanked = false;
    _calBlanked = false;
    blankValue = 1.0;
    return;
  }

  Serial.print("Calibration blank median from ");
  Serial.print(NUM_BLANK_SAMPLES);
  Serial.print(" samples: ");
  Serial.println(blankValue, 2);

  // Validate blank value
  if (blankValue < MIN_BLANK_VALUE) {
    Serial.print("ERROR: Calibration blank value too low: ");
    Serial.println(blankValue, 4);
    lv_label_set_text(_label_cal_instructions, "ERROR: Blank value too low!\nCheck sensor");
    isBlanked = false;
    _calBlanked = false;
    blankValue = 1.0;
    return;
  }

  isBlanked = true;
  _calBlanked = true;

  Serial.print("Blank value set to: ");
  Serial.println(blankValue, 4);

  // Update instructions for standard measurement
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
  // Debounce: Ignore button presses within 15 seconds of last calibration measurement
  unsigned long now = millis();
  if (now - _lastCalMeasureTime < 15000) {
    Serial.println("Calibration measure button debounced (too soon after last measurement)");
    return;
  }
  _lastCalMeasureTime = now;

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

  // Validate blank value
  if (blankValue < MIN_BLANK_VALUE) {
    lv_label_set_text(_label_cal_instructions, "ERROR: Invalid blank value!\nPlease re-blank");
    Serial.println("Error: Invalid blank value");
    return;
  }

  // Get standard concentration from calibration
  float standard = _calibrations->getStandard(_currentCalibrationName);
  if (standard == 0.0) {
    lv_label_set_text(_label_cal_instructions, "ERROR: No standard defined");
    Serial.println("Error: No standard");
    return;
  }

  // Show measuring status
  lv_label_set_text(_label_cal_instructions, "Measuring standard...\nPlease wait...");

  // Take measurement using standard procedure
  float raw = takeSensorMeasurement();

  if (raw < 0.0) {
    lv_label_set_text(_label_cal_instructions, "ERROR: Measurement failed!\nCheck serial output\nPress BACK to retry");
    return;
  }

  float transmittance = raw / blankValue;
  float absorbance = -log10(transmittance);
  if (absorbance < 0.0) absorbance = 0.0;

  Serial.print("Standard measurement: raw=");
  Serial.print(raw);
  Serial.print(" blank=");
  Serial.print(blankValue);
  Serial.print(" trans=");
  Serial.print(transmittance);
  Serial.print(" abs=");
  Serial.println(absorbance);

  // Calculate calibration coefficients
  // Point 1: (0, 0) - water blank
  // Point 2: (absorbance, standard) - standard measurement
  if (absorbance > MIN_ABSORBANCE_THRESHOLD) {
    float slope = (standard - 0.0) / (absorbance - 0.0);
    float intercept = 0.0 - (slope * 0.0);

    Serial.print("Calculating calibration:\n");
    Serial.print("  Point 1: abs=0, conc=0 (water blank)\n");
    Serial.print("  Point 2: abs=");
    Serial.print(absorbance, 4);
    Serial.print(", conc=");
    Serial.println(standard);
    Serial.print("  Slope: ");
    Serial.println(slope, 4);
    Serial.print("  Intercept: ");
    Serial.println(intercept, 4);

    // Update the calibration
    _calibrations->updateCoefficients(_currentCalibrationName, intercept, slope);

    // Show brief success message
    char successMsg[250];
    snprintf(successMsg, sizeof(successMsg),
             "SUCCESS!\n\nCalibration: %s\nSlope: %.4f\n\nReturning to menu...",
             _currentCalibrationName.c_str(), slope);
    lv_label_set_text(_label_cal_instructions, successMsg);

    // Wait briefly to show success message
    delay(2000);

    // Return to measure screen
    showMeasureScreen();
  } else {
    lv_label_set_text(_label_cal_instructions, "ERROR: Absorbance too low!\nCheck sample and blank\nPress BACK to retry");
    Serial.println("Error: Absorbance too low");
  }
}
