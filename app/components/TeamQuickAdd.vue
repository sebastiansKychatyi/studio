<script setup lang="ts">
// Quick add on every panel screen: one line → preview ("Expense 3,50 € · Food · today") → save.
// Rule-based parser (utils/quickParse.ts) works offline; saving goes through the offline outbox.
// Not sure (confidence < 0.6) → the user picks the type; phase 7 can plug an AI parser in here.
import { parseQuick, type QuickKind, type QuickResult } from '~/utils/quickParse'
import type { TeamBoardFull, TeamBoardItem } from '~/composables/useTeam'

const { t } = useSite()
const { locale } = useI18n()
const localePath = useLocalePath()
const route = useRoute()
const { api, peek, users, clients, study, loadAlarms, loadEvents, loadStudy } = useTeam()
const { pref } = usePrefs()

const p = computed(() => t.value.panel)
const q = computed(() => t.value.panel.quick)
const KINDS: QuickKind[] = ['expense', 'income', 'event', 'task', 'alarm', 'work']
const ICONS: Record<QuickKind, string> = { expense: 'wallet', income: 'income', event: 'calendar', task: 'tasks', alarm: 'alarm', work: 'study' }

const open = ref(false)
const text = ref('')
const forced = ref<QuickKind | null>(null)
const busy = ref(false)
const done = ref('')
const inputEl = ref<HTMLInputElement>()
const currency = pref<'EUR' | 'UAH' | 'USD'>('currency', 'EUR')
const openBoards = pref<number[]>('kanbanBoards', [])

const pad = (n: number) => String(n).padStart(2, '0')
const today = () => {
  const d = new Date()
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}
const parsed = computed<QuickResult>(() =>
  parseQuick(text.value, { today: today(), currency: currency.value, clients: clients.value, users: users.value, subjects: study.value.subjects }))
const kind = computed(() => forced.value ?? parsed.value.kind)
const unsure = computed(() => !forced.value && parsed.value.confidence < 0.6)
watch(text, () => (forced.value = null))

function show() {
  open.value = true
  done.value = ''
  nextTick(() => inputEl.value?.focus())
}
// PWA shortcut "Quick add" (?quick=1) and other screens' "+" buttons
watch(() => route.query.quick, (v) => {
  if (!v) return
  show()
  navigateTo({ query: { ...route.query, quick: undefined } }, { replace: true })
}, { immediate: true })
defineExpose({ show })

// Preview parts
const dayLabel = (s?: string) => {
  if (!s) return ''
  const diff = Math.round((Date.parse(s) - Date.parse(today())) / 86400000)
  return diff === 0 ? p.value.today.today.toLowerCase() : diff === 1 ? p.value.today.tomorrow.toLowerCase()
    : new Date(`${s}T12:00:00`).toLocaleDateString(locale.value, { weekday: 'short', day: 'numeric', month: 'short' })
}
const money = (n: number, cur: string) => new Intl.NumberFormat(locale.value, { style: 'currency', currency: cur, currencyDisplay: 'narrowSymbol' }).format(n)
const preview = computed(() => {
  const r = parsed.value
  const k = kind.value
  if (!k || !text.value.trim()) return []
  const client = clients.value.find((c) => c.id === r.client_id)?.name
  const who = users.value.find((u) => u.id === r.assignee_id)
  const subject = study.value.subjects.find((s) => s.id === r.subject_id)?.name
  const cats = (k === 'income' ? p.value.income.categories : p.value.expenses.categories) as Record<string, string>
  const parts: (string | undefined)[] =
    k === 'expense' || k === 'income' ? [r.amount !== undefined ? money(r.amount, r.currency ?? 'EUR') : q.value.noAmount, cats[r.category ?? 'other'], r.title, client, dayLabel(r.date)]
    : k === 'event' ? [r.title, `${dayLabel(r.date)} ${r.time ?? ''}${r.end ? `–${r.end}` : ''}`, client]
    : k === 'task' ? [r.title, r.date && `${q.value.until} ${dayLabel(r.date)}`, who && `@${who.username}`, client]
    : k === 'alarm' ? [r.time ?? q.value.noTime, r.days?.length === 7 ? p.value.alarms.everyDay : r.days?.length ? p.value.alarms.days.slice(0, 5).join(' ') : p.value.alarms.once, r.title]
    : [p.value.study.workKinds[r.workKind ?? 'assignment'], r.title, subject, r.date ? dayLabel(r.date) : q.value.noDate]
  return parts.filter(Boolean) as string[]
})
// What the chosen type still needs
const missing = computed(() => {
  const r = parsed.value
  if (kind.value === 'expense' || kind.value === 'income') return r.amount === undefined
  if (kind.value === 'alarm') return !r.time
  if (kind.value === 'work') return !r.date
  return !r.title
})

// First column of the first shown board (the task lands there)
async function taskColumn() {
  const boardId = openBoards.value[0]
  const full = boardId ? await peek<TeamBoardFull>(`/boards/${boardId}`) : undefined
  if (full?.columns[0]) return full.columns[0].id
  const list = (await peek<TeamBoardItem[]>('/boards')) ?? (await api<TeamBoardItem[]>('/boards'))
  return list[0]?.columns[0]?.id
}

async function save() {
  const r = parsed.value
  const k = kind.value
  if (!k || missing.value || busy.value) return
  busy.value = true
  try {
    if (k === 'expense' || k === 'income') {
      await api(k === 'income' ? '/income' : '/expenses', {
        method: 'POST',
        body: { amount: r.amount, currency: r.currency ?? 'EUR', category: r.category ?? 'other', note: r.title ?? '', spent_on: r.date ?? today(), ...(k === 'income' ? { client_id: r.client_id ?? null } : {}) },
      })
    } else if (k === 'event') {
      await api('/events', {
        method: 'POST',
        body: { title: r.title || q.value.event, date: r.date ?? today(), start: r.time ?? '09:00', end: r.end ?? '10:00', repeat: 'none', days: [], until: null, color: '#5B4BFF', note: '', remind: null, client_id: r.client_id ?? null },
      })
      loadEvents().catch(() => {})
    } else if (k === 'task') {
      const col = await taskColumn()
      if (!col) throw Object.assign(new Error('no board'), { status: 404 })
      await api(`/columns/${col}/cards`, { method: 'POST', body: { title: r.title, due_date: r.date ?? null, assignee_id: r.assignee_id ?? null, client_id: r.client_id ?? null } })
    } else if (k === 'alarm') {
      await api('/alarms', { method: 'POST', body: { time: r.time, label: r.title ?? '', days: r.days ?? [], enabled: true } })
      loadAlarms().catch(() => {})
    } else {
      await api('/study/works', { method: 'POST', body: { title: r.title || p.value.study.workKinds[r.workKind ?? 'assignment'], kind: r.workKind ?? 'assignment', due: r.date, due_time: r.time ?? null, subject_id: r.subject_id ?? null } })
      loadStudy().catch(() => {})
    }
    done.value = `${q.value.saved}: ${preview.value.slice(0, 2).join(' · ')}`
    text.value = ''
    setTimeout(() => (done.value = ''), 3000)
    open.value = false
  } catch (e) {
    done.value = isOffline(e) ? p.value.offlineOnly : httpStatus(e) === 404 && k === 'task' ? q.value.noBoard : p.value.errorServer
    setTimeout(() => (done.value = ''), 3500)
  } finally {
    busy.value = false
  }
}

// Full forms, when a line is not enough
const forms = computed(() => [
  { icon: 'tasks', label: q.value.kinds.task, to: localePath('/panel?new=task') },
  { icon: 'calendar', label: q.value.kinds.event, to: localePath(`/panel/calendar?new=event&date=${today()}`) },
  { icon: 'wallet', label: q.value.kinds.expense, to: localePath('/panel/expenses?new=expense') },
  { icon: 'alarm', label: q.value.kinds.alarm, to: localePath('/panel/alarms?new=alarm') },
])
const onKey = (e: KeyboardEvent) => e.key === 'Escape' && (open.value = false)
onMounted(() => addEventListener('keydown', onKey))
onBeforeUnmount(() => removeEventListener('keydown', onKey))
</script>

<template>
  <button type="button" class="qa-fab" :aria-label="q.title" :title="q.title" @click="show"><AppIcon name="plus" /></button>

  <div v-if="open" class="tm-overlay qa" @click.self="open = false">
    <form class="tm tm-sm" role="dialog" aria-modal="true" :aria-label="q.title" @submit.prevent="save">
      <header class="tm-head">
        <h2>{{ q.title }}</h2>
        <button type="button" class="tp-icon-btn sm" :aria-label="p.close" @click="open = false"><AppIcon name="close" /></button>
      </header>
      <input ref="inputEl" v-model="text" class="tp-input qa-input" maxlength="300" :placeholder="q.placeholder" enterkeyhint="done" autocomplete="off" :aria-label="q.title">
      <p class="qa-examples">{{ q.examples }}</p>

      <div v-if="text.trim()" class="qa-preview" :class="{ unsure }">
        <span class="qa-icon"><AppIcon :name="kind ? ICONS[kind] : 'spark'" /></span>
        <span class="qa-text">
          <b>{{ kind ? q.kinds[kind] : q.unknown }}</b>
          <small>{{ preview.join(' · ') }}</small>
        </span>
      </div>
      <!-- Not sure / wrong type: pick it -->
      <div v-if="text.trim()" class="qa-kinds" role="radiogroup" :aria-label="q.clarify">
        <span v-if="unsure" class="qa-unsure">{{ q.clarify }}</span>
        <button v-for="k in KINDS" :key="k" type="button" role="radio" :aria-checked="kind === k" :class="{ on: kind === k }" @click="forced = k">
          <AppIcon :name="ICONS[k]" />{{ q.kinds[k] }}
        </button>
      </div>
      <p v-if="text.trim() && missing" class="qa-missing">{{ q.missing[kind ?? 'task'] }}</p>

      <footer class="tm-foot">
        <nav class="qa-forms" :aria-label="q.forms">
          <NuxtLink v-for="x in forms" :key="x.icon" :to="x.to" :title="x.label" :aria-label="x.label" class="tp-icon-btn sm" @click="open = false"><AppIcon :name="x.icon" /></NuxtLink>
        </nav>
        <button class="btn btn-primary btn-sm" :disabled="!text.trim() || missing || busy">{{ p.save }}</button>
      </footer>
    </form>
  </div>
  <Transition name="toast"><div v-if="done" class="tp-toast qa-toast" role="status">{{ done }}</div></Transition>
</template>

<style>
/* ===== Quick add ===== */
.qa-fab {
  position: fixed; right: max(18px, env(safe-area-inset-right)); bottom: 28px; z-index: 65; display: grid; place-items: center;
  width: 56px; height: 56px; border-radius: 18px; border: 0; cursor: pointer; background: var(--accent); color: #fff;
  box-shadow: 0 12px 30px -10px rgba(91, 75, 255, .7); transition: transform .3s var(--ease);
}
.qa-fab:hover { transform: translateY(-2px) rotate(90deg); }
.qa-fab .ico { width: 24px; height: 24px; }
@media (max-width: 860px) { .qa-fab { bottom: calc(86px + env(safe-area-inset-bottom)); } }
@media print { .qa-fab { display: none !important; } }
.qa-input { width: 100%; font-size: 1.05rem !important; padding: 14px 16px; }
.qa-examples { margin: 6px 2px 12px; color: var(--muted); font-size: .78rem; font-weight: 600; }
.qa-preview { display: flex; align-items: center; gap: 12px; padding: 12px; border-radius: 16px; background: rgba(91, 75, 255, .08); border: 1px solid rgba(91, 75, 255, .25); }
.qa-preview.unsure { background: rgba(245, 158, 11, .1); border-color: rgba(245, 158, 11, .4); }
.qa-icon { flex: none; display: grid; place-items: center; width: 40px; height: 40px; border-radius: 12px; background: var(--surface); color: var(--accent); }
.qa-icon .ico { width: 20px; height: 20px; }
.qa-text { min-width: 0; display: grid; line-height: 1.3; }
.qa-text small { color: var(--ink-2); font-weight: 600; font-size: .84rem; overflow-wrap: anywhere; }
.qa-kinds { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin-top: 10px; }
.qa-unsure { flex-basis: 100%; color: #C27803; font-weight: 800; font-size: .8rem; }
.qa-kinds button {
  display: inline-flex; align-items: center; gap: 5px; min-height: 36px; padding: 0 10px; border-radius: 999px; cursor: pointer;
  border: 1px solid var(--line-2); background: none; color: var(--ink-2); font-weight: 700; font-size: .78rem;
}
.qa-kinds button .ico { width: 14px; height: 14px; }
.qa-kinds button.on { background: var(--accent); border-color: var(--accent); color: #fff; }
.qa-missing { margin-top: 8px; color: #E5484D; font-weight: 700; font-size: .8rem; }
.qa-forms { display: flex; gap: 4px; }
.qa .tm-foot { margin-top: 14px; }
.qa-toast { bottom: calc(150px + env(safe-area-inset-bottom)); }
</style>
