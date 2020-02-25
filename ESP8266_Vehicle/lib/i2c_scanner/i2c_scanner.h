#ifndef I2C_SCANNER_H
#define I2C_SCANNER_H

#include <Stream.h>

namespace i2c_scanner {

void scanPorts(Stream& serial);

}

#endif
