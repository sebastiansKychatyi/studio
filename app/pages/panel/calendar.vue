<script setup lang="ts">
// Personal planner: week (hour grid) and month views, weekly repeating events, kanban deadlines.
import type { EventDraft, TeamDue, TeamEvent } from '~/composables/useTeam'

const { t } = useSite()
const { locale } = useI18n()
const localePath = useLocalePath()
const { api } = useTeam()

const p = computed(() => t.value.panel)
const c = computed(() => t.value.panel.calendar)

// Local dates (no UTC shift)
const pad = (n: number) => String(n).padStart(2, '0')
const ymd = (d: Date) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
const asDate = (s: string) => new Date(`${s}T12:00:00`)
const addDays = (s: string, n: number) => {
  const d = asDate(s)
  d.setDate(d.getDate() + n)
  return ymd(d)
}
const mondayOf = (s: string) => addDays(s, -((asDate(s).getDay() + 6) % 7))
const toMin = (hhmm: string) => Number(hhmm.slice(0, 2)) * 60 + Number(hhmm.slice(3, 5))
const toTime = (m: number) => `${pad(Math.floor(m / 60) % 24)}:${pad(m % 60)}`
const duration = (min: number) => `${Math.floor(min / 60)} ${c.value.h}${min % 60 ? ` ${min % 60} ${c.value.m}` : ''}`

const now = ref(new Date())
const today = computed(() => ymd(now.value))
let clock: ReturnType<typeof setInterval> | undefined

// View + anchor day, view remembered per browser
const VIEW = 'team-calendar-view'
const view = ref<'week' | 'month'>('week')
const anchor = ref(ymd(new Date()))
watch(view, (v) => {
  try { localStorage.setItem(VIEW, v) } catch { /* private mode */ }
})

const events = ref<TeamEvent[]>([])
const due = ref<TeamDue[]>([])
const loading = ref(true)
const failed = ref(false)

// Visible range
const weekStart = computed(() => mondayOf(anchor.value))
const weekDays = computed(() => Array.from({ length: 7 }, (_, i) => addDays(weekStart.value, i)))
const monthStart = computed(() => `${anchor.value.slice(0, 7)}-01`)
const monthDays = computed(() => {
  const first = mondayOf(monthStart.value)
  return Array.from({ length: 42 }, (_, i) => addDays(first, i))
})
const range = computed(() =>
  view.value === 'week' ? [weekDays.value[0]!, weekDays.value[6]!] : [monthDays.value[0]!, monthDays.value[41]!]
)

function fail(err: unknown) {
  if (httpStatus(err) === 401) return navigateTo(localePath('/login'))
  failed.value = true
  setTimeout(() => (failed.value = false), 3000)
}

async function loadDue() {
  due.value = await api<TeamDue[]>('/due', { query: { from: range.value[0], to: range.value[1] } })
}
async function load() {
  try {
    const [list] = await Promise.all([api<TeamEvent[]>('/events'), loadDue()])
    events.value = list
  } catch (err) {
    fail(err)
  } finally {
    loading.value = false
  }
}
watch(range, () => loadDue().catch(fail))

// Occurrences of events on one day
interface Occ { ev: TeamEvent; date: string; start: number; end: number; lane: number; lanes: number }
function occursOn(e: TeamEvent, day: string) {
  if (e.repeat === 'none') return e.date === day
  return day >= e.date && (!e.until || day <= e.until) && e.days.includes(asDate(day).getDay()) && !e.skip.includes(day)
}
const byDay = computed(() => {
  const map = new Map<string, Occ[]>()
  const days = view.value === 'week' ? weekDays.value : monthDays.value
  for (const day of days) {
    const list = events.value
      .filter((e) => occursOn(e, day))
      .map((ev) => ({ ev, date: day, start: toMin(ev.start), end: toMin(ev.end), lane: 0, lanes: 1 }))
      .sort((a, b) => a.start - b.start || b.end - a.end)
    // Overlapping events share the width: lanes inside each overlap group
    let group: Occ[] = []
    let groupEnd = -1
    const close = () => group.forEach((o) => (o.lanes = Math.max(...group.map((g) => g.lane)) + 1))
    for (const o of list) {
      if (o.start >= groupEnd) {
        close()
        group = []
        groupEnd = -1
      }
      const used = new Set(group.filter((g) => g.end > o.start).map((g) => g.lane))
      while (used.has(o.lane)) o.lane++
      group.push(o)
      groupEnd = Math.max(groupEnd, o.end)
    }
    close()
    map.set(day, list)
  }
  return map
})
const dueByDay = computed(() => {
  const map = new Map<string, TeamDue[]>()
  for (const d of due.value) map.set(d.due_date, [...(map.get(d.due_date) ?? []), d])
  return map
})
const busy = (day: string) => (byDay.value.get(day) ?? []).reduce((s, o) => s + (o.end - o.start), 0)

// Labels
const title = computed(() => {
  if (view.value === 'month') return asDate(monthStart.value).toLocaleDateString(locale.value, { month: 'long', year: 'numeric' })
  const a = asDate(weekDays.value[0]!)
  const b = asDate(weekDays.value[6]!)
  const sameMonth = a.getMonth() === b.getMonth()
  return `${a.toLocaleDateString(locale.value, sameMonth ? { day: 'numeric' } : { day: 'numeric', month: 'short' })} – ${b.toLocaleDateString(locale.value, { day: 'numeric', month: 'short', year: 'numeric' })}`
})
const weekdayShort = (day: string) => asDate(day).toLocaleDateString(locale.value, { weekday: 'short' })
const weekLabels = computed(() => weekDays.value.map(weekdayShort))

function shift(n: number) {
  anchor.value = view.value === 'week' ? addDays(anchor.value, n * 7) : (() => {
    const d = asDate(monthStart.value)
    d.setMonth(d.getMonth() + n)
    return ymd(d)
  })()
}

// Week grid geometry
const HOUR = 46 // px per hour
const gridEl = ref<HTMLElement>()
const nowMin = computed(() => now.value.getHours() * 60 + now.value.getMinutes())
function scrollToMorning() {
  nextTick(() => gridEl.value?.scrollTo({ top: HOUR * 7 }))
}

// Editor
const editing = ref<{ event: TeamEvent | null; draft: EventDraft; occurrence: string | null } | null>(null)
const baseDraft = (date: string, start: number): EventDraft => ({
  title: '', date, start: toTime(start), end: toTime(Math.min(start + 60, 23 * 60 + 59)),
  repeat: 'none', days: [], until: null, color: '#5B4BFF', note: '',
})
function newAt(date: string, start = 9 * 60) {
  editing.value = { event: null, draft: baseDraft(date, start), occurrence: null }
}
function onGridClick(e: MouseEvent, day: string) {
  const top = e.clientY - (e.currentTarget as HTMLElement).getBoundingClientRect().top
  newAt(day, Math.min(Math.floor(top / HOUR * 2) * 30, 23 * 60))
}
function open(o: { ev: TeamEvent; date: string }) {
  const { id: _id, skip: _skip, ...draft } = o.ev
  editing.value = { event: o.ev, draft: { ...draft }, occurrence: o.date }
}

async function save(body: EventDraft) {
  const ev = editing.value?.event
  editing.value = null
  try {
    if (ev) await api(`/events/${ev.id}`, { method: 'PATCH', body })
    else await api('/events', { method: 'POST', body })
    events.value = await api<TeamEvent[]>('/events')
  } catch (err) {
    fail(err)
  }
}
async function skip(date: string) {
  const ev = editing.value?.event
  editing.value = null
  if (!ev) return
  try {
    const updated = await api<TeamEvent>(`/events/${ev.id}/skip`, { method: 'POST', body: { date } })
    events.value = events.value.map((e) => (e.id === ev.id ? updated : e))
  } catch (err) {
    fail(err)
  }
}
async function remove() {
  const ev = editing.value?.event
  editing.value = null
  if (!ev) return
  events.value = events.value.filter((e) => e.id !== ev.id)
  await api(`/events/${ev.id}`, { method: 'DELETE' }).catch(fail)
}

// Deadline → open its board
function openCard(d: TeamDue) {
  try { localStorage.setItem('team-board', String(d.board_id)) } catch { /* private mode */ }
  navigateTo(localePath('/panel'))
}

onMounted(() => {
  try { if (localStorage.getItem(VIEW) === 'month') view.value = 'month' } catch { /* private mode */ }
  clock = setInterval(() => (now.value = new Date()), 30000)
  load().then(scrollToMorning)
})
watch(view, (v) => v === 'week' && scrollToMorning())
onBeforeUnmount(() => clearInterval(clock))
</script>

<template>
  <div class="cal">
    <header class="tp-head">
      <div>
        <h1>{{ c.title }}</h1>
        <p>{{ c.subtitle }}</p>
      </div>
      <div class="cal-actions">
        <div class="ex-month">
          <button type="button" class="tp-icon-btn sm" :title="c.prev" :aria-label="c.prev" @click="shift(-1)"><AppIcon name="left" /></button>
          <Transition name="ex-flip" mode="out-in">
            <span :key="title" class="ex-month-label cal-range">{{ title }}</span>
          </Transition>
          <button type="button" class="tp-icon-btn sm" :title="c.next" :aria-label="c.next" @click="shift(1)"><AppIcon name="right" /></button>
        </div>
        <button type="button" class="btn btn-ghost btn-sm" @click="anchor = today">{{ c.today }}</button>
        <div class="ex-seg" role="radiogroup" :aria-label="c.title">
          <button type="button" role="radio" :aria-checked="view === 'week'" :class="{ on: view === 'week' }" @click="view = 'week'">{{ c.week }}</button>
          <button type="button" role="radio" :aria-checked="view === 'month'" :class="{ on: view === 'month' }" @click="view = 'month'">{{ c.month }}</button>
        </div>
        <button type="button" class="btn btn-primary btn-sm" @click="newAt(view === 'week' && !weekDays.includes(today) ? weekDays[0]! : today)">
          <AppIcon name="plus" /> {{ c.newEvent }}
        </button>
      </div>
    </header>

    <div v-if="loading" class="kb-loading"><span class="spinner" /></div>

    <!-- Week: hour grid -->
    <section v-else-if="view === 'week'" ref="gridEl" class="cal-week cal-scroll">
      <div class="cal-week-head">
        <span />
        <div v-for="(day, i) in weekDays" :key="day" class="cal-dayhead" :class="{ today: day === today, past: day < today }">
          <span class="cal-wd">{{ weekLabels[i] }}</span>
          <b class="cal-dn">{{ Number(day.slice(8)) }}</b>
          <small v-if="busy(day)" :title="c.busy">{{ c.busy }}: {{ duration(busy(day)) }}</small>
          <div class="cal-due">
            <button
              v-for="d in dueByDay.get(day) ?? []"
              :key="d.id"
              type="button"
              class="cal-due-chip"
              :class="{ done: d.done, late: !d.done && day < today }"
              :title="`${c.deadline}: ${d.title} · ${d.board_title} / ${d.column_title}`"
              @click="openCard(d)"
            >
              <AppIcon name="calendar" />{{ d.title }}
            </button>
          </div>
        </div>
      </div>

      <div class="cal-grid" :style="{ height: `${HOUR * 24}px` }">
          <div class="cal-hours">
            <span v-for="h in 24" :key="h" :style="{ top: `${(h - 1) * HOUR}px` }">{{ pad(h - 1) }}:00</span>
          </div>
          <div
            v-for="day in weekDays"
            :key="day"
            class="cal-col"
            :class="{ today: day === today }"
            @click.self="onGridClick($event, day)"
          >
            <button
              v-for="o in byDay.get(day) ?? []"
              :key="`${o.ev.id}-${day}`"
              type="button"
              class="cal-ev"
              :class="{ short: o.end - o.start < 45, past: day < today || (day === today && o.end < nowMin) }"
              :style="{
                '--c': o.ev.color,
                top: `${(o.start / 60) * HOUR}px`,
                height: `${Math.max(((o.end - o.start) / 60) * HOUR - 2, 18)}px`,
                left: `calc(${(o.lane / o.lanes) * 100}% + 2px)`,
                width: `calc(${100 / o.lanes}% - 4px)`,
              }"
              @click="open(o)"
            >
              <b>{{ o.ev.title }}</b>
              <small>{{ o.ev.start }}–{{ o.ev.end }}<AppIcon v-if="o.ev.repeat === 'weekly'" name="repeat" /></small>
            </button>
            <i v-if="day === today" class="cal-now" :style="{ top: `${(nowMin / 60) * HOUR}px` }" />
          </div>
      </div>
    </section>

    <!-- Month -->
    <section v-else class="cal-month">
      <div class="cal-month-head">
        <span v-for="(w, i) in weekLabels" :key="i">{{ w }}</span>
      </div>
      <div class="cal-month-grid">
        <div
          v-for="day in monthDays"
          :key="day"
          class="cal-cell"
          :class="{ today: day === today, out: day.slice(0, 7) !== monthStart.slice(0, 7) }"
          @click.self="newAt(day)"
        >
          <button type="button" class="cal-cell-day" :title="c.week" @click="anchor = day; view = 'week'">{{ Number(day.slice(8)) }}</button>
          <button
            v-for="d in dueByDay.get(day) ?? []"
            :key="`d${d.id}`"
            type="button"
            class="cal-due-chip"
            :class="{ done: d.done, late: !d.done && day < today }"
            :title="`${c.deadline}: ${d.title}`"
            @click="openCard(d)"
          >
            <AppIcon name="calendar" />{{ d.title }}
          </button>
          <button
            v-for="o in (byDay.get(day) ?? []).slice(0, 3)"
            :key="`${o.ev.id}-${day}`"
            type="button"
            class="cal-pill"
            :style="{ '--c': o.ev.color }"
            @click="open(o)"
          >
            <i />{{ o.ev.start }} {{ o.ev.title }}
          </button>
          <button v-if="(byDay.get(day)?.length ?? 0) > 3" type="button" class="cal-more" @click="anchor = day; view = 'week'">
            + {{ byDay.get(day)!.length - 3 }} {{ c.more }}
          </button>
        </div>
      </div>
    </section>

    <TeamEventModal
      v-if="editing"
      :event="editing.event"
      :draft="editing.draft"
      :occurrence="editing.occurrence"
      @close="editing = null"
      @save="save"
      @skip="skip"
      @delete="remove"
    />
    <Transition name="toast"><div v-if="failed" class="tp-toast" role="status">{{ p.errorServer }}</div></Transition>
  </div>
</template>

<style>
/* ===== Calendar ===== */
.cal-actions { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; }
.cal-actions .btn .ico { width: 16px; height: 16px; }
.cal-range { min-width: 190px; }

.cal-week { border-radius: var(--radius); background: var(--surface); border: 1px solid var(--line); box-shadow: var(--shadow); overflow: hidden; animation: tpUp .6s var(--ease) both; }
.cal-week-head, .cal-grid { display: grid; grid-template-columns: 56px repeat(7, minmax(110px, 1fr)); }
.cal-week-head { position: sticky; top: 0; z-index: 5; min-width: max-content; width: 100%; border-bottom: 1px solid var(--line); background: var(--surface); }
.cal-grid { min-width: max-content; width: 100%; }
.cal-dayhead { display: grid; align-content: start; gap: 2px; padding: 10px 8px 8px; border-left: 1px solid var(--line); min-width: 0; }
.cal-wd { font-size: .75rem; font-weight: 800; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }
.cal-dn { font-family: var(--font-display); font-size: 1.4rem; font-weight: 600; line-height: 1.1; }
.cal-dayhead small { font-size: .72rem; font-weight: 700; color: var(--accent); }
.cal-dayhead.today .cal-dn { display: inline-grid; place-items: center; justify-self: start; min-width: 34px; height: 34px; padding: 0 6px; border-radius: 999px; background: var(--accent); color: #fff; }
.cal-dayhead.past { opacity: .6; }
.cal-due { display: grid; gap: 3px; margin-top: 4px; }
.cal-due-chip {
  display: flex; align-items: center; gap: 4px; min-width: 0; padding: 2px 7px; border-radius: 8px; border: 0; cursor: pointer; text-align: left;
  background: #FFF1D6; color: #A15C00; font-size: .72rem; font-weight: 800; transition: transform .25s var(--ease);
}
.cal-due-chip .ico { flex: none; width: 12px; height: 12px; }
.cal-due-chip:hover { transform: translateX(2px); }
.cal-due-chip.late { background: #E5484D; color: #fff; }
.cal-due-chip.done { background: var(--bg-2); color: var(--muted); text-decoration: line-through; }
.cal-due-chip { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.cal-scroll { max-height: min(72vh, 820px); overflow: auto; }
.cal-grid { position: relative; }
.cal-hours { position: relative; }
.cal-hours span { position: absolute; right: 8px; transform: translateY(-50%); font-size: .7rem; font-weight: 700; color: var(--muted); font-variant-numeric: tabular-nums; }
.cal-hours span:first-child { display: none; }
.cal-col {
  position: relative; border-left: 1px solid var(--line); cursor: copy;
  background-image: linear-gradient(var(--line) 1px, transparent 1px), linear-gradient(rgba(0, 0, 0, .025) 1px, transparent 1px);
  background-size: 100% 46px, 100% 23px;
}
.cal-col.today { background-color: rgba(91, 75, 255, .035); }
.cal-ev {
  position: absolute; display: grid; align-content: start; gap: 1px; padding: 4px 7px; overflow: hidden; text-align: left; cursor: pointer;
  border: 0; border-left: 3px solid var(--c); border-radius: 8px; background: color-mix(in srgb, var(--c) 16%, #fff); color: var(--ink);
  transition: box-shadow .25s, transform .25s var(--ease), opacity .25s; animation: tpFade .35s both;
}
.cal-ev:hover { z-index: 2; box-shadow: var(--shadow); transform: translateY(-1px); }
.cal-ev b { font-size: .8rem; line-height: 1.2; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cal-ev small { display: flex; align-items: center; gap: 4px; font-size: .7rem; font-weight: 700; color: color-mix(in srgb, var(--c) 70%, #000); }
.cal-ev small .ico { width: 11px; height: 11px; }
.cal-ev.short { grid-auto-flow: column; justify-content: start; gap: 6px; align-items: center; padding-block: 1px; }
.cal-ev.past { opacity: .55; }
.cal-now { position: absolute; left: -1px; right: 0; height: 2px; background: #E5484D; z-index: 3; pointer-events: none; }
.cal-now::before { content: ''; position: absolute; left: -5px; top: -4px; width: 10px; height: 10px; border-radius: 50%; background: #E5484D; }

.cal-month { border-radius: var(--radius); background: var(--surface); border: 1px solid var(--line); box-shadow: var(--shadow); overflow: hidden; animation: tpUp .6s var(--ease) both; }
.cal-month-head, .cal-month-grid { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); }
.cal-month-head span { padding: 10px; font-size: .75rem; font-weight: 800; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; border-bottom: 1px solid var(--line); }
.cal-cell { display: grid; align-content: start; gap: 3px; min-height: 112px; padding: 6px; border-right: 1px solid var(--line); border-bottom: 1px solid var(--line); cursor: copy; min-width: 0; }
.cal-cell:nth-child(7n) { border-right: 0; }
.cal-cell.out { background: var(--bg); }
.cal-cell.out .cal-cell-day { color: var(--muted); }
.cal-cell-day { justify-self: start; min-width: 28px; height: 28px; padding: 0 6px; border-radius: 999px; border: 0; background: none; cursor: pointer; font-weight: 800; font-size: .85rem; }
.cal-cell-day:hover { background: var(--bg-2); }
.cal-cell.today .cal-cell-day { background: var(--accent); color: #fff; }
.cal-pill {
  display: flex; align-items: center; gap: 5px; min-width: 0; padding: 2px 6px; border-radius: 7px; border: 0; cursor: pointer; text-align: left;
  background: color-mix(in srgb, var(--c) 12%, #fff); font-size: .74rem; font-weight: 700; color: var(--ink-2);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.cal-pill i { flex: none; width: 7px; height: 7px; border-radius: 50%; background: var(--c); }
.cal-pill:hover { background: color-mix(in srgb, var(--c) 22%, #fff); }
.cal-more { justify-self: start; padding: 0 6px; border: 0; background: none; color: var(--muted); font-size: .72rem; font-weight: 800; cursor: pointer; }

@media (max-width: 720px) {
  .cal-cell { min-height: 74px; padding: 4px; }
  .cal-pill { font-size: .66rem; }
  .cal-pill i { display: none; }
}
</style>
