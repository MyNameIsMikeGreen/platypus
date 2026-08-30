const exportContainers = document.querySelectorAll("[data-ingredient-export]");
const COPY_LABEL_RESET_DELAY_MS = 2000;

const copyText = async (text) => {
  if (navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      // Fall through to the execCommand fallback below.
    }
  }
  return false;
};

for (const container of exportContainers) {
  const toggles = [...container.querySelectorAll("[data-ingredient-toggle]")];
  const clearButton = container.querySelector("[data-ingredient-clear]");
  const copyButton = container.querySelector("[data-ingredient-copy]");
  const status = container.querySelector("[data-ingredient-status]");
  const copyStatus = container.querySelector("[data-ingredient-copy-status]");
  const fallbackTextarea = container.querySelector("[data-ingredient-export-text]");

  if (toggles.length === 0 || !copyButton) {
    continue;
  }

  const defaultCopyLabel = copyButton.textContent;
  let copyLabelResetId = null;

  const selectedToggles = () => toggles.filter((toggle) => toggle.checked);

  const updateStatus = () => {
    const selectedCount = selectedToggles().length;
    if (status) {
      status.textContent = `${selectedCount} of ${toggles.length} ingredients selected`;
    }
    if (clearButton) {
      clearButton.textContent = selectedCount > 0 ? "Clear all" : "Select all";
    }
  };

  // Briefly swaps the button's own label (e.g. to "Copied!") so clicking it gives immediate,
  // in-place acknowledgement without the layout shift of showing separate text below it. The
  // full message is still announced to screen readers via the hidden live region.
  const flashCopyButtonLabel = (label, announcement) => {
    if (copyLabelResetId) {
      clearTimeout(copyLabelResetId);
    }
    copyButton.textContent = label;
    if (copyStatus) {
      copyStatus.textContent = announcement;
    }
    copyLabelResetId = setTimeout(() => {
      copyButton.textContent = defaultCopyLabel;
      copyLabelResetId = null;
    }, COPY_LABEL_RESET_DELAY_MS);
  };

  for (const toggle of toggles) {
    toggle.addEventListener("change", updateStatus);
  }

  if (clearButton) {
    clearButton.addEventListener("click", () => {
      const shouldSelectAll = clearButton.textContent === "Select all";
      for (const toggle of toggles) {
        toggle.checked = shouldSelectAll;
      }
      updateStatus();
    });
  }

  copyButton.addEventListener("click", async () => {
    const names = selectedToggles().map((toggle) => toggle.dataset.ingredientName);

    if (fallbackTextarea) {
      fallbackTextarea.classList.remove("ingredient-export-text-visible");
      fallbackTextarea.classList.add("visually-hidden");
    }

    if (names.length === 0) {
      flashCopyButtonLabel("Select an ingredient", "Select at least one ingredient to copy.");
      return;
    }

    const text = names.join("\n");
    const copied = await copyText(text);
    if (copied) {
      flashCopyButtonLabel(
        "Copied!",
        `Copied ${names.length} ingredient${names.length === 1 ? "" : "s"} to your clipboard.`,
      );
      return;
    }

    if (fallbackTextarea) {
      fallbackTextarea.value = text;
      fallbackTextarea.classList.remove("visually-hidden");
      fallbackTextarea.classList.add("ingredient-export-text-visible");
      fallbackTextarea.removeAttribute("aria-hidden");
      fallbackTextarea.focus();
      fallbackTextarea.select();
      flashCopyButtonLabel(
        "Copy manually below",
        "Couldn't copy automatically — the list is selected below, so press Ctrl/Cmd+C to copy it.",
      );
      return;
    }

    flashCopyButtonLabel("Couldn't copy", "Couldn't copy to your clipboard.");
  });

  updateStatus();
}
