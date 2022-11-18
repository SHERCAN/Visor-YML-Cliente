var ws = new WebSocket("ws://" + window.location.host + "/ws/");

async function processMessage(event) {
  var jsonObj = JSON.parse(event.data);
  jsonObj.forEach((key) => {
    document.getElementById(key.name).value = key.value;
  });
}
ws.onmessage = processMessage;

function sendValue(element) {
  console.log("in"+element.name);
  let jsonObj = {
    name: element.name,
    value: document.getElementById("in"+element.name).value,
  };
  
  console.log(jsonObj);
  ws.send(JSON.stringify(jsonObj));

}
