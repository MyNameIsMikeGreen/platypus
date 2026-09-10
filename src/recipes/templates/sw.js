{% load static %}// Platypus service worker: caches the app shell and visited pages so the recipe collection
// keeps working when the LAN connection to the server is briefly unavailable.
//
// Bump CACHE_VERSION whenever the precached asset list changes below, so returning visitors
// pick up the new set instead of keeping a stale cache around forever.
const CACHE_VERSION = "platypus-1";

const PRECACHE_URLS = [
  "{% url 'recipes:index' %}",
  "{% url 'recipes:planner' %}",
  "{% url 'recipes:about' %}",
  "{% url 'recipes:offline' %}",
  "{% url 'recipes:manifest' %}",
  "{% static 'recipes/site.css' %}",
  "{% static 'recipes/theme-toggle.js' %}",
  "{% static 'recipes/category-filter.js' %}",
  "{% static 'recipes/search-autocomplete.js' %}",
  "{% static 'recipes/ingredient-export.js' %}",
  "{% static 'recipes/gallery-lightbox.js' %}",
  "{% static 'recipes/planner.js' %}",
  "{% static 'recipes/favicon.svg' %}",
  "{% static 'recipes/apple-touch-icon.png' %}",
  "{% static 'recipes/icon-192.png' %}",
  "{% static 'recipes/icon-512.png' %}",
];

const OFFLINE_URL = "{% url 'recipes:offline' %}";

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(CACHE_VERSION)
      .then((cache) => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(keys.filter((key) => key !== CACHE_VERSION).map((key) => caches.delete(key)))
      )
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET" || new URL(request.url).origin !== self.location.origin) {
    return; // Only handle same-origin GETs; leave everything else (e.g. recipe photos) to the browser.
  }

  if (request.mode === "navigate") {
    event.respondWith(networkFirst(request));
    return;
  }

  event.respondWith(cacheFirst(request));
});

// Static assets rarely change once deployed, so serve them straight from the cache when present
// and only fall back to the network for anything not yet cached.
async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) {
    return cached;
  }
  try {
    const response = await fetch(request);
    await cachePut(request, response);
    return response;
  } catch {
    return Response.error();
  }
}

// Pages change more often, so prefer a fresh network copy and keep the cache updated with the
// latest visited version; fall back to the cache, then the offline page, when the network fails.
async function networkFirst(request) {
  try {
    const response = await fetch(request);
    await cachePut(request, response);
    return response;
  } catch {
    const cached = await caches.match(request);
    return cached || caches.match(OFFLINE_URL);
  }
}

async function cachePut(request, response) {
  if (response.ok) {
    const cache = await caches.open(CACHE_VERSION);
    await cache.put(request, response.clone());
  }
}
