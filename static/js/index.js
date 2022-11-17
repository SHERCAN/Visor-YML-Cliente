var clientID = Date.now();
var ws = new WebSocket("ws://" + window.location.host + "/ws/" + clientID);

// this.setState({
//   interval: setInterval(() => ws.send('echo'), 1000)
// });
async function processMessage(event) {
  var jsonObj = JSON.parse(event.data);
  console.log(jsonObj);
  // test();
  jsonObj.forEach((key) => {
    document.getElementById(key.name).value = key.value;
  });
  // setState({data: newData, count: count + 1});
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
