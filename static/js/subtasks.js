$("form#addSubtaskModalForm").submit((e) => {
  let form = document.getElementById("addSubtaskModalForm");
  e.preventDefault();
  let datas = new FormData(form);
  axios
    .post("/create/subtask", datas)
    .then((res) => {
      showModalAlert("addSubtaskModal", res);
      e.target.reset();
    })
    .catch((err) => console.log(err));
});

$("a.delete").click((e) => {
  let _id = e.target.parentNode.parentNode.parentNode.id;
  axios
    .post(`/delete/subtask/${_id}`)
    .then((res) => {
      showAlert(res);
      if (res.data.success) {
        $(`tr#${_id}`).remove();
      }
    })
    .catch((err) => console.log(err));
});
