// PWA images for the team panel: icons, maskable icon, notification badge, shortcut icons, iOS splash screens.
// Optional: install-dialog screenshots of a running panel.
// No dependencies: headless Chrome is driven over the DevTools protocol (Node 22+ has WebSocket).
//
//   node scripts/pwa-assets.mjs
//   node scripts/pwa-assets.mjs --screens http://localhost:3000 <username> <password>
//
// Chrome path: CHROME env or the usual install locations.
import { spawn } from 'node:child_process'
import { existsSync, mkdirSync, readFileSync, writeFileSync, mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

const OUT = 'public/pwa'
const BG = '#F6F5F1'
const logo = readFileSync('public/favicon.svg', 'utf8')
// The "D" mark of the logo, for maskable and monochrome versions
const D = 'M20 16h11c9.4 0 16 6.6 16 16s-6.6 16-16 16H20Zm8 7v18h3c5 0 8.5-3.7 8.5-9S36 23 31 23Z'
const GRADIENT = '<linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5B4BFF"/><stop offset=".55" stop-color="#FF7A59"/><stop offset="1" stop-color="#19C3A6"/></linearGradient>'
// Shortcut glyphs (same paths as AppIcon.vue)
const GLYPHS = {
  task: '<rect x="3" y="4" width="5" height="16" rx="1.5"/><rect x="10" y="4" width="5" height="10" rx="1.5"/><rect x="17" y="4" width="4" height="7" rx="1.5"/>',
  alarm: '<circle cx="12" cy="13" r="8"/><path d="M12 9v4l2.5 2M5 3 2 6M19 3l3 3"/>',
  expense: '<path d="M19 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-3"/><path d="M21 9h-5a3 3 0 0 0 0 6h5Z"/><path d="M16 12h.01"/>',
}

const svgPage = (svg, bg = 'transparent') =>
  `<!doctype html><html><body style="margin:0;background:${bg};display:grid;place-items:center;height:100vh">${svg}</body></html>`

const images = [
  { file: 'icon-192.png', w: 192, h: 192, html: svgPage(logo.replace('<svg ', '<svg width="192" height="192" ')) },
  { file: 'icon-512.png', w: 512, h: 512, html: svgPage(logo.replace('<svg ', '<svg width="512" height="512" ')) },
  // Maskable: full-bleed background, mark inside the 80% safe circle
  {
    file: 'maskable-512.png', w: 512, h: 512,
    html: svgPage(`<svg width="512" height="512" viewBox="0 0 64 64"><defs>${GRADIENT}</defs><rect width="64" height="64" fill="url(#g)"/><path d="${D}" fill="#fff" transform="translate(12.8 12.8) scale(.6)"/></svg>`),
  },
  // Android status bar badge: white mark on transparent
  { file: 'badge-96.png', w: 96, h: 96, html: svgPage(`<svg width="96" height="96" viewBox="8 8 48 48"><path d="${D}" fill="#fff"/></svg>`) },
  ...Object.entries(GLYPHS).map(([name, g]) => ({
    file: `shortcut-${name}.png`, w: 96, h: 96,
    html: svgPage(`<svg width="96" height="96" viewBox="0 0 24 24"><circle cx="12" cy="12" r="12" fill="#5B4BFF"/><g transform="translate(5 5) scale(.5833)" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${g}</g></svg>`),
  })),
]

// iOS splash screens: CSS size × pixel ratio (portrait) of current iPhones (same list in server/plugins/panel-head.ts)
const SPLASH = [
  [375, 667, 2], [414, 896, 2], [375, 812, 3], [414, 896, 3], [390, 844, 3], [428, 926, 3], [393, 852, 3], [430, 932, 3], [402, 874, 3], [440, 956, 3],
]
for (const [w, h, r] of SPLASH) {
  const size = Math.round(Math.min(w, h) * 0.32 * r)
  images.push({
    file: `splash-${w * r}x${h * r}.png`, w: w * r, h: h * r,
    html: svgPage(logo.replace('<svg ', `<svg width="${size}" height="${size}" `), BG),
  })
}

function findChrome() {
  const list = [
    process.env.CHROME,
    'C:/Program Files/Google/Chrome/Application/chrome.exe',
    'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser',
  ]
  const found = list.find((p) => p && existsSync(p))
  if (!found) throw new Error('Chrome not found, set CHROME=/path/to/chrome')
  return found
}

// Minimal DevTools protocol client
async function launch() {
  const profile = mkdtempSync(join(tmpdir(), 'pwa-assets-'))
  const proc = spawn(findChrome(), ['--headless=new', '--remote-debugging-port=0', `--user-data-dir=${profile}`, '--hide-scrollbars', 'about:blank'])
  const wsUrl = await new Promise((resolve, reject) => {
    proc.stderr.on('data', (d) => {
      const m = String(d).match(/ws:\/\/\S+/)
      if (m) resolve(m[0])
    })
    proc.on('exit', () => reject(new Error('Chrome exited')))
  })
  const browser = new WebSocket(wsUrl)
  await new Promise((r) => browser.addEventListener('open', r, { once: true }))
  let id = 0
  const waiting = new Map()
  const listeners = []
  browser.addEventListener('message', (e) => {
    const msg = JSON.parse(e.data)
    if (msg.id && waiting.has(msg.id)) {
      const { resolve, reject } = waiting.get(msg.id)
      waiting.delete(msg.id)
      msg.error ? reject(new Error(msg.error.message)) : resolve(msg.result)
    } else listeners.forEach((fn) => fn(msg))
  })
  const send = (method, params = {}, sessionId) =>
    new Promise((resolve, reject) => {
      waiting.set(++id, { resolve, reject })
      browser.send(JSON.stringify({ id, method, params, sessionId }))
    })
  const { targetId } = await send('Target.createTarget', { url: 'about:blank' })
  const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true })
  const page = (method, params) => send(method, params, sessionId)
  await page('Page.enable')
  const loaded = () => new Promise((r) => listeners.push(function on(m) {
    if (m.method === 'Page.loadEventFired' && m.sessionId === sessionId) {
      listeners.splice(listeners.indexOf(on), 1)
      r()
    }
  }))
  const close = () => {
    browser.close()
    proc.once('exit', () => setTimeout(() => {
      try {
        rmSync(profile, { recursive: true, force: true })
      } catch { /* Windows may still lock a file; it is a temp dir */ }
    }, 300))
    proc.kill()
  }
  return { page, loaded, close }
}

async function shot({ page, loaded }, { w, h, dpr = 1, url, html, transparent = true, wait = 0 }) {
  await page('Emulation.setDeviceMetricsOverride', { width: Math.round(w / dpr), height: Math.round(h / dpr), deviceScaleFactor: dpr, mobile: dpr > 1 })
  await page('Emulation.setDefaultBackgroundColorOverride', transparent ? { color: { r: 0, g: 0, b: 0, a: 0 } } : {})
  const done = loaded()
  if (html) {
    const { frameTree } = await page('Page.getFrameTree')
    await page('Page.navigate', { url: 'about:blank' })
    await page('Page.setDocumentContent', { frameId: frameTree.frame.id, html })
    await new Promise((r) => setTimeout(r, 150))
  } else {
    await page('Page.navigate', { url })
    await done
  }
  if (wait) await new Promise((r) => setTimeout(r, wait))
  const { data } = await page('Page.captureScreenshot', { format: 'png' })
  return Buffer.from(data, 'base64')
}

const chrome = await launch()
try {
  mkdirSync(OUT, { recursive: true })
  const args = process.argv.slice(2)
  if (args[0] === '--screens') {
    // Screenshots of the real panel for the Android install dialog
    const [, base, username, password] = args
    await shot(chrome, { w: 400, h: 400, url: `${base}/sk/login` })
    await chrome.page('Runtime.evaluate', {
      expression: `fetch('/api/team/auth/login',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(${JSON.stringify({ username, password })})}).then(r=>r.status)`,
      awaitPromise: true,
    })
    const screens = [
      ['screen-tasks.png', '/sk/panel', 1080, 1920, 2.75], ['screen-calendar.png', '/sk/panel/calendar', 1080, 1920, 2.75],
      ['screen-wide.png', '/sk/panel', 1920, 1080, 1],
    ]
    for (const [file, path, w, h, dpr] of screens) {
      writeFileSync(join(OUT, file), await shot(chrome, { w, h, dpr, url: base + path, transparent: false, wait: 2500 }))
      console.log(OUT + '/' + file)
    }
  } else {
    for (const img of images) {
      writeFileSync(join(OUT, img.file), await shot(chrome, img))
      console.log(`${OUT}/${img.file}`)
    }
  }
} finally {
  chrome.close()
}
