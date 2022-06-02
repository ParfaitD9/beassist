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

let hr = new XMLHttpRequest();

let field = document.querySelector("select#customers");
if (field) {
  $.get({
    url: "/api/customers",
    dataType: "json",
  })
    .done((res) => {
      res.forEach((element) => {
        let opt = document.createElement("option");
        opt.value = element.pk;
        opt.text = element.name;
        field.appendChild(opt);
      });
    })
    .fail((err) => {
      console.log(err);
    });
}

let tasks = document.querySelector("datalist#tasks");
if (tasks) {
  $.get({
    url: "/api/tasks",
    dataType: "json",
  })
    .done((res) => {
      res.forEach((element) => {
        let opt = document.createElement("option");
        opt.text = element.name;
        tasks.appendChild(opt);
      });
    })
    .fail((err) => {
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
  if (res.success) {
    msg.classList.remove("alert-danger");
    msg.classList.add("alert-success");
  } else {
    msg.classList.remove("alert-success");
    msg.classList.add("alert-danger");
  }
  msg.textContent = `${res.message}`;
}

function showModalAlert(res) {
  if (res.success) {
    document.querySelector(".alert").classList.remove("alert-danger");
    document.querySelector(".alert").classList.add("alert-success");
  } else {
    document.querySelector(".alert").classList.remove("alert-success");
    document.querySelector(".alert").classList.add("alert-danger");
  }
  $(".alert").text(`${res.message}`);
}
function getElementByName(name, block) {
  return block.getElementsByName(name)[0];
}
