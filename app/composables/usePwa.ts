// Installed app (PWA): service worker (panel only), "Install app" button, "New version — Update".

interface InstallPrompt extends Event {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

let prompt: InstallPrompt | null = null
let registration: Promise<ServiceWorkerRegistration | undefined> | undefined
let updating = false

export function usePwa() {
  const canInstall = useState('pwa-can-install', () => false) // Android/desktop Chrome offered install
  const standalone = useState('pwa-standalone', () => false) // running as the installed app
  const ios = useState('pwa-ios', () => false) // iPhone/iPad: install by hand (Share → Add to Home Screen)
  const updateReady = useState('pwa-update', () => false)
  const twa = useState('pwa-twa', () => false) // inside the Android app (android/): can hand alarms to the system Clock

  // From a client plugin: the browser may offer install before the panel is mounted
  function listen() {
    standalone.value = matchMedia('(display-mode: standalone)').matches || (navigator as { standalone?: boolean }).standalone === true
    ios.value = /iphone|ipad|ipod/i.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)
    try {
      if (new URLSearchParams(location.search).get('source') === 'twa' || document.referrer.startsWith('android-app://')) localStorage.setItem('duo-twa', '1')
      twa.value = localStorage.getItem('duo-twa') === '1'
    } catch { /* storage blocked */ }
    if (twa.value) standalone.value = true
    addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault()
      prompt = e as InstallPrompt
      canInstall.value = true
    })
    addEventListener('appinstalled', () => {
      prompt = null
      canInstall.value = false
    })
  }

  // From the panel shell; the public site never registers the worker
  function register() {
    if (registration || import.meta.dev || !('serviceWorker' in navigator)) return registration
    registration = navigator.serviceWorker.register('/sw.js', { scope: '/' }).then((reg) => {
      const watch = (sw: ServiceWorker | null) =>
        sw?.addEventListener('statechange', () => {
          if (sw.state === 'installed' && navigator.serviceWorker.controller) updateReady.value = true
        })
      if (reg.waiting && navigator.serviceWorker.controller) updateReady.value = true
      reg.addEventListener('updatefound', () => watch(reg.installing))
      // A new deploy is noticed when the app comes back to the screen, and hourly
      const check = () => reg.update().catch(() => {})
      document.addEventListener('visibilitychange', () => document.visibilityState === 'visible' && check())
      setInterval(check, 3600_000)
      return reg
    }).catch(() => undefined)
    navigator.serviceWorker.addEventListener('controllerchange', () => {
      if (updating) location.reload()
    })
    return registration
  }

  async function install() {
    if (!prompt) return
    await prompt.prompt()
    if ((await prompt.userChoice).outcome === 'accepted') canInstall.value = false
    prompt = null
  }

  // New worker takes over, then the page reloads with the new version
  async function update() {
    const reg = await registration
    if (!reg?.waiting) return location.reload()
    updating = true
    reg.waiting.postMessage('skip-waiting')
  }

  // Child pages mount before the shell: registering here too is harmless (done once)
  return { canInstall, standalone, ios, updateReady, twa, listen, register, install, update, ready: register }
}
