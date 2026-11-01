// Snoozed alarms/reminders: shown in the alarms list, kept across reloads (localStorage)
// and also scheduled on the server, so the push comes even when the app is closed.

export interface Snooze {
  at: number // ms timestamp when it rings again
  time: string // original HH:MM
  label: string
  tag: string // same tag as the notification (alarm-12, event-5-2026-11-02)
  alarmId: number
}

const KEY = 'alarm-snoozes'
export const SNOOZE_MIN = 5

function read(): Snooze[] {
  try {
    return JSON.parse(localStorage.getItem(KEY) ?? '[]')
  } catch {
    return []
  }
}

export function useSnoozes() {
  const list = useState<Snooze[]>('alarm-snoozes', () => (import.meta.client ? read() : []))
  const { api } = useTeam()

  function save() {
    try {
      localStorage.setItem(KEY, JSON.stringify(list.value))
    } catch { /* private mode */ }
  }

  function add(s: Omit<Snooze, 'at'>) {
    const item = { ...s, at: Date.now() + SNOOZE_MIN * 60000 }
    list.value = [...list.value.filter((x) => x.tag !== s.tag), item].sort((a, b) => a.at - b.at)
    save()
    // Push from the server if the app is closed by then (same tag: no double notification)
    api('/push/snooze', { method: 'POST', body: { alarm_id: s.alarmId, time: s.time, label: s.label, tag: s.tag, minutes: SNOOZE_MIN } }).catch(() => {})
  }

  // fired = it rang in the app (the server push comes by itself), else cancelled by the user
  function remove(s: Snooze, fired = false) {
    list.value = list.value.filter((x) => x.tag !== s.tag)
    save()
    if (!fired) api('/push/snooze/cancel', { method: 'POST', body: { tag: s.tag } }).catch(() => {})
  }

  return { list, add, remove }
}
