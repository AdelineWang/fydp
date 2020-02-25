# FYDP

### ESP8266_Vehicle

This is the directory for the vehicle firmware. You need VSCode and PlatformIO to build and upload the firmware. With PlatformIO, you should be able to simply open the project (folder) and then hit build/upload.

*NOTE:* If you get an error during build about HTTP_HEAD being redefined, then navigate to the .pio/libdeps/huzzah/WifiManager_ID\* library source files. Replace all instances of HTTP_HEAD to HTTP_HEADER and the problem should be resolved.

### V2i_coordinator_server

This is the directory for the central coordinator. There is a node.js-based web-socket server that communicates between vehicles. It also includes a simulator in Python used in the 4A demo. It implements the car-following algorithm we will be using. This needs to be rewritten to be completely in Python since we will be using OpenCV for vehicle detection.

