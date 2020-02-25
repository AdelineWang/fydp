#ifndef V2I_CONNECTION_H
#define V2I_CONNECTION_H

#include <Arduino.h>
#include <WebSocketsClient.h>

namespace v2i {

class V2iConnection : public WebSocketsClient {
public:
  typedef std::function<void(uint8_t* payload, size_t length)> CommandHandler;

  void begin(String addr, uint32_t port);
  void registerCommandHandler(CommandHandler callback);

private:
  CommandHandler handler;
  
  void webSocketEventHandler(WStype_t type, uint8_t* payload, size_t length);
};

}

#endif
