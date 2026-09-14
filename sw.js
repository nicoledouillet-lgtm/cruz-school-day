/* Offline support. Cruz's phone loses signal on the bus and at school, so the
   page has to open with no network at all and still show the right week.

   Shell (html/icons/manifest): serve from cache instantly, refresh in the
   background — a deploy shows up on the next launch.
   week.json: try the network first so a Sunday refresh lands immediately,
   fall back to the last saved copy when there's nothing to reach. */

var CACHE = "cruz-school-day-v13";
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
  /* Deliberately not cache.addAll(SHELL). That goes through the HTTP cache and
     the CDN edge, and GitHub Pages serves HTML with a ten-minute max-age — so
     an install moments after a deploy could bake the PREVIOUS app into the new
     cache, and it would stay there until something else evicted it. Observed,
     not theoretical: v12 installed with v11's index.html.

     cache:"reload" bypasses the browser's HTTP cache; the ?v= query makes it a
     different URL to the CDN, forcing a trip to the origin. The response is
     stored under the clean URL so lookups still match. */
  e.waitUntil(
    caches.open(CACHE).then(function (c) {
      return Promise.all(SHELL.map(function (url) {
        return fetch(url + "?v=" + CACHE, { cache: "reload" })
          .then(function (res) {
            if (!res || !res.ok) throw new Error("precache failed: " + url);
            return c.put(url, res);
          });
      }));
    }).then(function () { return self.skipWaiting(); })
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
