<script setup lang="ts">
// Time tracking: the timer (one runs at a time), entries of a period (edit, add by hand),
// report period × client / project with amounts by rate, CSV / PDF (print) and an invoice from it.
import { hm, type TeamInvoice, type TimeEntry, type TimeReport } from '~/composables/useTeam'

const { t } = useSite()
const { locale } = useI18n()
const localePath = useLocalePath()
const route = useRoute()
const { api, clients, projects, synced } = useTeam()
const timer = useTimer()

const p = computed(() => t.value.panel)
const m = computed(() => t.value.panel.time)
const pad = (n: number) => String(n).padStart(2, '0')
const ymd = (d: Date) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
const failed = ref('')
const toast = (e: unknown, text?: string) => {
  failed.value = text ?? (isOffline(e) ? p.value.offlineOnly : p.value.errorServer)
  setTimeout(() => (failed.value = ''), 3500)
}
const clientName = (id: number | null) => clients.value.find((x) => x.id === id)?.name ?? ''
const projectName = (id: number | null) => projects.value.find((x) => x.id === id)?.title ?? ''
const projectsOf = (cid: number | null) => projects.value.filter((x) => x.client_id === cid && x.status !== 'done')
const money = (n: number, cur: string) => {
  try {
    return new Intl.NumberFormat(locale.value, { style: 'currency', currency: cur, currencyDisplay: 'narrowSymbol' }).format(n)
  } catch {
    return `${n.toFixed(2)} ${cur}`
  }
}

// ===== Timer =====
const startForm = reactive({ client_id: null as number | null, project_id: null as number | null, note: '' })
watch(() => startForm.client_id, () => (startForm.project_id = null))
async function start() {
  await timer.start({ ...startForm, note: startForm.note.trim() }).catch(toast)
  startForm.note = ''
}
async function stop() {
  await timer.stop().catch(toast)
  load()
}

// ===== Period, filters =====
type Period = 'week' | 'month' | 'last' | 'custom'
const period = ref<Period>('month')
const range = reactive({ from: '', to: '' })
function setPeriod(kind: Period) {
  period.value = kind
  const d = new Date()
  if (kind === 'week') {
    const mon = new Date(d)
    mon.setDate(d.getDate() - ((d.getDay() + 6) % 7))
    Object.assign(range, { from: ymd(mon), to: ymd(d) })
  } else if (kind === 'month') Object.assign(range, { from: ymd(new Date(d.getFullYear(), d.getMonth(), 1)), to: ymd(new Date(d.getFullYear(), d.getMonth() + 1, 0)) })
  else if (kind === 'last') Object.assign(range, { from: ymd(new Date(d.getFullYear(), d.getMonth() - 1, 1)), to: ymd(new Date(d.getFullYear(), d.getMonth(), 0)) })
}
setPeriod('month')
const filter = reactive({ client: (Number(route.query.client) || null) as number | null, project: null as number | null })
watch(() => filter.client, () => (filter.project = null))

const entries = ref<TimeEntry[]>([])
const report = ref<TimeReport | null>(null)
const loading = ref(true)
async function load() {
  const query = { from: range.from, to: range.to, ...(filter.client ? { client: filter.client } : {}), ...(filter.project ? { project: filter.project } : {}) }
  try {
    const [list, rep] = await Promise.all([
      api<TimeEntry[]>('/time', { query: { from: range.from, to: range.to } }),
      api<TimeReport>('/time/report', { query }),
    ])
    entries.value = list.filter((x) => (!filter.client || x.client_id === filter.client) && (!filter.project || x.project_id === filter.project))
    report.value = rep
  } catch (e) {
    toast(e)
  } finally {
    loading.value = false
  }
}
watch([() => range.from, () => range.to, () => filter.client, () => filter.project], load)
watch(synced, load)
onMounted(load)

const minutesOf = (x: TimeEntry) => Math.max(Math.round(((x.end ? Date.parse(x.end) : Date.now()) - Date.parse(x.start)) / 60000), 0)
const clockOf = (iso: string) => new Date(iso).toLocaleTimeString(locale.value, { hour: '2-digit', minute: '2-digit' })
const days = computed(() => {
  const out: { day: string; label: string; minutes: number; items: TimeEntry[] }[] = []
  for (const x of entries.value) {
    const day = ymd(new Date(x.start))
    let g = out.find((d) => d.day === day)
    if (!g) {
      g = { day, label: new Date(`${day}T12:00:00`).toLocaleDateString(locale.value, { weekday: 'short', day: 'numeric', month: 'long' }), minutes: 0, items: [] }
      out.push(g)
    }
    g.items.push(x)
    g.minutes += minutesOf(x)
  }
  return out
})

// ===== Entry editor (also "add by hand") =====
const toLocal = (iso: string) => {
  const d = new Date(iso)
  return `${ymd(d)}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}
const edit = ref<{ id: number | null; client_id: number | null; project_id: number | null; note: string; start: string; end: string } | null>(null)
function openEntry(x?: TimeEntry) {
  const now = new Date()
  const hourAgo = new Date(now.getTime() - 3600000)
  edit.value = x
    ? { id: x.id, client_id: x.client_id, project_id: x.project_id, note: x.note, start: toLocal(x.start), end: x.end ? toLocal(x.end) : '' }
    : { id: null, client_id: filter.client, project_id: filter.project, note: '', start: toLocal(hourAgo.toISOString()), end: toLocal(now.toISOString()) }
}
const editError = ref(false)
async function saveEntry() {
  const e = edit.value
  if (!e) return
  editError.value = !e.start || !e.end || e.end <= e.start
  if (editError.value) return
  const body = { client_id: e.client_id, project_id: e.project_id, note: e.note.trim(), start: new Date(e.start).toISOString(), end: new Date(e.end).toISOString() }
  try {
    if (e.id) await api(`/time/${e.id}`, { method: 'PATCH', body })
    else await api('/time', { method: 'POST', body })
    edit.value = null
    await load()
  } catch (err) {
    toast(err)
  }
}
const sureDelete = ref(false)
async function deleteEntry() {
  if (!sureDelete.value) {
    sureDelete.value = true
    setTimeout(() => (sureDelete.value = false), 3000)
    return
  }
  const id = edit.value?.id
  edit.value = null
  sureDelete.value = false
  if (id) await api(`/time/${id}`, { method: 'DELETE' }).catch(toast)
  await load()
}

// ===== Export =====
function exportCsv() {
  if (!report.value) return
  const dec = locale.value === 'en' ? '.' : ','
  const cell = (s: string) => `"${s.replace(/"/g, '""')}"`
  const rows = [[m.value.task, m.value.client, m.value.project, m.value.hours, m.value.rate, m.value.amount, m.value.currency].map(cell).join(';')]
  for (const r of report.value.rows) {
    rows.push([cell(r.title), cell(clientName(r.client_id)), cell(projectName(r.project_id)), (r.minutes / 60).toFixed(2).replace('.', dec),
      r.rate === null ? '' : String(r.rate).replace('.', dec), r.amount === null ? '' : r.amount.toFixed(2).replace('.', dec), r.currency].join(';'))
  }
  const url = URL.createObjectURL(new Blob(['﻿' + rows.join('\r\n')], { type: 'text/csv;charset=utf-8' }))
  const a = document.createElement('a')
  a.href = url
  a.download = `time-${range.from}-${range.to}.csv`
  a.click()
  URL.revokeObjectURL(url)
}
const printReport = () => window.print()
async function makeInvoice() {
  if (!filter.client) return toast(null, m.value.pickClient)
  try {
    const inv = await api<TeamInvoice>('/time/invoice', { method: 'POST', body: { client_id: filter.client, project_id: filter.project, from: range.from, to: range.to } })
    navigateTo(localePath(`/panel/invoice?id=${inv.id}`))
  } catch (e) {
    const s = httpStatus(e)
    toast(e, s === 409 ? m.value.nothingToBill : s === 422 ? m.value.noRate : undefined)
  }
}
const periodLabel = computed(() => `${new Date(`${range.from}T12:00:00`).toLocaleDateString(locale.value)} – ${new Date(`${range.to}T12:00:00`).toLocaleDateString(locale.value)}`)
</script>

<template>
  <div class="tt">
    <header class="tp-head no-print">
      <div>
        <h1>{{ m.title }}</h1>
        <p>{{ m.subtitle }}</p>
      </div>
      <button type="button" class="btn btn-ghost btn-sm" @click="openEntry()"><AppIcon name="plus" /> {{ m.addByHand }}</button>
    </header>

    <!-- Timer -->
    <section class="sd-card tt-timer no-print" :class="{ on: timer.running.value }">
      <template v-if="timer.running.value">
        <p class="tt-clock">{{ timer.clock.value }}</p>
        <p class="tt-what">{{ [clientName(timer.running.value.client_id), projectName(timer.running.value.project_id), timer.running.value.note].filter(Boolean).join(' · ') || m.noClient }}</p>
        <button type="button" class="btn tt-stop" @click="stop"><AppIcon name="stop" /> {{ m.stop }}</button>
      </template>
      <form v-else class="tt-start" @submit.prevent="start">
        <select v-model="startForm.client_id" class="tp-input" :aria-label="m.client">
          <option :value="null">{{ m.noClient }}</option>
          <option v-for="x in clients" :key="x.id" :value="x.id">{{ x.name }}</option>
        </select>
        <select v-model="startForm.project_id" class="tp-input" :aria-label="m.project" :disabled="!startForm.client_id">
          <option :value="null">{{ m.noProject }}</option>
          <option v-for="x in projectsOf(startForm.client_id)" :key="x.id" :value="x.id">{{ x.title }}</option>
        </select>
        <input v-model="startForm.note" class="tp-input" maxlength="300" :placeholder="m.notePh" :aria-label="m.note">
        <button class="btn btn-primary tt-go"><AppIcon name="play" /> {{ m.start }}</button>
      </form>
    </section>

    <!-- Period and filters -->
    <section class="sd-card no-print">
      <div class="ex-seg tt-period" role="radiogroup" :aria-label="m.period">
        <button v-for="k in (['week', 'month', 'last', 'custom'] as const)" :key="k" type="button" role="radio" :aria-checked="period === k" :class="{ on: period === k }" @click="setPeriod(k)">{{ m.periods[k] }}</button>
      </div>
      <div class="tt-filters">
        <input v-if="period === 'custom'" v-model="range.from" type="date" class="tp-input" :aria-label="m.from">
        <input v-if="period === 'custom'" v-model="range.to" type="date" class="tp-input" :aria-label="m.to">
        <select v-model="filter.client" class="tp-input" :aria-label="m.client">
          <option :value="null">{{ m.allClients }}</option>
          <option v-for="x in clients" :key="x.id" :value="x.id">{{ x.name }}</option>
        </select>
        <select v-model="filter.project" class="tp-input" :aria-label="m.project" :disabled="!filter.client">
          <option :value="null">{{ m.allProjects }}</option>
          <option v-for="x in projects.filter((y) => y.client_id === filter.client)" :key="x.id" :value="x.id">{{ x.title }}</option>
        </select>
      </div>
    </section>

    <!-- Report -->
    <section v-if="report" class="sd-card tt-report">
      <div class="sd-bar">
        <h2><AppIcon name="chart" /> {{ m.report }} <small class="tt-range">{{ periodLabel }}<template v-if="filter.client"> · {{ clientName(filter.client) }}</template></small></h2>
        <span class="tt-export no-print">
          <button type="button" class="btn btn-ghost btn-sm" :disabled="!report.rows.length" @click="exportCsv"><AppIcon name="download" /> CSV</button>
          <button type="button" class="btn btn-ghost btn-sm" :disabled="!report.rows.length" @click="printReport"><AppIcon name="doc" /> PDF</button>
        </span>
      </div>
      <div class="tt-totals">
        <div><small>{{ m.total }}</small><b>{{ hm(report.minutes) }}</b></div>
        <div v-for="(v, cur) in report.amounts" :key="cur"><small>{{ m.amount }}</small><b>{{ money(v, String(cur)) }}</b></div>
        <div><small>{{ m.unbilled }}</small><b>{{ hm(report.unbilled_minutes) }}</b></div>
      </div>
      <p v-if="!report.rows.length" class="sd-muted">{{ m.empty }}</p>
      <table v-else class="tt-table">
        <thead><tr><th>{{ m.task }}</th><th>{{ m.hours }}</th><th>{{ m.amount }}</th></tr></thead>
        <tbody>
          <tr v-for="(r, i) in report.rows" :key="i">
            <td><b>{{ r.title || '—' }}</b><small>{{ [clientName(r.client_id), projectName(r.project_id)].filter(Boolean).join(' · ') }}</small></td>
            <td>{{ hm(r.minutes) }}</td>
            <td>{{ r.amount === null ? '—' : money(r.amount, r.currency) }}</td>
          </tr>
        </tbody>
      </table>
      <button v-if="report.unbilled_minutes" type="button" class="btn btn-primary btn-sm tt-invoice no-print" @click="makeInvoice"><AppIcon name="cash" /> {{ m.makeInvoice }}</button>
      <p v-if="report.unbilled_minutes && !filter.client" class="sd-muted no-print">{{ m.pickClient }}</p>
    </section>

    <!-- Entries -->
    <section class="sd-card no-print">
      <h2><AppIcon name="clock" /> {{ m.entries }}</h2>
      <div v-if="loading" class="kb-loading"><span class="spinner" /></div>
      <p v-else-if="!days.length" class="sd-muted">{{ m.empty }}</p>
      <div v-for="d in days" :key="d.day" class="tt-day">
        <h3>{{ d.label }}<b>{{ hm(d.minutes) }}</b></h3>
        <button v-for="x in d.items" :key="x.id" type="button" class="tt-entry" :class="{ running: !x.end, billed: x.invoice_id }" @click="x.end && openEntry(x)">
          <span class="tt-entry-time">{{ clockOf(x.start) }}–{{ x.end ? clockOf(x.end) : '…' }}</span>
          <span class="cr-inv-text"><b>{{ x.note || projectName(x.project_id) || clientName(x.client_id) || m.noClient }}</b><small>{{ [clientName(x.client_id), projectName(x.project_id)].filter(Boolean).join(' · ') }}<template v-if="x.invoice_id"> · {{ m.billed }}</template></small></span>
          <b class="tt-entry-dur">{{ hm(minutesOf(x)) }}</b>
        </button>
      </div>
    </section>

    <!-- Entry editor -->
    <div v-if="edit" class="tm-overlay" @click.self="edit = null">
      <form class="tm" role="dialog" aria-modal="true" :aria-label="m.entry" @submit.prevent="saveEntry">
        <header class="tm-head">
          <h2>{{ edit.id ? m.entry : m.addByHand }}</h2>
          <button type="button" class="tp-icon-btn sm" :aria-label="p.close" @click="edit = null"><AppIcon name="close" /></button>
        </header>
        <div class="tm-row">
          <label class="tp-field"><span>{{ m.from }}</span><input v-model="edit.start" type="datetime-local" required></label>
          <label class="tp-field"><span>{{ m.to }}</span><input v-model="edit.end" type="datetime-local" required :class="{ invalid: editError }"></label>
        </div>
        <div class="tm-row">
          <label class="tp-field">
            <span>{{ m.client }}</span>
            <select v-model="edit.client_id" @change="edit.project_id = null"><option :value="null">{{ m.noClient }}</option><option v-for="x in clients" :key="x.id" :value="x.id">{{ x.name }}</option></select>
          </label>
          <label class="tp-field">
            <span>{{ m.project }}</span>
            <select v-model="edit.project_id" :disabled="!edit.client_id"><option :value="null">{{ m.noProject }}</option><option v-for="x in projectsOf(edit.client_id)" :key="x.id" :value="x.id">{{ x.title }}</option></select>
          </label>
        </div>
        <label class="tp-field"><span>{{ m.note }}</span><input v-model="edit.note" maxlength="300" :placeholder="m.notePh"></label>
        <footer class="tm-foot">
          <button v-if="edit.id" type="button" class="btn btn-sm tm-delete" :class="{ sure: sureDelete }" @click="deleteEntry"><AppIcon name="trash" /> {{ sureDelete ? p.sure : p.delete }}</button>
          <div class="tm-foot-right">
            <button type="button" class="btn btn-ghost btn-sm" @click="edit = null">{{ p.cancel }}</button>
            <button class="btn btn-primary btn-sm">{{ p.save }}</button>
          </div>
        </footer>
      </form>
    </div>

    <Transition name="toast"><div v-if="failed" class="tp-toast" role="status">{{ failed }}</div></Transition>
  </div>
</template>

<style>
/* ===== Time tracking ===== */
.tt { display: grid; gap: 12px; max-width: 980px; }
.tt .btn .ico { width: 16px; height: 16px; }
.tt-timer { display: grid; justify-items: center; gap: 6px; text-align: center; }
.tt-timer.on { border-color: rgba(229, 72, 77, .4); background: color-mix(in srgb, #E5484D 6%, var(--surface)); }
.tt-clock { font-family: var(--font-display); font-weight: 600; font-size: clamp(2.4rem, 10vw, 3.4rem); letter-spacing: -.03em; font-variant-numeric: tabular-nums; line-height: 1.1; }
.tt-what { color: var(--ink-2); font-weight: 700; }
.tt-stop { min-height: 48px; background: #E5484D; color: #fff; }
.tt-start { display: grid; grid-template-columns: 1fr 1fr 1.4fr auto; gap: 8px; width: 100%; }
.tt-go { min-height: 48px; }
.tt-period { flex-wrap: wrap; }
.tt-filters { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
.tt-filters .tp-input { flex: 1 1 160px; }
.tt-range { color: var(--muted); font-weight: 600; font-size: .8rem; }
.tt-export { display: flex; gap: 6px; }
.tt-totals { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
.tt-totals div { display: grid; padding: 10px 14px; border-radius: 14px; background: var(--bg); border: 1px solid var(--line); }
.tt-totals small { color: var(--muted); font-weight: 700; font-size: .74rem; }
.tt-totals b { font-family: var(--font-display); font-weight: 600; font-size: 1.15rem; font-variant-numeric: tabular-nums; }
.tt-table { width: 100%; border-collapse: collapse; font-size: .9rem; }
.tt-table th { text-align: left; padding: 6px 8px; color: var(--muted); font-size: .74rem; text-transform: uppercase; letter-spacing: .03em; border-bottom: 1px solid var(--line-2); }
.tt-table td { padding: 8px; border-bottom: 1px solid var(--line); vertical-align: top; font-variant-numeric: tabular-nums; }
.tt-table td small { display: block; color: var(--muted); font-size: .76rem; font-weight: 600; }
.tt-table th:not(:first-child), .tt-table td:not(:first-child) { text-align: right; white-space: nowrap; }
.tt-invoice { margin-top: 12px; }
.tt-day h3 { display: flex; justify-content: space-between; margin: 12px 4px 6px; font-size: .8rem; font-weight: 800; color: var(--muted); text-transform: capitalize; }
.tt-day h3 b { color: var(--ink-2); }
.tt-entry {
  display: flex; align-items: center; gap: 10px; width: 100%; min-height: 52px; margin-bottom: 6px; padding: 8px 12px; border-radius: 14px; cursor: pointer;
  background: var(--bg); border: 1px solid var(--line); text-align: left; color: var(--ink);
}
.tt-entry.running { border-color: rgba(229, 72, 77, .45); cursor: default; }
.tt-entry.billed { opacity: .7; }
.tt-entry-time { flex: none; font-weight: 800; font-size: .8rem; color: var(--muted); font-variant-numeric: tabular-nums; }
.tt-entry-dur { flex: none; font-variant-numeric: tabular-nums; }
@media (max-width: 640px) {
  .tt-start { grid-template-columns: 1fr 1fr; }
  .tt-start input { grid-column: 1 / -1; }
  .tt-go { grid-column: 1 / -1; }
  .tt-entry-time { font-size: .74rem; }
}
/* PDF = the browser's print / "Save as PDF" of the report */
@media print {
  .tt .no-print { display: none !important; }
  .tt-report { border: 0; box-shadow: none; padding: 0; }
}
</style>
