const search = document.querySelector("[data-search-combobox]");

if (search) {
  const input = search.querySelector("input");
  const category = search.closest("form").querySelector("[data-search-category]");
  const suggestions = search.querySelector("[role='listbox']");
  const status = search.querySelector("[data-search-status]");
  const recipes = [...document.querySelectorAll("[data-search-option]")].map((option) => ({
    category: option.dataset.category,
    title: option.value,
    url: option.dataset.url,
  }));
  let matches = [];
  let activeIndex = -1;

  input.removeAttribute("list");

  const closeSuggestions = () => {
    suggestions.hidden = true;
    suggestions.replaceChildren();
    input.setAttribute("aria-expanded", "false");
    input.removeAttribute("aria-activedescendant");
    activeIndex = -1;
  };

  const activateSuggestion = (index) => {
    const options = [...suggestions.querySelectorAll("[role='option']")];
    if (!options.length) {
      return;
    }

    activeIndex = (index + options.length) % options.length;
    for (const [optionIndex, option] of options.entries()) {
      option.setAttribute("aria-selected", String(optionIndex === activeIndex));
    }
    input.setAttribute("aria-activedescendant", options[activeIndex].id);
    options[activeIndex].scrollIntoView({ block: "nearest" });
  };

  const renderSuggestions = () => {
    const query = input.value.trim().toLocaleLowerCase();
    closeSuggestions();
    if (!query) {
      status.textContent = "";
      return;
    }

    matches = recipes
      .filter(
        (recipe) =>
          (!category.value || recipe.category === category.value) &&
          recipe.title.toLocaleLowerCase().includes(query),
      )
      .slice(0, 8);
    if (!matches.length) {
      status.textContent = "No recipe suggestions";
      return;
    }

    const fragment = document.createDocumentFragment();
    for (const [index, recipe] of matches.entries()) {
      const option = document.createElement("li");
      const link = document.createElement("a");
      option.id = `recipe-suggestion-${index}`;
      option.role = "option";
      option.dataset.category = recipe.category;
      option.setAttribute("aria-selected", "false");
      link.href = recipe.url;
      link.tabIndex = -1;
      link.textContent = recipe.title;
      option.addEventListener("pointerenter", () => activateSuggestion(index));
      option.append(link);
      fragment.append(option);
    }

    suggestions.append(fragment);
    suggestions.hidden = false;
    input.setAttribute("aria-expanded", "true");
    status.textContent = `${matches.length} recipe suggestions available`;
  };

  input.addEventListener("input", renderSuggestions);
  input.addEventListener("focus", renderSuggestions);
  category.addEventListener("change", renderSuggestions);
  input.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeSuggestions();
      return;
    }
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      if (suggestions.hidden) {
        renderSuggestions();
      }
      activateSuggestion(activeIndex + (event.key === "ArrowDown" ? 1 : -1));
      return;
    }
    if (event.key === "Enter" && activeIndex >= 0) {
      event.preventDefault();
      window.location.assign(matches[activeIndex].url);
    }
  });

  document.addEventListener("pointerdown", (event) => {
    if (!search.contains(event.target)) {
      closeSuggestions();
    }
  });
}
