const express = require('express');
const path = require('path');
const { createServer } = require('http');
const WebSocket = require('ws');

const app = new express();
app.use(express.static(path.join(__dirname, 'public')));

const server = createServer(app);

// WebSockets
const wss = new WebSocket.Server({ server });
let sockets = {};

wss.on('connection', function(ws, req) {
  ws.isAlive = true;
  let id = null;

  ws.on('message', function(msg) {
    let json;
    try {
      json = JSON.parse(msg);
    } catch (error) {
      console.log(msg);
      console.log(error);
      return;
    }
    if (!json.hasOwnProperty('id') || !json.hasOwnProperty('type')) {
      console.log(json);
      console.log("Illegal message!");
      return;
    }

    id = json.id;
    if (!sockets.hasOwnProperty(id)) {
      sockets[id] = { socket: ws, isCalibrated: false };
      if (id !== -2) {
        console.log(`Vehicle ${id} connected.`);
      }

      let calibrateCommand = {
        id: id,
        type: "calibrate"
      };
      ws.send(JSON.stringify(calibrateCommand));
    }

    switch (json.type) {
      case 'calibrate_finished':
        console.log("Calibration complete.");
        sockets[id].isCalibrated = true;
        break;
      case 'status':
      case 'hello':
        break;
      case 'drive':
        if(!sockets.hasOwnProperty(json.vehId)) {
          break;
        }
        sockets[json.vehId].socket.send(JSON.stringify(
          {id: id, type:"drive", speed: json.speed, steering: json.steering}))
        break;
      case 'calib_drive':
      case 'calib_flip_forward':
      case 'calib_flip_steering':
      case 'calib_sat':
        if (!sockets.hasOwnProperty(id)) {
          ws.send(JSON.stringify({ id: id, type: 'invalid_id'}));
          break;
        }
        sockets[id].socket.send(msg);
        break;
      default:
        console.log("Ignoring...");
        break;
    }
  });

  ws.on('close', function() {
    if (sockets.hasOwnProperty(id)) {
      delete sockets[id];
      if (id !== -2) {
        console.log(`Vehicle ${id} disconnected.`);
      }
    }
  });

  ws.on('pong', heartbeat);
});

// Heartbeat
function noop() {}

function heartbeat() {
  this.isAlive = true;
}

const interval = setInterval(function ping() {
  wss.clients.forEach(function each(ws) {
    if (ws.isAlive === false)
      return ws.terminate();

    ws.isAlive = false;
    ws.ping(noop);
  });
}, 15000);

server.listen(8080, () => {
  console.log(`Server listening on port: ${server.address().port}`);
});
