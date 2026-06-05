/**
 * Navbar móvil — menú hamburguesa (RF-015).
 * TODO: sincronizar estado con foco trap si se añade drawer completo.
 */
(function () {
  "use strict";

  var toggle = document.getElementById("navbar-toggle");
  var panel = document.getElementById("navbar-panel");

  if (!toggle || !panel) {
    return;
  }

  function setOpen(open) {
    panel.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  }

  toggle.addEventListener("click", function () {
    var isOpen = panel.classList.contains("is-open");
    setOpen(!isOpen);
  });

  window.addEventListener("resize", function () {
    if (window.matchMedia("(min-width: 768px)").matches) {
      setOpen(false);
    }
  });

  var userTrigger = document.getElementById("navbar-user-trigger");
  var userDropdown = document.getElementById("navbar-user-dropdown");

  if (userTrigger && userDropdown) {
    function setUserMenuOpen(open) {
      userDropdown.hidden = !open;
      userDropdown.classList.toggle("is-open", open);
      userTrigger.setAttribute("aria-expanded", open ? "true" : "false");
    }

    userTrigger.addEventListener("click", function () {
      var isOpen = !userDropdown.hidden;
      setUserMenuOpen(!isOpen);
    });

    document.addEventListener("click", function (evt) {
      if (
        !userTrigger.contains(evt.target) &&
        !userDropdown.contains(evt.target)
      ) {
        setUserMenuOpen(false);
      }
    });
  }
})();
