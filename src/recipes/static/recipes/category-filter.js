const TOTAL_TIME_STEPS = [15, 30, 45, 60, 90, 120, 180, 240, 360, 480, 720, 1440, Infinity];
const ACTIVE_TIME_STEPS = [10, 15, 20, 30, 45, 60, 90, 120, Infinity];

const formatDuration = (minutes) => {
  if (!Number.isFinite(minutes)) {
    return "Any duration";
  }
  if (minutes < 60) {
    return `${minutes} min or less`;
  }
  if (minutes < 1440) {
    const hours = Math.floor(minutes / 60);
    const remainder = minutes % 60;
    const hourLabel = `${hours} hr${hours === 1 ? "" : "s"}`;
    return remainder === 0
      ? `${hourLabel} or less`
      : `${hourLabel} ${remainder} min or less`;
  }
  const days = Math.floor(minutes / 1440);
  return `${days} day${days === 1 ? "" : "s"} or less`;
};

const controls = document.querySelector("[data-category-controls]");
const tagControls = document.querySelector("[data-tag-controls]");
const timeControls = document.querySelector("[data-time-controls]");

if (controls) {
  const toggles = [...controls.querySelectorAll("[data-category-toggle]")];
  const tagToggles = [...(tagControls?.querySelectorAll("[data-tag-toggle]") ?? [])];
  const cards = [...document.querySelectorAll(".category-card[data-category]")];
  const status = controls.querySelector("[data-category-status]");
  const tagStatus = tagControls?.querySelector("[data-tag-status]") ?? null;
  const categoryEmpty = document.querySelector("[data-category-empty]");
  const timeEmpty = document.querySelector("[data-time-empty]");

  const totalSlider = timeControls?.querySelector("[data-total-time-slider]") ?? null;
  const activeSlider = timeControls?.querySelector("[data-active-time-slider]") ?? null;
  const totalValueOutput = timeControls?.querySelector("[data-total-time-value]") ?? null;
  const activeValueOutput = timeControls?.querySelector("[data-active-time-value]") ?? null;

  const updateSliderDisplay = (slider, steps, output) => {
    if (!slider || !output) {
      return;
    }
    const threshold = steps[Number(slider.value)];
    const label = formatDuration(threshold);
    output.textContent = label;
    slider.setAttribute("aria-valuetext", label);
  };

  const applyFilters = () => {
    const enabledCategories = new Set(
      toggles.filter((toggle) => toggle.checked).map((toggle) => toggle.value),
    );
    const enabledTags = new Set(
      tagToggles.filter((toggle) => toggle.checked).map((toggle) => toggle.value),
    );
    const totalThreshold = totalSlider ? TOTAL_TIME_STEPS[Number(totalSlider.value)] : Infinity;
    const activeThreshold = activeSlider
      ? ACTIVE_TIME_STEPS[Number(activeSlider.value)]
      : Infinity;

    let cardsWithMatches = 0;

    for (const card of cards) {
      const categoryEnabled = enabledCategories.has(card.dataset.category);
      const items = [...card.querySelectorAll("[data-recipe-item]")];
      let matchCount = 0;

      for (const item of items) {
        const totalMinutes = Number(item.dataset.totalMinutes);
        const activeMinutes = Number(item.dataset.activeMinutes);
        const itemTags = item.dataset.tags ? item.dataset.tags.split(",") : [];
        const tagMatches =
          itemTags.length === 0 || itemTags.some((tag) => enabledTags.has(tag));
        const matches =
          totalMinutes <= totalThreshold && activeMinutes <= activeThreshold && tagMatches;
        item.hidden = !matches;
        matchCount += Number(matches);
      }

      const visible = categoryEnabled && matchCount > 0;
      card.hidden = !visible;
      cardsWithMatches += Number(visible);
    }

    status.textContent = `Showing ${enabledCategories.size} of ${cards.length} categories`;
    if (tagStatus) {
      tagStatus.textContent = `Showing ${enabledTags.size} of ${tagToggles.length} tags`;
    }
    categoryEmpty.hidden = enabledCategories.size !== 0;
    timeEmpty.hidden = enabledCategories.size === 0 || cardsWithMatches !== 0;
  };

  for (const toggle of toggles) {
    toggle.addEventListener("change", applyFilters);
  }

  for (const toggle of tagToggles) {
    toggle.addEventListener("change", applyFilters);
  }

  if (totalSlider) {
    totalSlider.addEventListener("input", () => {
      updateSliderDisplay(totalSlider, TOTAL_TIME_STEPS, totalValueOutput);
      applyFilters();
    });
    updateSliderDisplay(totalSlider, TOTAL_TIME_STEPS, totalValueOutput);
  }

  if (activeSlider) {
    activeSlider.addEventListener("input", () => {
      updateSliderDisplay(activeSlider, ACTIVE_TIME_STEPS, activeValueOutput);
      applyFilters();
    });
    updateSliderDisplay(activeSlider, ACTIVE_TIME_STEPS, activeValueOutput);
  }

  applyFilters();
}
