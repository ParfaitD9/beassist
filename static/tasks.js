$("#addTaskModalForm").submit((e) => {
  let form = document.getElementById("addTaskModalForm");
  e.preventDefault();
  let datas = new FormData(form);
  hr.open("POST", "/create/task");
  hr.send(datas);
  hr.onreadystatechange = (r) => {
    if (hr.readyState === 4) {
      res = JSON.parse(hr.responseText);
      if (res.success) {
        document.querySelector(".alert").classList.remove("alert-danger");
        document.querySelector(".alert").classList.add("alert-success");
        $(".alert").text(`Tâche ${res.data.name} enrégistrée`);
      } else {
        document.querySelector(".alert").classList.remove("alert-success");
        document.querySelector(".alert").classList.add("alert-danger");
        $(".alert").text(`Erreur ${r.message} lors de la création de la tâche`);
      }

      e.target.reset();
    }
  };
});

$("a.delete").click((e) => {
  e.preventDefault();
  let _id = e.target.parentNode.parentNode.parentNode.id;
  $.post({
    url: `/delete/task/${_id}`,
    dataType: "json",
  }).then((res) => {
    let block = document.querySelector("div#sending");
    if (block) {
      document.body.querySelector(".container").removeChild(block);
    }

    let msg = document.createElement("div");
    msg.id = "sending";
    msg.classList.add("alert");
    if (res.success) {
      msg.classList.remove("alert-danger");
      msg.classList.add("alert-success");
      msg.textContent = `Tâche ${res.data.name} supprimée`;
    } else {
      msg.classList.remove("alert-success");
      msg.classList.add("alert-danger");
      msg.textContent = `Erreur ${res.message} lors de la suppression de tâche`;
    }
    document.body.querySelector(".container").appendChild(msg);
    console.log(res);
  });
});

$("a.edit").click((e) => {
  e.preventDefault();
  let _id = e.target.parentNode.parentNode.parentNode.id;
  $.post({
    url: `/defacture/task/${_id}`,
    dataType: "json",
  })
    .done((res) => {
      let block = document.querySelector("div#sending");
      if (block) {
        document.body.querySelector(".container").removeChild(block);
      }

      let msg = document.createElement("div");
      msg.id = "sending";
      msg.classList.add("alert");

      document.body.querySelector(".container").appendChild(msg);
      if (res.success) {
        msg.classList.remove("alert-danger");
        msg.classList.add("alert-success");
        msg.textContent = `Tâche ${res.data.name} défacturée`;
      } else {
        msg.classList.remove("alert-success");
        msg.classList.add("alert-danger");
        msg.textContent = `${res.message}`;
      }
    })
    .fail((err) => {
      console.log(err);
    });
});
