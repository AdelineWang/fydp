#include "Accel.h"

#include <Adafruit_LIS3DH.h>
#include <Adafruit_Sensor.h>

#define NORMAL    0
#define CALIBRATE 1

#define CALIBRATE_SAMPLE_COUNT 5

using namespace veh;

Accel::Accel() {
  lis = Adafruit_LIS3DH();

  axOffset = 0;
  ayOffset = 0;
  azOffset = 0;
}

void Accel::begin() {
  if (!lis.begin()) {
    Serial.println("LIS3DH not found!");
    ESP.restart();
  } else {
    lis.setRange(LIS3DH_RANGE_2_G);
    lis.setDataRate(LIS3DH_DATARATE_25_HZ);
  }
}

void Accel::calibrate(CalibrateFinished callback) {
  float ax[CALIBRATE_SAMPLE_COUNT] = {0};
  float ay[CALIBRATE_SAMPLE_COUNT] = {0};
  float az[CALIBRATE_SAMPLE_COUNT] = {0};

  for (int i = 0; i < CALIBRATE_SAMPLE_COUNT; ++i) {
    sensors_event_t event;
    lis.getEvent(&event);

    ax[i] = event.acceleration.x;
    ay[i] = event.acceleration.y;
    az[i] = event.acceleration.z;

    delay(100);
  }

  float axSum = 0;
  float aySum = 0;
  float azSum = 0;
  for (int i = 0; i < CALIBRATE_SAMPLE_COUNT; ++i) {
    axSum += ax[i];
    aySum += ay[i];
    azSum += az[i];
  }

  axOffset = axSum / CALIBRATE_SAMPLE_COUNT;
  ayOffset = aySum / CALIBRATE_SAMPLE_COUNT;
  azOffset = azSum / CALIBRATE_SAMPLE_COUNT;

  callback();
}

accel_vec_t Accel::getData() {
  sensors_event_t event;
  lis.getEvent(&event);

  accel_vec_t data;
  data.x = event.acceleration.x - axOffset;
  data.y = event.acceleration.y - ayOffset;
  data.z = event.acceleration.z - azOffset;

  return data;
}
