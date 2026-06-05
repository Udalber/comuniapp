/**
 * ComuniApp — Validación y UX de formularios de autenticación (RF-001, RF-002, RNF-008).
 */
(function () {
  "use strict";

  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  function qs(selector, root) {
    return (root || document).querySelector(selector);
  }

  function qsa(selector, root) {
    return Array.prototype.slice.call(
      (root || document).querySelectorAll(selector)
    );
  }

  function setFieldError(fieldEl, message) {
    var wrap = fieldEl.closest(".auth-field");
    if (!wrap) {
      return;
    }
    var errorEl = wrap.querySelector(".auth-field__error[data-js-error]");
    if (errorEl) {
      errorEl.textContent = message || "";
    }
    wrap.classList.toggle("auth-field--invalid", Boolean(message));
    fieldEl.setAttribute(
      "aria-invalid",
      message ? "true" : "false"
    );
  }

  function validateEmailInput(input) {
    var value = input.value.trim();
    if (!value) {
      setFieldError(input, "Este campo es obligatorio.");
      return false;
    }
    if (!EMAIL_RE.test(value)) {
      setFieldError(input, "Introduce un correo electrónico válido.");
      return false;
    }
    setFieldError(input, "");
    return true;
  }

  function validateRequired(input) {
    if (!input.value.trim()) {
      setFieldError(input, "Este campo es obligatorio.");
      return false;
    }
    setFieldError(input, "");
    return true;
  }

  function getPasswordStrength(password) {
    if (!password) {
      return { level: "", label: "" };
    }
    var score = 0;
    if (password.length >= 8) {
      score += 1;
    }
    if (password.length >= 12) {
      score += 1;
    }
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) {
      score += 1;
    }
    if (/\d/.test(password)) {
      score += 1;
    }
    if (/[^A-Za-z0-9]/.test(password)) {
      score += 1;
    }
    if (score <= 2) {
      return { level: "weak", label: "Contraseña débil" };
    }
    if (score <= 4) {
      return { level: "medium", label: "Contraseña media" };
    }
    return { level: "strong", label: "Contraseña fuerte" };
  }

  function initPasswordStrength(form) {
    var passwordInput = qs('[data-auth="password"]', form);
    var strengthEl = qs(".auth-strength", form);
    if (!passwordInput || !strengthEl) {
      return;
    }
    var labelEl = qs(".auth-strength__label", strengthEl);

    function update() {
      var result = getPasswordStrength(passwordInput.value);
      strengthEl.setAttribute("data-level", result.level);
      if (labelEl) {
        labelEl.textContent = result.label;
      }
    }

    passwordInput.addEventListener("input", update);
    update();
  }

  function initPasswordToggles(root) {
    qsa("[data-password-toggle]", root).forEach(function (btn) {
      var targetId = btn.getAttribute("aria-controls");
      var input = targetId ? document.getElementById(targetId) : null;
      if (!input) {
        return;
      }
      btn.addEventListener("click", function () {
        var isHidden = input.type === "password";
        input.type = isHidden ? "text" : "password";
        btn.setAttribute("aria-pressed", isHidden ? "true" : "false");
        btn.textContent = isHidden ? "Ocultar" : "Mostrar";
      });
    });
  }

  function initRegisterForm() {
    var form = qs('[data-auth-form="register"]');
    if (!form) {
      return;
    }

    var fullName = qs("#id_full_name", form);
    var email = qs("#id_email", form);
    var password = qs("#id_password", form);

    if (fullName) {
      fullName.addEventListener("blur", function () {
        validateRequired(fullName);
      });
      fullName.addEventListener("input", function () {
        if (fullName.value.trim()) {
          setFieldError(fullName, "");
        }
      });
    }

    if (email) {
      email.addEventListener("blur", function () {
        validateEmailInput(email);
      });
      email.addEventListener("input", function () {
        if (email.value.trim()) {
          validateEmailInput(email);
        }
      });
    }

    if (password) {
      password.addEventListener("blur", function () {
        if (!password.value) {
          setFieldError(password, "Este campo es obligatorio.");
        } else {
          setFieldError(password, "");
        }
      });
    }

    initPasswordStrength(form);
    initPasswordToggles(form);

    form.addEventListener("submit", function (evt) {
      var ok = true;
      if (fullName && !validateRequired(fullName)) {
        ok = false;
      }
      if (email && !validateEmailInput(email)) {
        ok = false;
      }
      if (password && !password.value) {
        setFieldError(password, "Este campo es obligatorio.");
        ok = false;
      }
      if (!ok) {
        evt.preventDefault();
      }
    });
  }

  function initLoginForm() {
    var form = qs('[data-auth-form="login"]');
    if (!form) {
      return;
    }

    var email = qs("#id_login_email", form);
    var password = qs("#id_login_password", form);
    var submitBtn = qs('[data-auth="login-submit"]', form);

    function updateSubmitState() {
      if (!submitBtn) {
        return;
      }
      var ready =
        email &&
        email.value.trim() &&
        password &&
        password.value.length > 0;
      submitBtn.disabled = !ready;
    }

    if (email) {
      email.addEventListener("input", updateSubmitState);
      email.addEventListener("blur", function () {
        if (email.value.trim()) {
          validateEmailInput(email);
        }
      });
    }

    if (password) {
      password.addEventListener("input", updateSubmitState);
    }

    initPasswordToggles(form);
    updateSubmitState();
  }

  function initMessagesDismiss() {
    qsa("[data-message-dismiss]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var item = btn.closest(".messages__item");
        if (item) {
          item.remove();
        }
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initRegisterForm();
    initLoginForm();
    initMessagesDismiss();
  });
})();
