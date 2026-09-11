// Lets you cross off method steps as you cook. State lives only in the DOM (no
// localStorage/sessionStorage), so it intentionally resets whenever the page is
// reloaded or navigated away from, ready for a clean run through the recipe next time.
const progressContainers = document.querySelectorAll("[data-method-progress]");

for (const container of progressContainers) {
  const toggles = [...container.querySelectorAll("[data-method-step-toggle]")];
  const status = container.querySelector("[data-method-status]");
  const resetButton = container.querySelector("[data-method-reset]");

  if (toggles.length === 0) {
    continue;
  }

  const completedCount = () => toggles.filter((toggle) => toggle.checked).length;

  const updateStatus = () => {
    const completed = completedCount();

    if (status) {
      status.textContent =
        completed === toggles.length
          ? `All ${toggles.length} steps completed`
          : `${completed} of ${toggles.length} steps completed`;
    }

    if (resetButton) {
      resetButton.hidden = completed === 0;
    }
  };

  for (const toggle of toggles) {
    toggle.addEventListener("change", updateStatus);
  }

  if (resetButton) {
    resetButton.addEventListener("click", () => {
      for (const toggle of toggles) {
        toggle.checked = false;
      }
      updateStatus();
    });
  }

  updateStatus();
}
