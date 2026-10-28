<script setup lang="ts">
// Rings alarms and calendar reminders while the panel is open.
// setInterval (not rAF) so it keeps ticking in background tabs.
import { eventOccursOn } from '~/composables/useTeam'

const { t } = useSite()
const { alarms, events, api } = useTeam()
const a = computed(() => t.value.panel.alarms)
const c = computed(() => t.value.panel.calendar)

const ringing = ref<{ time: string; label: string } | null>(null)
const snoozes: { at: number; time: string; label: string }[] = []
const fired = new Set<string>()

let tickTimer: ReturnType<typeof setInterval> | undefined
let beepTimer: ReturnType<typeof setInterval> | undefined
let stopTimer: ReturnType<typeof setTimeout> | undefined
let ctx: AudioContext | undefined
const title = { saved: '' }

const pad = (n: number) => String(n).padStart(2, '0')

function tick() {
  const now = new Date()
  const hm = `${pad(now.getHours())}:${pad(now.getMinutes())}`
  for (const al of alarms.value) {
    if (!al.enabled || al.time !== hm || (al.days.length && !al.days.includes(now.getDay()))) continue
    const key = `${al.id}|${now.toDateString()}|${hm}`
    if (fired.has(key)) continue
    fired.add(key)
    ring(al.time, al.label)
    // One-time alarm switches itself off
    if (!al.days.length) {
      al.enabled = false
      api(`/alarms/${al.id}`, { method: 'PATCH', body: { enabled: false } }).catch(() => {})
    }
  }
  remindEvents(now)
  const due = snoozes.findIndex((s) => s.at <= now.getTime())
  if (due >= 0) {
    const [s] = snoozes.splice(due, 1)
    ring(s!.time, s!.label)
  }
}

// Calendar reminders: occurrence start minus `remind` minutes falls on this minute
const ymd = (d: Date) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
function remindEvents(now: Date) {
  const minute = Math.floor(now.getTime() / 60000)
  for (const e of events.value) {
    if (e.remind === null) continue
    // The occurrence may be up to `remind` minutes ahead (also on a later day)
    for (let k = 0; k <= Math.ceil(e.remind / 1440) + 1; k++) {
      const day = new Date(now.getFullYear(), now.getMonth(), now.getDate() + k)
      const date = ymd(day)
      if (!eventOccursOn(e, date)) continue
      const [h, m] = e.start.split(':').map(Number)
      const start = new Date(day.getFullYear(), day.getMonth(), day.getDate(), h, m)
      if (Math.floor(start.getTime() / 60000) - e.remind !== minute) continue
      const key = `ev${e.id}|${date}|${e.start}|${e.remind}`
      if (fired.has(key)) continue
      fired.add(key)
      const when = k === 0 ? '' : ` · ${start.toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'short' })}`
      ring(e.start, `${c.value.reminder}: ${e.title}${when}`)
    }
  }
}

// Browsers allow audio only after a user gesture
function unlock() {
  try {
    ctx ??= new AudioContext()
    ctx.resume()
  } catch { /* no Web Audio */ }
}

function beep() {
  if (!ctx) return
  const start = ctx.currentTime
  for (let i = 0; i < 3; i++) {
    const osc = ctx.createOscillator()
    const gain = ctx.createGain()
    const at = start + i * 0.22
    osc.type = 'sine'
    osc.frequency.value = i === 2 ? 1175 : 880
    gain.gain.setValueAtTime(0.0001, at)
    gain.gain.exponentialRampToValueAtTime(0.25, at + 0.02)
    gain.gain.exponentialRampToValueAtTime(0.0001, at + 0.18)
    osc.connect(gain).connect(ctx.destination)
    osc.start(at)
    osc.stop(at + 0.2)
  }
}

function ring(time: string, label: string) {
  if (!ringing.value) title.saved = document.title
  ringing.value = { time, label }
  document.title = `⏰ ${time} ${label}`.trim()
  unlock()
  beep()
  clearInterval(beepTimer)
  beepTimer = setInterval(beep, 1400)
  clearTimeout(stopTimer)
  stopTimer = setTimeout(silence, 2 * 60 * 1000) // ring at most 2 min
  if ('Notification' in window && Notification.permission === 'granted') {
    new Notification(`⏰ ${time}`, { body: label || a.value.ringing, tag: 'duo-alarm' })
  }
}

function silence() {
  clearInterval(beepTimer)
  clearTimeout(stopTimer)
}

function stop() {
  silence()
  ringing.value = null
  document.title = title.saved
}

function snooze() {
  const r = ringing.value
  stop()
  if (r) snoozes.push({ ...r, at: Date.now() + 5 * 60 * 1000 })
}

onMounted(() => {
  tickTimer = setInterval(tick, 1000)
  addEventListener('pointerdown', unlock, { once: true })
  addEventListener('keydown', unlock, { once: true })
})
onBeforeUnmount(() => {
  stop()
  clearInterval(tickTimer)
  removeEventListener('pointerdown', unlock)
  removeEventListener('keydown', unlock)
  ctx?.close()
})
</script>

<template>
  <Transition name="ring">
    <div v-if="ringing" class="ring-overlay" role="alertdialog" aria-live="assertive" :aria-label="a.ringing">
      <div class="ring-card">
        <span class="ring-bell" aria-hidden="true"><AppIcon name="alarm" /></span>
        <p class="ring-time">{{ ringing.time }}</p>
        <p class="ring-label">{{ ringing.label || a.ringing }}</p>
        <div class="ring-actions">
          <button type="button" class="btn btn-ghost" @click="snooze">{{ a.snooze }}</button>
          <button type="button" class="btn btn-primary" @click="stop">{{ a.stop }}</button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style>
.ring-overlay {
  position: fixed; inset: 0; z-index: 400; display: grid; place-items: center; padding: 16px;
  background: rgba(246, 245, 241, .75); -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px);
}
.ring-card {
  width: min(380px, 100%); padding: 34px 28px 28px; text-align: center; border-radius: var(--radius);
  background: var(--surface); box-shadow: var(--shadow-lg); border: 1px solid var(--line);
}
.ring-bell {
  display: inline-grid; place-items: center; width: 84px; height: 84px; border-radius: 50%; color: #fff;
  background: conic-gradient(from 200deg, var(--accent), var(--accent-2), var(--accent-3), var(--accent));
  animation: ringPulse 1.4s infinite;
}
.ring-bell .ico { width: 40px; height: 40px; animation: ringShake 1.4s infinite; }
@keyframes ringPulse { 0% { box-shadow: 0 0 0 0 rgba(91, 75, 255, .45); } 100% { box-shadow: 0 0 0 26px rgba(91, 75, 255, 0); } }
@keyframes ringShake { 0%, 40%, 100% { transform: rotate(0); } 5%, 15%, 25%, 35% { transform: rotate(-14deg); } 10%, 20%, 30% { transform: rotate(14deg); } }
.ring-time { margin-top: 18px; font-family: var(--font-display); font-weight: 600; font-size: 3rem; letter-spacing: -.03em; line-height: 1; }
.ring-label { margin-top: 8px; color: var(--ink-2); font-weight: 600; overflow-wrap: anywhere; }
.ring-actions { display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; margin-top: 24px; }
.ring-enter-active, .ring-leave-active { transition: opacity .3s; }
.ring-enter-active .ring-card { animation: ringIn .45s var(--ease) both; }
@keyframes ringIn { from { opacity: 0; transform: translateY(20px) scale(.97); } }
.ring-enter-from, .ring-leave-to { opacity: 0; }
.tp.dark .ring-overlay { background: rgba(14, 14, 19, .75); }
</style>
