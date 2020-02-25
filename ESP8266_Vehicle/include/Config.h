#ifndef CONFIG_H
#define CONFIG_H

namespace veh {

struct Config {
  char hostname[64];
  char port[16];
  bool flipForward;
  bool flipSteering;
  int deadzone;
  float maxSpeed;
};

class ConfigManager {
public:
  static const char* filename;
  static void begin();
  static void loadConfig(Config& config);
  static bool saveConfig(Config& config);
};

}

#endif
