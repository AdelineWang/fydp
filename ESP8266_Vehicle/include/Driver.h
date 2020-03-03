#ifndef DRIVER_H
#define DRIVER_H

#include <Arduino.h>

#include "Calibration.h"

#define ENA 2
#define IN1 16
#define IN2 0
#define ENB 12
#define IN3 15
#define IN4 13

namespace veh {

typedef struct {
  uint8_t ena;
  uint8_t in1;
  uint8_t in2;
} driver_pins_t;

typedef struct {
  float speed;
  float steering;
} driver_command_t;

class Driver {
public:
  void begin();
  void begin(driver_pins_t config);
  void flipForwardReverse();
  void calibrateSpeed(int length, float* desiredSpeeds, int* pwmVals);

  void drive(driver_command_t command);
  void driveRaw(driver_command_t command);

  float getSpeed();

private:
  typedef struct {
    uint8_t in1;
    uint8_t in2;
  } direction_t;

  driver_pins_t pins = {
    ENA,
    IN1,
    IN2
  };

  const direction_t DIR_A = {
    LOW,  // in1
    HIGH  // in2
  };
  const direction_t DIR_B = {
    HIGH, // in1
    LOW   // in2
  };

  direction_t forward = DIR_A;
  direction_t reverse = DIR_B;

  driver_command_t heldCommand = { 0, 0 };

  PwmMapper speedMapper;
};

}

#endif
