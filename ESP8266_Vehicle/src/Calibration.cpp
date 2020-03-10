#include "Calibration.h"

#include "Arduino.h"

using namespace veh;

namespace {

bool mappingsSort(mapping_t a, mapping_t b) {
  return a.desiredVal < b.desiredVal;
}

}

PwmMapper::PwmMapper() : isCalibrated(false) {
  for (mapping_t& mapping : mappings) {
    mapping.desiredVal = 0;
    mapping.pwmVal = 0;
  }
}

void PwmMapper::calibrate(int length, float* desiredVals, int* pwmVals) {
  for (int i = 0; i < length; ++i) {
    mapping_t mapping = { desiredVals[i], pwmVals[i] };
    mappings.push_back(mapping);
  }
  std::sort(mappings.begin(), mappings.end(), mappingsSort);
  isCalibrated = true;
}

int PwmMapper::map(float desiredVal) {
  if (!isCalibrated) return 1023;

  // Edge cases
  if (desiredVal < mappings.front().desiredVal) {
    return 0;
  } else if (desiredVal == mappings.front().desiredVal) {
    return mappings.front().pwmVal;
  } else if (desiredVal >= mappings.back().desiredVal) {
    return mappings.back().pwmVal;
  }

  // Linear search for points surrounding desired value
  int low = 0;
  int high = 0;
  for (size_t i = 0; i < mappings.size(); ++i) {
    if (desiredVal >= mappings[i].desiredVal
        && desiredVal < mappings[i + 1].desiredVal) {
      low = i;
      high = i + 1;
      break;
    }
  }

  // Linearize based on surrounding two points
  mapping_t lowPoint = mappings[low];
  mapping_t highPoint = mappings[high];
  return lowPoint.pwmVal 
    + (desiredVal - lowPoint.desiredVal) / (highPoint.desiredVal - lowPoint.desiredVal)
    * (highPoint.pwmVal - lowPoint.pwmVal);
}
