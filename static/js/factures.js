$("#addFactureModalForm").submit((e) => {
  let form = document.getElementById("addFactureModalForm");
  e.preventDefault();
  let datas = new FormData(form);
  axios
    .post("/create/facture", datas)
    .then((res) => {
      showModalAlert("addFactureModal", res);
      e.target.reset();
    })
    .catch((err) => {
      console.log(err);
    });
});

$("#editFactureModalForm").submit((e) => {
  e.preventDefault();
  let datas = new FormData(document.querySelector("form#editFactureModalForm"));
  datas.append("facture", document.querySelector("span#hash").textContent);

  axios
    .post("/send", datas)
    .then((res) => {
      showModalAlert("editFactureModal", res);
      $("#message").val("");
    })
    .catch((err) => {
      console.log(err);
    });
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

function getRowInfos(rowId) {
  let row = $(`tr#${rowId}`);
  fields = row.children();
  return {
    hash: fields[1].textContent,
    customer: fields[2].textContent,
    date: fields[3].textContent,
    price: fields[5].textContent,
  };
}

$("a.edit").click((e) => {
  let infos = getRowInfos(e.target.parentNode.parentNode.parentNode.id);
  document.querySelector("span#hash").textContent = infos.hash;
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
