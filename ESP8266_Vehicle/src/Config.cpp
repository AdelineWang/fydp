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
  const size_t CAPACITY = JSON_OBJECT_SIZE(9) + 4*JSON_ARRAY_SIZE(MAX_CALIB_DATA_COUNT);
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
  config.flipForward = doc["flipForward"] | false;
  parseSpeedData(config, doc);
  parseSteeringData(config, doc);

  configFile.close();
}

bool ConfigManager::saveConfig(Config& config) {
  File configFile = SPIFFS.open(ConfigManager::filename, "w");
  if (!configFile) {
    Serial.println("Failed to create config file.");
    return false;
  }

  const size_t CAPACITY = JSON_OBJECT_SIZE(9) + 4*JSON_ARRAY_SIZE(MAX_CALIB_DATA_COUNT);
  StaticJsonDocument<CAPACITY> doc;
  doc["hostname"] = config.hostname;
  doc["port"] = config.port;
  doc["flipForward"] = config.flipForward;

  doc["desiredSpeedsLen"] = config.desiredSpeedsLen;
  JsonArray desiredSpeeds = doc.createNestedArray("desiredSpeeds");
  JsonArray desiredSpeedsPwm = doc.createNestedArray("desiredSpeedsPwm");
  for (int i = 0; i < config.desiredSpeedsLen; ++i) {
    desiredSpeeds.add(config.desiredSpeeds[i]);
    desiredSpeedsPwm.add(config.desiredSpeedsPwm[i]);
  }

  doc["desiredSteeringLen"] = config.desiredSteeringLen;
  JsonArray desiredSteering = doc.createNestedArray("desiredSteering");
  JsonArray desiredSteeringPwm = doc.createNestedArray("desiredSteeringPwm");
  for (int i = 0; i < config.desiredSteeringLen; ++i) {
    desiredSteering.add(config.desiredSteering[i]);
    desiredSteeringPwm.add(config.desiredSteeringPwm[i]);
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

void ConfigManager::zeroSteeringData(Config& config) {
  for (int i = 0; i < MAX_CALIB_DATA_COUNT; ++i) {
    config.desiredSteering[i] = 0;
    config.desiredSteeringPwm[i] = 0;
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

void ConfigManager::parseSteeringData(Config& config, JsonDocument& doc) {
  zeroSteeringData(config);
  config.desiredSteeringLen = doc["desiredSteeringLen"] | 0;
  if (config.desiredSpeedsLen >= 0) {
    int i = 0;
    JsonArray desiredSteering = doc["desiredSteering"];
    for (float steering : desiredSteering) {
      config.desiredSteering[i] = steering;
      ++i;
    }

    i = 0;
    JsonArray desiredSteeringPwm = doc["desiredSteeringPwm"];
    for (int pwm : desiredSteeringPwm) {
      config.desiredSteeringPwm[i] = pwm;
      ++i;
    }
  }
}
