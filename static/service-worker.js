const CACHE_NAME = "wes-pwa-v2";

const urlsToCache = [
  "/",
  "/signin",
  "/signup",

  "/supervisordashboard",
  "/mentordashboard",
  "/menteedashboard",

  "/profile",

  "/supervisor_tasks",
  "/mentor_tasks",
  "/mentee_tasks",

  "/supervisor_calendar",
  "/mentor_calendar",
  "/mentee_calendar",

  "/static/img/logo.jpg",
  "/static/manifest.json",
  "/static/service-worker.js",
];

// Install SW
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
  );
});

// Fetch (offline first)
self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});
