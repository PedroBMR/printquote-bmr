/**
 * Service worker do PrintQuote by BMR (versão web).
 * Deixa o app instalável e funcional offline: pré-cacheia os arquivos
 * essenciais e serve tudo do cache quando não há rede. Bump em CACHE
 * a cada release pra invalidar o cache antigo.
 */
const CACHE = "printquote-v1";

const ASSETS = [
  "./",
  "./index.html",
  "./manifest.json",
  "./css/style.css",
  "./js/core.js",
  "./js/store.js",
  "./js/app.js",
  "./assets/favicon-32.png",
  "./assets/icon-256.png",
  "./assets/icon-512.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE)
      .then((cache) => cache.addAll(ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;

  const url = new URL(req.url);
  // Deixa recursos de outra origem (ex.: fontes do Google) passarem direto.
  if (url.origin !== self.location.origin) return;

  // Navegações: tenta a rede (pega atualizações) e cai pro index em cache offline.
  if (req.mode === "navigate") {
    event.respondWith(fetch(req).catch(() => caches.match("./index.html")));
    return;
  }

  // Demais assets: stale-while-revalidate (responde do cache, atualiza em segundo plano).
  event.respondWith(
    caches.match(req).then((cached) => {
      const network = fetch(req)
        .then((res) => {
          if (res && res.status === 200) {
            const copy = res.clone();
            caches.open(CACHE).then((cache) => cache.put(req, copy));
          }
          return res;
        })
        .catch(() => cached);
      return cached || network;
    })
  );
});
