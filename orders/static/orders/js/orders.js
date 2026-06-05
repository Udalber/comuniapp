/**
 * ComuniApp — Checkout: validación onBlur y paneles de pago (RF-010, RF-011).
 */
(function () {
  "use strict";

  var PHONE_RE = /^[\d\s+\-()]{7,20}$/;
  var POSTAL_RE = /^\d{4,10}$/;
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
    var wrap = fieldEl.closest(".checkout-field");
    if (!wrap) {
      return;
    }
    var errorEl = wrap.querySelector(".checkout-field__error[data-js-error]");
    if (errorEl) {
      errorEl.textContent = message || "";
    }
    wrap.classList.toggle("checkout-field--invalid", Boolean(message));
    fieldEl.setAttribute("aria-invalid", message ? "true" : "false");
  }

  function validateRequired(input) {
    if (!input.value.trim()) {
      setFieldError(input, "Este campo es obligatorio.");
      return false;
    }
    setFieldError(input, "");
    return true;
  }

  function validatePostal(input) {
    var value = input.value.trim();
    if (!value) {
      setFieldError(input, "Este campo es obligatorio.");
      return false;
    }
    if (!POSTAL_RE.test(value)) {
      setFieldError(input, "Introduce un código postal válido (4–10 dígitos).");
      return false;
    }
    setFieldError(input, "");
    return true;
  }

  function validatePhone(input) {
    var value = input.value.trim();
    if (!value) {
      setFieldError(input, "Este campo es obligatorio.");
      return false;
    }
    if (!PHONE_RE.test(value)) {
      setFieldError(input, "Introduce un teléfono válido.");
      return false;
    }
    setFieldError(input, "");
    return true;
  }

  function getValidator(input) {
    var name = input.name || input.id || "";
    if (name.indexOf("postal") !== -1) {
      return validatePostal;
    }
    if (name.indexOf("phone") !== -1 || name.indexOf("nequi") !== -1 || name.indexOf("daviplata") !== -1) {
      return validatePhone;
    }
    if (input.type === "email") {
      return function (el) {
        var value = el.value.trim();
        if (!value) {
          setFieldError(el, "Este campo es obligatorio.");
          return false;
        }
        if (!EMAIL_RE.test(value)) {
          setFieldError(el, "Introduce un correo electrónico válido.");
          return false;
        }
        setFieldError(el, "");
        return true;
      };
    }
    if (input.required || input.hasAttribute("data-checkout-field")) {
      var fieldName = input.getAttribute("data-checkout-field") || name;
      if (fieldName === "instructions" || fieldName === "save_address") {
        return null;
      }
      return validateRequired;
    }
    return null;
  }

  function initBlurValidation(form) {
    qsa(".input, select.input, textarea.input", form).forEach(function (input) {
      var validator = getValidator(input);
      if (!validator) {
        return;
      }
      input.addEventListener("blur", function () {
        validator(input);
      });
    });
  }

  function initSavedAddresses(page) {
    var form = qs("[data-checkout-form='address']", page);
    if (!form) {
      return;
    }
    var hiddenId = qs("#id_saved_address_id", form);
    var fields = {
      line1: qs("#id_line1", form),
      city: qs("#id_city", form),
      department: qs("#id_department", form),
      postal_code: qs("#id_postal_code", form),
      phone: qs("#id_phone", form),
      instructions: qs("#id_instructions", form),
    };

    qsa("[data-saved-address]", page).forEach(function (radio) {
      radio.addEventListener("change", function () {
        if (!radio.checked) {
          return;
        }
        if (hiddenId) {
          hiddenId.value = radio.value;
        }
        if (fields.line1) fields.line1.value = radio.getAttribute("data-address-line1") || "";
        if (fields.city) fields.city.value = radio.getAttribute("data-address-city") || "";
        if (fields.department) fields.department.value = radio.getAttribute("data-address-department") || "";
        if (fields.postal_code) fields.postal_code.value = radio.getAttribute("data-address-postal") || "";
        if (fields.phone) fields.phone.value = radio.getAttribute("data-address-phone") || "";
        if (fields.instructions) {
          fields.instructions.value = radio.getAttribute("data-address-instructions") || "";
        }
        Object.keys(fields).forEach(function (key) {
          if (fields[key]) {
            setFieldError(fields[key], "");
          }
        });
      });
    });

    Object.keys(fields).forEach(function (key) {
      var input = fields[key];
      if (!input) {
        return;
      }
      input.addEventListener("input", function () {
        if (hiddenId) {
          hiddenId.value = "";
        }
        qsa("[data-saved-address]", page).forEach(function (r) {
          r.checked = false;
        });
      });
    });

    form.addEventListener("submit", function () {
      var checked = qs("[data-saved-address]:checked", form);
      if (checked && hiddenId) {
        hiddenId.value = checked.value;
      }
    });
  }

  function showPaymentPanel(method) {
    qsa("[data-payment-panel]").forEach(function (panel) {
      var isActive = panel.getAttribute("data-payment-panel") === method;
      panel.hidden = !isActive;
    });
  }

  function initPaymentPanels(page) {
    var radios = qsa("[data-payment-method-radio]", page);
    if (!radios.length) {
      return;
    }

    function update() {
      var selected = qs("[data-payment-method-radio]:checked", page);
      showPaymentPanel(selected ? selected.value : "");
    }

    radios.forEach(function (radio) {
      radio.addEventListener("change", update);
    });
    update();
  }

  function initAddressPage(page) {
    var form = qs("[data-checkout-form='address']", page);
    if (form) {
      initBlurValidation(form);
    }
    initSavedAddresses(page);
  }

  function initPaymentPage(page) {
    var form = qs("[data-checkout-form='payment']", page);
    if (form) {
      initBlurValidation(form);
    }
    initPaymentPanels(page);
  }

  function init() {
    var page = qs("[data-checkout-page]");
    if (!page) {
      return;
    }
    var pageType = page.getAttribute("data-checkout-page");
    if (pageType === "address") {
      initAddressPage(page);
    } else if (pageType === "payment") {
      initPaymentPage(page);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
