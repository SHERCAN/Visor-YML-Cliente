var clientID = Date.now();
var ws = new WebSocket("ws://" + window.location.host + "/ws/" +clientID);
function processMessage(event) {
  var jsonObj = JSON.parse(event.data);
  jsonObj.forEach((key) => {
    document.getElementById(key.name.replace(/\ /g, "")).value = key.value;
  });
}

ws.onmessage = processMessage;

// var ws = new WebSocket("ws://localhost:8000/ws");
// ws.onmessage = function (event) {
//   var jsonObj = JSON.parse(event.data);
//   console.log(jsonObj);
//   jsonObj.forEach((key) => {
//     document.getElementById(key.name.replace(/\ /g, "")).value = key.value;
//   });
// };
