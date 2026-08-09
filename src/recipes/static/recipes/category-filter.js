const controls = document.querySelector("[data-category-controls]");

if (controls) {
  const toggles = [...controls.querySelectorAll("[data-category-toggle]")];
  const cards = [...document.querySelectorAll(".category-card[data-category]")];
  const status = controls.querySelector("[data-category-status]");
  const emptyState = document.querySelector("[data-category-empty]");

  const updateCategories = () => {
    const enabled = new Set(
      toggles.filter((toggle) => toggle.checked).map((toggle) => toggle.value),
    );
    let visibleCount = 0;

    for (const card of cards) {
      const visible = enabled.has(card.dataset.category);
      card.hidden = !visible;
      visibleCount += Number(visible);
    }

    emptyState.hidden = visibleCount !== 0;
    status.textContent = `Showing ${visibleCount} of ${cards.length} categories`;
  };

  for (const toggle of toggles) {
    toggle.addEventListener("change", updateCategories);
  }

  updateCategories();
}
