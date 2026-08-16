/* Atana IM Tasks service worker — offline cache + background sync hook */
const CACHE = "atana-im-tasks-v214";
const ASSETS = [
  "./",
  "./index.html",
  "./Atana-IM-Tasks.html",
  "./manifest.json",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/icon-512-maskable.png",
  "./screenshots/desktop.png",
  "./screenshots/mobile.png"
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// Network-first for navigations; cache-first for static assets
self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;

  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  // App shell / HTML — network first, fall back to cache (offline)
  if (req.mode === "navigate" || req.headers.get("accept")?.includes("text/html")) {
    e.respondWith(
      fetch(req)
        .then((res) => {
          const clone = res.clone();
          caches.open(CACHE).then((c) => c.put(req, clone));
          return res;
        })
        .catch(() => caches.match("./index.html").then((r) => r || caches.match(req)))
    );
    return;
  }

  // Static assets — cache first
  e.respondWith(
    caches.match(req).then((cached) => {
      if (cached) return cached;
      return fetch(req).then((res) => {
        const clone = res.clone();
        caches.open(CACHE).then((c) => c.put(req, clone));
        return res;
      });
    })
  );
});

// Background Sync: replay queued offline actions when connectivity returns
self.addEventListener("sync", (e) => {
  if (e.tag === "atana-data-sync") {
    e.waitUntil(
      self.clients.matchAll({ type: "window", includeUncontrolled: true }).then((clients) => {
        clients.forEach((c) => c.postMessage({ type: "ATANA_BACKGROUND_SYNC" }));
      })
    );
  }
});

// Periodic Background Sync (where supported) — nudge clients to refresh caches
self.addEventListener("periodicsync", (e) => {
  if (e.tag === "atana-periodic-refresh") {
    e.waitUntil(
      caches.open(CACHE).then((c) =>
        Promise.all(
          ASSETS.map((url) =>
            fetch(url)
              .then((res) => c.put(url, res))
              .catch(() => {})
          )
        )
      )
    );
  }
});

// Optional: allow page to skip waiting / claim
self.addEventListener("message", (e) => {
  if (e.data && e.data.type === "SKIP_WAITING") self.skipWaiting();
});
