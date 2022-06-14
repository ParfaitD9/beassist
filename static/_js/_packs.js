$(document).ready((e) => {
  paginate();
  load_subtasks();
  load_customers();
});

var currentPack = {
  name: "",
  subtasks: [],
  customer: "",
};

$("form#addPackModalForm").submit((e) => {
  e.preventDefault();
  currentPack.name = $("#inputName").val();
  currentPack.customer = $("#customers").val();

  let datas = new FormData();
  datas.append("data", JSON.stringify(currentPack));
  axios
    .post("/create/pack", datas)
    .then((res) => {
      showModalAlert("addPackModal", res);
      $("ul#associes")
        .children()
        .each((i, obj) => {
          obj.remove();
        });
      currentPack = {
        name: "",
        subtasks: [],
        customer: "",
      };
    })
    .catch((err) => console.log(err));
});

$("form#facturePackModalForm").submit((e) => {
  e.preventDefault();
  let _id = $("span#facture-pack").text();
  let obj = $("#inputObj").val();
  facturePack(_id, obj);
});

function facturePack(_id, obj, inmass = false) {
  let datas = new FormData();
  datas.append("obj", obj);
  axios
    .post(`/facture/pack/${_id}`, datas)
    .then((res) => {
      showModalAlert(inmass ? "facturePacksModal" : "facturePackModal", res);
    })
    .catch((err) => console.log(err));
}

$("#facturePacksModal").click((e) => {
  $("#facturePacksModal div.alert p").text(
    "Les clients sélectionnés seront facturés."
  );
});

$("#facturePacksModalForm").submit((e) => {
  e.preventDefault();
  let msg = $("#inputMasseObj").val();
  let dts = new FormData();
  dts.append("packs", JSON.stringify(getCheckeds()));
  dts.append("msg", msg);
  axios
    .post("/facture/mass", dts)
    .then((res) => {
      showModalAlert("facturePacksModal", res);
    })
    .catch((err) => console.log(err));
  e.target.reset();
});

$("input#add-subtask").click((e) => {
  let sub = document.createElement("li");
  sub.textContent = `${$("input#inputSubtask").val()} ${$(
    "input#inputValue"
  ).val()}`;
  currentPack.subtasks.push({
    name: $("input#inputSubtask").val(),
    value: $("input#inputValue").val(),
  });
  $("ul#associes").append(sub);
  $("input#inputSubtask").val("");
  $("input#inputValue").val("");
});

$("a.edit").click((e) => {
  let _id = e.target.parentNode.parentNode.parentNode.id;
  $("span#facture-pack").text(_id);
  $("#facturePackModal p").text("");
  $("#facturePackModal div.alert").removeClass("alert-success alert-danger");
  $("#inputObj").val("");
});

$("a.delete").click((e) => {
  e.preventDefault();
  let _id = e.target.parentNode.parentNode.parentNode.id;
  axios
    .post(`/delete/pack/${_id}`)
    .then((res) => {
      showAlert(res);
      if (res.data.success) {
        $(`tr#${_id}`).remove();
      }
    })
    .catch((err) => console.log(err));
});
