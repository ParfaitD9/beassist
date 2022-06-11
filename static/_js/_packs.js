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
  let datas = new FormData();
  datas.append("obj", $("#inputObj").val());
  axios
    .post(`/facture/pack/${$("span#facture-pack").text()}`, datas)
    .then((res) => {
      showModalAlert("facturePackModal", res);
    })
    .catch((err) => console.log(res));
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
