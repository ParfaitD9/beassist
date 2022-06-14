$(document).ready((e) => {
  paginate();
  load_customers();
  load_subtasks();
});

$("form#addTaskModalForm").submit((e) => {
  e.preventDefault();
  let datas = new FormData(e.target);

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
  let hash = e.target.parentNode.parentNode.parentNode.id;
  axios
    .post(`/delete/task/${hash}`)
    .then((res) => {
      showAlert(res);
      if (res.data.success) {
        $(`tr#${hash}`).remove();
      }
    })
    .catch((err) => {
      console.log(err);
    });
});

$('i[title="Défacturer"]').click((e) => {
  e.preventDefault();
  let _id = e.currentTarget.parentNode.parentNode.parentNode.id;
  axios
    .post(`/defacture/task/${_id}`)
    .then((res) => {
      $(`tr#${_id}`).children()[5].textContent = "";
      showAlert(res);
    })
    .catch((err) => console.log(err));
});
