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
      if (res.data.success) {
        showAlert(res);
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
  let chkds = getCheckeds();
  chkds.forEach((obj, i) => {
    let li = document.createElement("li");
    li.textContent = $(`tr#${obj}`).children()[1].textContent;
    $("ul#toFacture").append(li);
  });
});

$("#facturerEmployeeModalForm").submit((e) => {
  e.preventDefault();
  console.log("Demande de facture");
  let datas = new FormData();
  datas.append(
    "customers",
    JSON.stringify(getCheckeds().map((e) => Number.parseInt(e)))
  );
  datas.append("obj", $("#facturation-obj").val());
  axios
    .post("facturer/default", datas)
    .then((res) => {
      console.log(res);
      showModalAlert("facturerEmployeeModal", res);
      $("#facturation-obj").val("");
    })
    .catch((err) => {
      console.log(err);
    });
});

$("input#pro").click((e) => {
  if (e.target.checked) {
    $("input#reg").prop("checked", false);
  }
});

$('i[title="Convertir"]').click((e) => {
  let hash = e.currentTarget.parentNode.parentNode.parentNode.id;
  axios
    .get(`/claim/prospect/${hash}`)
    .then((res) => {
      showAlert(res);
      $(`tr#${hash}`).remove();
    })
    .catch((err) => console.log(err));
});

$('i[title="Régulariser"]').click((e) => {
  let hash = e.currentTarget.parentNode.parentNode.parentNode.id;
  axios
    .get(`/regularise/customer/${hash}`)
    .then((res) => {
      showAlert(res);
      $(`tr#${hash}`).remove();
    })
    .catch((err) => console.log(err));
});
