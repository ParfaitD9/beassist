function paginate() {
  if (document.querySelector("ul.pagination")) {
    let pagination = document.querySelector("ul.pagination");
    let path = window.location.pathname;
    let uri = new window.URL(window.location.href);
    let page = Number.parseInt(uri.searchParams.get("page")) || 1;

    let previous = document.createElement("li");
    previous.classList.add("page-item");
    if (page <= 1) {
      previous.classList.add("disabled");
    }

    let previous_link = document.createElement("a");
    previous_link.href = page <= 1 ? "#" : `${path}?page=${page - 1}`;
    previous_link.innerText = "Précédent";
    previous.appendChild(previous_link);
    pagination.appendChild(previous);

    for (let i = page - 2; i <= page + 2; i++) {
      if (i >= 1) {
        let li = document.createElement("li");
        li.classList.add("page-item");
        if (i == page) {
          li.classList.add("active");
        }
        let a = document.createElement("a");
        a.classList.add("page-link");
        a.href = `${path}?page=${i}`;
        a.textContent = i;
        li.appendChild(a);
        pagination.appendChild(li);
      }
    }

    let next = document.createElement("li");
    next.classList.add("page-item");

    let next_link = document.createElement("a");
    next_link.href = `${path}?page=${page + 1}`;
    next_link.innerText = "Suivant";
    next.appendChild(next_link);
    pagination.appendChild(next);
  }
}

function load_customers() {
  let select = document.querySelector("select#customers");
  if (select) {
    axios
      .get("/api/customers")
      .then((res) => {
        res.data.forEach((cus) => {
          let opt = document.createElement("option");
          opt.value = cus.pk;
          opt.text = cus.name;
          select.appendChild(opt);
        });
      })
      .catch((err) => console.log(err));
  }
}

function load_citys() {
  let select = document.querySelector("datalist#cities");
  if (select) {
    axios
      .get("/api/cities")
      .then((res) => {
        res.data.forEach((city) => {
          let opt = document.createElement("option");
          opt.text = city.name;
          select.appendChild(opt);
        });
      })
      .catch((err) => console.log(err));
  }
}

function load_subtasks() {
  let dt = document.querySelector("datalist#subtasks");
  if (dt) {
    axios
      .get("/api/subtasks")
      .then((res) => {
        res.data.forEach((sub) => {
          let opt = document.createElement("option");
          opt.text = sub.name;
          dt.appendChild(opt);
        });
      })
      .catch((err) => console.log(err));
  }
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

function showModalAlert(modalId, res) {
  let modal = document.getElementById(modalId);
  let msg = modal.querySelector("div.alert");
  msg.querySelector("p").textContent = "";
  if (res.data.success) {
    msg.classList.remove("alert-danger");
    msg.classList.add("alert-success");
  } else {
    msg.classList.remove("alert-success");
    msg.classList.add("alert-danger");
    console.log(res.data.message);
  }
  msg.querySelector("p").textContent = `${res.data.message}`;
}

function showAlert(res) {
  let container = document.body.querySelector("main.container");
  let block = container.querySelector("div#c-alert");
  if (block) {
    container.removeChild(block);
  }

  let msg = document.createElement("div");
  msg.id = "c-alert";
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

$(document).ready((e) => {
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
