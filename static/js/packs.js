$(document).ready((e) => {
  axios
    .get("/api/subtasks")
    .then((res) => {
      res.data.forEach((el) => {
        let opt = document.createElement("option");
        opt.text = el.name;
        document.querySelector("datalist#subtasks").appendChild(opt);
      });
    })
    .catch((err) => {
      console.log(err);
    });
});
var currentPack = {
  name: "",
  subtasks: [],
  customer: "",
};
$("input#add-subtask").click((e) => {
  let sub = document.createElement("li");
  sub.textContent = `${$("input#subtask").val()} ${$("input#value").val()}`;
  currentPack.subtasks.push({
    name: $("input#subtask").val(),
    value: $("input#value").val(),
  });
  $("ul#associes").append(sub);
  $("input#subtask").val("");
  $("input#value").val("");
});

$("#addPackModalForm").submit((e) => {
  e.preventDefault();
  currentPack.name = $("#pack-name").val();
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
    .catch((err) => console.log(JSON.stringify(currentPack)));
});

$("a.edit").click((e) => {
  $("span#facture-pack").text(e.target.parentNode.parentNode.parentNode.id);
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

$("#facturePackModalForm").submit((e) => {
  e.preventDefault();
  console.log(e.target.parentNode);

  let datas = new FormData();
  datas.append("obj", $("#obj").val());
  axios
    .post(`/facture/pack/${$("span#facture-pack").text()}`, datas)
    .then((res) => {
      showModalAlert("facturePackModal", res);
    })
    .catch((err) => console.log(res));
});
