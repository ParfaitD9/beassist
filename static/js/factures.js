$("#addFactureModalForm").submit((e) => {
  let form = document.getElementById("addFactureModalForm");
  e.preventDefault();
  let datas = new FormData(form);
  hr.open("POST", "/create/facture");
  hr.send(datas);
  hr.onreadystatechange = (r) => {
    if (hr.readyState === 4) {
      res = JSON.parse(hr.responseText);
      showModalAlert(res);
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
      if (res.success) {
        $(`tr#${hash}`).remove();
      }
    })
    .fail((err) => {
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

function sendMail(datas) {}
