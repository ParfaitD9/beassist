function getTaches(debut, fin) {
  axios.get(`/api/taches/${debut}/${fin}`).then((res) => {
    console.log(res.data);
  });
}
function getDayFactures(date, callback, results) {
  axios
    .get(`/api/factures/${date}`)
    .then((res) => {
      callback(res, results);
    })
    .catch((err) => console.log(err));
}

function getRangeModel(model, start, end, callback, chart) {
  axios
    .get(`/api/${model}/${start.toDateString()}/${end.toDateString()}`)
    .then((res) => {
      callback(res.data, chart);
    })
    .catch((err) => console.log(err));
}
const getDatesBetween = (startDate, endDate) => {
  const dates = [];

  // Strip hours minutes seconds etc.
  let currentDate = new Date(
    startDate.getFullYear(),
    startDate.getMonth(),
    startDate.getDate()
  );

  while (currentDate <= endDate) {
    dates.push(currentDate);

    currentDate = new Date(
      currentDate.getFullYear(),
      currentDate.getMonth(),
      currentDate.getDate() + 1 // Will increase month if over range
    );
  }

  return dates;
};

const myCallback = (data, chart) => {
  chart.data.labels = data.map((a) => a.date);
  chart.data.datasets[0].data = data.map((a) => a.point);
  chart.data.datasets[1].data = data.map((a) => a.count);
  chart.update();
};

let _tasks = [];
let today = new Date();
let month_start = new Date(today.getFullYear(), today.getMonth(), 1);

const ctx = document.getElementById("factures-cpt").getContext("2d");
const factureChart = new Chart(ctx, {
  type: "bar",
  data: {
    labels: [],
    datasets: [
      {
        label: `Somme facturée jounalièrement`,
        data: [],
        backgroundColor: "rgba(255, 99, 132, 0.2)",
        borderColor: "rgba(255, 99, 132, 1)",
        borderWidth: 1,
      },
      {
        label: `Nb. factures générée`,
        data: [],
        backgroundColor: "rgba(75, 192, 192, 0.2)",
        borderColor: "rgba(75, 192, 192, 1)",
        borderWidth: 1,
      },
    ],
  },
  options: {
    scales: {
      y: {
        beginAtZero: true,
        display: true,
        type: "logarithmic",
      },
    },
  },
});

const ctx2 = document.getElementById("tasks-cpt").getContext("2d");
const taskChart = new Chart(ctx2, {
  type: "bar",
  data: {
    labels: [],
    datasets: [
      {
        label: `Coût des tâches effectués`,
        data: [],
        backgroundColor: "rgba(255, 99, 132, 0.2)",
        borderColor: "rgba(255, 99, 132, 1)",
        borderWidth: 1,
      },
      {
        label: `Nb. de tâches`,
        data: [],
        backgroundColor: "rgba(75, 192, 192, 0.2)",
        borderColor: "rgba(75, 192, 192, 1)",
        borderWidth: 1,
      },
    ],
  },
  options: {
    scales: {
      y: {
        beginAtZero: true,
        display: true,
        type: "logarithmic",
      },
    },
  },
});
getRangeModel("factures", month_start, today, myCallback, factureChart);
getRangeModel("tasks", month_start, today, myCallback, taskChart);
