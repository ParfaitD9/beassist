$(document).ready((e) => {
  paginate();
  load_customers();
});

$("form#addFactureModalForm").submit((e) => {
  e.preventDefault();
  let dts = new FormData(e.target);

  axios
    .post("/create/facture", dts)
    .then((res) => {
      showModalAlert("addFactureModal", res);
      if (res.success) {
        e.target.reset();
      }
    })
    .catch((err) => console.log(err));
});

$("form#sendFactureModalForm").submit((e) => {
  e.preventDefault();
  let _id = $("span#hash").text();
  let dts = new FormData(e.target);
  dts.append("facture", _id);

  axios
    .post("/send", dts)
    .then((res) => {
      showModalAlert("sendFactureModal", res);
      $(`tr#${_id}`).children()[4].textContent = "Oui";
      e.target.reset();
    })
    .catch((err) => console.log(err));
});

$("#sendFacturesModalForm").submit((e) => {
  e.preventDefault();
  let datas = new FormData(document.querySelector("#sendFacturesModalForm"));
  datas.append("factures", JSON.stringify(getCheckeds()));
  axios
    .post("/send/tomass", datas)
    .then((res) => {
      showModalAlert("sendFacturesModal", res);
    })
    .catch((err) => console.log(err));
});

$("a.edit").click((e) => {
  let _id = e.target.parentNode.parentNode.parentNode.id;
  $("span#hash").text(_id);
});

$("a.delete").click((e) => {
  e.preventDefault();
  let hash = e.target.parentNode.parentNode.parentNode.id;
  axios
    .post(`/delete/facture/${hash}`)
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
