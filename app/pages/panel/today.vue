<script setup lang="ts">
// "Today": the whole day on one screen — next alarm, timeline, tasks, money; Today / Tomorrow.
// Tasks and money come from GET /today (server, user's time zone); events and the alarm are
// computed from the local data, so offline changes show at once.
import { classesOn, eventOccursOn, type Currency, type StudyWork, type TeamToday, type TodayBill, type TodayCard } from '~/composables/useTeam'

const { t } = useSite()
const { locale } = useI18n()
const localePath = useLocalePath()
const route = useRoute()
const { api, user, alarms, events, study, synced, waiting, online } = useTeam()
const { pref } = usePrefs()
const { list: snoozes } = useSnoozes()

const p = computed(() => t.value.panel)
const d = computed(() => t.value.panel.today)

const pad = (n: number) => String(n).padStart(2, '0')
const ymd = (x: Date) => `${x.getFullYear()}-${pad(x.getMonth() + 1)}-${pad(x.getDate())}`
const now = ref(new Date())
let clock: ReturnType<typeof setInterval> | undefined

// Today / Tomorrow (?date= from the evening summary)
const tomorrow = ref(false)
const day = computed(() => {
  const x = new Date(now.value)
  if (tomorrow.value) x.setDate(x.getDate() + 1)
  return ymd(x)
})
const isToday = computed(() => day.value === ymd(now.value))

const data = ref<TeamToday | null>(null)
const loading = ref(true)
const unreachable = ref(false)
// Shown from the local copy (no network or server down)
const offline = computed(() => unreachable.value || !online.value)
const failed = ref('')
const doneIds = ref(new Set<number>()) // cards ticked here or waiting in the outbox
const paidIds = ref(new Set<number>())

async function load() {
  try {
    data.value = await api<TeamToday>('/today', { query: { date: day.value } })
    unreachable.value = false
  } catch (e) {
    if (isOffline(e)) unreachable.value = true
    else failed.value = p.value.errorServer
  } finally {
    loading.value = false
  }
  // Offline ticks not sent yet
  for (const op of await waiting()) {
    const card = op.url.match(/^\/cards\/(\d+)$/)
    if (card && op.body?.column_id) doneIds.value.add(Number(card[1]))
    const bill = op.url.match(/^\/expenses\/recurring\/(\d+)\/pay$/)
    if (bill) paidIds.value.add(Number(bill[1]))
  }
}
watch(day, load)
watch(synced, load)
onMounted(() => {
  if (route.query.date === ymd(new Date(Date.now() + 86400000))) tomorrow.value = true
  load()
  clock = setInterval(() => (now.value = new Date()), 30000)
})
onBeforeUnmount(() => clearInterval(clock))

// Header
const greeting = computed(() => {
  const h = now.value.getHours()
  const name = (user.value?.name || user.value?.username || '').split(' ')[0]
  return `${h < 5 ? d.value.night : h < 12 ? d.value.morning : h < 18 ? d.value.afternoon : d.value.evening}${name ? `, ${name}` : ''}`
})
const dateLabel = computed(() => new Date(`${day.value}T12:00:00`).toLocaleDateString(locale.value, { weekday: 'long', day: 'numeric', month: 'long' }))

// Next alarm (local alarms + snoozed ones)
const nextAlarm = computed(() => {
  let best: { at: Date; label: string } | null = null
  const base = now.value
  for (const al of alarms.value) {
    if (!al.enabled) continue
    const [h, m] = al.time.split(':').map(Number)
    for (let k = 0; k < 8; k++) {
      const at = new Date(base.getFullYear(), base.getMonth(), base.getDate() + k, h, m)
      if (at > base && (!al.days.length || al.days.includes(at.getDay()))) {
        if (!best || at < best.at) best = { at, label: al.label }
        break
      }
    }
  }
  for (const s of snoozes.value) if (!best || s.at < best.at.getTime()) best = { at: new Date(s.at), label: s.label }
  return best
})
const alarmText = computed(() => {
  const a = nextAlarm.value
  if (!a) return d.value.noAlarm
  const time = `${pad(a.at.getHours())}:${pad(a.at.getMinutes())}`
  const diff = Math.round((new Date(ymd(a.at)).getTime() - new Date(ymd(now.value)).getTime()) / 86400000)
  const when = diff === 0 ? d.value.todayAt : diff === 1 ? d.value.tomorrowAt : a.at.toLocaleDateString(locale.value, { weekday: 'long' })
  return `${when} ${time}${a.label ? ` · ${a.label}` : ''}`
})

// Timeline: own events and classes of the day, "now" line between past and coming ones
const toMin = (hm: string) => Number(hm.slice(0, 2)) * 60 + Number(hm.slice(3, 5))
const dayEvents = computed(() => [
  ...events.value.filter((e) => eventOccursOn(e, day.value)).map((e) => ({
    key: `e${e.id}`, title: e.title, start: e.start, end: e.end, color: e.color, sub: '', repeat: e.repeat === 'weekly',
    to: `/panel/calendar?date=${day.value}&event=${e.id}`,
  })),
  ...classesOn(study.value, day.value).map(({ lesson: l, subject: s }) => ({
    key: `c${l.id}`, title: s.name, start: l.start, end: l.end, color: s.color, repeat: false, to: '/panel/study',
    sub: [t.value.panel.study.kinds[l.kind], l.room || s.room].filter(Boolean).join(' · '),
  })),
].sort((a, b) => a.start.localeCompare(b.start) || a.end.localeCompare(b.end)))

// Study: not done, due within a week or overdue; tick = done (works offline)
// Timer and clients: follow-ups due, invoices still unpaid
const timer = useTimer()
const { clients } = useTeam()
const clientName = (id: number | null) => clients.value.find((x) => x.id === id)?.name ?? ''
const followups = computed(() => (data.value?.followups ?? []).filter((x) => !doneIds.value.has(-x.id)))
const unpaid = computed(() => (data.value?.waiting ?? []).filter((x) => !paidIds.value.has(-x.id)))
async function followupDone(id: number) {
  doneIds.value = new Set([...doneIds.value, -id])
  await api(`/client-log/${id}`, { method: 'PATCH', body: { followup_done: true } }).catch(() => doneIds.value.delete(-id))
}
async function invoicePaid(id: number) {
  paidIds.value = new Set([...paidIds.value, -id])
  await api(`/invoices/${id}/pay`, { method: 'POST', body: {} }).catch((e) => {
    paidIds.value.delete(-id)
    failed.value = isOffline(e) ? p.value.offlineOnly : p.value.errorServer
  })
}
const fmtMoney = (n: number, cur: string) => {
  try {
    return new Intl.NumberFormat(locale.value, { style: 'currency', currency: cur, currencyDisplay: 'narrowSymbol' }).format(n)
  } catch {
    return `${n.toFixed(2)} ${cur}`
  }
}

const studyWorks = computed(() => {
  const limit = new Date(`${day.value}T12:00:00`)
  limit.setDate(limit.getDate() + 7)
  return study.value.works.filter((w) => w.status !== 'done' && w.due <= ymd(limit))
})
const subjectName = (w: StudyWork) => study.value.subjects.find((x) => x.id === w.subject_id)?.name
const daysLeft = (w: StudyWork) => Math.round((Date.parse(w.due) - Date.parse(day.value)) / 86400000)
async function workDone(w: StudyWork) {
  w.status = 'done'
  await api(`/study/works/${w.id}`, { method: 'PATCH', body: { status: 'done' } }).catch((e) => {
    w.status = 'todo'
    failed.value = isOffline(e) ? p.value.offlineOnly : p.value.errorServer
  })
}
const nowMin = computed(() => now.value.getHours() * 60 + now.value.getMinutes())
const nowAt = computed(() => (isToday.value ? dayEvents.value.findIndex((e) => toMin(e.end) > nowMin.value) : -2))

// Tasks: tick = move to the board's last column (works offline)
const visible = (list: TodayCard[]) => list.filter((c) => !doneIds.value.has(c.id))
const taskGroups = computed(() => {
  const tk = data.value?.tasks
  if (!tk) return []
  return [
    { key: 'overdue', title: d.value.overdue, cards: visible(tk.overdue) },
    { key: 'today', title: isToday.value ? d.value.dueToday : d.value.dueTomorrow, cards: visible(tk.today) },
    { key: 'assigned', title: d.value.assigned, cards: visible(tk.assigned) },
  ].filter((g) => g.cards.length)
})
const taskCount = computed(() => taskGroups.value.reduce((n, g) => n + g.cards.length, 0))
async function done(card: TodayCard) {
  doneIds.value = new Set([...doneIds.value, card.id])
  // Then refresh the local copy of the day (offline it would show the card again)
  await api(`/cards/${card.id}`, { method: 'PATCH', body: { column_id: card.done_column_id } }).then(() => { if (online.value) load() }, (e) => {
    doneIds.value.delete(card.id)
    failed.value = isOffline(e) ? p.value.offlineOnly : p.value.errorServer
  })
}
const shortDate = (s: string) => new Date(`${s}T12:00:00`).toLocaleDateString(locale.value, { day: 'numeric', month: 'short' })

// Money in the account's display currency
const currency = pref<Currency>('currency', 'EUR')
const rates = ref<Record<Currency, number>>({ EUR: 1, UAH: 51.5, USD: 1.16 })
onMounted(() => api<Record<Currency, number>>('/rates').then((r) => (rates.value = r)).catch(() => {}))
const fmt = (n: number, cur: Currency) => new Intl.NumberFormat(locale.value, { style: 'currency', currency: cur, currencyDisplay: 'narrowSymbol' }).format(n)
const eur = (n: number) => fmt(n * rates.value[currency.value], currency.value)
const bills = computed(() => (data.value?.money.bills ?? []).filter((b) => !paidIds.value.has(b.id)))
async function pay(b: TodayBill) {
  paidIds.value = new Set([...paidIds.value, b.id])
  await api(`/expenses/recurring/${b.id}/pay`, { method: 'POST', body: { month: data.value!.money.month, spent_on: isToday.value ? day.value : undefined } }).then(() => { if (online.value) load() }, (e) => {
    paidIds.value.delete(b.id)
    failed.value = isOffline(e) ? p.value.offlineOnly : p.value.errorServer
  })
}

watch(failed, (v) => v && setTimeout(() => (failed.value = ''), 3500))
</script>

<template>
  <div class="td">
    <header class="td-head">
      <div>
        <p class="td-date">{{ dateLabel }}</p>
        <h1>{{ tomorrow ? d.tomorrowTitle : greeting }}</h1>
      </div>
      <div class="ex-seg td-switch" role="radiogroup" :aria-label="d.title">
        <button type="button" role="radio" :aria-checked="!tomorrow" :class="{ on: !tomorrow }" @click="tomorrow = false">{{ d.today }}</button>
        <button type="button" role="radio" :aria-checked="tomorrow" :class="{ on: tomorrow }" @click="tomorrow = true">{{ d.tomorrow }}</button>
      </div>
    </header>

    <NuxtLink :to="localePath('/panel/alarms')" class="td-alarm" :class="{ off: !nextAlarm }">
      <AppIcon name="alarm" /><span>{{ alarmText }}</span><AppIcon name="right" />
    </NuxtLink>

    <p v-if="offline" class="td-offline"><AppIcon name="plug" />{{ data ? d.offlineOld : d.offlineNone }}</p>

    <!-- Timeline -->
    <section class="td-block" :class="{ empty: !dayEvents.length }">
      <h2><AppIcon name="calendar" />{{ d.plan }}<span v-if="!dayEvents.length" class="td-none">{{ d.noEvents }}</span></h2>
      <ol v-if="dayEvents.length" class="td-line">
        <template v-for="(e, i) in dayEvents" :key="e.key">
          <li v-if="i === nowAt" class="td-now"><span>{{ d.now }} · {{ pad(now.getHours()) }}:{{ pad(now.getMinutes()) }}</span></li>
          <li>
            <NuxtLink :to="localePath(e.to)" class="td-ev" :class="{ past: isToday && toMin(e.end) <= nowMin }" :style="{ '--c': e.color }">
              <span class="td-ev-time">{{ e.start }}<small>{{ e.end }}</small></span>
              <span class="td-ev-text"><b>{{ e.title }}</b><small v-if="e.sub">{{ e.sub }}</small></span>
              <AppIcon v-if="e.sub" name="study" /><AppIcon v-else-if="e.repeat" name="repeat" />
            </NuxtLink>
          </li>
        </template>
        <li v-if="nowAt === -1" class="td-now"><span>{{ d.now }} · {{ d.dayOver }}</span></li>
      </ol>
    </section>

    <!-- Tasks -->
    <section class="td-block" :class="{ empty: !loading && !taskCount }">
      <h2><AppIcon name="tasks" />{{ d.tasks }}<span v-if="!loading && !taskCount" class="td-none">{{ data ? d.noTasks : '—' }}</span></h2>
      <div v-for="g in taskGroups" :key="g.key" class="td-group" :class="g.key">
        <h3>{{ g.title }} <span class="kb-count">{{ g.cards.length }}</span></h3>
        <TransitionGroup tag="ul" name="kb-card" class="td-tasks">
          <li v-for="c in g.cards" :key="c.id" class="td-task">
            <button type="button" class="td-check" :title="d.markDone" :aria-label="`${d.markDone}: ${c.title}`" @click="done(c)"><AppIcon name="check" /></button>
            <NuxtLink :to="localePath(`/panel?board=${c.board_id}&card=${c.id}`)" class="td-task-text">
              <b>{{ c.title }}</b>
              <small>{{ c.board_title }} · {{ c.column_title }}<template v-if="c.due_date && g.key === 'overdue'"> · {{ shortDate(c.due_date) }}</template></small>
            </NuxtLink>
          </li>
        </TransitionGroup>
      </div>
    </section>

    <!-- Timer -->
    <section v-if="isToday" class="td-block td-timer" :class="{ empty: !timer.running.value, on: timer.running.value }">
      <h2>
        <AppIcon name="clock" />{{ t.panel.time.title }}
        <template v-if="timer.running.value">
          <b class="td-clock">{{ timer.clock.value }}</b>
          <small class="td-none">{{ clientName(timer.running.value.client_id) || timer.running.value.note }}</small>
          <button type="button" class="rc-pay td-stop" @click="timer.stop().catch(() => {})"><AppIcon name="stop" />{{ t.panel.time.stop }}</button>
        </template>
        <NuxtLink v-else :to="localePath('/panel/time')" class="rc-pay td-start"><AppIcon name="play" />{{ t.panel.time.start }}</NuxtLink>
      </h2>
    </section>

    <!-- Clients: contact again, waiting for payment -->
    <section v-if="followups.length || unpaid.length" class="td-block">
      <h2><AppIcon name="briefcase" />{{ t.panel.clients.title }}</h2>
      <div v-if="followups.length" class="td-group">
        <h3>{{ d.contact }} <span class="kb-count">{{ followups.length }}</span></h3>
        <ul class="td-tasks">
          <li v-for="x in followups" :key="x.id" class="td-task">
            <button type="button" class="td-check" :title="d.markDone" :aria-label="`${d.markDone}: ${x.client}`" @click="followupDone(x.id)"><AppIcon name="check" /></button>
            <NuxtLink :to="localePath(`/panel/clients?id=${x.client_id}`)" class="td-task-text"><b>{{ x.client }}</b><small>{{ x.text }}</small></NuxtLink>
          </li>
        </ul>
      </div>
      <div v-if="unpaid.length" class="td-group">
        <h3>{{ d.waiting }} <span class="kb-count">{{ unpaid.length }}</span></h3>
        <ul class="td-bills">
          <li v-for="x in unpaid" :key="x.id" :class="{ late: x.overdue }">
            <NuxtLink :to="localePath(`/panel/clients?id=${x.client_id}`)" class="td-bill-text"><b>{{ x.client }} · {{ fmtMoney(x.amount, x.currency) }}</b><small>{{ x.number }} {{ x.title }} · {{ x.overdue ? d.billLate : shortDate(x.due) }}</small></NuxtLink>
            <button type="button" class="rc-pay" @click="invoicePaid(x.id)"><AppIcon name="check" />{{ t.panel.clients.paid }}</button>
          </li>
        </ul>
      </div>
    </section>

    <!-- Study deadlines -->
    <section v-if="study.semester || study.works.length" class="td-block" :class="{ empty: !studyWorks.length }">
      <h2><AppIcon name="study" />{{ d.study }}<span v-if="!studyWorks.length" class="td-none">{{ d.noStudy }}</span></h2>
      <TransitionGroup v-if="studyWorks.length" tag="ul" name="kb-card" class="td-tasks td-study">
        <li v-for="w in studyWorks" :key="w.id" class="td-task" :class="{ late: daysLeft(w) < 0 }">
          <button type="button" class="td-check" :title="d.markDone" :aria-label="`${d.markDone}: ${w.title}`" @click="workDone(w)"><AppIcon name="check" /></button>
          <NuxtLink :to="localePath('/panel/study')" class="td-task-text">
            <b>{{ w.title }}</b>
            <small>{{ t.panel.study.workKinds[w.kind] }}<template v-if="subjectName(w)"> · {{ subjectName(w) }}</template> · {{ shortDate(w.due) }}<template v-if="w.due_time"> {{ w.due_time }}</template></small>
          </NuxtLink>
        </li>
      </TransitionGroup>
    </section>

    <!-- Money -->
    <section v-if="data" class="td-block">
      <h2><AppIcon name="wallet" />{{ d.money }}</h2>
      <div class="td-money">
        <NuxtLink :to="localePath('/panel/expenses')"><small>{{ isToday ? d.spentToday : d.spentDay }}</small><b>{{ eur(data.money.spent_today) }}</b></NuxtLink>
        <NuxtLink :to="localePath('/panel/expenses')"><small>{{ d.spentMonth }}</small><b>{{ eur(data.money.spent_month) }}</b></NuxtLink>
      </div>
      <ul v-if="bills.length" class="td-bills">
        <li v-for="b in bills" :key="b.id" :class="{ late: b.overdue }">
          <span class="td-bill-text"><b>{{ b.title }}</b><small>{{ b.overdue ? d.billLate : d.billToday }} · {{ b.amount ? fmt(b.amount, b.currency) : p.recurring.variable }}</small></span>
          <button v-if="b.amount" type="button" class="rc-pay" @click="pay(b)"><AppIcon name="check" />{{ p.expenses.rec.pay }}</button>
          <NuxtLink v-else :to="localePath('/panel/expenses')" class="rc-pay">{{ p.expenses.rec.pay }}…</NuxtLink>
        </li>
      </ul>
    </section>


    <Transition name="toast"><div v-if="failed" class="tp-toast" role="status">{{ failed }}</div></Transition>
  </div>
</template>

<style>
/* ===== Today ===== */
.td { display: grid; gap: 14px; max-width: 760px; }
.td-head { display: flex; flex-wrap: wrap; align-items: flex-end; justify-content: space-between; gap: 12px; animation: tpUp .6s var(--ease) both; }
.td-date { color: var(--muted); font-weight: 700; font-size: .9rem; }
.td-date::first-letter { text-transform: uppercase; }
.td-head h1 { font-family: var(--font-display); font-weight: 600; font-size: clamp(1.5rem, 5vw, 2.1rem); letter-spacing: -.03em; line-height: 1.15; }
.td-switch button { min-height: 36px; padding: 0 14px; }
.td-alarm {
  display: flex; align-items: center; gap: 10px; min-height: 48px; padding: 10px 14px; border-radius: 16px;
  background: var(--surface); border: 1px solid var(--line); font-weight: 700; font-size: .92rem;
}
.td-alarm .ico { width: 18px; height: 18px; color: var(--accent); }
.td-alarm span { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.td-alarm span::first-letter { text-transform: uppercase; }
.td-alarm .ico:last-child { color: var(--muted); }
.td-alarm.off { color: var(--muted); }
.td-alarm.off .ico:first-child { color: var(--muted); }
.td-offline { display: flex; align-items: center; gap: 8px; padding: 10px 14px; border-radius: 14px; background: var(--bg-2); color: var(--ink-2); font-size: .85rem; font-weight: 700; }
.td-offline .ico { width: 16px; height: 16px; }

.td-block { padding: 16px; border-radius: 22px; background: var(--surface); border: 1px solid var(--line); animation: tpUp .6s var(--ease) both; }
.td-block h2 { display: flex; align-items: center; gap: 8px; font-size: .95rem; font-weight: 800; }
.td-block h2 .ico { width: 17px; height: 17px; color: var(--accent); }
/* Nothing to show: one line */
.td-block.empty { padding: 12px 16px; }
.td-none { margin-left: auto; color: var(--muted); font-weight: 600; font-size: .85rem; }

.td-line { display: grid; gap: 6px; margin-top: 12px; }
.td-ev {
  display: grid; grid-template-columns: 52px minmax(0, 1fr) auto; align-items: center; gap: 10px; min-height: 52px; padding: 8px 12px;
  border-radius: 14px; border-left: 4px solid var(--c); background: color-mix(in srgb, var(--c) 10%, var(--surface));
}
.td-ev-text { min-width: 0; display: grid; line-height: 1.25; }
.td-ev-text b { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.td-ev-text small { color: var(--muted); font-weight: 600; font-size: .76rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.td-timer h2 { flex-wrap: wrap; }
.td-timer.on { border-color: rgba(229, 72, 77, .4); }
.td-clock { color: #E5484D; font-variant-numeric: tabular-nums; }
.td-start, .td-stop { margin-left: auto; min-height: 40px; }
.td-stop { background: #E5484D; }
.td-timer .td-none { margin-left: 0; flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.td-study .td-task.late { border-color: rgba(229, 72, 77, .4); }
.td-study .td-task.late small { color: #E5484D; }
.td-ev .ico { width: 15px; height: 15px; color: var(--muted); }
.td-ev-time { display: grid; font-weight: 800; font-variant-numeric: tabular-nums; line-height: 1.2; }
.td-ev-time small { color: var(--muted); font-weight: 700; font-size: .75rem; }
.td-ev.past { opacity: .5; }
.td-now { display: flex; align-items: center; gap: 8px; color: #E5484D; font-size: .75rem; font-weight: 800; }
.td-now::before, .td-now::after { content: ''; height: 2px; background: #E5484D; }
.td-now::before { width: 10px; border-radius: 2px; }
.td-now::after { flex: 1; }

.td-group { margin-top: 12px; }
.td-group h3 { display: flex; align-items: center; gap: 6px; margin-bottom: 6px; font-size: .8rem; font-weight: 800; color: var(--muted); text-transform: uppercase; letter-spacing: .03em; }
.td-group.overdue h3 { color: #E5484D; }
.td-tasks { display: grid; gap: 6px; }
.td-task { display: flex; align-items: center; gap: 6px; padding: 4px 8px 4px 4px; border-radius: 14px; background: var(--bg); border: 1px solid var(--line); }
.td-group.overdue .td-task { border-color: rgba(229, 72, 77, .4); }
.td-check {
  flex: none; display: grid; place-items: center; width: 44px; height: 44px; border: 0; border-radius: 12px; cursor: pointer; background: none; color: transparent;
}
.td-check::before { content: ''; position: absolute; width: 22px; height: 22px; border-radius: 50%; border: 2px solid var(--line-2); transition: border-color .2s, background .2s; }
.td-check { position: relative; }
.td-check .ico { position: relative; width: 14px; height: 14px; }
.td-check:hover::before { border-color: #19C3A6; background: rgba(25, 195, 166, .12); }
.td-check:hover { color: #0E9F85; }
.td-task-text { flex: 1; min-width: 0; display: grid; line-height: 1.3; padding: 6px 0; }
.td-task-text b { font-size: .92rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.td-task-text small { color: var(--muted); font-weight: 600; font-size: .76rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.td-money { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 12px; }
.td-money a { display: grid; padding: 12px; border-radius: 14px; background: var(--bg); border: 1px solid var(--line); }
.td-money small { color: var(--muted); font-weight: 700; font-size: .78rem; }
.td-money b { font-family: var(--font-display); font-weight: 600; font-size: 1.25rem; font-variant-numeric: tabular-nums; }
.td-bills { display: grid; gap: 6px; margin-top: 8px; }
.td-bills li { display: flex; align-items: center; gap: 10px; padding: 8px 8px 8px 12px; border-radius: 14px; background: var(--bg); border: 1px solid var(--line); }
.td-bills li.late { border-color: rgba(229, 72, 77, .45); }
.td-bill-text { flex: 1; min-width: 0; display: grid; line-height: 1.3; }
.td-bill-text b { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: .92rem; }
.td-bill-text small { color: var(--muted); font-weight: 600; font-size: .76rem; }
.td-bills li.late small { color: #E5484D; }
.td-bills .rc-pay { min-height: 40px; }

@media (max-width: 860px) {
  .td { padding-bottom: 60px; }
}
@media (max-width: 400px) {
  .td-block { padding: 14px 12px; }
  .td-money b { font-size: 1.1rem; }
}
</style>
