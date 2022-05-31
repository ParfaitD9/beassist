const selectid = document.getElementById;
//const select = document.querySelector;

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
        document.querySelector(".alert").classList.remove("alert-danger");
        document.querySelector(".alert").classList.add("alert-success");
        $(".alert").text(`Client ${res.data.name} enrégistré`);
      } else {
        document.querySelector(".alert").classList.remove("alert-success");
        document.querySelector(".alert").classList.add("alert-danger");
        $(".alert").text(
          `Erreur ${res.message} lors de l'enrégistrement du client`
        );
      }

      e.target.reset();
    }
  };
});
