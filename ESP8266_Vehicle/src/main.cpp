#include <Arduino.h>
#include <Hash.h> // Workaround for Hash.h compile time bug
#include <math.h>

#include <ArduinoJson.h>
#include <ESP8266WiFi.h>
#include <WiFiManager.h>

#include "Accel.h"
#include "Config.h"
#include "Driver.h"
#include "V2iConnection.h"

String AP_SSID = "ESP" + String(ESP.getChipId());
String AP_PASS = "FYDP202033";

veh::Accel accel;
veh::Driver driver;
v2i::V2iConnection connection;

const unsigned long DATA_INTERVAL = 3000;
unsigned long prevMillis = 0;

bool shouldSaveConfig = false;

void connectWiFi(String ssid, String password);
void handleCommand(uint8_t* payload, size_t length);
void saveConfig();

void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.println();
  Serial.println();
  delay(500);

  accel.begin();
  driver.begin();

  veh::ConfigManager configManager;
  veh::Config config;
  configManager.begin();
  configManager.loadConfig(config);
  if (config.isForwardFlipped) {
    driver.flipForwardReverse();
  }
  if (config.isSteeringFlipped) {
    driver.flipSteering();
  }
  if (config.desiredSpeedsLen > 0) {
    driver.calibrateSpeed(config.desiredSpeedsLen, config.desiredSpeeds,
                          config.desiredSpeedsPwm);
  }
  driver.calibrateSteering(config.minAngle, config.maxAngle, config.midAngle);

  WiFiManagerParameter ipParam("server",
    "Server IP",
    config.hostname,
    sizeof(config.hostname));
  WiFiManagerParameter portParam("port",
    "Server Port",
    config.port,
    sizeof(config.port));

  // WiFi.disconnect();
  WiFiManager wifiManager;
  wifiManager.addParameter(&ipParam);
  wifiManager.addParameter(&portParam);
  wifiManager.setSaveConfigCallback(saveConfig);
  if (!wifiManager.autoConnect(AP_SSID.c_str(), AP_PASS.c_str())) {
    Serial.println("WiFi Manager AP timed out!");
    delay(3000);
    ESP.restart();
  }

  strcpy(config.hostname, ipParam.getValue());
  strcpy(config.port, portParam.getValue());
  if (shouldSaveConfig) {
    Serial.println("Saving config...");
    configManager.saveConfig(config);
  }

  connection.begin(config.hostname, atoi(config.port));
  connection.registerCommandHandler(handleCommand);
  connection.enableHeartbeat(15000, 3000, 2);
  connection.setReconnectInterval(1000);
}

void loop() {
  connection.loop();

  unsigned long currMillis = millis();
  if (abs(currMillis - prevMillis) < DATA_INTERVAL)
      return;

  veh::accel_vec_t a = accel.getData();

  const int capacity = JSON_OBJECT_SIZE(4);
  StaticJsonDocument<capacity> doc;
  doc["id"] = ESP.getChipId();
  doc["type"] = "status";
  doc["v"] = driver.getSpeed();
  doc["a"] = sqrtf(a.x*a.x + a.y*a.y);

  char msg[capacity];
  serializeJson(doc, msg);
  connection.sendTXT(msg);

  prevMillis = currMillis;
}

void saveConfig() {
  shouldSaveConfig = true;
}

void connectWiFi(String ssid, String password) {
  WiFi.begin(ssid, password);
  Serial.print("Connecting...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("Connected - IP Address: ");
  Serial.println(WiFi.localIP());
}

void handleCommand(uint8_t* payload, size_t length) {
  const size_t CAPACITY = JSON_OBJECT_SIZE(8) + 2*JSON_ARRAY_SIZE(MAX_CALIB_DATA_COUNT);
  DynamicJsonDocument doc(CAPACITY);
  DeserializationError error = deserializeJson(doc, payload, length);
  if (error) {
    Serial.println(F("deserializeJson() failed!"));
    Serial.println(error.c_str());
    return;
  }

  const char* type = doc["type"];
  if (!type) {
    Serial.println("Command with no type.");
    return;
  }

  if (strcmp("drive", type) == 0) {
    float speed = doc["speed"];
    float steering = doc["steering"];
    veh::driver_command_t command = { speed, steering };
    driver.drive(command);
  } else if (strcmp("calib_drive", type) == 0) {
    float speed = doc["speed"];
    float steering = doc["steering"];
    veh::driver_command_t command = { speed, steering };
    driver.driveRaw(command);
  } else if (strcmp("calibrate", type) == 0) {
    driver.driveRaw({ 0, 0 });
    accel.calibrate([]() {
      const uint16_t capacity = JSON_OBJECT_SIZE(3);
      StaticJsonDocument<capacity> doc;
      doc["id"] = ESP.getChipId();
      doc["type"] = "calibrate_finished";

      char msg[capacity];
      serializeJson(doc, msg);
      connection.sendTXT(msg);
    });
  } else if (strcmp("calib_flip_forward", type) == 0) {
    veh::ConfigManager configManager;
    veh::Config config;
    configManager.begin();
    configManager.loadConfig(config);
    config.isForwardFlipped = !config.isForwardFlipped;
    configManager.saveConfig(config);

    driver.flipForwardReverse();
  } else if (strcmp("calib_flip_steering", type) == 0) {
    veh::ConfigManager configManager;
    veh::Config config;
    configManager.begin();
    configManager.loadConfig(config);
    config.isSteeringFlipped = !config.isSteeringFlipped;
    configManager.saveConfig(config);

    driver.flipSteering();
  } else if (strcmp("calib_speed", type) == 0) {
    veh::ConfigManager configManager;
    veh::Config config;
    configManager.begin();
    configManager.loadConfig(config);
    configManager.parseSpeedData(config, doc);
    configManager.saveConfig(config);

    driver.calibrateSpeed(config.desiredSpeedsLen, config.desiredSpeeds,
                          config.desiredSpeedsPwm);
  } else if (strcmp("calib_steering", type) == 0) {
    int minAngle = doc["minAngle"];
    int maxAngle = doc["maxAngle"];
    int midAngle = doc["midAngle"];
    driver.calibrateSteering(minAngle, maxAngle, midAngle);

    veh::ConfigManager configManager;
    veh::Config config;
    configManager.begin();
    configManager.loadConfig(config);
    config.minAngle = minAngle;
    config.maxAngle = maxAngle;
    config.midAngle = midAngle;
    configManager.saveConfig(config);
  }
}
