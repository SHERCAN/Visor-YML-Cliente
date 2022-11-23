// Modal para la grafica
var graphData = [];
const modal = document.getElementById("modal");
const btnCerrar = document.getElementById("btn-cerrar-modal");
function openModal(element) {
  httpGet(30);
  // graphData = httpGet(30);
  modal.showModal();
}

btnCerrar.addEventListener("click", () => {
  graphData = [];
  modal.close();
});

// Grafica de datos
const ctx = document.getElementById("myChart").getContext("2d");

var newChart = new Chart(ctx, {
  type: "line",
  data: {
    labels: [
      1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    ],
    datasets: [
      {
        label: "Register ##",
        data: [],
        borderColor: "rgb(75, 192, 192)",
      },
    ],
  },
  options: {
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  },
});
Chart.defaults.backgroundColor = "#48E42E";
Chart.defaults.borderColor = "#48E42E";
Chart.defaults.color = "#000000";

// Websocket de conexion
var ws = new WebSocket("ws://" + window.location.host + "/ws/");
async function processMessage(event) {
  var jsonObj = JSON.parse(event.data);
  jsonObj.forEach((key) => {
    document.getElementById(key.name).value = key.value;
    if (key.name == "GridsidevoltageL1-N") {
      graphData.shift();
      graphData.push(key.value);
      newChart.data.datasets[0].data = graphData;
      newChart.update();
    }
  });
}
ws.onmessage = processMessage;

function sendValue(element) {
  console.log("in" + element.name);
  let jsonObj = {
    name: element.name,
    value: document.getElementById("in" + element.name).value,
  };

  console.log(jsonObj);
  ws.send(JSON.stringify(jsonObj));
}
// llamada a la pagina web

// async function httpGet(elemento) {
//   let theUrl = "http://141.147.133.37/get_registers";
//   // let theUrl = "http://127.0.0.1:5000/get_registers";
//   let response = await fetch(theUrl);
//   await response.json().forEach((element) => {
//     if (graphData.length < 20) {
//       graphData.push(element[30]);
//       newChart.data.datasets[0].data = graphData;
//     }
//   });
// }
function httpGet(register) {
  let theUrl = "http://141.147.133.37/get_registers";
  // let theUrl = "http://127.0.0.1:5000/get_registers";
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.open("GET", theUrl, false); // false for synchronous request
  xmlHttp.send(null);
  JSON.parse(xmlHttp.responseText).forEach((element) => {
    if (graphData.length < 20) {
      graphData.push(element[30]);
      newChart.data.datasets[0].data = graphData;
    }
  });
  console.log(graphData);
}
