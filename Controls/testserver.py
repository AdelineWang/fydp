# Basically just print whatever gets sent thru the websocket (debugging)
import asyncio
import websockets
import json

trafficLights = {}
speedLimits = {}

async def processNewMessage(websocket, path):
    async for message in websocket:
      message_json = json.loads(message)
      #print(message_json)
      message_type = message_json['type']
      if message_type:
        # Switch on message type
        if message_type == 'set_vehicle_speed':
          veh_id = message_json['veh_id']
          speed = message_json['speed']
          
        elif message_type == 'change_lane':
          veh_id = message_json['veh_id']
        elif message_type == 'add_traffic_signal':
          position = message_json['position']
          signal_change_period = message_json['signalChangePeriod']
          if position:
            trafficLights[position] = signal_change_period
          print(f"Traffic light positions: {trafficLights}")
        elif message_type == 'add_speed_limit':
          position = message_json['position']
          speed = message_json['speed']
          if position:
            speedLimits[position] = speed
          print(f"Speed limit positions: {speedLimits}")
        elif message_type == 'get_traffic_signals':
          response = json.dumps({'type': 'traffic_light_positions', 'data': list(trafficLights.keys())})
          print(response)
          await websocket.send(response)
        elif message_type == 'delete_traffic_signal':
          position = message_json['position']
          if position:
            del trafficLights[position]
        elif message_type == 'get_speed_limits':
          response = json.dumps({'type': 'speed_limit_positions', 'data': list(speedLimits.keys())})
          print(response)
          await websocket.send(response)
        elif message_type == 'delete_speed_limit':
          position = message_json['position']
          if position:
            del speedLimits[position]
        elif message_type == 'hello':
          response = json.dumps({'type': 'traffic_light_positions', 'data': list(trafficLights.keys())})
          print(response)
          await websocket.send(response)
          response = json.dumps({'type': 'speed_limit_positions', 'data': list(speedLimits.keys())})
          print(response)
          await websocket.send(response)
        else:
          print(f'Unrecognized message type: {message_type}')
      
print("Starting server...")
start_server = websockets.serve(processNewMessage, "localhost", 8069)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()