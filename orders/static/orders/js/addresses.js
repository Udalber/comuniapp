(function () {
  "use strict";

  var form = document.querySelector("[data-address-delete-form]");
  if (!form) {
    return;
  }

  form.addEventListener("submit", function (event) {
    if (form.dataset.confirmed === "true") {
      return;
    }
    event.preventDefault();
    var confirmed = window.confirm(
      "¿Estás seguro de que deseas eliminar esta dirección?"
    );
    if (confirmed) {
      form.dataset.confirmed = "true";
      form.submit();
    }
  });
})();
