// Caches the app so it opens instantly and works with spotty park Wi-Fi. Wait times always go to the network.
const CACHE = "qc-v56";
const SHELL = ["./", "index.html", "manifest.json", "icon-192.png", "icon-512.png", "icon-180.png", "leaflet.js", "leaflet.css"];
self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL.map(u => new Request(u, {cache:"reload"}))))); self.skipWaiting(); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))); self.clients.claim(); });
self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if (url.origin !== location.origin || e.request.method !== "GET") return;   // live waits + fonts: network only
  // newest copy from GitHub when the signal is good; if it's slow (3 s) or fails, open the saved copy instead.
  // Only good answers are saved, so a half-finished deploy can never replace the working copy.
  const net = fetch(e.request, {cache:"no-cache"}).then(r => {
    if (r.ok && r.type === "basic"){ const copy = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); }
    return r;
  });
  const saved = () => caches.match(e.request).then(r => r || caches.match("index.html"));
  e.respondWith(new Promise(resolve => {
    let done = false;
    const finish = r => { if (!done && r){ done = true; resolve(r); } };
    const timer = setTimeout(() => saved().then(r => { if (r) finish(r); }), 3000);
    net.then(r => { clearTimeout(timer); if (r.ok) finish(r); else saved().then(c => finish(c || r)); })
       .catch(() => { clearTimeout(timer); saved().then(r => finish(r || Response.error())); });
  }));
});
// tapping a show alert opens the app
self.addEventListener("notificationclick", e => {
  e.notification.close();
  e.waitUntil(self.clients.matchAll({type:"window", includeUncontrolled:true}).then(cs => cs.length ? cs[0].focus() : self.clients.openWindow("./")));
});
