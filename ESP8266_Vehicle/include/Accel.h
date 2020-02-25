#ifndef ACCEL_H
#define ACCEL_H

#include <Adafruit_LIS3DH.h>

namespace veh {

typedef struct {
  float x;
  float y;
  float z;
} accel_vec_t;

class Accel {
public:
  typedef std::function<void()> CalibrateFinished;

  Accel();

  void begin();
  void calibrate(CalibrateFinished callback);

  accel_vec_t getData();

private:
  Adafruit_LIS3DH lis;

  float axOffset;
  float ayOffset;
  float azOffset;
};

}

#endif
