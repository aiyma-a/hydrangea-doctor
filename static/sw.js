// Service worker: makes the app installable and opens instantly by caching the app shell.
// The ML itself needs the internet (it runs on the server).
const CACHE = "hydrangea-v30";
const SHELL = ["./", "index.html", "style.css", "app.js", "manifest.webmanifest", "icons/icon-192.png", "icons/leaves.svg"];

self.addEventListener("install", (e) => e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL.map((u) => new Request(u, { cache: "reload" })))).then(() => self.skipWaiting())));
self.addEventListener("activate", (e) =>
  e.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET" || url.pathname.includes("/api/")) return; // always live
  // Network first so updates show up; fall back to cache when offline.
  e.respondWith(fetch(e.request, { cache: "no-cache" }).then((r) => {
    const copy = r.clone(); caches.open(CACHE).then((c) => c.put(e.request, copy)); return r;
  }).catch(() => caches.match(e.request)));
});
