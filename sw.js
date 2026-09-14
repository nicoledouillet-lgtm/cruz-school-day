/* Offline support. Cruz's phone loses signal on the bus and at school, so the
   page has to open with no network at all and still show the right week.

   Shell (html/icons/manifest): serve from cache instantly, refresh in the
   background — a deploy shows up on the next launch.
   week.json: try the network first so a Sunday refresh lands immediately,
   fall back to the last saved copy when there's nothing to reach. */

var CACHE = "cruz-school-day-v10";
var SHELL = [
  "./",
  "./index.html",
  "./week.json",
  "./manifest.webmanifest",
  "./icon-180.png",
  "./icon-192.png",
  "./icon-512.png"
];

self.addEventListener("install", function (e) {
  e.waitUntil(
    caches.open(CACHE)
      .then(function (c) { return c.addAll(SHELL); })
      .then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener("activate", function (e) {
  e.waitUntil(
    caches.keys()
      .then(function (keys) {
        return Promise.all(keys.map(function (k) {
          return k === CACHE ? null : caches.delete(k);
        }));
      })
      .then(function () { return self.clients.claim(); })
  );
});

self.addEventListener("fetch", function (e) {
  var req = e.request;
  if (req.method !== "GET") return;

  var url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  var path = url.pathname.split("/").pop();

  /* This week's homework: freshest wins, cache is the safety net. */
  if (path === "week.json") {
    e.respondWith(
      fetch(req)
        .then(function (res) {
          if (res && res.ok) {
            var copy = res.clone();
            caches.open(CACHE).then(function (c) { c.put("./week.json", copy); });
          }
          return res;
        })
        .catch(function () {
          return caches.match("./week.json", { ignoreSearch: true });
        })
    );
    return;
  }

  /* Everything else: instant from cache, quietly updated for next time. */
  e.respondWith(
    caches.match(req, { ignoreSearch: true }).then(function (hit) {
      var live = fetch(req).then(function (res) {
        if (res && res.ok) {
          var copy = res.clone();
          caches.open(CACHE).then(function (c) { c.put(req, copy); });
        }
        return res;
      }).catch(function () { return hit; });

      return hit || live;
    })
  );
});
