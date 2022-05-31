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

$("a#sendFacture").click((e) => {
  e.preventDefault();
  let hash = e.target.parentNode.parentNode.parentNode.id;
  hr.open("GET", `/send?facture=${hash}`);
  hr.send();

  hr.onreadystatechange = (e) => {
    if (hr.readyState === 4) {
      res = JSON.parse(hr.responseText);
      let block = document.querySelector("div#sending");
      if (block) {
        document.body.removeChild(block);
      }

      let msg = document.createElement("div");
      msg.id = "sending";
      msg.classList.add("alert");
      if (res.success) {
        msg.classList.remove("alert-danger");
        msg.classList.add("alert-success");
        msg.textContent = `Facture ${res.hash} envoyée à ${res.customer}`;
      } else {
        msg.classList.remove("alert-success");
        msg.classList.add("alert-danger");
        msg.textContent = `Erreur ${res.message} lors de l'envoi de la facture ${hash}`;
      }
      document.body.appendChild(msg);
    }
  };
});
