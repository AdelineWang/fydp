#include "V2iConnection.h"

#include <Arduino.h>
#include <WebSocketsClient.h>

using namespace v2i;

void V2iConnection::begin(String addr, uint32_t port) {
  WebSocketsClient::begin(addr, port);

  auto webSocketEventHandlerWrapper = std::bind(
    &V2iConnection::webSocketEventHandler, this,
    std::placeholders::_1,
    std::placeholders::_2,
    std::placeholders::_3);
  onEvent(webSocketEventHandlerWrapper);
}

void V2iConnection::registerCommandHandler(CommandHandler callback) {
  handler = callback;
}

void V2iConnection::webSocketEventHandler(WStype_t type, uint8_t* payload, size_t length) {
  switch (type) {
    case WStype_CONNECTED:
      Serial.println("[WSc] Connected!");
      break;
    case WStype_DISCONNECTED:
      Serial.println("[WSc] Disconnected!");
      break;
    case WStype_TEXT:
      Serial.printf("[WSc] Text: %s\n", payload);
      if (handler) {
        handler(payload, length);
      } else {
        Serial.println("[WSc] Missing command handler!");
      }
      break;
    case WStype_BIN:
      Serial.printf("[WSc] Binary (%u):\n", length);
      hexdump(payload, length);
      break;
    case WStype_PING:
      // Pong is sent automatically.
      // Serial.println("[WSc] Got ping!");
      break;
    case WStype_PONG:
      // Serial.println("[WSc] Got pong!");
      break;
    default:
      Serial.println("[WSc] Unhandled web socket symbol!");
      break;
  }
}
