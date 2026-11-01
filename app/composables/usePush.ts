// Notifications on this device: permission, Web Push subscription (backend/app/notify.py), test.

// VAPID key: base64url → bytes (applicationServerKey)
function keyBytes(key: string) {
  const raw = atob(key.replace(/-/g, '+').replace(/_/g, '/').padEnd(Math.ceil(key.length / 4) * 4, '='))
  return Uint8Array.from(raw, (c) => c.charCodeAt(0))
}

// Notification from the open page. Android Chrome allows them only through the service worker
// (new Notification() throws there), so the worker is used whenever there is one.
export async function notifyLocal(title: string, options: NotificationOptions & { data?: unknown }) {
  if (!('Notification' in window) || Notification.permission !== 'granted') return
  const reg = await navigator.serviceWorker?.getRegistration().catch(() => undefined)
  const full = { icon: '/pwa/icon-192.png', badge: '/pwa/badge-96.png', ...options }
  if (reg) return reg.showNotification(title, full).catch(() => {})
  try {
    new Notification(title, full)
  } catch { /* not allowed here */ }
}

export function usePush() {
  const permission = useState<NotificationPermission | 'unsupported'>('push-permission', () => 'default')
  const subscribed = useState('push-subscribed', () => false)
  const serverReady = useState('push-server', () => true) // API has VAPID keys
  const { api } = useTeam()
  const { ready } = usePwa()

  const supported = () => 'Notification' in window && 'serviceWorker' in navigator && 'PushManager' in window

  async function check() {
    if (!supported()) return (permission.value = 'unsupported')
    permission.value = Notification.permission
    const reg = await ready()
    subscribed.value = !!(await reg?.pushManager.getSubscription())
    return permission.value
  }

  // Ask for permission, then subscribe this device to Web Push
  async function enable() {
    if (!supported()) return (permission.value = 'unsupported')
    permission.value = await Notification.requestPermission()
    if (permission.value !== 'granted') return permission.value
    const { key, enabled } = await api<{ key: string; enabled: boolean }>('/push/key')
    serverReady.value = enabled
    const reg = await ready()
    if (!enabled || !reg) return permission.value // in-app notifications only
    const sub = (await reg.pushManager.getSubscription()) ?? (await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: keyBytes(key) }))
    await api('/push/subscribe', { method: 'POST', body: sub.toJSON() })
    subscribed.value = true
    return permission.value
  }

  async function disable() {
    const sub = await (await ready())?.pushManager.getSubscription()
    if (sub) {
      await api('/push/unsubscribe', { method: 'POST', body: { endpoint: sub.endpoint } }).catch(() => {})
      await sub.unsubscribe()
    }
    subscribed.value = false
  }

  const test = () => api<{ sent: number }>('/push/test', { method: 'POST' })

  return { permission, subscribed, serverReady, check, enable, disable, test }
}
