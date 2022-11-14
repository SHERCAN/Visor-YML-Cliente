var ws = new WebSocket("ws://localhost:8000/ws");
ws.onmessage = function (event) {
  var jsonObj = JSON.parse(event.data);
  jsonObj.forEach((key) => {
    document.getElementById(key.name.replace(/\ /g, "")).value = key.value;
  });
};
