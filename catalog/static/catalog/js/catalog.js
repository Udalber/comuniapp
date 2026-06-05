(function () {
  "use strict";

  var filterToggle = document.getElementById("catalog-filter-toggle");
  var filterClose = document.getElementById("catalog-filter-close");
  var filterPanel = document.getElementById("catalog-filters");
  var filterOverlay = document.getElementById("catalog-filter-overlay");
  var filterForm = document.getElementById("catalog-filters-form");

  function openFilters() {
    if (!filterPanel) return;
    filterPanel.classList.add("is-open");
    if (filterOverlay) filterOverlay.hidden = false;
    if (filterToggle) filterToggle.setAttribute("aria-expanded", "true");
    document.body.style.overflow = "hidden";
  }

  function closeFilters() {
    if (!filterPanel) return;
    filterPanel.classList.remove("is-open");
    if (filterOverlay) filterOverlay.hidden = true;
    if (filterToggle) filterToggle.setAttribute("aria-expanded", "false");
    document.body.style.overflow = "";
  }

  if (filterToggle) {
    filterToggle.addEventListener("click", openFilters);
  }
  if (filterClose) {
    filterClose.addEventListener("click", closeFilters);
  }
  if (filterOverlay) {
    filterOverlay.addEventListener("click", closeFilters);
  }

  if (filterForm) {
    var autoSubmitControls = filterForm.querySelectorAll(
      'input[type="checkbox"], select[name="sort"]'
    );
    autoSubmitControls.forEach(function (control) {
      control.addEventListener("change", function () {
        filterForm.submit();
      });
    });

    var priceInputs = filterForm.querySelectorAll(
      'input[name="price_min"], input[name="price_max"]'
    );
    priceInputs.forEach(function (input) {
      input.addEventListener("change", function () {
        filterForm.submit();
      });
    });
  }
})();
