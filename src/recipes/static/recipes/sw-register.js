// Registers the service worker (see sw.js) so previously visited pages and the app shell keep
// working without a network connection. Safe to skip entirely in browsers without support.
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js");
  });
}
