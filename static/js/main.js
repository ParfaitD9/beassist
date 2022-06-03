$(document).ready(function () {
  // Activate tooltip
  $('[data-toggle="tooltip"]').tooltip();

  // Select/Deselect checkboxes
  var checkbox = $('table tbody input[type="checkbox"]');
  $("#selectAll").click(function () {
    if (this.checked) {
      checkbox.each(function () {
        this.checked = true;
      });
    } else {
      checkbox.each(function () {
        this.checked = false;
      });
    }
  });
  checkbox.click(function () {
    if (!this.checked) {
      $("#selectAll").prop("checked", false);
    }
  });
});

const hr = new XMLHttpRequest();

let field = document.querySelector("select#customers");
if (field) {
  axios
    .get("/api/customers")
    .then((res) => {
      res.data.forEach((element) => {
        let opt = document.createElement("option");
        opt.value = element.pk;
        opt.text = element.name;
        field.appendChild(opt);
      });
    })
    .catch((err) => {
      console.log(err);
    });
}

let tasks = document.querySelector("datalist#tasks");
if (tasks) {
  axios
    .get("/api/tasks")
    .then((res) => {
      res.data.forEach((element) => {
        let opt = document.createElement("option");
        opt.text = element.name;
        tasks.appendChild(opt);
      });
    })
    .catch((err) => {
      console.log(err);
    });
}

function showAlert(res) {
  let block = document.querySelector("div#alert");
  let container = document.body.querySelector(".container");
  if (block) {
    container.removeChild(block);
  }

  let msg = document.createElement("div");
  msg.id = "alert";
  msg.classList.add("alert");

  container.appendChild(msg);
  if (res.data.success) {
    msg.classList.remove("alert-danger");
    msg.classList.add("alert-success");
  } else {
    msg.classList.remove("alert-success");
    msg.classList.add("alert-danger");
  }
  msg.textContent = `${res.data.message}`;
}

function showModalAlert(modalId, res) {
  let modal = document
    .querySelector(`#${modalId}`)
    .querySelector("div.modal-body");
  if (modal.querySelector(".alert")) {
    modal.removeChild(modal.querySelector(".alert"));
  }
  let msg = document.createElement("div");
  msg.classList.add("alert");
  if (res.data.success) {
    msg.classList.remove("alert-danger");
    msg.classList.add("alert-success");
  } else {
    msg.classList.remove("alert-success");
    msg.classList.add("alert-danger");
  }
  msg.textContent = `${res.data.message}`;
  modal.appendChild(msg);
}

function getElementByName(name, block) {
  return block.getElementsByName(name)[0];
}

function getCheckeds() {
  let rs = [];
  $('table tbody input[type="checkbox"]').each((i, obj) => {
    if (obj.checked) {
      rs.push(obj.value);
    }
  });
  return rs;
}
