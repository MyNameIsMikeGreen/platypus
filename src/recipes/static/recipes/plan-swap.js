// Lets you swap a single meal-plan recipe for another from the same category, so you can keep
// the recipes you like and re-roll only the rest. The server chooses the replacement and renders
// both its row and the rebuilt shared shopping list; they're swapped into the page in place,
// without a reload, so your place on the page, the rest of the plan and your shopping-list
// selections all stay put.
const plan = document.querySelector("[data-plan]");
// Must match INGREDIENT_EXPORT_REFRESH_EVENT in ingredient-export.js.
const SHOPPING_LIST_REFRESH_EVENT = "ingredient-export:refresh";

if (plan) {
  const swapUrl = plan.dataset.planSwapUrl;
  const status = plan.querySelector("[data-plan-swap-status]");
  // Recipes swapped out of each category, so repeated swaps work through every alternative
  // before any of them is offered again.
  const rejectedIdsByCategory = new Map();
  // Swaps run one at a time, as each needs the plan left by the previous one to stay unique.
  let pendingSwaps = Promise.resolve();

  const plannedIds = () =>
    [...plan.querySelectorAll("[data-plan-slot]")].map((slot) => slot.dataset.recipeId);

  // Ingredients keep whatever selection they already had; only newly added ones start selected.
  const replaceShoppingList = (incoming) => {
    const current = plan.querySelector("[data-ingredient-export]");
    if (!current || !incoming) {
      return;
    }
    const currentChecklist = current.querySelector(".ingredient-checklist");
    const incomingChecklist = incoming.querySelector(".ingredient-checklist");
    const selectionByName = new Map(
      [...currentChecklist.querySelectorAll("[data-ingredient-toggle]")].map((toggle) => [
        toggle.dataset.ingredientName.toLowerCase(),
        toggle.checked,
      ]),
    );
    for (const toggle of incomingChecklist.querySelectorAll("[data-ingredient-toggle]")) {
      toggle.checked = selectionByName.get(toggle.dataset.ingredientName.toLowerCase()) ?? true;
    }
    const scrollTop = currentChecklist.scrollTop;
    currentChecklist.replaceWith(incomingChecklist);
    incomingChecklist.scrollTop = scrollTop;
    current.querySelector("[data-ingredient-count]").textContent =
      incoming.querySelector("[data-ingredient-count]").textContent;
    current.dispatchEvent(new CustomEvent(SHOPPING_LIST_REFRESH_EVENT));
  };

  const swap = async (button) => {
    const slot = button.closest("[data-plan-slot]");
    const category = slot.closest("[data-plan-group]").dataset.planGroup;
    const rejectedIds = rejectedIdsByCategory.get(category) ?? new Set();
    const outgoingId = slot.dataset.recipeId;
    const outgoingTitle = slot.querySelector("a").textContent;
    const params = new URLSearchParams();
    for (const id of plannedIds()) {
      params.append("plan", id);
    }
    params.append("swap", outgoingId);
    for (const id of rejectedIds) {
      params.append("rejected", id);
    }

    try {
      const response = await fetch(`${swapUrl}?${params}`);
      if (!response.ok) {
        throw new Error(`Swap failed with status ${response.status}`);
      }
      const fragment = new DOMParser().parseFromString(await response.text(), "text/html");
      const incomingSlot = fragment.querySelector("[data-plan-slot]");
      const incomingId = incomingSlot.dataset.recipeId;

      // Every alternative has now been offered, so start working through them again.
      if (rejectedIds.has(incomingId)) {
        rejectedIds.clear();
      }
      rejectedIds.add(outgoingId);
      rejectedIdsByCategory.set(category, rejectedIds);

      // Keep the swapped row exactly where it was on screen, even if content above it (such as
      // an open shopping list) changes height.
      const hadFocus = document.activeElement === button;
      const topBefore = slot.getBoundingClientRect().top;
      slot.replaceWith(incomingSlot);
      replaceShoppingList(fragment.querySelector("[data-ingredient-export]"));
      window.scrollBy(0, incomingSlot.getBoundingClientRect().top - topBefore);

      if (hadFocus) {
        incomingSlot.querySelector("[data-plan-swap]")?.focus({ preventScroll: true });
      }
      status.textContent = `Swapped ${outgoingTitle} for ${incomingSlot.querySelector("a").textContent}.`;
    } catch {
      button.removeAttribute("aria-disabled");
      button.removeAttribute("aria-busy");
      status.textContent = `Couldn't swap ${outgoingTitle}. Please try again.`;
    }
  };

  plan.addEventListener("click", (event) => {
    const button = event.target.closest("[data-plan-swap]");
    // Ignores buttons that are busy, or that have nothing to swap in. aria-disabled (rather than
    // disabled) keeps keyboard focus on the button while it's busy.
    if (!button || button.getAttribute("aria-disabled") === "true") {
      return;
    }
    button.setAttribute("aria-disabled", "true");
    button.setAttribute("aria-busy", "true");
    pendingSwaps = pendingSwaps.then(() => swap(button));
  });
}
