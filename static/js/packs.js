$(document).ready((e) => {
  $.get({
    url: "/api/subtasks",
  })
    .done((res) => {
      res.forEach((el) => {
        let opt = document.createElement("option");
        opt.text = el.name;
        document.querySelector("datalist#subtasks").appendChild(opt);
      });
    })
    .fail((err) => {});
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

  $.post({
    url: "/create/pack",
    data: {
      data: JSON.stringify(currentPack),
    },
  })
    .done((res) => {
      showModalAlert(res);
      currentPack = {
        name: "",
        subtasks: [],
        customer: "",
      };
    })
    .fail((err) => {
      console.log(err);
    });
});

$("a.edit").click((e) => {
  $("span#facture-pack").text(e.target.parentNode.parentNode.parentNode.id);
});

$("a.delete").click((e) => {
  e.preventDefault();
  let _id = e.target.parentNode.parentNode.parentNode.id;
  $.post({
    url: `/delete/pack/${_id}`,
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

$("#facturePackModalForm").submit((e) => {
  e.preventDefault();
  console.log(e.target.parentNode);

  $.post({
    url: `/facture/pack/${$("span#facture-pack").text()}`,
    data: {
      obj: $("#obj").val(),
    },
  })
    .done((res) => {
      showAlert(res);
    })
    .fail((err) => {
      console.log(err);
    });
});
