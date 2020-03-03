#include "Driver.h"

#include <Arduino.h>
#include <Servo.h>

using namespace veh;

void Driver::begin() {
  pinMode(pins.ena, OUTPUT);
  pinMode(pins.in1, OUTPUT);
  pinMode(pins.in2, OUTPUT);

  analogWrite(pins.ena, 0);
  digitalWrite(pins.in1, LOW);
  digitalWrite(pins.in2, LOW);

  steering.attach(pins.servo);
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

void Driver::flipSteering() {
  isSteeringFlipped = !isSteeringFlipped;
}

void Driver::calibrateSpeed(int length, float* desiredSpeeds, int* pwmVals) {
  speedMapper.calibrate(length, desiredSpeeds, pwmVals);
}

void Driver::calibrateSteering(int minAngle, int maxAngle, int midAngle) {
  minSteeringAngle = minAngle;
  maxSteeringAngle = maxAngle;
  midSteeringAngle = midAngle;
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

  int angle = isSteeringFlipped ? midSteeringAngle - command.steering
    : midSteeringAngle + command.steering;
  angle = max(angle, minSteeringAngle);
  angle = min(angle, maxSteeringAngle);
  steering.write(angle);
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

  steering.write(command.steering);
}
