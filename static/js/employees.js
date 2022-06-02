$("#addEmployeeModalForm").submit((e) => {
  let form = document.getElementById("addEmployeeModalForm");
  e.preventDefault();
  let datas = new FormData(form);
  hr.open("POST", "/create/customer");
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
  let hash = e.target.parentNode.parentNode.parentNode.id;
  $.post({
    url: `/delete/customer/${hash}`,
  })
    .done((res) => {
      showAlert(res);
      if (res.success) {
        $(`tr#${hash}`).remove();
      }
    })
    .fail((err) => {
      console.log(err);
    });
});
