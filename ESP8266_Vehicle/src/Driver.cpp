#include "Driver.h"

#include <Arduino.h>

using namespace veh;

void Driver::begin() {
  pinMode(pins.ena, OUTPUT);
  pinMode(pins.in1, OUTPUT);
  pinMode(pins.in2, OUTPUT);

  analogWrite(pins.ena, 0);
  digitalWrite(pins.in1, LOW);
  digitalWrite(pins.in2, LOW);
}

void Driver::begin(driver_pins_t config) {
  pins = config;
  begin();
}

void Driver::flipForwardReverse() {
  Driver::direction_t temp = forward;
  forward = reverse;
  reverse = temp;
}

void Driver::calibrateSpeed(int length, float* desiredSpeeds, int* pwmVals) {
  speedMapper.calibrate(length, desiredSpeeds, pwmVals);
}

float Driver::getSpeed() {
  return heldCommand.speed;
}

void Driver::drive(driver_command_t command) {
  heldCommand = command;

  if (command.speed > 0) {
    digitalWrite(pins.in1, forward.in1);
    digitalWrite(pins.in2, forward.in2);
  } else if (command.speed < 0) {
    digitalWrite(pins.in1, reverse.in1);
    digitalWrite(pins.in2, reverse.in2);
  } else {
    digitalWrite(pins.in1, LOW);
    digitalWrite(pins.in2, LOW);
  }

  int pulseWidth = speedMapper.map(std::abs(command.speed));
  analogWrite(pins.ena, pulseWidth);

  // TODO: Steering
}

void Driver::driveRaw(driver_command_t command) {
  if (command.speed > 0) {
    digitalWrite(pins.in1, forward.in1);
    digitalWrite(pins.in2, forward.in2);
  } else if (command.speed < 0) {
    digitalWrite(pins.in1, reverse.in1);
    digitalWrite(pins.in2, reverse.in2);
  } else {
    digitalWrite(pins.in1, LOW);
    digitalWrite(pins.in2, LOW);
  }

  int pulseWidth = command.speed;
  analogWrite(pins.ena, pulseWidth);

  // TODO: Steering
}
