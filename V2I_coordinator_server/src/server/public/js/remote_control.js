let ws = null;

function connect() {
  const addr = $('#serverUrl').val();
  ws = new WebSocket(addr);

  ws.onopen = function () {
    console.log('Connected to ' + addr);
    ws.send(JSON.stringify({ id: -1, type: 'hello' }));
  };
  ws.onerror = function (error) {
    console.log('WebSocket error: ' + error);
  };
  ws.onclose = function () {
    console.log('Closing...');
    ws = null;
  }
  ws.onmessage = function (msg) {
    console.log('Received: ' + msg.data);
  };
}

function sendDriverCommand() {
  const vehicleId = $('#vehicleId').val();
  const speed = parseInt($('#rawSpeed').val());
  const steering = parseInt($('#steering').val());

  let command = { id: vehicleId, type: 'calib_drive', speed: speed, steering: steering };
  ws.send(JSON.stringify(command));
}

function sendForwardDirectionCalibration() {
  const vehicleId = $('#vehicleId').val();
  let command = { id: vehicleId, type: 'calib_drive', speed: 0, steering: 0 };
  ws.send(JSON.stringify(command));

  command = { id: vehicleId, type: 'calib_flip_forward' };
  ws.send(JSON.stringify(command)); 
}

function sendSteeringDirectionCalibration() {
  const vehicleId = $('#vehicleId').val();
  let command = { id: vehicleId, type: 'calib_drive', speed: 0, steering: 0 };
  ws.send(JSON.stringify(command));

  command = { id: vehicleId, type: 'calib_flip_steering' };
  ws.send(JSON.stringify(command)); 
}

function sendCalibrationCommand() {
  const vehicleId = $('#vehicleId').val();
  const deadzone = parseInt($('#deadzone').val());
  const maxSpeed = parseFloat($('#maxSpeed').val());

  command = { id: vehicleId, type: 'calib_sat', deadzone: deadzone, maxSpeed: maxSpeed}
  ws.send(JSON.stringify(command));
}

$(document).ready(function () {
  $('#connectButton').click(function (e) { connect(); });
  $('#sendButton').click(function (e) { sendDriverCommand(); });
  $('#flipForwardReverseButton').click(function (e) { sendForwardDirectionCalibration(); });
  $('#flipLeftRightButton').click(function (e) { sendSteeringDirectionCalibration(); });
  $('#sendCalibButton').click(function (e) { sendCalibrationCommand(); });

  $("#rawSpeed").val(0);
  $("#rawSpeed").keyup(function() {
    $("#rawSpeedSlider").slider("option", "value", parseInt($(this).val()) );
  });
  $("#rawSpeedSlider" ).slider({
    value: 0,
    min: 0,
    max: 1023,
    step: 1,        
  
    slide: function (event, ui) {
      let value = $("#rawSpeedSlider").slider("option", "value");
      $('#rawSpeed').val(value);
      sendDriverCommand();
    }
  });
  
  $("#steering").val(0);
  $("#steering").keyup(function() {
    $("#steeringSlider").slider("option", "value", parseInt($(this).val()) );
  });
  $("#steeringSlider" ).slider({
    value: 0,
    min: -1023,
    max: 1023,
    step: 1,        
  
    slide: function (event, ui) {
      let value = $("#steeringSlider").slider("option", "value");
      $('#steering').val(value);
      sendDriverCommand();
    }
  });
});
