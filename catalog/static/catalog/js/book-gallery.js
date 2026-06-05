/**
 * ComuniApp — Galería del detalle de libro (RF-006)
 * Miniaturas, imagen principal y visor modal accesible.
 */
(function () {
  "use strict";

  var gallery = document.querySelector("[data-book-gallery]");
  if (!gallery) {
    return;
  }

  var mainFrame = document.getElementById("book-gallery-main-frame");
  var mainTrigger = document.getElementById("book-gallery-main-trigger");
  var thumbs = gallery.querySelectorAll("[data-gallery-thumb]");
  var modal = document.getElementById("book-gallery-modal");
  var modalTitle = document.getElementById("book-gallery-modal-title");
  var modalBody = document.getElementById("book-gallery-modal-body");
  var modalCloseButtons = modal
    ? modal.querySelectorAll("[data-gallery-close]")
    : [];
  var lastFocusedElement = null;

  var PLACEHOLDER_SVG =
    '<svg class="book-detail__placeholder-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">' +
    '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>' +
    '<path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>' +
    "</svg>";

  function buildPlaceholderMarkup(caption) {
    return (
      '<div class="book-detail__placeholder" aria-hidden="true">' +
      PLACEHOLDER_SVG +
      '<span class="book-detail__placeholder-label">' +
      escapeHtml(caption) +
      "</span></div>"
    );
  }

  function buildImageMarkup(url, caption, bookTitle) {
    var alt = caption + " de " + bookTitle;
    return (
      '<img class="book-detail__main-img" id="book-gallery-main-img" src="' +
      escapeHtml(url) +
      '" alt="' +
      escapeHtml(alt) +
      '" width="480" height="640">'
    );
  }

  function escapeHtml(text) {
    var div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  function getBookTitle() {
    var titleEl = document.querySelector(".book-detail__title");
    return titleEl ? titleEl.textContent.trim() : "libro";
  }

  function setActiveThumb(activeThumb) {
    thumbs.forEach(function (thumb) {
      var isActive = thumb === activeThumb;
      thumb.classList.toggle("is-active", isActive);
      if (isActive) {
        thumb.setAttribute("aria-current", "true");
      } else {
        thumb.removeAttribute("aria-current");
      }
    });
  }

  function updateMainImage(thumb) {
    var url = thumb.getAttribute("data-image-url");
    var caption = thumb.getAttribute("data-caption") || "";
    var isPlaceholder = thumb.getAttribute("data-is-placeholder") === "true";
    var bookTitle = getBookTitle();

    if (isPlaceholder || !url) {
      mainFrame.innerHTML = buildPlaceholderMarkup(caption);
    } else {
      mainFrame.innerHTML = buildImageMarkup(url, caption, bookTitle);
    }

    if (mainTrigger) {
      mainTrigger.setAttribute(
        "aria-label",
        "Ampliar imagen: " + caption
      );
    }

    setActiveThumb(thumb);
  }

  function updateModalContent(thumb) {
    if (!modalBody || !modalTitle) {
      return;
    }

    var url = thumb.getAttribute("data-image-url");
    var caption = thumb.getAttribute("data-caption") || "";
    var isPlaceholder = thumb.getAttribute("data-is-placeholder") === "true";
    var bookTitle = getBookTitle();

    modalTitle.textContent = caption;

    if (isPlaceholder || !url) {
      modalBody.innerHTML =
        '<div class="book-detail__modal-placeholder" aria-hidden="true">' +
        PLACEHOLDER_SVG +
        '<span class="book-detail__placeholder-label">' +
        escapeHtml(caption) +
        "</span></div>";
    } else {
      var alt = caption + " de " + bookTitle;
      modalBody.innerHTML =
        '<img class="book-detail__modal-img" id="book-gallery-modal-img" src="' +
        escapeHtml(url) +
        '" alt="' +
        escapeHtml(alt) +
        '">';
    }
  }

  function getActiveThumb() {
    return gallery.querySelector("[data-gallery-thumb].is-active");
  }

  function openModal() {
    if (!modal) {
      return;
    }

    var activeThumb = getActiveThumb() || thumbs[0];
    if (activeThumb) {
      updateModalContent(activeThumb);
    }

    lastFocusedElement = document.activeElement;
    modal.removeAttribute("hidden");
    document.body.style.overflow = "hidden";

    var closeBtn = modal.querySelector(".book-detail__modal-close");
    if (closeBtn) {
      closeBtn.focus();
    }
  }

  function closeModal() {
    if (!modal || modal.hasAttribute("hidden")) {
      return;
    }

    modal.setAttribute("hidden", "");
    document.body.style.overflow = "";

    if (lastFocusedElement && typeof lastFocusedElement.focus === "function") {
      lastFocusedElement.focus();
    }
    lastFocusedElement = null;
  }

  thumbs.forEach(function (thumb) {
    thumb.addEventListener("click", function () {
      updateMainImage(thumb);
    });
  });

  if (mainTrigger) {
    mainTrigger.addEventListener("click", openModal);
  }

  modalCloseButtons.forEach(function (btn) {
    btn.addEventListener("click", closeModal);
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && modal && !modal.hasAttribute("hidden")) {
      closeModal();
    }
  });
})();
