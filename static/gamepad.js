const haveEvents = "ongamepadconnected" in window;
const controllers = {};

var socket = io();

if (navigator.getGamepads) {
  // Add an event listener for gamepad connection/disconnection events
  window.addEventListener("gamepadconnected", function (event) {
    console.log(
      "Gamepad connected at index %d: %s. %d buttons, %d axis.",
      event.gamepad.index,
      event.gamepad.id,
      event.gamepad.buttons.length,
      event.gamepad.axes.length
    );
  });
  window.addEventListener("gamepaddisconnected", function (event) {
    console.log(
      "Gamepad disconnected from index %d: %s",
      event.gamepad.index,
      event.gamepad.id
    );
  });
}

function polling() {
  const gamepad = navigator.getGamepads()[0];
  buttons = gamepad.buttons
  data = []
  for (let i = 0; i < buttons.length; i++) {
    data[i] = buttons[i].value;
  }
  socket.emit('buttons', { data: data });

  axis = gamepad.axes
  socket.emit('axis', {data: [axis[0], axis[1]]})
}

setInterval(polling, 20);
