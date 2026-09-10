// Applies the site theme (light/dark) as early as possible, before first paint, to avoid a
// flash of the wrong theme. Loaded synchronously (no `defer`) in `<head>`, before `<body>` is
// parsed, so it must not assume any element other than `<html>` exists yet.
(() => {
  "use strict";

  const STORAGE_KEY = "platypus-theme";
  const LIGHT_COLOR = "#f7f4eb";
  const DARK_COLOR = "#12150e";
  const root = document.documentElement;

  function storedTheme() {
    try {
      const value = window.localStorage.getItem(STORAGE_KEY);
      return value === "dark" || value === "light" ? value : null;
    } catch {
      return null; // Storage may be unavailable, e.g. in private browsing.
    }
  }

  function systemPrefersDark() {
    return (
      typeof window.matchMedia === "function" &&
      window.matchMedia("(prefers-color-scheme: dark)").matches
    );
  }

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    const meta = document.querySelector("[data-theme-color]");
    if (meta) {
      meta.setAttribute("content", theme === "dark" ? DARK_COLOR : LIGHT_COLOR);
    }
  }

  function updateToggle(theme) {
    const toggle = document.querySelector("[data-theme-toggle]");
    if (!toggle) {
      return;
    }
    const isDark = theme === "dark";
    toggle.setAttribute("aria-pressed", String(isDark));
    const icon = toggle.querySelector("[data-theme-icon]");
    if (icon) {
      icon.textContent = isDark ? "☀️" : "🌙";
    }
    const label = toggle.querySelector("[data-theme-label]");
    if (label) {
      label.textContent = isDark ? "Switch to light mode" : "Switch to dark mode";
    }
  }

  let theme = storedTheme() ?? (systemPrefersDark() ? "dark" : "light");
  applyTheme(theme);

  document.addEventListener("DOMContentLoaded", () => {
    updateToggle(theme);
    document.addEventListener("click", (event) => {
      const toggle = event.target.closest("[data-theme-toggle]");
      if (!toggle) {
        return;
      }
      theme = theme === "dark" ? "light" : "dark";
      try {
        window.localStorage.setItem(STORAGE_KEY, theme);
      } catch {
        // Ignore storage errors, e.g. in private browsing.
      }
      applyTheme(theme);
      updateToggle(theme);
    });
  });
})();
