// Team panel service worker (template; modules/pwa.mjs fills in the version and the precache list).
// Handles only the panel: its pages, build files, fonts and icons. Public pages, /robots.txt,
// /sitemap.xml, /llms.txt and the API are never intercepted or cached here.
/* global self, caches, clients */

const VERSION = __VERSION__
const PRECACHE = __PRECACHE__ // hashed /_nuxt files of this build
const FONT_CSS = __FONT_CSS__ // Google Fonts stylesheet of the site
const LANGS = ['sk', 'cs', 'uk', 'en']
const ASSETS = `assets-${VERSION}`
const SHELL = 'shell' // last panel page (SPA shell, same for every panel URL)
const FONTS = 'fonts'
const PANEL = new RegExp(`^/(${LANGS.join('|')})/panel(/|$)`)
// PWA start URL and shortcuts: /panel?go=… → the panel page in the last used language
const GO = { task: '/panel?new=task', alarm: '/panel/alarms?new=alarm', expense: '/panel/expenses?new=expense' }

self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(ASSETS)
    await cache.addAll([...PRECACHE, '/pwa/icon-192.png', '/pwa/badge-96.png', '/favicon.svg'])
    // Shell for offline start (any language: the client router reads the URL)
    const lang = await lastLang()
    const shell = await fetch(`/${lang}/panel`, { credentials: 'include' }).catch(() => null)
    if (shell?.ok) await (await caches.open(SHELL)).put('/__shell', shell)
    await cacheFonts().catch(() => {})
    // First install takes over right away; updates wait for the "Update" button
    if (!self.registration.active) self.skipWaiting()
  })())
})

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    for (const key of await caches.keys()) if (key.startsWith('assets-') && key !== ASSETS) await caches.delete(key)
    await self.clients.claim()
  })())
})

self.addEventListener('message', (event) => {
  if (event.data === 'skip-waiting') self.skipWaiting()
  if (event.data === 'version') event.source?.postMessage({ type: 'version', version: VERSION })
})

// Web Push from the API (backend/app/notify.py): { title, body, tag, url, alarm?, actions?, … }
self.addEventListener('push', (event) => {
  let data = {}
  try {
    data = event.data ? event.data.json() : {}
  } catch {
    data = { body: event.data ? event.data.text() : '' }
  }
  const { title = 'Duo Studio', url = '/panel', alarm = null, ...options } = data
  event.waitUntil(self.registration.showNotification(title, {
    icon: '/pwa/icon-192.png', badge: '/pwa/badge-96.png', ...options, data: { url, alarm },
  }))
})

// Tap: open the screen of the notification; alarm buttons: snooze 10 min / turn off
self.addEventListener('notificationclick', (event) => {
  const { url, alarm } = event.notification.data || {}
  event.notification.close()
  if (event.action === 'stop') return
  if (event.action === 'snooze' && alarm) {
    event.waitUntil(fetch('/api/team/push/snooze', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ alarm_id: alarm.id, time: alarm.time, label: alarm.label, minutes: 10 }),
    }))
    return
  }
  event.waitUntil(openPage(url || '/panel'))
})

async function openPage(url) {
  const list = await self.clients.matchAll({ type: 'window', includeUncontrolled: true })
  const panel = list.find((c) => PANEL.test(new URL(c.url).pathname))
  if (panel) {
    await panel.focus()
    panel.postMessage({ type: 'open', url }) // the open app switches screens without reloading
    return
  }
  return self.clients.openWindow(url)
}

// Background Sync: network is back → an open panel sends its waiting offline changes
self.addEventListener('sync', (event) => {
  if (event.tag !== 'team-sync') return
  event.waitUntil(self.clients.matchAll({ type: 'window' }).then((list) => list.forEach((c) => c.postMessage('flush'))))
})

self.addEventListener('fetch', (event) => {
  const req = event.request
  if (req.method !== 'GET') return
  const url = new URL(req.url)
  if (url.origin === self.location.origin) {
    if (req.mode === 'navigate') {
      if (url.pathname === '/panel') event.respondWith(start(req, url))
      else if (PANEL.test(url.pathname)) event.respondWith(page(req, url))
      return
    }
    if (url.pathname.startsWith('/_nuxt/') && !url.pathname.startsWith('/_nuxt/builds/latest')) event.respondWith(cacheFirst(req, ASSETS))
    else if (url.pathname.startsWith('/pwa/') || url.pathname === '/favicon.svg') event.respondWith(cacheFirst(req, ASSETS))
    return
  }
  if (url.hostname === 'fonts.googleapis.com') event.respondWith(staleWhileRevalidate(req, FONTS))
  else if (url.hostname === 'fonts.gstatic.com') event.respondWith(cacheFirst(req, FONTS))
})

// Panel page: network first (fresh deploys), cached shell when offline
async function page(req, url) {
  const lang = url.pathname.split('/')[1]
  try {
    const res = await withTimeout(fetch(req), 4000)
    if (res.ok && (res.headers.get('content-type') || '').includes('text/html')) {
      const cache = await caches.open(SHELL)
      await cache.put('/__shell', res.clone())
      await cache.put('/__lang', new Response(lang))
    }
    return res
  } catch {
    const shell = await caches.match('/__shell', { cacheName: SHELL })
    return shell || new Response('Offline', { status: 503, headers: { 'content-type': 'text/plain' } })
  }
}

// /panel → /<last language>/panel (server does the same with a cookie; this works offline)
async function start(req, url) {
  try {
    return await withTimeout(fetch(req), 3000)
  } catch {
    const target = GO[url.searchParams.get('go')] || '/panel/today'
    return Response.redirect(`/${await lastLang()}${target}`, 302)
  }
}

// Fonts work offline from the first start: the stylesheet and every font file it lists
async function cacheFonts() {
  if (!FONT_CSS) return
  const cache = await caches.open(FONTS)
  const css = await fetch(FONT_CSS)
  if (!css.ok) return
  await cache.put(FONT_CSS, css.clone())
  const files = (await css.text()).match(/https:\/\/fonts\.gstatic\.com\/[^)]+/g) || []
  await Promise.all(files.map(async (url) => {
    const res = await fetch(url)
    if (res.ok) await cache.put(url, res)
  }))
}

async function lastLang() {
  const saved = await caches.match('/__lang', { cacheName: SHELL })
  const lang = saved ? await saved.text() : ''
  return LANGS.includes(lang) ? lang : LANGS[0]
}

async function cacheFirst(req, name) {
  const hit = await caches.match(req, { cacheName: name, ignoreVary: true })
  if (hit) return hit
  const res = await fetch(req)
  if (res.ok) (await caches.open(name)).put(req, res.clone())
  return res
}

async function staleWhileRevalidate(req, name) {
  const cache = await caches.open(name)
  const hit = await cache.match(req, { ignoreVary: true })
  const fresh = fetch(req).then((res) => {
    if (res.ok) cache.put(req, res.clone())
    return res
  })
  return hit || fresh
}

function withTimeout(promise, ms) {
  return Promise.race([promise, new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), ms))])
}
