<script setup lang="ts">
// Rings alarms and calendar reminders while the panel is open.
// setInterval (not rAF) so it keeps ticking in background tabs.
import { classesOn, eventOccursOn } from '~/composables/useTeam'

const { t } = useSite()
const { alarms, events, study, api } = useTeam()
const a = computed(() => t.value.panel.alarms)
const c = computed(() => t.value.panel.calendar)

const ringing = ref<{ time: string; label: string; tag: string; alarmId: number } | null>(null)
const { list: snoozes, add: addSnooze, remove: removeSnooze } = useSnoozes()
const fired = new Set<string>()
let ringStart = 0

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
    ring(al.time, al.label, `alarm-${al.id}`, al.id)
    // One-time alarm switches itself off
    if (!al.days.length) {
      al.enabled = false
      api(`/alarms/${al.id}`, { method: 'PATCH', body: { enabled: false } }).catch(() => {})
    }
  }
  remindEvents(now)
  remindClasses(now)
  const due = snoozes.value.find((s) => s.at <= now.getTime())
  if (due) {
    removeSnooze(due, true)
    ring(due.time, due.label, due.tag, due.alarmId)
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
      ring(e.start, `${c.value.reminder}: ${e.title}${when}`, `event-${e.id}-${date}`)
    }
  }
}

// Classes: `remind` minutes (semester setting) before the start, on days with that class
function remindClasses(now: Date) {
  const remind = study.value.semester?.remind
  if (remind === null || remind === undefined) return
  const at = new Date(now.getTime() + remind * 60000)
  const hm = `${pad(at.getHours())}:${pad(at.getMinutes())}`
  for (const { lesson, subject } of classesOn(study.value, ymd(at))) {
    const key = `cl${lesson.id}|${ymd(at)}`
    if (lesson.start !== hm || fired.has(key)) continue
    fired.add(key)
    ring(lesson.start, `${subject.name}${lesson.room || subject.room ? ` · ${lesson.room || subject.room}` : ''}`, `class-${lesson.id}`)
  }
}

// Browsers allow audio only after a user gesture
function unlock() {
  try {
    ctx ??= new AudioContext()
    ctx.resume()
  } catch { /* no Web Audio */ }
}

// Loud alarm pattern: 4 bright square-wave notes per second through a compressor,
// getting louder for ~20 s. Plays at the phone's MEDIA volume (browser limit).
let out: AudioNode | undefined
function beep() {
  if (!ctx) return
  if (!out) {
    const comp = ctx.createDynamicsCompressor()
    comp.threshold.value = -12
    comp.ratio.value = 6
    comp.connect(ctx.destination)
    out = comp
  }
  const level = Math.min(0.45 + (Date.now() - ringStart) / 20000 * 0.55, 1)
  const start = ctx.currentTime
  const notes = [988, 1319, 988, 1319]
  notes.forEach((freq, i) => {
    const at = start + i * 0.13
    for (const [type, f, part] of [['square', freq, 0.6], ['triangle', freq * 2, 0.4]] as const) {
      const osc = ctx!.createOscillator()
      const gain = ctx!.createGain()
      osc.type = type
      osc.frequency.value = f
      gain.gain.setValueAtTime(0.0001, at)
      gain.gain.exponentialRampToValueAtTime(level * part, at + 0.01)
      gain.gain.setValueAtTime(level * part, at + 0.09)
      gain.gain.exponentialRampToValueAtTime(0.0001, at + 0.12)
      osc.connect(gain).connect(out!)
      osc.start(at)
      osc.stop(at + 0.13)
    }
  })
  navigator.vibrate?.([400, 150, 400])
}

// tag = same as the Web Push of this alarm/reminder: the phone shows one notification, not two
function ring(time: string, label: string, tag = 'duo-alarm', alarmId = 0) {
  if (!ringing.value) {
    title.saved = document.title
    ringStart = Date.now()
  }
  ringing.value = { time, label, tag, alarmId }
  document.title = `⏰ ${time} ${label}`.trim()
  unlock()
  beep()
  clearInterval(beepTimer)
  beepTimer = setInterval(beep, 1000)
  clearTimeout(stopTimer)
  stopTimer = setTimeout(silence, 2 * 60 * 1000) // ring at most 2 min
  notifyLocal(`⏰ ${time}`, { body: label || a.value.ringing, tag, requireInteraction: true, data: { url: location.pathname } })
}

function silence() {
  clearInterval(beepTimer)
  clearTimeout(stopTimer)
  navigator.vibrate?.(0)
}

function stop() {
  silence()
  ringing.value = null
  document.title = title.saved
}

function snooze() {
  const r = ringing.value
  stop()
  // Listed on the alarms page, survives reloads, comes by push if the app is closed
  if (r) addSnooze(r)
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
