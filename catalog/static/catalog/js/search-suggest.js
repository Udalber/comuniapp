(function () {
  "use strict";

  var MIN_CHARS = 3;
  var DEBOUNCE_MS = 300;
  var suggestUrl = document.body.getAttribute("data-suggest-url");
  if (!suggestUrl) return;

  var searchInputs = document.querySelectorAll(
    '#navbar-search, #hero-search, input[name="q"][type="search"]'
  );

  searchInputs.forEach(function (input) {
    var wrapper = input.closest("form");
    if (!wrapper) return;

    wrapper.classList.add("search-suggest");
    var list = document.createElement("ul");
    list.className = "search-suggest__list";
    list.setAttribute("role", "listbox");
    list.hidden = true;
    wrapper.appendChild(list);

    var debounceTimer = null;
    var activeIndex = -1;

    function clearSuggestions() {
      list.innerHTML = "";
      list.hidden = true;
      activeIndex = -1;
    }

    function renderSuggestions(results) {
      list.innerHTML = "";
      if (!results.length) {
        list.hidden = true;
        return;
      }

      results.forEach(function (item, index) {
        var li = document.createElement("li");
        li.className = "search-suggest__item";
        li.setAttribute("role", "option");
        li.id = "suggest-option-" + index;

        var link = document.createElement("a");
        link.href = item.url;
        link.innerHTML =
          '<span class="search-suggest__title">' +
          escapeHtml(item.title) +
          "</span><br>" +
          '<span class="search-suggest__author">' +
          escapeHtml(item.author) +
          "</span>";
        li.appendChild(link);
        list.appendChild(li);
      });

      list.hidden = false;
    }

    function escapeHtml(text) {
      var div = document.createElement("div");
      div.textContent = text;
      return div.innerHTML;
    }

    function fetchSuggestions(query) {
      fetch(suggestUrl + "?q=" + encodeURIComponent(query))
        .then(function (response) {
          return response.json();
        })
        .then(function (data) {
          renderSuggestions(data.results || []);
        })
        .catch(function () {
          clearSuggestions();
        });
    }

    input.addEventListener("input", function () {
      var query = input.value.trim();
      clearTimeout(debounceTimer);

      if (query.length < MIN_CHARS) {
        clearSuggestions();
        return;
      }

      debounceTimer = setTimeout(function () {
        fetchSuggestions(query);
      }, DEBOUNCE_MS);
    });

    input.addEventListener("keydown", function (event) {
      var items = list.querySelectorAll(".search-suggest__item a");
      if (!items.length || list.hidden) return;

      if (event.key === "ArrowDown") {
        event.preventDefault();
        activeIndex = Math.min(activeIndex + 1, items.length - 1);
        items[activeIndex].focus();
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        activeIndex = Math.max(activeIndex - 1, 0);
        items[activeIndex].focus();
      } else if (event.key === "Escape") {
        clearSuggestions();
      }
    });

    document.addEventListener("click", function (event) {
      if (!wrapper.contains(event.target)) {
        clearSuggestions();
      }
    });
  });
})();
