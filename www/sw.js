/* 离线缓存：App 外壳先用缓存（秒开），数据走网络、失败再用缓存。改了外壳文件记得把 VERSION 加一。 */
var VERSION = "mr-app-v2";
var SHELL = ["./", "./index.html", "./app.css", "./app.js", "./config.js", "./data/snapshot.js", "./manifest.webmanifest",
  "./icons/icon-192.png", "./icons/icon-512.png", "./icons/apple-touch-icon.png"];
self.addEventListener("install", function (e) {
  e.waitUntil(caches.open(VERSION).then(function (c) { return c.addAll(SHELL); }).then(function () { return self.skipWaiting(); }));
});
self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (ks) {
    return Promise.all(ks.filter(function (k) { return k !== VERSION; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});
self.addEventListener("fetch", function (e) {
  var url = new URL(e.request.url);
  if (e.request.method !== "GET") return;                       // AI 请求等不经过缓存
  if (url.pathname.endsWith("/data.json")) {                     // 数据：网络优先
    e.respondWith(fetch(e.request).then(function (r) {
      var copy = r.clone(); caches.open(VERSION).then(function (c) { c.put(e.request, copy); }); return r;
    }).catch(function () { return caches.match(e.request); }));
    return;
  }
  if (url.origin === location.origin) {                          // 外壳：缓存优先
    e.respondWith(caches.match(e.request).then(function (r) { return r || fetch(e.request); }));
  }
});
