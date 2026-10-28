<script setup lang="ts">
// Monthly templates (rent, subscriptions, salary…) with a one-click "paid" / "received" per month.
// A template without amount is variable: the amount is asked on click, prefilled with the last one.
import { CURRENCIES, type Currency, type MoneyCat, type MoneyKind, type TeamMoney } from '~/composables/useTeam'

interface Template {
  id: number
  title: string
  category: string
  amount: number | null
  currency: Currency
  day: number
  entry: TeamMoney | null
  last_amount: number | null
  last_currency: Currency | null
}

const props = defineProps<{
  kind: MoneyKind
  month: string // YYYY-MM
  thisMonth: string
  today: string // YYYY-MM-DD
  cats: MoneyCat[]
  rates: Record<Currency, number>
  view: Currency
}>()
const emit = defineEmits<{ changed: []; error: [err: unknown] }>()

const { t } = useSite()
const { locale } = useI18n()
const { api } = useTeam()
const r = computed(() => t.value.panel.recurring)
const k = computed(() => t.value.panel[props.kind].rec)

const SYMBOLS: Record<Currency, string> = { EUR: '€', UAH: '₴', USD: '$' }
const fmtIn = (n: number, currency: Currency) =>
  new Intl.NumberFormat(locale.value, { style: 'currency', currency, currencyDisplay: 'narrowSymbol' }).format(n)
const cat = (key: string) => props.cats.find((c) => c.key === key) ?? props.cats.at(-1)!
const parse = (s: string) => Math.round(Number(s.replace(',', '.').replace(/\s/g, '')) * 100) / 100
const decimal = (n: number) => n.toFixed(2).replace('.', locale.value === 'en' ? '.' : ',')

const items = ref<Template[]>([])
const loading = ref(true)

async function load() {
  try {
    items.value = await api<Template[]>(`/${props.kind}/recurring`, { query: { month: props.month } })
  } catch (e) {
    emit('error', e)
  } finally {
    loading.value = false
  }
}
watch(() => [props.kind, props.month], load)
onMounted(load)
defineExpose({ load })

// Status in the shown month
const lastDay = computed(() => {
  const [y, m] = props.month.split('-').map(Number)
  return new Date(y!, m!, 0).getDate()
})
const dueDay = (x: Template) => Math.min(x.day, lastDay.value)
function status(x: Template) {
  if (x.entry) return 'done'
  if (props.month < props.thisMonth) return 'late'
  if (props.month > props.thisMonth) return 'wait'
  const today = Number(props.today.slice(8))
  return dueDay(x) < today ? 'late' : dueDay(x) - today <= 3 ? 'soon' : 'wait'
}
const sorted = computed(() => [...items.value].sort((a, b) => Number(!!a.entry) - Number(!!b.entry) || dueDay(a) - dueDay(b)))
// Still expected this month (fixed amounts only), in the display currency
const expected = computed(() =>
  items.value
    .filter((x) => !x.entry && x.amount)
    .reduce((s, x) => s + (x.amount! / props.rates[x.currency]) * props.rates[props.view], 0)
)
const variableLeft = computed(() => items.value.filter((x) => !x.entry && !x.amount).length)
const doneCount = computed(() => items.value.filter((x) => x.entry).length)

// Pay / receive
const busyId = ref<number | null>(null)
const asking = ref<number | null>(null) // template whose amount is being entered
const ask = reactive({ amount: '', currency: 'EUR' as Currency, error: false })
const vFocus = { mounted: (el: HTMLInputElement) => (el.focus(), el.select()) }

function payDate(x: Template) {
  // Today in the current month, otherwise the template's day
  return props.month === props.thisMonth ? props.today : `${props.month}-${String(dueDay(x)).padStart(2, '0')}`
}

function startPay(x: Template) {
  if (x.amount) return pay(x)
  asking.value = x.id
  ask.amount = x.last_amount ? decimal(x.last_amount) : ''
  ask.currency = x.last_currency ?? x.currency
  ask.error = false
}

async function pay(x: Template, amount?: number, currency?: Currency) {
  if (busyId.value) return
  busyId.value = x.id
  try {
    const body = { month: props.month, spent_on: payDate(x), amount, currency }
    x.entry = await api<TeamMoney>(`/${props.kind}/recurring/${x.id}/pay`, { method: 'POST', body })
    asking.value = null
    emit('changed')
  } catch (e) {
    emit('error', e)
    await load()
  } finally {
    busyId.value = null
  }
}

function confirmAsk(x: Template) {
  const amount = parse(ask.amount)
  ask.error = !(amount > 0)
  if (!ask.error) pay(x, amount, ask.currency)
}

async function undo(x: Template) {
  if (!x.entry || busyId.value) return
  busyId.value = x.id
  try {
    await api(`/${props.kind}/${x.entry.id}`, { method: 'DELETE' })
    x.entry = null
    emit('changed')
  } catch (e) {
    emit('error', e)
  } finally {
    busyId.value = null
  }
}

// Add / edit template
const editing = ref<number | 'new' | null>(null)
const form = reactive({ title: '', amount: '', currency: 'EUR' as Currency, day: 1, category: '' })
const formError = ref(false)

function openForm(x?: Template) {
  editing.value = x ? x.id : 'new'
  formError.value = false
  Object.assign(form, x
    ? { title: x.title, amount: x.amount ? decimal(x.amount) : '', currency: x.currency, day: x.day, category: x.category }
    : { title: '', amount: '', currency: props.view, day: Number(props.today.slice(8)), category: props.cats[0]?.key ?? 'other' })
}

async function saveForm() {
  const amount = form.amount.trim() ? parse(form.amount) : null
  formError.value = amount !== null && !(amount > 0)
  if (formError.value || !form.title.trim()) return
  const body = { title: form.title.trim(), amount, currency: form.currency, day: Math.min(Math.max(Number(form.day) || 1, 1), 31), category: form.category }
  try {
    if (editing.value === 'new') await api(`/${props.kind}/recurring`, { method: 'POST', body })
    else await api(`/${props.kind}/recurring/${editing.value}`, { method: 'PATCH', body })
    editing.value = null
    await load()
  } catch (e) {
    emit('error', e)
  }
}

const confirmDel = ref(false)
async function removeTemplate() {
  if (!confirmDel.value) {
    confirmDel.value = true
    setTimeout(() => (confirmDel.value = false), 3000)
    return
  }
  confirmDel.value = false
  const id = editing.value
  editing.value = null
  try {
    await api(`/${props.kind}/recurring/${id}`, { method: 'DELETE' })
    await load()
  } catch (e) {
    emit('error', e)
  }
}
</script>

<template>
  <section class="rc" :class="`rc-${kind}`">
    <header class="rc-head">
      <div>
        <h2><AppIcon name="repeat" /> {{ k.title }} <span v-if="items.length" class="rc-count">{{ doneCount }} / {{ items.length }}</span></h2>
        <p v-if="expected || variableLeft">
          {{ r.expected }}: <b>{{ fmtIn(expected, view) }}</b><template v-if="variableLeft"> + {{ variableLeft }} × {{ r.variable.toLowerCase() }}</template>
        </p>
        <p v-else-if="items.length" class="rc-all">✓ {{ k.allDone }}</p>
      </div>
      <button type="button" class="btn btn-ghost btn-sm" @click="openForm()"><AppIcon name="plus" /> {{ k.new }}</button>
    </header>

    <!-- Template form -->
    <Transition name="rc-form">
      <form v-if="editing" class="rc-form" @submit.prevent="saveForm">
        <div class="rc-form-grid">
          <label class="tp-field">
            <span>{{ r.name }}</span>
            <input v-model="form.title" v-focus maxlength="120" required :placeholder="k.namePh">
          </label>
          <label class="tp-field">
            <span>{{ r.amount }}</span>
            <span class="ex-amount">
              <input v-model="form.amount" inputmode="decimal" autocomplete="off" :placeholder="r.variable" :class="{ invalid: formError }">
              <span class="ex-seg sm" role="radiogroup" :aria-label="r.amount">
                <button v-for="c in CURRENCIES" :key="c" type="button" role="radio" :aria-checked="form.currency === c" :class="{ on: form.currency === c }" @click="form.currency = c">{{ SYMBOLS[c] }}</button>
              </span>
            </span>
            <small class="rc-hint">{{ r.variableHint }}</small>
          </label>
          <label class="tp-field rc-day">
            <span>{{ r.day }}</span>
            <input v-model.number="form.day" type="number" min="1" max="31" required>
          </label>
        </div>
        <div class="tp-field">
          <span>{{ t.panel[kind].category }}</span>
          <div class="ex-cats">
            <button
              v-for="c in cats"
              :key="c.key"
              type="button"
              class="ex-cat"
              :class="{ on: form.category === c.key }"
              :style="{ '--c': c.color }"
              @click="form.category = c.key"
            >
              <AppIcon :name="c.icon" />{{ c.name }}
            </button>
          </div>
        </div>
        <div class="rc-form-actions">
          <button class="btn btn-primary btn-sm">{{ t.panel.save }}</button>
          <button type="button" class="btn btn-ghost btn-sm" @click="editing = null">{{ t.panel.cancel }}</button>
          <button v-if="editing !== 'new'" type="button" class="btn btn-sm tm-delete" :class="{ sure: confirmDel }" @click="removeTemplate">
            <AppIcon name="trash" /> {{ confirmDel ? t.panel.sure : t.panel.delete }}
          </button>
        </div>
      </form>
    </Transition>

    <div v-if="loading" class="rc-empty"><span class="spinner" /></div>
    <p v-else-if="!items.length && !editing" class="rc-empty">{{ k.empty }}</p>
    <TransitionGroup v-else tag="ul" name="kb-card" class="rc-list">
      <li v-for="x in sorted" :key="x.id" class="rc-item" :class="status(x)" :style="{ '--c': cat(x.category).color }">
        <span class="ex-dot"><AppIcon :name="cat(x.category).icon" /></span>
        <button type="button" class="rc-text" :title="r.edit" @click="openForm(x)">
          <b>{{ x.title }}</b>
          <small>
            {{ r.every }} {{ dueDay(x) }}.
            · {{ x.amount ? fmtIn(x.amount, x.currency) : r.variable }}
            <template v-if="status(x) === 'late'"> · <em>{{ r.overdue }}</em></template>
          </small>
        </button>

        <!-- Done: amount + undo -->
        <template v-if="x.entry">
          <span class="rc-done"><small>✓ {{ k.done }}</small><b>{{ fmtIn(x.entry.original_amount, x.entry.currency) }}</b></span>
          <button type="button" class="tp-icon-btn sm rc-undo" :disabled="busyId === x.id" :title="r.undo" :aria-label="r.undo" @click="undo(x)"><AppIcon name="close" /></button>
        </template>

        <!-- Variable amount: ask inline -->
        <form v-else-if="asking === x.id" class="rc-ask" @submit.prevent="confirmAsk(x)">
          <span class="ex-amount">
            <input v-model="ask.amount" v-focus inputmode="decimal" autocomplete="off" placeholder="0,00" :class="{ invalid: ask.error }" @keydown.esc="asking = null">
            <span class="ex-seg sm">
              <button v-for="c in CURRENCIES" :key="c" type="button" :class="{ on: ask.currency === c }" @click="ask.currency = c">{{ SYMBOLS[c] }}</button>
            </span>
          </span>
          <button class="rc-pay" :disabled="busyId === x.id">✓</button>
          <button type="button" class="tp-icon-btn sm" :aria-label="t.panel.cancel" @click="asking = null"><AppIcon name="close" /></button>
        </form>

        <button v-else type="button" class="rc-pay" :disabled="busyId === x.id" @click="startPay(x)">
          <AppIcon :name="kind === 'income' ? 'download' : 'wallet'" /> {{ k.pay }}
        </button>
      </li>
    </TransitionGroup>
  </section>
</template>

<style>
/* ===== Monthly templates ===== */
.rc { margin-bottom: 18px; padding: 20px 22px; border-radius: var(--radius); background: var(--surface); border: 1px solid var(--line); box-shadow: var(--shadow); animation: tpUp .7s var(--ease) .05s both; }
.rc-head { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 12px; }
.rc-head h2 { display: flex; align-items: center; gap: 8px; font-size: 1rem; font-weight: 800; }
.rc-head h2 .ico { width: 18px; height: 18px; color: var(--accent); }
.rc-income .rc-head h2 .ico { color: #0E9F85; }
.rc-count { padding: 1px 9px; border-radius: 999px; background: var(--bg-2); color: var(--muted); font-size: .75rem; }
.rc-head p { margin-top: 3px; color: var(--muted); font-size: .85rem; font-weight: 600; }
.rc-head p b { color: var(--ink); }
.rc-head .rc-all { color: #0E9F85; font-weight: 800; }
.rc-head .btn .ico { width: 16px; height: 16px; }
.rc-empty { display: grid; place-items: center; padding: 14px; color: var(--muted); font-size: .9rem; border-radius: 16px; border: 1px dashed var(--line-2); }
.rc-empty .spinner { width: 22px; height: 22px; border-color: var(--line-2); border-top-color: var(--accent); }

.rc-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(330px, 1fr)); gap: 8px; }
.rc-item {
  display: flex; align-items: center; gap: 10px; padding: 8px 10px 8px 8px; border-radius: 16px;
  background: var(--bg); border: 1px solid var(--line); transition: border-color .25s, background .25s, opacity .25s;
}
.rc-item.late { border-color: rgba(229, 72, 77, .45); background: #FFF6F6; }
.rc-item.soon { border-color: rgba(245, 158, 11, .45); }
.rc-item.done { opacity: .75; }
.rc-text { flex: 1; min-width: 0; display: grid; padding: 0; border: 0; background: none; text-align: left; cursor: pointer; line-height: 1.3; }
.rc-text b { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: .92rem; }
.rc-text small { color: var(--muted); font-weight: 600; font-size: .76rem; }
.rc-text em { font-style: normal; color: #E5484D; font-weight: 800; }
.rc-text:hover b { color: var(--accent); }
.rc-pay {
  flex: none; display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; border-radius: 999px; border: 0; cursor: pointer;
  background: var(--ink); color: #fff; font-weight: 800; font-size: .82rem; transition: background .2s, transform .3s var(--ease);
}
.rc-pay .ico { width: 15px; height: 15px; }
.rc-pay:hover { background: var(--accent); transform: translateY(-1px); }
.rc-income .rc-pay:hover { background: #0E9F85; }
.rc-pay:disabled { opacity: .6; cursor: progress; }
.rc-done { flex: none; display: grid; justify-items: end; line-height: 1.2; white-space: nowrap; }
.rc-done small { font-size: .72rem; font-weight: 800; color: #0E9F85; }
.rc-done b { font-size: .9rem; font-variant-numeric: tabular-nums; }
.rc-undo { flex: none; background: transparent; }
.rc-ask { flex: none; display: flex; align-items: center; gap: 6px; }
.rc-ask .ex-amount input { width: 190px; padding: 8px 110px 8px 12px; border-radius: 12px; border: 1px solid var(--line-2); font-weight: 700; }
.rc-ask .ex-amount input.invalid { border-color: #E5484D; }
.rc-ask .ex-seg.sm button { min-width: 26px; height: 24px; padding: 0 6px; }

.rc-form { margin-bottom: 14px; padding: 16px; border-radius: 18px; background: var(--bg); border: 1px solid rgba(91, 75, 255, .3); }
.rc-form-grid { display: grid; grid-template-columns: 1.2fr 1.2fr 110px; gap: 12px; }

@media (max-width: 720px) {
  .rc-form-grid { grid-template-columns: 1fr; }
  .rc-list { grid-template-columns: 1fr; }
  .rc-item { flex-wrap: wrap; }
  .rc-ask { width: 100%; }
  .rc-ask .ex-amount { flex: 1; }
  .rc-ask .ex-amount input { width: 100%; }
}
</style>
