#include "Driver.h"

#include <Arduino.h>

using namespace veh;

void Driver::begin() {
  pinMode(pins.ena, OUTPUT);
  pinMode(pins.in1, OUTPUT);
  pinMode(pins.in2, OUTPUT);
  pinMode(pins.enb, OUTPUT);
  pinMode(pins.in3, OUTPUT);
  pinMode(pins.in4, OUTPUT);

  analogWrite(pins.ena, 0);
  analogWrite(pins.enb, 0);
  digitalWrite(pins.in1, LOW);
  digitalWrite(pins.in2, LOW);
  digitalWrite(pins.in3, LOW);
  digitalWrite(pins.in4, LOW);
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

void Driver::flipLeftRight() {
  Driver::direction_t temp = left;
  left = right;
  right = temp;
}

void Driver::updateSaturation(int deadzone, float maxSpeed) {
  Driver::deadzone = deadzone;
  Driver::maxSpeed = maxSpeed;
}

float Driver::getSpeed() {
  return heldCommand.speed;
}

void Driver::drive(driver_command_t command) {
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

  int pulseWidth;
  if (command.speed < 0.8) {
    pulseWidth = 0;
  } else if (command.speed >= maxSpeed) {
    pulseWidth = 1023;
  } else {
    pulseWidth = (1023 - deadzone)*(command.speed / maxSpeed) + deadzone;
  }
  analogWrite(pins.ena, pulseWidth);

  if (command.steering > 0) {
    digitalWrite(pins.in3, right.in1);
    digitalWrite(pins.in4, right.in2);
  } else if (command.steering < 0) {
    digitalWrite(pins.in3, left.in1);
    digitalWrite(pins.in4, left.in2);
  } else {
    digitalWrite(pins.in3, LOW);
    digitalWrite(pins.in4, LOW);
  }
  // TODO: Scaling
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

  if (command.steering > 0) {
    digitalWrite(pins.in3, right.in1);
    digitalWrite(pins.in4, right.in2);
  } else if (command.steering < 0) {
    digitalWrite(pins.in3, left.in1);
    digitalWrite(pins.in4, left.in2);
  } else {
    digitalWrite(pins.in3, LOW);
    digitalWrite(pins.in4, LOW);
  }

  // pulseWidth = command.steering;
  // analogWrite(pins.enb, 0);
}
