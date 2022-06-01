$("#addFactureModalForm").submit((e) => {
  let form = document.getElementById("addFactureModalForm");
  e.preventDefault();
  let datas = new FormData(form);
  hr.open("POST", "/create/facture");
  hr.send(datas);
  hr.onreadystatechange = (r) => {
    if (hr.readyState === 4) {
      res = JSON.parse(hr.responseText);
      if (res.success) {
        document.querySelector(".alert").classList.remove("alert-danger");
        document.querySelector(".alert").classList.add("alert-success");
        $(".alert").text(`Facture ${res.data.hash} générée`);
      } else {
        document.querySelector(".alert").classList.remove("alert-success");
        document.querySelector(".alert").classList.add("alert-danger");
        $(".alert").text(
          `Erreur ${res.message} lors de la génération de facture`
        );
      }

      e.target.reset();
    }
  };
});

$("#editFactureModalForm").submit((e) => {
  e.preventDefault();
  console.log("<Submited");
  let datas = new FormData(document.querySelector("form#editFactureModalForm"));
  datas.append("facture", document.querySelector("span#hash").textContent);
  hr.open("POST", "/send");
  hr.onreadystatechange = (e) => {
    if (hr.readyState === 4) {
      res = JSON.parse(hr.responseText);
      showAlert(res);
    }
  };
  hr.send(datas);
});

$("a.delete").click((e) => {
  e.preventDefault();
  let hash = e.target.parentNode.parentNode.parentNode.id;
  $.post(`/delete/facture/${hash}`)
    .done((res) => {
      showAlert(res);
    })
    .fail((err) => {
      console.log(err);
    });
});

function getRowInfos(rowId) {
  let row = document.querySelector(`tr#${rowId}`);
  let fields = row.getElementsByTagName("td");
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

function sendMail(datas) {}
