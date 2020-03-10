#include "Config.h"

#include <Arduino.h>
#include <FS.h>

#include <ArduinoJson.h>

using namespace veh;

const char* ConfigManager::filename = "/config.json";

void ConfigManager::begin() {
  if (!SPIFFS.begin()) {
    Serial.println("Failed to mount FS.");
  }
}

void ConfigManager::loadConfig(Config& config) {
  File configFile = SPIFFS.open(ConfigManager::filename, "r");
  const size_t CAPACITY = JSON_OBJECT_SIZE(10) + 2*JSON_ARRAY_SIZE(MAX_CALIB_DATA_COUNT);
  StaticJsonDocument<CAPACITY> doc;
  DeserializationError error = deserializeJson(doc, configFile);
  if (error) {
    Serial.println("Failed to read config file, using default config.");
  }

  strlcpy(config.hostname,
    doc["hostname"] | "0.0.0.0",
    sizeof(config.hostname));
  strlcpy(config.port,
    doc["port"] | "8080",
    sizeof(config.port));
  config.isForwardFlipped = doc["isForwardFlipped"] | false;
  config.isSteeringFlipped = doc["isSteeringFlipped"] | false;
  config.minAngle = doc["minAngle"] | 0;
  config.maxAngle = doc["maxAngle"] | 60;
  config.midAngle = doc["midAngle"] | 30;
  parseSpeedData(config, doc);

  configFile.close();
}

bool ConfigManager::saveConfig(Config& config) {
  File configFile = SPIFFS.open(ConfigManager::filename, "w");
  if (!configFile) {
    Serial.println("Failed to create config file.");
    return false;
  }

  const size_t CAPACITY = JSON_OBJECT_SIZE(10) + 2*JSON_ARRAY_SIZE(MAX_CALIB_DATA_COUNT);
  StaticJsonDocument<CAPACITY> doc;
  doc["hostname"] = config.hostname;
  doc["port"] = config.port;
  doc["isForwardFlipped"] = config.isForwardFlipped;
  doc["isSteeringFlipped"] = config.isSteeringFlipped;
  doc["minAngle"] = config.minAngle;
  doc["maxAngle"] = config.maxAngle;
  doc["midAngle"] = config.midAngle;

  doc["desiredSpeedsLen"] = config.desiredSpeedsLen;
  JsonArray desiredSpeeds = doc.createNestedArray("desiredSpeeds");
  JsonArray desiredSpeedsPwm = doc.createNestedArray("desiredSpeedsPwm");
  for (int i = 0; i < config.desiredSpeedsLen; ++i) {
    desiredSpeeds.add(config.desiredSpeeds[i]);
    desiredSpeedsPwm.add(config.desiredSpeedsPwm[i]);
  }

  if (serializeJson(doc, configFile) == 0) {
    Serial.println("Failed to write to config file.");
    configFile.close();
    return false;
  }

  configFile.close();
  return true;
}

void ConfigManager::zeroSpeedData(Config& config) {
  for (int i = 0; i < MAX_CALIB_DATA_COUNT; ++i) {
    config.desiredSpeeds[i] = 0;
    config.desiredSpeedsPwm[i] = 0;
  }
}

void ConfigManager::parseSpeedData(Config& config, JsonDocument& doc) {
  zeroSpeedData(config);
  config.desiredSpeedsLen = doc["desiredSpeedsLen"] | 0;
  if (config.desiredSpeedsLen >= 0) {
    int i = 0;
    JsonArray desiredSpeeds = doc["desiredSpeeds"];
    for (float speed : desiredSpeeds) {
      config.desiredSpeeds[i] = speed;
      ++i;
    }

    i = 0;
    JsonArray desiredSpeedsPwm = doc["desiredSpeedsPwm"];
    for (int pwm : desiredSpeedsPwm) {
      config.desiredSpeedsPwm[i] = pwm;
      ++i;
    }
  }
}
