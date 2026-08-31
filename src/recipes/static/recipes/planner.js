const form = document.querySelector("[data-quantity-form]");

if (form) {
  const inputs = [...form.querySelectorAll("[data-quantity-input]")];
  const total = form.querySelector("[data-quantity-total]");

  const updateTotal = () => {
    const sum = inputs.reduce((acc, input) => acc + (Number(input.value) || 0), 0);
    total.textContent =
      sum === 0 ? "No recipes selected yet" : `${sum} recipe${sum === 1 ? "" : "s"} selected`;
  };

  for (const button of form.querySelectorAll("[data-quantity-step]")) {
    button.addEventListener("click", () => {
      const input = button.parentElement.querySelector("[data-quantity-input]");
      const step = Number(button.dataset.quantityStep);
      const min = Number(input.min || 0);
      const max = Number(input.max || Infinity);
      const next = (Number(input.value) || 0) + step;
      input.value = Math.min(max, Math.max(min, next));
      updateTotal();
    });
  }

  for (const input of inputs) {
    input.addEventListener("input", updateTotal);
  }

  updateTotal();
}
