/**
 * Carrito — mejora progresiva: add (detalle), +/- y eliminar (/cart/).
 * Reutiliza la región .messages de base.html para toasts.
 */
(function () {
  "use strict";

  function getCartDetailUrl() {
    var cartLink = qs(".navbar__cart");
    return cartLink ? cartLink.getAttribute("href") : "/cart/";
  }

  function qs(sel, root) {
    return (root || document).querySelector(sel);
  }

  function qsa(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }

  function getCsrfToken(form) {
    var input = form && form.querySelector('input[name="csrfmiddlewaretoken"]');
    return input ? input.value : "";
  }

  function getCookie(name) {
    var match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
    return match ? decodeURIComponent(match[2]) : "";
  }

  /* —— Toasts (reutiliza .messages de base.html) —— */

  function ensureMessagesRegion() {
    var region = qs(".messages");
    if (region) {
      return region;
    }
    region = document.createElement("div");
    region.className = "messages";
    region.setAttribute("role", "region");
    region.setAttribute("aria-label", "Notificaciones");
    region.setAttribute("aria-live", "polite");
    var list = document.createElement("ul");
    list.className = "messages__list";
    region.appendChild(list);
    var main = qs("#main-content");
    if (main && main.parentNode) {
      main.parentNode.insertBefore(region, main);
    } else {
      document.body.insertBefore(region, document.body.firstChild);
    }
    return region;
  }

  function showToast(message, tag) {
    var region = ensureMessagesRegion();
    var list = qs(".messages__list", region) || region;
    var item = document.createElement("li");
    item.className =
      "messages__item messages__item--" + (tag || "info");
    item.setAttribute("role", "status");

    var text = document.createElement("span");
    text.className = "messages__text";
    text.textContent = message;

    var dismiss = document.createElement("button");
    dismiss.type = "button";
    dismiss.className = "messages__dismiss";
    dismiss.setAttribute("data-message-dismiss", "");
    dismiss.setAttribute("aria-label", "Cerrar notificación");
    dismiss.innerHTML = "&times;";

    dismiss.addEventListener("click", function () {
      item.remove();
      if (!list.children.length && region.parentNode) {
        region.remove();
      }
    });

    item.appendChild(text);
    item.appendChild(dismiss);
    list.appendChild(item);

    window.setTimeout(function () {
      if (item.parentNode) {
        item.remove();
        if (!list.children.length && region.parentNode) {
          region.remove();
        }
      }
    }, 5000);
  }

  /* —— Badge del navbar —— */

  function updateCartBadge(count) {
    var badge = qs(".navbar__cart-badge");
    var link = qs(".navbar__cart");
    if (badge) {
      badge.textContent = String(count);
    }
    if (link) {
      var label =
        count === 1
          ? "Carrito de compras, 1 artículo"
          : "Carrito de compras, " + count + " artículos";
      link.setAttribute("aria-label", label);
    }
    var summaryCount = qs("[data-cart-summary-count]");
    if (summaryCount) {
      summaryCount.textContent = String(count);
    }
  }

  function updateCartTotal(formatted) {
    var totalEl = qs("[data-cart-total]");
    if (totalEl && formatted) {
      totalEl.textContent = formatted;
    }
  }

  function updateLineSubtotal(row, formatted) {
    var subtotalEl = qs("[data-line-subtotal]", row);
    if (subtotalEl && formatted) {
      subtotalEl.textContent = formatted;
    }
  }

  function updateQtyDisplay(row, qty) {
    var qtyEl = qs("[data-qty-display]", row);
    if (qtyEl) {
      qtyEl.textContent = String(qty);
    }
    var decreaseBtn = qs("[data-qty-decrease]", row);
    var increaseBtn = qs("[data-qty-increase]", row);
    if (decreaseBtn) {
      decreaseBtn.value = String(Math.max(0, qty - 1));
    }
    if (increaseBtn) {
      increaseBtn.value = String(qty + 1);
    }
  }

  function postForm(url, form, quantity) {
    var body = new FormData();
    body.append("csrfmiddlewaretoken", getCsrfToken(form) || getCookie("csrftoken"));
    if (quantity !== undefined) {
      body.append("quantity", String(quantity));
    }
    return fetch(url, {
      method: "POST",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        Accept: "application/json",
      },
      body: body,
      credentials: "same-origin",
    }).then(function (res) {
      if (!res.ok) {
        throw new Error("Error en la petición");
      }
      return res.json();
    });
  }

  /* —— Detalle: agregar al carrito —— */

  function setAddButtonInCart(btn) {
    if (!btn) return;
    btn.textContent = "Ver en el carrito";
    btn.classList.remove("btn--accent");
    btn.classList.add("btn--primary");
    btn.removeAttribute("data-add-to-cart");
    btn.setAttribute("data-in-cart", "");
    if (btn.tagName === "BUTTON") {
      btn.type = "button";
      btn.addEventListener("click", function () {
        window.location.href = getCartDetailUrl();
      });
    }
  }

  function initAddToCart() {
    var form = qs("[data-add-to-cart-form]");
    if (!form) return;

    var btn = qs("[data-add-to-cart]", form);
    if (btn && btn.hasAttribute("data-in-cart")) {
      btn.addEventListener("click", function () {
        window.location.href = getCartDetailUrl();
      });
    }

    form.addEventListener("submit", function (evt) {
      evt.preventDefault();
      var submitBtn = qs("[data-add-to-cart]", form);
      if (submitBtn && submitBtn.hasAttribute("data-in-cart")) {
        window.location.href = getCartDetailUrl();
        return;
      }

      postForm(form.action, form, 1).then(function (data) {
        if (data.message) {
          var tag = data.message.indexOf("Ya en") === 0 ? "warning" : "success";
          showToast(data.message, tag);
        }
        updateCartBadge(data.count);
        if (data.in_cart && submitBtn) {
          setAddButtonInCart(submitBtn);
        }
      }).catch(function () {
        form.submit();
      });
    });
  }

  /* —— Página carrito: cantidad y eliminar —— */

  function removeCartRow(row) {
    if (!row) return;
    row.remove();
    var list = qs(".cart-list");
    if (list && !list.children.length) {
      window.location.reload();
    }
  }

  function initCartPage() {
    var page = qs("[data-cart-page]");
    if (!page) return;

    qsa("[data-cart-update-form]", page).forEach(function (form) {
      form.addEventListener("submit", function (evt) {
        evt.preventDefault();
        var submitter = evt.submitter;
        var qty = submitter ? parseInt(submitter.value, 10) : 0;
        if (isNaN(qty)) return;

        postForm(form.action, form, qty).then(function (data) {
          updateCartBadge(data.count);
          updateCartTotal(data.total_formatted);
          var row = form.closest("[data-cart-item]");
          if (!data.in_cart) {
            removeCartRow(row);
          } else {
            updateQtyDisplay(row, qty);
            updateLineSubtotal(row, data.line_subtotal_formatted);
          }
        }).catch(function () {
          form.submit();
        });
      });
    });

    qsa("[data-cart-remove-form]", page).forEach(function (form) {
      form.addEventListener("submit", function (evt) {
        evt.preventDefault();
        var btn = qs("[data-remove-item]", form);
        var label = btn ? btn.getAttribute("aria-label") : "Eliminar del carrito";
        var confirmed = window.confirm(
          (label || "Eliminar del carrito") + ".\n\n¿Confirmas que deseas eliminar este artículo?"
        );
        if (!confirmed) return;

        postForm(form.action, form).then(function (data) {
          if (data.message) {
            showToast(data.message, "success");
          }
          updateCartBadge(data.count);
          updateCartTotal(data.total_formatted);
          removeCartRow(form.closest("[data-cart-item]"));
        }).catch(function () {
          if (window.confirm("¿Eliminar este artículo del carrito?")) {
            form.submit();
          }
        });
      });
    });
  }

  function init() {
    initAddToCart();
    initCartPage();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
