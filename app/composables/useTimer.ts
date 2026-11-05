// Time tracking timer: one runs at a time. The start time is kept on the server (and in the local
// copy), so it keeps counting while the app is closed; start / stop work offline through the outbox.
import type { TimeEntry } from '~/composables/useTeam'

let ticker: ReturnType<typeof setInterval> | undefined

export function useTimer() {
  const running = useState<TimeEntry | null>('time-running', () => null)
  const now = useState('time-now', () => Date.now())
  const { api, peek } = useTeam()

  async function load() {
    const cached = await peek<TimeEntry | null>('/time/running')
    if (cached !== undefined) running.value = cached
    running.value = await api<TimeEntry | null>('/time/running')
  }

  function tick() {
    if (import.meta.server || ticker) return
    ticker = setInterval(() => (now.value = Date.now()), 1000)
  }

  // Seconds since start
  const elapsed = computed(() => (running.value ? Math.max(Math.floor((now.value - Date.parse(running.value.start)) / 1000), 0) : 0))
  const clock = computed(() => {
    const s = elapsed.value
    return `${Math.floor(s / 3600)}:${String(Math.floor((s % 3600) / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`
  })

  async function start(link: { client_id?: number | null; project_id?: number | null; card_id?: number | null; note?: string }) {
    const at = new Date().toISOString()
    running.value = await api<TimeEntry>('/time/start', { method: 'POST', body: { ...link, note: link.note ?? '', start: at } })
  }

  async function stop() {
    const end = new Date().toISOString()
    const was = running.value
    running.value = null
    try {
      await api('/time/stop', { method: 'POST', body: { end } })
    } catch (e) {
      running.value = was
      throw e
    }
  }

  return { running, elapsed, clock, load, tick, start, stop }
}
