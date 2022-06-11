$(document).ready((e) => {
  load_citys();
  paginate();
});

$("form#addCustomerModalForm").submit((e) => {
  e.preventDefault();
  let datas = new FormData(e.target);
  axios
    .post("/create/customer", datas)
    .then((res) => {
      showModalAlert("addCustomerModal", res);
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

$('i[title="Régulariser"]').click((e) => {
  e.preventDefault();
  let hash = e.currentTarget.parentNode.parentNode.parentNode.id;
  axios
    .post(`/regularise/customer/${hash}`)
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

$('i[title="Convertir"]').click((e) => {
  e.preventDefault();
  let hash = e.currentTarget.parentNode.parentNode.parentNode.id;
  axios
    .post(`/claim/prospect/${hash}`)
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

$('a[href="#factureCustomerModal"]').click(() => {
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

$("form#factureCustomerModalForm").submit((e) => {
  e.preventDefault();
  let datas = new FormData();
  datas.append(
    "customers",
    JSON.stringify(getCheckeds().map((e) => Number.parseInt(e)))
  );
  datas.append("obj", $("#facturation-obj").val());
  axios
    .post("facturer/customers", datas)
    .then((res) => {
      console.log(res);
      showModalAlert("factureCustomerModal", res);
      $("#facturation-obj").val("");
    })
    .catch((err) => {
      console.log(err);
    });
});
