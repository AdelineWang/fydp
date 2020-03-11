var vehicleId;
var ws = null;

function connect() {
  const addr = 'ws://localhost:8069'
  ws = new WebSocket(addr);

  ws.onopen = function() {
    console.log('Connected to ' + addr);
    ws.send(JSON.stringify({ id: -1, type: 'hello' }));
  };
  ws.onerror = function(error) {
    console.log('WebSocket error: ' + error);
  };
  ws.onclose = function() {
    console.log('Closing...');
    ws = null;
  }
  ws.onmessage = function(msg) {
    console.log('Received: ' + msg.data);
    let obj = JSON.parse(msg.data);
    
    var msgType = obj['type'];
    if (msgType == 'traffic_light_positions') {
      var payload = obj['data'];
      console.log(payload);
      buildTrafficLightList(payload);
    }
    else if (msgType == 'speed_limit_positions') {
      var payload = obj['data'];
      console.log(payload);
      buildSpeedLimitList(payload);
    }
  };
}

function buildTrafficLightList(positions) {
  buildListEntry("trafficlightpositionselect", positions);
}

function buildSpeedLimitList(positions) {
  buildListEntry("speedlimitpositionselect", positions);
}

function buildListEntry(id, array) {
  var myParent = document.getElementById(id);
  var oldList = document.getElementById(id+"list");
  if (oldList != null) {
    oldList.parentNode.removeChild(oldList);
  }
  //Create and append select list
  var selectList = document.createElement("select");
  selectList.id = id+"list";
  myParent.appendChild(selectList);

  //Create and append the options
  for (var i = 0; i < array.length; i++) {
      var option = document.createElement("option");
      option.value = array[i];
      option.text = array[i];
      selectList.appendChild(option);
  }
}

function sendGetTrafficLights() {
  let command = {
      id: 'test_scenario_manager',
      type: 'get_traffic_signals'
  };
  console.log(ws);
  let string = JSON.stringify(command);
  ws.send(string);
}

function sendGetSpeedLimits() {
  let command = {
      id: 'test_scenario_manager',
      type: 'get_speed_limits'
  };
  ws.send(JSON.stringify(command));
}

function sendSetSpeedCommand() {
  const speed = parseInt($('#desiredspeed').val());
  
  if (speed >= 0) {
    let command = {
      id: 'test_scenario_manager',
      veh_id: vehicleId,
      type: 'set_vehicle_speed',
      speed: speed
    };
    ws.send(JSON.stringify(command));
  }
}

function sendLaneChangeCommand() {
  let command = {
    id: 'test_scenario_manager',
    veh_id: vehicleId,
    type: 'change_lane'
  };
  ws.send(JSON.stringify(command));
}

function sendAddTrafficSignalCommand() {
  let position = parseInt($('#trafficlightposition').val());
  let signalChangePeriod = parseInt($('#signalchangeperiod').val());
  console.log($('#trafficlightposition').val());
  console.log(position);
  let command = {
    id: 'test_scenario_manager',
    type: 'add_traffic_signal',
    position: position,
    signalChangePeriod: signalChangePeriod
  };
  ws.send(JSON.stringify(command));
  sendGetTrafficLights();
}

function sendAddSpeedLimitCommand() {
  let position = parseInt($('#speedlimitposition').val());
  let speed = parseInt($('#newspeed').val());
  
  let command = {
    id: 'test_scenario_manager',
    type: 'add_speed_limit',
    position: position,
    speed: speed
  };
  ws.send(JSON.stringify(command));
  sendGetSpeedLimits();
}

function deleteTrafficLight() {
  let position = parseInt($('#trafficlightpositionselectlist').val());
  let command = {
    id: 'test_scenario_manager',
    type: 'delete_traffic_signal',
    position: position
  };
  ws.send(JSON.stringify(command));
  sendGetTrafficLights();
}

function deleteSpeedLimit() {
  let position = parseInt($('#speedlimitpositionselectlist').val());
  let command = {
    id: 'test_scenario_manager',
    type: 'delete_speed_limit',
    position: position
  };
  ws.send(JSON.stringify(command));
  sendGetSpeedLimits();
}

function setSelectedVehicle() {
  if (document.getElementById('red').checked) {
    vehicleId = document.getElementById('red').value;
  }
  else if (document.getElementById('green').checked) {
    vehicleId = document.getElementById('green').value;
  }
  else if (document.getElementById('blue').checked) {
    vehicleId = document.getElementById('blue').value;
  }
}

$(document).ready(function() {
  connect();
  
  $('#updateButton').click(function() { sendSetSpeedCommand(); });
  $('#laneChangeButton').click(function() { sendLaneChangeCommand(); });
  $('#addtrafficlight').click(function() { sendAddTrafficSignalCommand(); });
  $('#addspeedlimit').click(function() { sendAddSpeedLimitCommand(); });
  $('#removetrafficlight').click(function() { deleteTrafficLight(); });
  $('#removespeedlimit').click(function() { deleteSpeedLimit(); });
  
  // if there's a better way for this let me know (I don't know JS)
  $('#red').click(function() { setSelectedVehicle(); });
  $('#green').click(function() { setSelectedVehicle(); });
  $('#blue').click(function() { setSelectedVehicle(); });

  // Initial val for radio
  setSelectedVehicle();
});