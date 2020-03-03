#ifndef CALIBRATION_H
#define CALIBRATION_H

#include "Arduino.h"

namespace veh {

typedef struct {
  float desiredVal;
  int pwmVal;
} mapping_t;

class PwmMapper {
public:
  PwmMapper();
  void calibrate(int length, float* desiredVals, int* pwmVals);
  int map(float desiredVal);

private:
  bool isCalibrated;
  std::vector<mapping_t> mappings;
};

}

#endif
