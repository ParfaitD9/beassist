$("#addTaskModalForm").submit((e) => {
  let form = document.getElementById("addTaskModalForm");
  e.preventDefault();
  let datas = new FormData(form);
  axios
    .post("/create/task", datas)
    .then((res) => {
      showModalAlert("addTaskModal", res);
      e.target.reset();
    })
    .catch((err) => console.log(err));
});

$("a.delete").click((e) => {
  e.preventDefault();
  let _id = e.target.parentNode.parentNode.parentNode.id;
  axios
    .post(`/delete/task/${_id}`)
    .then((res) => {
      if (res.data.success) {
        $(`tr#${_id}`).remove();
      }
      showAlert(res);
    })
    .catch((err) => console.log(err));
});

$("a.edit").click((e) => {
  e.preventDefault();
  let _id = e.target.parentNode.parentNode.parentNode.id;
  axios
    .post(`/defacture/task/${_id}`)
    .then((res) => {
      $(`tr#${_id}`).children()[5].textContent = "";
      showAlert(res);
    })
    .catch((err) => console.log(err));
});
