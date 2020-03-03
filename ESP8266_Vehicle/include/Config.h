#ifndef CONFIG_H
#define CONFIG_H

#define MAX_CALIB_DATA_COUNT 64

namespace veh {

struct Config {
  char hostname[64];
  char port[16];
  bool flipForward;
  int desiredSpeedsLen;
  float desiredSpeeds[MAX_CALIB_DATA_COUNT];
  int desiredSpeedsPwm[MAX_CALIB_DATA_COUNT];
  int desiredSteeringLen;
  float desiredSteering[MAX_CALIB_DATA_COUNT];
  int desiredSteeringPwm[MAX_CALIB_DATA_COUNT];
};

class ConfigManager {
public:
  static const char* filename;
  static void begin();
  static void resetConfig(Config& config);
  static void loadConfig(Config& config);
  static bool saveConfig(Config& config);
};

}

#endif
