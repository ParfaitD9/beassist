var hr = new XMLHttpRequest();
const selectid = document.getElementById;
//const select = document.querySelector;

var field = document.querySelector("select#customers");
if (field) {
  hr.open("GET", "/api/customers");
  hr.send();
  hr.onreadystatechange = (e) => {
    if (hr.readyState === 4) {
      JSON.parse(hr.responseText).forEach((element) => {
        let opt = document.createElement("option");
        opt.value = element.pk;
        opt.text = element.name;

        field.appendChild(opt);
      });
    }
    console.log("Je sais pas");
  };
}

$("#addEmployeeModalForm").submit((e) => {
  let form = document.getElementById("addEmployeeModalForm");
  e.preventDefault();
  let datas = new FormData(form);
  hr.open("POST", "/create/customer");
  hr.send(datas);
  hr.onreadystatechange = (r) => {
    if (hr.readyState === 4) {
      res = JSON.parse(hr.responseText);
      if (res.success) {
        document.querySelector(".alert").classList.toggle("alert-success");
        $(".alert").text(`Client ${res.data.name} enrégistré`);
      } else {
        document.querySelector(".alert").classList.toggle("alert-danger");
        $(".alert").text(
          `Erreur ${res.message} lors de l'enrégistrement du client`
        );
      }

      e.target.reset();
    }
  };
});

$("#addTaskModalForm").submit((e) => {
  let form = document.getElementById("addTaskModalForm");
  e.preventDefault();
  let datas = new FormData(form);
  hr.open("POST", "/create/task");
  hr.send(datas);
  hr.onreadystatechange = (r) => {
    if (hr.readyState === 4) {
      res = JSON.parse(hr.responseText);
      if (res.success) {
        document.querySelector(".alert").classList.toggle("alert-success");
        $(".alert").text(`Tâche ${res.data.name} enrégistrée`);
      } else {
        document.querySelector(".alert").classList.toggle("alert-danger");
        $(".alert").text(`Erreur ${r.message} lors de la création de la tâche`);
      }

      e.target.reset();
    }
  };
});

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
        document.querySelector(".alert").classList.toggle("alert-success");
        $(".alert").text(`Facture ${res.data.hash} générée`);
      } else {
        document.querySelector(".alert").classList.toggle("alert-danger");
        $(".alert").text(
          `Erreur ${r.message} lors de la génération de facture`
        );
      }

      e.target.reset();
    }
  };
});

$("a#sendFacture").click((e) => {
  e.preventDefault();
  let hash = $("a#sendFacture").parent().parent().attr("id");
  hr.open("GET", `/send?facture=${hash}`);
  hr.send();

  hr.onreadystatechange = (e) => {
    if (hr.readyState === 4) {
      res = JSON.parse(hr.responseText);
      let msg = document.createElement("div");
      msg.classList.add("alert");
      if (res.success) {
        msg.classList.toggle("alert-success");
        msg.textContent = `Facture ${res.hash} envoyée à ${res.customer}`;
      } else {
        msg.classList.toggle("alert-danger");
        msg.textContent = `Erreur ${res.message} lors de l'envoi de la facture ${hash}`;
      }
      document.querySelector("body").appendChild(msg);
    }
  };
});
