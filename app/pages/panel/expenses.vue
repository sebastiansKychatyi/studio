<script setup lang="ts">
// Personal expenses (EUR): month view, stats, categories, 6-month chart, CSV export
import { EXPENSE_CATEGORIES, type ExpenseCategory, type TeamExpense } from '~/composables/useTeam'

const { t } = useSite()
const { locale } = useI18n()
const localePath = useLocalePath()
const { api } = useTeam()

const p = computed(() => t.value.panel)
const e = computed(() => t.value.panel.expenses)

const COLORS: Record<ExpenseCategory, string> = {
  food: '#FF7A59', transport: '#3B82F6', home: '#5B4BFF', software: '#19C3A6',
  tech: '#8B5CF6', fun: '#F59E0B', health: '#EC4899', other: '#9CA3AF',
}

// Local dates (no UTC shift)
const pad = (n: number) => String(n).padStart(2, '0')
const ymd = (d: Date) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
const today = ymd(new Date())
const thisMonth = today.slice(0, 7)
const shiftMonth = (m: string, n: number) => {
  const [y, mo] = m.split('-').map(Number)
  const d = new Date(y!, mo! - 1 + n, 1)
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}`
}
const asDate = (s: string) => new Date(`${s}T12:00:00`)

const month = ref(thisMonth)
const items = ref<TeamExpense[]>([])
const history = ref<{ month: string; total: number }[]>([])
const loading = ref(true)
const ready = ref(false)
const failed = ref(false)

const money = computed(() => new Intl.NumberFormat(locale.value, { style: 'currency', currency: 'EUR', currencyDisplay: 'narrowSymbol' }))
const fmt = (n: number) => money.value.format(n)
const monthLabel = (m: string, opts: Intl.DateTimeFormatOptions = { month: 'long', year: 'numeric' }) =>
  asDate(`${m}-01`).toLocaleDateString(locale.value, opts)

function fail(err: unknown) {
  if (httpStatus(err) === 401) return navigateTo(localePath('/login'))
  failed.value = true
  setTimeout(() => (failed.value = false), 3000)
}

async function load() {
  ready.value = false
  try {
    const [list, sum] = await Promise.all([
      api<TeamExpense[]>('/expenses', { query: { month: month.value } }),
      api<{ month: string; total: number }[]>('/expenses/summary', { query: { month: month.value } }),
    ])
    items.value = list
    history.value = sum
  } catch (err) {
    fail(err)
  } finally {
    loading.value = false
    // Let bars grow from zero
    setTimeout(() => (ready.value = true), 60)
  }
}

watch(month, () => {
  resetForm()
  load()
})
onMounted(load)

// Stats
const total = computed(() => items.value.reduce((s, x) => s + x.amount, 0))
const prevTotal = computed(() => history.value.at(-2)?.total ?? 0)
const delta = computed(() => (prevTotal.value ? Math.round(((total.value - prevTotal.value) / prevTotal.value) * 100) : null))
const perDay = computed(() => {
  const [y, m] = month.value.split('-').map(Number)
  const days = month.value === thisMonth ? new Date().getDate() : new Date(y!, m!, 0).getDate()
  return month.value > thisMonth ? 0 : total.value / days
})

const byCategory = computed(() => {
  const sums = new Map<ExpenseCategory, number>()
  for (const x of items.value) sums.set(x.category, (sums.get(x.category) ?? 0) + x.amount)
  return [...sums.entries()]
    .map(([cat, sum]) => ({ cat, sum, pct: total.value ? (sum / total.value) * 100 : 0 }))
    .sort((a, b) => b.sum - a.sum)
})
const maxMonth = computed(() => Math.max(...history.value.map((h) => h.total), 1))

const days = computed(() => {
  const groups: { date: string; label: string; sum: number; items: TeamExpense[] }[] = []
  for (const x of items.value) {
    let g = groups.at(-1)
    if (g?.date !== x.spent_on) {
      g = { date: x.spent_on, label: asDate(x.spent_on).toLocaleDateString(locale.value, { weekday: 'short', day: 'numeric', month: 'long' }), sum: 0, items: [] }
      groups.push(g)
    }
    g.sum += x.amount
    g.items.push(x)
  }
  return groups
})

// Animated total
const shown = ref(0)
let tween: ReturnType<typeof setInterval> | undefined
watch(total, (to) => {
  clearInterval(tween)
  const from = shown.value
  const start = Date.now()
  tween = setInterval(() => {
    const k = Math.min((Date.now() - start) / 600, 1)
    shown.value = from + (to - from) * (1 - (1 - k) ** 3)
    if (k === 1) clearInterval(tween)
  }, 16)
})
onBeforeUnmount(() => clearInterval(tween))

// Form (add / edit)
const formEl = ref<HTMLElement>()
const editingId = ref<number | null>(null)
const busy = ref(false)
const amountError = ref(false)
const form = reactive({ amount: '', category: 'food' as ExpenseCategory, note: '', spent_on: today })

function resetForm() {
  editingId.value = null
  amountError.value = false
  form.amount = ''
  form.note = ''
  form.spent_on = month.value === thisMonth ? today : `${month.value}-01`
}

function edit(x: TeamExpense) {
  editingId.value = x.id
  form.amount = x.amount.toFixed(2).replace('.', locale.value === 'en' ? '.' : ',')
  form.category = x.category
  form.note = x.note
  form.spent_on = x.spent_on
  formEl.value?.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

async function save() {
  const amount = Math.round(Number(form.amount.replace(',', '.').replace(/\s/g, '')) * 100) / 100
  amountError.value = !(amount > 0 && amount <= 1_000_000)
  if (amountError.value || busy.value || !form.spent_on) return
  busy.value = true
  const body = { amount, category: form.category, note: form.note.trim(), spent_on: form.spent_on }
  try {
    if (editingId.value) await api(`/expenses/${editingId.value}`, { method: 'PATCH', body })
    else await api('/expenses', { method: 'POST', body })
    const keepCategory = form.category
    resetForm()
    form.category = keepCategory
    await load()
  } catch (err) {
    fail(err)
  } finally {
    busy.value = false
  }
}

const confirmId = ref<number | null>(null)
async function remove(x: TeamExpense) {
  if (confirmId.value !== x.id) {
    confirmId.value = x.id
    setTimeout(() => confirmId.value === x.id && (confirmId.value = null), 3000)
    return
  }
  items.value = items.value.filter((i) => i !== x)
  if (editingId.value === x.id) resetForm()
  try {
    await api(`/expenses/${x.id}`, { method: 'DELETE' })
    await load()
  } catch (err) {
    fail(err)
  }
}

// CSV for Excel: BOM, ";" separator, decimal comma outside English
function exportCsv() {
  const dec = locale.value === 'en' ? '.' : ','
  const cell = (s: string) => `"${s.replace(/"/g, '""')}"`
  const rows = [[e.value.date, e.value.category, e.value.amount, e.value.note].map(cell).join(';')]
  for (const x of [...items.value].reverse()) {
    rows.push([x.spent_on, cell(e.value.categories[x.category]), x.amount.toFixed(2).replace('.', dec), cell(x.note)].join(';'))
  }
  const url = URL.createObjectURL(new Blob(['﻿' + rows.join('\r\n')], { type: 'text/csv;charset=utf-8' }))
  const a = document.createElement('a')
  a.href = url
  a.download = `expenses-${month.value}.csv`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <div class="ex">
    <header class="tp-head">
      <div>
        <h1>{{ e.title }}</h1>
        <p>{{ e.subtitle }}</p>
      </div>
      <div class="ex-head-actions">
        <div class="ex-month">
          <button type="button" class="tp-icon-btn sm" :title="e.prev" :aria-label="e.prev" @click="month = shiftMonth(month, -1)"><AppIcon name="left" /></button>
          <Transition name="ex-flip" mode="out-in">
            <span :key="month" class="ex-month-label">{{ monthLabel(month) }}</span>
          </Transition>
          <button type="button" class="tp-icon-btn sm" :title="e.next" :aria-label="e.next" @click="month = shiftMonth(month, 1)"><AppIcon name="right" /></button>
        </div>
        <button type="button" class="btn btn-ghost btn-sm" :disabled="!items.length" @click="exportCsv"><AppIcon name="download" /> {{ e.export }}</button>
      </div>
    </header>

    <!-- Stats -->
    <div class="ex-stats">
      <section class="ex-stat ex-stat-main">
        <p class="ex-stat-label">{{ e.total }}</p>
        <p class="ex-stat-value">{{ fmt(shown) }}</p>
        <p v-if="delta !== null" class="ex-delta" :class="delta > 0 ? 'up' : 'down'">
          {{ delta > 0 ? '▲' : '▼' }} {{ Math.abs(delta) }} % <span>{{ e.vsPrev }}</span>
        </p>
      </section>
      <section class="ex-stat">
        <p class="ex-stat-label">{{ e.perDay }}</p>
        <p class="ex-stat-value sm">{{ fmt(perDay) }}</p>
      </section>
      <section class="ex-stat">
        <p class="ex-stat-label">{{ e.count }}</p>
        <p class="ex-stat-value sm">{{ items.length }}</p>
      </section>
    </div>

    <div class="ex-grid">
      <!-- Add / edit -->
      <form ref="formEl" class="ex-card ex-form" :class="{ editing: editingId }" @submit.prevent="save">
        <h2>{{ editingId ? e.editing : e.add }}</h2>
        <div class="ex-form-row">
          <label class="tp-field">
            <span>{{ e.amount }}</span>
            <input
              v-model="form.amount"
              inputmode="decimal"
              autocomplete="off"
              placeholder="0,00"
              required
              :class="{ invalid: amountError }"
              @input="amountError = false"
            >
          </label>
          <label class="tp-field">
            <span>{{ e.date }}</span>
            <input v-model="form.spent_on" type="date" required>
          </label>
        </div>
        <div class="tp-field">
          <span>{{ e.category }}</span>
          <div class="ex-cats" role="radiogroup" :aria-label="e.category">
            <button
              v-for="c in EXPENSE_CATEGORIES"
              :key="c"
              type="button"
              role="radio"
              class="ex-cat"
              :class="{ on: form.category === c }"
              :aria-checked="form.category === c"
              :style="{ '--c': COLORS[c] }"
              @click="form.category = c"
            >
              <i />{{ e.categories[c] }}
            </button>
          </div>
        </div>
        <label class="tp-field">
          <span>{{ e.note }}</span>
          <input v-model="form.note" maxlength="200" :placeholder="e.notePh">
        </label>
        <div class="ex-form-actions">
          <button class="btn btn-primary" :disabled="busy">
            <AppIcon :name="editingId ? 'edit' : 'plus'" /> {{ editingId ? p.save : e.add }}
          </button>
          <button v-if="editingId" type="button" class="btn btn-ghost" @click="resetForm">{{ p.cancel }}</button>
        </div>
      </form>

      <div class="ex-side">
        <!-- Categories -->
        <section class="ex-card">
          <h2>{{ e.byCategory }}</h2>
          <ul v-if="byCategory.length" class="ex-bars">
            <li v-for="row in byCategory" :key="row.cat" :style="{ '--c': COLORS[row.cat] }">
              <div class="ex-bar-text">
                <span><i />{{ e.categories[row.cat] }}</span>
                <b>{{ fmt(row.sum) }}</b>
              </div>
              <div class="ex-bar"><span :style="{ width: ready ? `${row.pct.toFixed(1)}%` : '0%' }" /></div>
            </li>
          </ul>
          <p v-else class="ex-muted">{{ e.empty }}</p>
        </section>

        <!-- Last 6 months -->
        <section class="ex-card">
          <h2>{{ e.history }}</h2>
          <div class="ex-chart">
            <button
              v-for="h in history"
              :key="h.month"
              type="button"
              class="ex-col"
              :class="{ active: h.month === month }"
              :title="`${monthLabel(h.month)}: ${fmt(h.total)}`"
              @click="month = h.month"
            >
              <span class="ex-col-val">{{ h.total ? Math.round(h.total) : '' }}</span>
              <span class="ex-col-bar" :style="{ height: ready ? `${Math.max((h.total / maxMonth) * 100, 2).toFixed(1)}%` : '2%' }" />
              <span class="ex-col-label">{{ monthLabel(h.month, { month: 'short' }) }}</span>
            </button>
          </div>
        </section>
      </div>
    </div>

    <!-- List by day -->
    <div v-if="loading" class="kb-loading"><span class="spinner" /></div>
    <div v-else-if="days.length" class="ex-days">
      <section v-for="d in days" :key="d.date" class="ex-day">
        <header><span>{{ d.label }}</span><b>{{ fmt(d.sum) }}</b></header>
        <TransitionGroup tag="ul" name="kb-card">
          <li
            v-for="x in d.items"
            :key="x.id"
            class="ex-row"
            :class="{ editing: editingId === x.id }"
            :style="{ '--c': COLORS[x.category] }"
          >
            <button type="button" class="ex-row-main" @click="edit(x)">
              <i class="ex-dot" />
              <span class="ex-row-text">
                <b>{{ x.note || e.categories[x.category] }}</b>
                <small v-if="x.note">{{ e.categories[x.category] }}</small>
              </span>
              <span class="ex-row-amount">−{{ fmt(x.amount) }}</span>
            </button>
            <button
              type="button"
              class="tp-icon-btn sm danger"
              :class="{ confirm: confirmId === x.id }"
              :title="confirmId === x.id ? p.sure : p.delete"
              :aria-label="confirmId === x.id ? p.sure : p.delete"
              @click="remove(x)"
            >
              <AppIcon name="trash" />
            </button>
          </li>
        </TransitionGroup>
      </section>
    </div>
    <p v-else class="al-empty">{{ e.empty }}</p>

    <Transition name="toast"><div v-if="failed" class="tp-toast" role="status">{{ p.errorServer }}</div></Transition>
  </div>
</template>

<style>
/* ===== Expenses ===== */
.ex-head-actions { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; }
.ex-month { display: flex; align-items: center; gap: 6px; padding: 4px; border-radius: 999px; background: var(--surface); border: 1px solid var(--line); }
.ex-month-label { min-width: 150px; text-align: center; font-weight: 800; font-size: .95rem; }
.ex-month-label::first-letter { text-transform: uppercase; }
.ex-flip-enter-active, .ex-flip-leave-active { transition: opacity .2s, transform .25s var(--ease); }
.ex-flip-enter-from { opacity: 0; transform: translateY(8px); }
.ex-flip-leave-to { opacity: 0; transform: translateY(-8px); }
.ex-head-actions .btn .ico { width: 16px; height: 16px; }
.ex-head-actions .btn:disabled { opacity: .45; cursor: default; }

.ex-stats { display: grid; grid-template-columns: 1.4fr 1fr 1fr; gap: 14px; margin-bottom: 18px; }
.ex-stat {
  padding: 20px 22px; border-radius: 22px; background: var(--surface); border: 1px solid var(--line);
  animation: tpUp .6s var(--ease) both;
}
.ex-stat:nth-child(2) { animation-delay: .05s; }
.ex-stat:nth-child(3) { animation-delay: .1s; }
.ex-stat-main { position: relative; overflow: hidden; background: var(--ink); color: #fff; border-color: var(--ink); }
.ex-stat-main::after {
  content: ''; position: absolute; right: -60px; top: -60px; width: 180px; height: 180px; border-radius: 50%;
  background: radial-gradient(circle, rgba(91, 75, 255, .55), transparent 70%); animation: float1 14s ease-in-out infinite;
}
.ex-stat-label { font-size: .82rem; font-weight: 700; color: var(--muted); }
.ex-stat-main .ex-stat-label { color: rgba(255, 255, 255, .6); }
.ex-stat-value { position: relative; z-index: 1; font-family: var(--font-display); font-weight: 600; font-size: clamp(1.8rem, 3.2vw, 2.4rem); letter-spacing: -.03em; line-height: 1.15; margin-top: 4px; font-variant-numeric: tabular-nums; }
.ex-stat-value.sm { font-size: clamp(1.3rem, 2.4vw, 1.7rem); }
.ex-delta { position: relative; z-index: 1; margin-top: 6px; font-size: .82rem; font-weight: 800; }
.ex-delta.up { color: #FFB4A2; }
.ex-delta.down { color: #7DEBD6; }
.ex-delta span { font-weight: 600; color: rgba(255, 255, 255, .55); }

.ex-grid { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 18px; margin-bottom: 26px; align-items: start; }
.ex-side { display: grid; gap: 18px; }
.ex-card { padding: 22px; border-radius: var(--radius); background: var(--surface); border: 1px solid var(--line); box-shadow: var(--shadow); animation: tpUp .7s var(--ease) both; }
.ex-card h2 { font-size: 1rem; font-weight: 800; margin-bottom: 16px; }
.ex-form { transition: box-shadow .3s, border-color .3s; }
.ex-form.editing { border-color: rgba(91, 75, 255, .45); box-shadow: 0 0 0 4px rgba(91, 75, 255, .1), var(--shadow); }
.ex-form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.ex-form input.invalid { border-color: #E5484D; box-shadow: 0 0 0 4px rgba(229, 72, 77, .12); }
.ex-form input[inputmode="decimal"] { font-family: var(--font-display); font-weight: 600; font-size: 1.15rem; }
.ex-cats { display: flex; flex-wrap: wrap; gap: 6px; }
.ex-cat {
  display: inline-flex; align-items: center; gap: 7px; padding: 7px 12px; border-radius: 999px; cursor: pointer;
  border: 1px solid var(--line-2); background: #fff; font-size: .82rem; font-weight: 700; color: var(--ink-2);
  transition: background .2s, color .2s, border-color .2s, transform .3s var(--ease);
}
.ex-cat i { width: 8px; height: 8px; border-radius: 50%; background: var(--c); transition: background .2s; }
.ex-cat:hover { border-color: var(--c); }
.ex-cat.on { background: var(--c); border-color: var(--c); color: #fff; transform: translateY(-1px); }
.ex-cat.on i { background: #fff; }
.ex-form-actions { display: flex; gap: 8px; margin-top: 4px; }
.ex-form-actions .btn:disabled { opacity: .7; cursor: progress; }

.ex-bars { display: grid; gap: 12px; }
.ex-bar-text { display: flex; justify-content: space-between; gap: 10px; font-size: .88rem; margin-bottom: 5px; }
.ex-bar-text span { display: flex; align-items: center; gap: 8px; font-weight: 700; color: var(--ink-2); }
.ex-bar-text i { width: 10px; height: 10px; border-radius: 3px; background: var(--c); }
.ex-bar-text b { font-variant-numeric: tabular-nums; }
.ex-bar { height: 8px; border-radius: 99px; background: var(--bg-2); overflow: hidden; }
.ex-bar span { display: block; height: 100%; border-radius: inherit; background: var(--c); transition: width .9s var(--ease); }
.ex-muted { color: var(--muted); font-size: .9rem; }

.ex-chart { display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; height: 170px; }
.ex-col { display: grid; grid-template-rows: auto 1fr auto; justify-items: center; gap: 6px; padding: 0; border: 0; background: none; cursor: pointer; min-width: 0; }
.ex-col-val { font-size: .72rem; font-weight: 800; color: var(--muted); height: 1em; }
.ex-col-bar {
  align-self: end; width: 100%; max-width: 44px; border-radius: 10px 10px 4px 4px; background: var(--bg-2);
  transition: height .9s var(--ease), background .25s;
}
.ex-col:hover .ex-col-bar { background: #D9D4FF; }
.ex-col.active .ex-col-bar { background: linear-gradient(180deg, #8B7FFF, var(--accent)); }
.ex-col.active .ex-col-val { color: var(--accent); }
.ex-col-label { font-size: .75rem; font-weight: 700; color: var(--muted); text-transform: capitalize; }
.ex-col.active .ex-col-label { color: var(--ink); }

.ex-days { display: grid; gap: 18px; }
.ex-day header { display: flex; justify-content: space-between; padding: 0 6px 8px; font-size: .85rem; font-weight: 800; color: var(--muted); }
.ex-day header span::first-letter { text-transform: uppercase; }
.ex-day header b { color: var(--ink-2); font-variant-numeric: tabular-nums; }
.ex-day ul { display: grid; gap: 6px; }
.ex-row {
  display: flex; align-items: center; gap: 8px; padding: 4px 10px 4px 4px; border-radius: 16px;
  background: var(--surface); border: 1px solid var(--line); transition: box-shadow .25s, border-color .25s;
}
.ex-row:hover { box-shadow: var(--shadow); }
.ex-row.editing { border-color: rgba(91, 75, 255, .45); }
.ex-row-main { flex: 1; min-width: 0; display: flex; align-items: center; gap: 12px; padding: 10px 12px; border: 0; background: none; cursor: pointer; text-align: left; }
.ex-dot { flex: none; width: 34px; height: 34px; border-radius: 11px; background: var(--c); opacity: .9; box-shadow: inset 0 0 0 9px rgba(255, 255, 255, .55); }
.ex-row-text { flex: 1; min-width: 0; display: grid; line-height: 1.3; }
.ex-row-text b { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: .95rem; }
.ex-row-text small { color: var(--muted); font-weight: 600; font-size: .78rem; }
.ex-row-amount { font-weight: 800; font-variant-numeric: tabular-nums; white-space: nowrap; }

@media (max-width: 1100px) { .ex-grid { grid-template-columns: 1fr; } }
@media (max-width: 640px) {
  .ex-stats { grid-template-columns: 1fr 1fr; }
  .ex-stat-main { grid-column: 1 / -1; }
  .ex-form-row { grid-template-columns: 1fr; }
  .ex-month-label { min-width: 120px; }
}
</style>
