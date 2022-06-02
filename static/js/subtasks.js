$("form#addSubtaskModalForm").submit((e) => {
  let form = document.getElementById("addSubtaskModalForm");
  e.preventDefault();
  console.log("Submited");
  let datas = new FormData(form);
  hr.open("POST", "/create/subtask");
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
  let _id = e.target.parentNode.parentNode.parentNode.id;
  $.post({
    url: `/delete/subtask/${_id}`,
  })
    .done((res) => {
      showAlert(res);
      if (res.success) {
        $(`tr#${_id}`).remove();
      }
    })
    .fail((err) => {
      console.log(err);
    });
});
