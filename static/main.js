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
