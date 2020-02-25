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
  StaticJsonDocument<512> doc;
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
  config.flipSteering = doc["flipSteering"] | false;
  config.deadzone = doc["deadzone"] | 0;
  config.maxSpeed = doc["maxSpeed"] | 10.0;
  
  configFile.close();
}

bool ConfigManager::saveConfig(Config& config) {
  File configFile = SPIFFS.open(ConfigManager::filename, "w");
  if (!configFile) {
    Serial.println("Failed to create config file.");
    return false;
  }

  StaticJsonDocument<512> doc;
  doc["hostname"] = config.hostname;
  doc["port"] = config.port;
  doc["flipForward"] = config.flipForward;
  doc["flipSteering"] = config.flipSteering;
  doc["deadzone"] = config.deadzone;
  doc["maxSpeed"] = config.maxSpeed;

  if (serializeJson(doc, configFile) == 0) {
    Serial.println("Failed to write to config file.");
    configFile.close();
    return false;
  }

  configFile.close();
  return true;
}
