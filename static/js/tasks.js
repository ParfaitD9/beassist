$("#addTaskModalForm").submit((e) => {
  let form = document.getElementById("addTaskModalForm");
  e.preventDefault();
  let datas = new FormData(form);
  hr.open("POST", "/create/task");
  hr.send(datas);
  hr.onreadystatechange = (r) => {
    if (hr.readyState === 4) {
      res = JSON.parse(hr.responseText);
      showModalAlert(res);

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
    if (res.success) {
      $(`tr#${_id}`).remove();
    }
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
      $(`tr#${_id}`).children()[5].textContent = "";
      showAlert(res);
    })
    .fail((err) => {
      console.log(err);
    });
});
