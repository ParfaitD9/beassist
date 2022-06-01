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
    showAlert(res);
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
      showAlert(res);
    })
    .fail((err) => {
      console.log(err);
    });
});
