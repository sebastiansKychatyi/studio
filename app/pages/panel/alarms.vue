<script setup lang="ts">
// Personal alarms: live clock, add form, list with on/off switches
import type { TeamAlarm } from '~/composables/useTeam'

const { t } = useSite()
const { locale } = useI18n()
const localePath = useLocalePath()
const { api, alarms, loadAlarms } = useTeam()

const p = computed(() => t.value.panel)
const a = computed(() => t.value.panel.alarms)
const WEEK = [1, 2, 3, 4, 5, 6, 0] // Monday first, JS weekday numbers

const pad = (n: number) => String(n).padStart(2, '0')
const now = ref(new Date())
let clock: ReturnType<typeof setInterval> | undefined

const nextHour = () => `${pad((new Date().getHours() + 1) % 24)}:00`
const form = reactive({ time: nextHour(), label: '', days: [] as number[] })
const busy = ref(false)
const failed = ref(false)
const confirmId = ref<number | null>(null)

const permission = ref<NotificationPermission | 'unsupported'>('default')

onMounted(() => {
  clock = setInterval(() => (now.value = new Date()), 1000)
  permission.value = 'Notification' in window ? Notification.permission : 'unsupported'
  loadAlarms().catch(fail)
})
onBeforeUnmount(() => clearInterval(clock))

function fail(e: unknown) {
  if (httpStatus(e) === 401) return navigateTo(localePath('/login'))
  failed.value = true
  setTimeout(() => (failed.value = false), 3000)
  loadAlarms().catch(() => {})
}

const dateLabel = computed(() => now.value.toLocaleDateString(locale.value, { weekday: 'long', day: 'numeric', month: 'long' }))

function toggleDay(list: number[], d: number) {
  const i = list.indexOf(d)
  if (i >= 0) list.splice(i, 1)
  else list.push(d)
}

function daysText(days: number[]) {
  if (!days.length) return a.value.once
  if (days.length === 7) return a.value.everyDay
  return WEEK.filter((d) => days.includes(d)).map((d) => a.value.days[WEEK.indexOf(d)]).join(' · ')
}

async function add() {
  if (busy.value || !form.time) return
  busy.value = true
  try {
    const created = await api<TeamAlarm>('/alarms', { method: 'POST', body: { ...form, label: form.label.trim() } })
    alarms.value = [...alarms.value, created].sort((x, y) => x.time.localeCompare(y.time))
    form.label = ''
    form.days = []
  } catch (e) {
    fail(e)
  } finally {
    busy.value = false
  }
}

async function patch(al: TeamAlarm, body: Partial<TeamAlarm>) {
  Object.assign(al, body)
  await api(`/alarms/${al.id}`, { method: 'PATCH', body }).catch(fail)
}

async function remove(al: TeamAlarm) {
  if (confirmId.value !== al.id) {
    confirmId.value = al.id
    setTimeout(() => confirmId.value === al.id && (confirmId.value = null), 3000)
    return
  }
  alarms.value = alarms.value.filter((x) => x !== al)
  await api(`/alarms/${al.id}`, { method: 'DELETE' }).catch(fail)
}

async function askPermission() {
  if (permission.value === 'unsupported') return
  permission.value = await Notification.requestPermission()
}
</script>

<template>
  <div class="al">
    <header class="tp-head">
      <div>
        <h1>{{ a.title }}</h1>
        <p>{{ a.subtitle }}</p>
      </div>
      <button
        v-if="permission !== 'unsupported'"
        type="button"
        class="btn btn-ghost btn-sm al-notify"
        :class="permission"
        :disabled="permission !== 'default'"
        @click="askPermission"
      >
        <AppIcon name="bell" />
        {{ permission === 'granted' ? a.notifyOn : permission === 'denied' ? a.notifyBlocked : a.notify }}
      </button>
    </header>

    <div class="al-grid">
      <!-- Live clock -->
      <section class="al-clock" aria-live="off">
        <div class="al-clock-ring" aria-hidden="true">
          <i :style="{ transform: `rotate(${(now.getHours() * 3600 + now.getMinutes() * 60 + now.getSeconds()) * 6}deg)` }" />
        </div>
        <p class="al-time">
          {{ pad(now.getHours()) }}<span class="al-colon">:</span>{{ pad(now.getMinutes()) }}<small>{{ pad(now.getSeconds()) }}</small>
        </p>
        <p class="al-date">{{ dateLabel }}</p>
        <p class="al-hint">{{ a.hint }}</p>
      </section>

      <!-- New alarm -->
      <form class="al-form" @submit.prevent="add">
        <div class="al-form-row">
          <label class="tp-field al-time-field">
            <span>{{ a.time }}</span>
            <input v-model="form.time" type="time" required>
          </label>
          <label class="tp-field">
            <span>{{ a.label }}</span>
            <input v-model="form.label" maxlength="120" :placeholder="a.labelPh">
          </label>
        </div>
        <div class="al-days" role="group" :aria-label="a.time">
          <button
            v-for="(d, i) in WEEK"
            :key="d"
            type="button"
            class="al-day"
            :class="{ on: form.days.includes(d) }"
            :aria-pressed="form.days.includes(d)"
            @click="toggleDay(form.days, d)"
          >
            {{ a.days[i] }}
          </button>
          <span class="al-days-note">{{ daysText(form.days) }}</span>
        </div>
        <button class="btn btn-primary" :disabled="busy"><AppIcon name="plus" /> {{ a.add }}</button>
      </form>
    </div>

    <!-- List -->
    <TransitionGroup v-if="alarms.length" tag="ul" name="kb-card" class="al-list">
      <li v-for="al in alarms" :key="al.id" class="al-item" :class="{ off: !al.enabled }">
        <p class="al-item-time">{{ al.time }}</p>
        <div class="al-item-text">
          <b>{{ al.label || a.ringing }}</b>
          <small>{{ daysText(al.days) }}</small>
        </div>
        <button
          type="button"
          class="al-switch"
          role="switch"
          :aria-checked="al.enabled"
          :aria-label="al.label || al.time"
          @click="patch(al, { enabled: !al.enabled })"
        >
          <i />
        </button>
        <button
          type="button"
          class="tp-icon-btn sm danger"
          :class="{ confirm: confirmId === al.id }"
          :title="confirmId === al.id ? p.sure : p.delete"
          :aria-label="confirmId === al.id ? p.sure : p.delete"
          @click="remove(al)"
        >
          <AppIcon name="trash" />
        </button>
      </li>
    </TransitionGroup>
    <p v-else class="al-empty">{{ a.empty }}</p>

    <Transition name="toast"><div v-if="failed" class="tp-toast" role="status">{{ p.errorServer }}</div></Transition>
  </div>
</template>

<style>
/* ===== Alarms ===== */
.al-grid { display: grid; grid-template-columns: minmax(0, .9fr) minmax(0, 1.1fr); gap: 18px; margin-bottom: 22px; }
.al-clock, .al-form { padding: 26px; border-radius: var(--radius); background: var(--surface); border: 1px solid var(--line); box-shadow: var(--shadow); animation: tpUp .7s var(--ease) both; }
.al-form { animation-delay: .08s; display: grid; align-content: start; gap: 6px; }
.al-clock { position: relative; overflow: hidden; display: grid; align-content: center; text-align: center; isolation: isolate; }
.al-clock-ring { position: absolute; inset: 50% auto auto 50%; width: 260px; height: 260px; margin: -130px 0 0 -130px; border-radius: 50%; border: 1px dashed var(--line-2); z-index: -1; }
.al-clock-ring i { position: absolute; inset: 0; transition: transform .5s var(--ease); }
.al-clock-ring i::after { content: ''; position: absolute; top: -5px; left: 50%; width: 10px; height: 10px; margin-left: -5px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 14px var(--accent); }
.al-time { font-family: var(--font-display); font-weight: 600; font-size: clamp(3rem, 7vw, 4.6rem); letter-spacing: -.04em; line-height: 1; }
.al-time small { font-size: .32em; color: var(--muted); margin-left: 6px; letter-spacing: 0; }
.al-colon { animation: blink 1s steps(1) infinite; }
@keyframes blink { 50% { opacity: .25; } }
.al-date { margin-top: 10px; font-weight: 700; color: var(--ink-2); }
.al-date::first-letter { text-transform: uppercase; }
.al-hint { margin-top: 14px; font-size: .82rem; color: var(--muted); max-width: 300px; justify-self: center; }

.al-form-row { display: grid; grid-template-columns: 140px 1fr; gap: 12px; }
.al-time-field input { font-variant-numeric: tabular-nums; }
.al-days { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin: 2px 0 14px; }
.al-day {
  width: 42px; height: 42px; border-radius: 50%; border: 1px solid var(--line-2); background: #fff; cursor: pointer;
  font-weight: 800; font-size: .8rem; color: var(--ink-2); transition: background .2s, color .2s, border-color .2s, transform .3s var(--ease);
}
.al-day:hover { border-color: var(--ink); }
.al-day.on { background: var(--accent); border-color: var(--accent); color: #fff; transform: scale(1.06); }
.al-days-note { margin-left: 6px; color: var(--muted); font-size: .85rem; font-weight: 600; }
.al-form .btn { justify-self: start; }
.al-notify .ico { width: 16px; height: 16px; }
.al-notify.granted { color: #13896F; border-color: rgba(25, 195, 166, .4); }
.al-notify:disabled { cursor: default; }

.al-list { display: grid; gap: 10px; }
.al-item {
  display: grid; grid-template-columns: auto minmax(0, 1fr) auto auto; align-items: center; gap: 16px; padding: 14px 18px;
  border-radius: 20px; background: var(--surface); border: 1px solid var(--line); transition: opacity .3s, box-shadow .3s;
}
.al-item:hover { box-shadow: var(--shadow); }
.al-item.off { opacity: .55; }
.al-item-time { font-family: var(--font-display); font-weight: 600; font-size: 1.7rem; letter-spacing: -.03em; font-variant-numeric: tabular-nums; }
.al-item-text { display: grid; line-height: 1.3; }
.al-item-text b { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.al-item-text small { color: var(--muted); font-weight: 600; }
.al-switch { position: relative; width: 50px; height: 30px; border-radius: 999px; border: 0; cursor: pointer; background: var(--line-2); transition: background .3s; }
.al-switch i { position: absolute; top: 3px; left: 3px; width: 24px; height: 24px; border-radius: 50%; background: #fff; box-shadow: 0 2px 6px rgba(18, 18, 22, .2); transition: transform .35s var(--ease); }
.al-switch[aria-checked="true"] { background: var(--accent-3); }
.al-switch[aria-checked="true"] i { transform: translateX(20px); }
.al-empty { padding: 30px; text-align: center; color: var(--muted); border-radius: 20px; border: 1px dashed var(--line-2); }

@media (max-width: 960px) { .al-grid { grid-template-columns: 1fr; } }
@media (max-width: 480px) {
  .al-form-row { grid-template-columns: 1fr; }
  .al-item { grid-template-columns: auto minmax(0, 1fr) auto; gap: 10px 12px; }
  .al-item .tp-icon-btn { grid-column: 3; }
}
</style>
