"use strict"

let ws = null;
let desiredSpeeds = [];
let pwmValues = [];

function connect() {
  const addr = $('#url').val();
  ws = new WebSocket(addr);

  ws.onopen = function() {
    console.log('Connected to ' + addr);
    ws.send(JSON.stringify({ id: -1, type: 'hello' }));

    let connectButton = $('#connectButton');
    connectButton.removeClass("btn-success");
    connectButton.addClass("btn-danger");
    connectButton.html("Disconnect");
  };
  ws.onerror = function(error) {
    console.log('WebSocket error: ' + error);
  };
  ws.onclose = function() {
    console.log('Closing...');
    ws = null;

    let connectButton = $('#connectButton');
    connectButton.removeClass("btn-danger");
    connectButton.addClass("btn-success");
    connectButton.html("Connect");
  }
  ws.onmessage = function(msg) {
    console.log('Received: ' + msg.data);
  };
}

// ref: http://stackoverflow.com/a/1293163/2343
// This will parse a delimited string into an array of
// arrays. The default delimiter is the comma, but this
// can be overriden in the second argument.
function CSVToArray(strData, strDelimiter) {
  // Check to see if the delimiter is defined. If not,
  // then default to comma.
  strDelimiter = (strDelimiter || ",");

  // Create a regular expression to parse the CSV values.
  var objPattern = new RegExp(
    (
      // Delimiters.
      "(\\" + strDelimiter + "|\\r?\\n|\\r|^)" +

      // Quoted fields.
      "(?:\"([^\"]*(?:\"\"[^\"]*)*)\"|" +

      // Standard fields.
      "([^\"\\" + strDelimiter + "\\r\\n]*))"
    ),
    "gi"
  );

  // Create an array to hold our data. Give the array
  // a default empty first row.
  var arrData = [[]];

  // Create an array to hold our individual pattern
  // matching groups.
  var arrMatches = null;

  // Keep looping over the regular expression matches
  // until we can no longer find a match.
  while (arrMatches = objPattern.exec(strData)) {
    // Get the delimiter that was found.
    var strMatchedDelimiter = arrMatches[1];

    // Check to see if the given delimiter has a length
    // (is not the start of string) and if it matches
    // field delimiter. If id does not, then we know
    // that this delimiter is a row delimiter.
    if (
      strMatchedDelimiter.length &&
      strMatchedDelimiter !== strDelimiter
    ) {
      // Since we have reached a new row of data,
      // add an empty row to our data array.
      arrData.push([]);
    }

    var strMatchedValue;
    // Now that we have our delimiter out of the way,
    // let's check to see which kind of value we
    // captured (quoted or unquoted).
    if (arrMatches[2]) {
      // We found a quoted value. When we capture
      // this value, unescape any double quotes.
      strMatchedValue = arrMatches[2].replace(
        new RegExp("\"\"", "g"),
        "\""
      );
    } else {
      // We found a non-quoted value.
      strMatchedValue = arrMatches[3];
    }

    // Now that we have our value string, let's add
    // it to the data array.
    arrData[arrData.length - 1].push(strMatchedValue);
  }

  // Return the parsed data.
  return (arrData);
}

function setupRawSlider(limitId, valueId, sliderId, defaultLimit, defaultValue,
                        isDoubleSided) {
  let limit = $(limitId);
  limit.val(defaultLimit);

  let value = $(valueId);
  value.val(defaultValue);

  let slider = $(sliderId).slider({
    value: value.val(),
    min: isDoubleSided ? -limit.val() : 0,
    max: limit.val(),
    step: 1,
    slide: function (e, ui) {
      value.val(ui.value);
      try {
        $.throttle(200, sendRawDriveCommand());
      } catch (e) {
        console.error(e.message);
      };
    }
  });

  value.on('change', function() {
    if (this.value < 0) {
      this.value = 0;
    }
    slider.slider('value', this.value);
  });

  limit.on('change', function() {
    if (this.value < 0) {
      this.value = 0;
    }
    slider.slider('option', 'min', isDoubleSided ? -this.value : 0);
    slider.slider('option', 'max', this.value);
    value.val(0);
  });
}

function sendRawDriveCommand() {
  const vehicleId = $('#vehicleId').val();
  const speed = parseInt($('#pwm').val());
  const steering = parseInt($('#servoPos').val());
  let command = {
    id: vehicleId,
    type: 'calib_drive',
    speed: speed,
    steering: steering
  };
  ws.send(JSON.stringify(command));
}

function sendFlipSteeringCommand() {
  const vehicleId = $('#vehicleId').val();
  let command = { id: vehicleId, type: 'calib_flip_steering' };
  ws.send(JSON.stringify(command));
}

function sendCalibrateSteeringCommand() {
  const vehicleId = $('#vehicleId').val();
  const minServoAngle = parseInt($('#minServoAngle').val());
  const maxServoAngle = parseInt($('#maxServoAngle').val());
  const midServoAngle = parseInt($('#midServoAngle').val());
  let command = {
    id: vehicleId,
    type: 'calib_steering',
    minServoAngle: minServoAngle,
    maxServoAngle: maxServoAngle,
    midServoAngle: midServoAngle
  };
  ws.send(JSON.stringify(command));
}

function parseSpeedData() {
  desiredSpeeds = [];
  pwmValues = [];

  let speedDataTableBody = $('#speedDataTableBody');
  speedDataTableBody.html('');

  let parsedData = CSVToArray($('#speedData').val(), ',');
  let tbodyHtml = '';
  parsedData.forEach(function(item, index) {
    if (item.length !== 2) {
      throw 'Row must be 2 elements';
    }
    desiredSpeeds.push(parseFloat(item[0]));
    pwmValues.push(parseInt(item[1]));

    const speedColHtml = '<td>' + desiredSpeeds[index] + '</td>';
    const pwmColHtml = '<td>' + pwmValues[index] + '</td>';
    tbodyHtml = tbodyHtml.concat('<tr>' + speedColHtml + pwmColHtml + "</tr>");
  });

  speedDataTableBody.html(tbodyHtml);
}

function sendCalibrateSpeedCommand() {
  const vehicleId = $('#vehicleId').val();
  let command = {
    id: vehicleId,
    type: 'calib_speed',
    desiredSpeedsLen: desiredSpeeds.length,
    desiredSpeeds: desiredSpeeds,
    desiredSpeedsPwm: pwmValues
  };
  ws.send(JSON.stringify(command));
}

function sendFlipForwardCommand() {
  const vehicleId = $('#vehicleId').val();
  let command = { id: vehicleId, type: 'calib_flip_forward' };
  ws.send(JSON.stringify(command));
}

function sendDriveCommand() {
  const vehicleId = $('#vehicleId').val();
  const speed = parseFloat($('#speed').val());
  const steering = parseFloat($('#steeringAngle').val());
  let command = {
    id: -1,
    vehId: vehicleId,
    type: 'drive',
    speed: speed,
    steering: steering
  };
  ws.send(JSON.stringify(command));
}

$(document).ready(function() {
  $('#connectButton').click(function() { connect(); });
  $('#sendRawDriveButton').click(function() { sendRawDriveCommand(); });
  $('#flipSteeringButton').click(function() { sendFlipSteeringCommand(); });
  $('#calibrateSteeringButton')
    .click(function() { sendCalibrateSteeringCommand(); });
  $('#parseSpeedDataButton').click(function() { parseSpeedData(); });
  $('#calibrateSpeedDataButton').click(function() { sendCalibrateSpeedCommand(); });
  $('#flipForwardButton').click(function() { sendFlipForwardCommand(); });
  $('#sendDriveButton').click(function() { sendDriveCommand(); });

  setupRawSlider('#maxPwm', '#pwm', '#pwmSlider', 1023, 0, true);
  setupRawSlider('#maxServoPos', '#servoPos', '#servoPosSlider', 90, 0, false);
});
