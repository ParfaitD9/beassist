$("#addEmployeeModalForm").submit((e) => {
  let form = document.getElementById("addEmployeeModalForm");
  e.preventDefault();
  let datas = new FormData(form);
  axios
    .post("/create/customer", datas)
    .then((res) => {
      showModalAlert("addEmployeeModal", res);
      e.target.reset();
    })
    .catch((err) => {
      console.log(err);
    });
});

$("a.delete").click((e) => {
  e.preventDefault();
  let hash = e.target.parentNode.parentNode.parentNode.id;
  axios
    .post(`/delete/customer/${hash}`)
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

$('a[href="#facturerEmployeeModal"]').click(() => {
  $("ul#toFacture li").each((i, obj) => {
    obj.remove();
  });
  $('table tbody input[type="checkbox"]').each((i, obj) => {
    if (obj.checked) {
      toFacture.push(obj.value);
    }
  });
  let chkds = getCheckeds();
  chkds.forEach((obj, i) => {
    let li = document.createElement("li");
    li.textContent = $(`tr#${obj}`).children()[1].textContent;
    $("ul#toFacture").append(li);
  });
});

$("#facturerEmployeeModalForm").submit((e) => {
  e.preventDefault();
  let datas = new FormData();
  datas.append(
    "customers",
    JSON.stringify(toFacture.map((e) => Number.parseInt(e)))
  );
  datas.append("obj", $("#facturation-obj").val());
  axios
    .post("facturer/default", datas)
    .then((res) => {
      console.log(res);
      showModalAlert("facturerEmployeeModal", res);
      $("#facturation-obj").text();
    })
    .catch((err) => {
      console.log(err);
    });
});
