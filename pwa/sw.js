// ═══════════════════════════════════════════════════════════════════
//  SAFER-VLA Service Worker — Offline-First PWA
// ═══════════════════════════════════════════════════════════════════
//
//  Caching strategy:
//    - PRECACHE:  Command Center HTML, Three.js, fonts (install-time)
//    - RUNTIME:   Network-first for API, stale-while-revalidate for assets
//    - OFFLINE:   Serve cached Command Center when offline
//
//  Version: 1.0.0 — auto-updates on new deploy
// ═══════════════════════════════════════════════════════════════════

const CACHE_NAME = 'safer-vla-v1';
const RUNTIME_CACHE = 'safer-vla-runtime-v1';

// Assets to precache at install time
const PRECACHE_URLS = [
  '/fastbot_command_center.html',
  '/pwa/manifest.json',
  '/pwa/icons/icon-192.png',
  '/pwa/icons/icon-512.png',
  '/pwa/offline.html',
  // Three.js (CDN — cached on first load)
  'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js',
  'https://cdn.jsdelivr.net/gh/mrdoob/three.js@r128/examples/js/loaders/STLLoader.js',
  // Fonts
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap',
];

// ─── Install ──────────────────────────────────────────────────────
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[SW] Precaching app shell');
        return cache.addAll(PRECACHE_URLS.map(url => {
          return new Request(url, { mode: url.startsWith('http') ? 'cors' : 'same-origin' });
        }));
      })
      .then(() => self.skipWaiting())
      .catch(err => {
        console.warn('[SW] Precache partial failure (CDN assets may fail offline):', err);
        return self.skipWaiting();
      })
  );
});

// ─── Activate ─────────────────────────────────────────────────────
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys
          .filter(key => key !== CACHE_NAME && key !== RUNTIME_CACHE)
          .map(key => {
            console.log('[SW] Removing old cache:', key);
            return caches.delete(key);
          })
      ))
      .then(() => self.clients.claim())
  );
});

// ─── Fetch ────────────────────────────────────────────────────────
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // Skip non-GET requests
  if (event.request.method !== 'GET') return;

  // Skip WebSocket and WebRTC signaling
  if (url.protocol === 'ws:' || url.protocol === 'wss:') return;

  // API calls: network-first with cache fallback
  if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/ws/')) {
    event.respondWith(networkFirst(event.request));
    return;
  }

  // Static assets: cache-first
  if (isStaticAsset(url)) {
    event.respondWith(cacheFirst(event.request));
    return;
  }

  // HTML pages: stale-while-revalidate
  event.respondWith(staleWhileRevalidate(event.request));
});

// ─── Caching Strategies ───────────────────────────────────────────

async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;

  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(RUNTIME_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    return offlineFallback(request);
  }
}

async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(RUNTIME_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await caches.match(request);
    return cached || new Response(
      JSON.stringify({ error: 'offline', message: 'No network connection' }),
      { status: 503, headers: { 'Content-Type': 'application/json' } }
    );
  }
}

async function staleWhileRevalidate(request) {
  const cached = await caches.match(request);

  const fetchPromise = fetch(request).then(response => {
    if (response.ok) {
      caches.open(RUNTIME_CACHE).then(cache => cache.put(request, response.clone()));
    }
    return response;
  }).catch(() => null);

  return cached || await fetchPromise || offlineFallback(request);
}

async function offlineFallback(request) {
  // For HTML requests, serve the offline page
  if (request.headers.get('Accept')?.includes('text/html')) {
    const offline = await caches.match('/pwa/offline.html');
    if (offline) return offline;
    // Fallback: serve cached Command Center
    const cc = await caches.match('/fastbot_command_center.html');
    if (cc) return cc;
  }
  return new Response('Offline', { status: 503, statusText: 'Service Unavailable' });
}

function isStaticAsset(url) {
  const ext = url.pathname.split('.').pop().toLowerCase();
  return ['js', 'css', 'png', 'jpg', 'webp', 'svg', 'woff2', 'woff', 'ttf', 'stl', 'onnx'].includes(ext);
}

// ─── Background Sync (dataset uploads) ────────────────────────────
self.addEventListener('sync', event => {
  if (event.tag === 'upload-dataset') {
    event.waitUntil(uploadPendingDatasets());
  }
});

async function uploadPendingDatasets() {
  // Read pending dataset uploads from IndexedDB
  // (implemented in Command Center JS, queued when offline)
  console.log('[SW] Background sync: uploading pending datasets');
}

// ─── Push Notifications (training complete) ───────────────────────
self.addEventListener('push', event => {
  if (!event.data) return;

  const data = event.data.json();
  event.waitUntil(
    self.registration.showNotification(data.title || 'SAFER-VLA', {
      body: data.body || 'Training update available',
      icon: '/pwa/icons/icon-192.png',
      badge: '/pwa/icons/icon-192.png',
      tag: data.tag || 'safer-vla',
      data: data,
    })
  );
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  event.waitUntil(
    clients.matchAll({ type: 'window' }).then(windowClients => {
      for (const client of windowClients) {
        if (client.url.includes('fastbot_command_center') && 'focus' in client) {
          return client.focus();
        }
      }
      return clients.openWindow('/fastbot_command_center.html');
    })
  );
});

console.log('[SW] SAFER-VLA Service Worker loaded (v1)');
