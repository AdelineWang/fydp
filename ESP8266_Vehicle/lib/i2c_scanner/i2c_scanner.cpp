#include "i2c_scanner.h"

#include <Stream.h>

#include <Arduino.h>
#include <Wire.h>

void i2c_scanner::scanPorts(Stream& serial) {
  serial.println();
  serial.println("I2C scanner. Scanning ...");
  byte count = 0;

  Wire.begin();
  for (byte i = 8; i < 120; i++) {
    Wire.beginTransmission (i);
    if (Wire.endTransmission () == 0) {
      serial.print("Found address: ");
      serial.print(i, DEC);
      serial.print(" (0x");
      serial.print(i, HEX);
      serial.println(")");
      count++;
      delay (1);
    }
  }

  serial.println("Done.");
  serial.print("Found ");
  serial.print(count, DEC);
  serial.println(" device(s).");
}
