<script setup lang="ts">
import { formatUsd, newId } from '~/utils/prototype'

defineProps<{ preview?: boolean }>()

type Tab = 'feed' | 'wallet'
type InvoiceStatus = 'waiting' | 'confirming' | 'paid'

interface Listing {
  id: number
  title: string
  priceCents: number
  city: string
  category: string
  icon: string
  verified: boolean
  vip: boolean
  boostedAt: number
  mine: boolean
}

interface Invoice {
  id: string
  amountCents: number
  status: InvoiceStatus
}

interface LedgerEntry {
  id: string
  label: string
  amountCents: number
}

const TABS: { id: Tab; label: string }[] = [
  { id: 'feed', label: 'Listings' },
  { id: 'wallet', label: 'Wallet' },
]
const CATEGORY_ALL = 'All'
const CATEGORIES = [CATEGORY_ALL, 'Electronics', 'Home', 'Transport', 'Services']
const TOP_UP_OPTIONS_CENTS = [1000, 2500, 5000]
const BUMP_PRICE_CENTS = 200
const VIP_PRICE_CENTS = 900
const CONFIRMING_DELAY_MS = 1600
const PAID_DELAY_MS = 3400
const NOTICE_DURATION_MS = 3200

const listings = ref<Listing[]>([
  { id: 1, title: 'MacBook Air M2, 16 GB', priceCents: 89900, city: 'Nitra', category: 'Electronics', icon: '💻', verified: true, vip: true, boostedAt: 0, mine: false },
  { id: 2, title: 'Oak dining table + 4 chairs', priceCents: 24000, city: 'Bratislava', category: 'Home', icon: '🪑', verified: false, vip: false, boostedAt: 0, mine: false },
  { id: 3, title: 'Škoda Octavia 2019, 1.6 TDI', priceCents: 1120000, city: 'Košice', category: 'Transport', icon: '🚗', verified: true, vip: false, boostedAt: 0, mine: false },
  { id: 4, title: 'Next.js performance audit', priceCents: 12000, city: 'Remote', category: 'Services', icon: '⚡', verified: true, vip: false, boostedAt: 0, mine: true },
  { id: 5, title: 'iPhone 14 Pro, 256 GB', priceCents: 74000, city: 'Prague', category: 'Electronics', icon: '📱', verified: true, vip: false, boostedAt: 0, mine: false },
  { id: 6, title: 'Electric standing desk', priceCents: 19000, city: 'Nitra', category: 'Home', icon: '🖥️', verified: false, vip: false, boostedAt: 0, mine: false },
])

const tab = ref<Tab>('feed')
const category = ref(CATEGORY_ALL)
const balanceCents = ref(1500)
const ledger = ref<LedgerEntry[]>([{ id: 'seed', label: 'Welcome credit', amountCents: 1500 }])
const invoice = ref<Invoice | null>(null)
const webhookLog = ref<string[]>([])
const notice = ref('')
const processedInvoiceIds = new Set<string>()
let boostCounter = 0
let invoiceTimers: ReturnType<typeof setTimeout>[] = []
let noticeTimer: ReturnType<typeof setTimeout> | undefined

const myListing = computed(() => listings.value.find((l) => l.mine)!)
const visibleListings = computed(() =>
  listings.value
    .filter((l) => category.value === CATEGORY_ALL || l.category === category.value)
    .toSorted((a, b) => Number(b.vip) - Number(a.vip) || b.boostedAt - a.boostedAt || a.id - b.id)
)
const countFor = (name: string) => (name === CATEGORY_ALL ? listings.value.length : listings.value.filter((l) => l.category === name).length)

function showNotice(message: string) {
  notice.value = message
  clearTimeout(noticeTimer)
  noticeTimer = setTimeout(() => (notice.value = ''), NOTICE_DURATION_MS)
}

function recordLedger(label: string, amountCents: number) {
  ledger.value.unshift({ id: newId(), label, amountCents })
  balanceCents.value += amountCents
}

function spend(label: string, priceCents: number, apply: (listing: Listing) => void) {
  if (balanceCents.value < priceCents) {
    showNotice('Not enough balance. Top up first.')
    return
  }
  recordLedger(label, -priceCents)
  apply(myListing.value)
  showNotice(`${label} applied`)
}

const bump = () => spend('Bump', BUMP_PRICE_CENTS, (l) => (l.boostedAt = ++boostCounter))
const makeVip = () => spend('VIP placement', VIP_PRICE_CENTS, (l) => (l.vip = true))

function logWebhook(line: string) {
  webhookLog.value.unshift(line)
}

function clearInvoiceTimers() {
  invoiceTimers.forEach(clearTimeout)
  invoiceTimers = []
}

function deliverWebhook() {
  const current = invoice.value
  if (!current) return
  if (processedInvoiceIds.has(current.id)) {
    logWebhook('Duplicate delivery ignored (idempotency key already processed)')
    return
  }
  processedInvoiceIds.add(current.id)
  current.status = 'paid'
  recordLedger('Crypto deposit', current.amountCents)
  logWebhook('Signature valid, balance credited once')
}

function createInvoice(amountCents: number) {
  clearInvoiceTimers()
  webhookLog.value = []
  invoice.value = { id: `inv_${newId()}`, amountCents, status: 'waiting' }
  invoiceTimers.push(
    setTimeout(() => {
      if (!invoice.value) return
      invoice.value.status = 'confirming'
      logWebhook('Payment detected, 1/2 confirmations')
    }, CONFIRMING_DELAY_MS),
    setTimeout(deliverWebhook, PAID_DELAY_MS)
  )
}

onBeforeUnmount(() => {
  clearInvoiceTimers()
  clearTimeout(noticeTimer)
})
</script>

<template>
  <div class="cls" :class="{ 'is-preview': preview }" :inert="preview || undefined">
    <div class="cls-bar">
      <i /><i /><i />
      <span>board.example / {{ tab }}</span>
      <div class="cls-tabs" role="tablist">
        <button v-for="t in TABS" :key="t.id" type="button" role="tab" :aria-selected="tab === t.id" :class="{ on: tab === t.id }" @click="tab = t.id">
          {{ t.label }}
        </button>
      </div>
      <b class="cls-balance">{{ formatUsd(balanceCents) }}</b>
    </div>

    <div v-if="tab === 'feed'" class="cls-body cls-feed">
      <aside>
        <p class="cls-cap">Categories</p>
        <button v-for="c in CATEGORIES" :key="c" type="button" :class="{ on: category === c }" @click="category = c">
          {{ c }} <span>{{ countFor(c) }}</span>
        </button>
      </aside>
      <TransitionGroup name="cls-card" tag="ul" class="cls-grid">
        <li v-for="l in visibleListings" :key="l.id" :class="{ vip: l.vip }">
          <div class="cls-thumb">{{ l.icon }}<em v-if="l.vip">VIP</em></div>
          <h4>{{ l.title }}</h4>
          <p class="cls-price">{{ formatUsd(l.priceCents) }}</p>
          <p class="cls-meta">{{ l.city }} <span v-if="l.verified" class="cls-ok">✓ verified</span><span v-if="l.mine" class="cls-mine">yours</span></p>
        </li>
      </TransitionGroup>
    </div>

    <div v-else class="cls-body cls-wallet">
      <section class="cls-card-box">
        <p class="cls-cap">Top up with crypto</p>
        <div class="cls-amounts">
          <button v-for="a in TOP_UP_OPTIONS_CENTS" :key="a" type="button" @click="createInvoice(a)">{{ formatUsd(a) }}</button>
        </div>
        <div v-if="invoice" class="cls-invoice" :class="invoice.status">
          <p><b>{{ invoice.id }}</b> · {{ formatUsd(invoice.amountCents) }}</p>
          <ol class="cls-steps">
            <li :class="{ done: true }">Invoice created</li>
            <li :class="{ done: invoice.status !== 'waiting' }">Payment detected</li>
            <li :class="{ done: invoice.status === 'paid' }">Webhook verified</li>
          </ol>
          <ul class="cls-log"><li v-for="(line, i) in webhookLog" :key="i">{{ line }}</li></ul>
          <button v-if="invoice.status === 'paid'" type="button" class="cls-ghost" @click="deliverWebhook">Replay webhook</button>
        </div>
        <p v-else class="cls-hint">Pick an amount to create an invoice. The balance is credited only after a verified webhook.</p>
      </section>

      <section class="cls-card-box">
        <p class="cls-cap">Promote your listing</p>
        <div class="cls-mylisting">
          <span>{{ myListing.icon }}</span>
          <div><h4>{{ myListing.title }}</h4><p class="cls-meta">{{ myListing.vip ? 'VIP placement active' : 'Standard placement' }}</p></div>
        </div>
        <div class="cls-actions">
          <button type="button" @click="bump">Bump <span>{{ formatUsd(BUMP_PRICE_CENTS) }}</span></button>
          <button type="button" :disabled="myListing.vip" @click="makeVip">VIP <span>{{ formatUsd(VIP_PRICE_CENTS) }}</span></button>
        </div>
        <p class="cls-cap">Ledger</p>
        <ul class="cls-ledger">
          <li v-for="e in ledger" :key="e.id"><span>{{ e.label }}</span><b :class="{ neg: e.amountCents < 0 }">{{ e.amountCents < 0 ? '−' : '+' }}{{ formatUsd(Math.abs(e.amountCents)) }}</b></li>
        </ul>
      </section>
    </div>

    <p v-if="notice" class="cls-notice" role="status">{{ notice }}</p>
  </div>
</template>

<style>
.cls { position: relative; width: 960px; height: 600px; border-radius: 16px; overflow: hidden; display: flex; flex-direction: column; background: #F5F7FB; color: #111827; font-family: 'Manrope', system-ui, sans-serif; text-align: left; box-shadow: 0 30px 70px -30px rgba(0, 0, 0, .45); }
.cls button { font: inherit; color: inherit; cursor: pointer; }
.cls.is-preview { pointer-events: none; }
.cls-bar { display: flex; align-items: center; gap: 6px; padding: 10px 14px; background: #fff; border-bottom: 1px solid #E5E9F2; }
.cls-bar > i { width: 10px; height: 10px; border-radius: 50%; background: #D9DEEA; }
.cls-bar > span { margin-left: 10px; font-size: 12px; color: #6B7280; background: #F5F7FB; padding: 3px 12px; border-radius: 999px; }
.cls-tabs { margin-left: auto; display: flex; background: #EEF1F8; border-radius: 999px; padding: 3px; }
.cls-tabs button { border: 0; background: none; padding: 5px 16px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.cls-tabs button.on { background: #2F5BEA; color: #fff; }
.cls-balance { margin-left: 12px; font-size: 13px; padding: 5px 12px; border-radius: 999px; background: #E8EEFF; color: #2F5BEA; }
.cls-body { flex: 1; min-height: 0; padding: 20px 24px; }
.cls-cap { font-size: 11px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; color: #6B7280; margin-bottom: 10px; }
.cls-feed { display: grid; grid-template-columns: 170px 1fr; gap: 24px; }
.cls-feed aside { display: flex; flex-direction: column; gap: 4px; }
.cls-feed aside button { display: flex; justify-content: space-between; border: 0; background: none; padding: 9px 12px; border-radius: 10px; font-size: 13px; font-weight: 600; text-align: left; }
.cls-feed aside button span { color: #9CA3AF; }
.cls-feed aside button.on, .cls-feed aside button:hover { background: #E8EEFF; color: #2F5BEA; }
.cls-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; align-content: start; }
.cls-grid li { background: #fff; border: 1px solid #E5E9F2; border-radius: 14px; padding: 10px 10px 12px; transition: transform .3s, box-shadow .3s; }
.cls-grid li:hover { transform: translateY(-3px); box-shadow: 0 14px 30px -18px rgba(47, 91, 234, .6); }
.cls-grid li.vip { border-color: #F5C451; background: #FFFBEF; }
.cls-thumb { position: relative; height: 96px; border-radius: 10px; display: grid; place-items: center; font-size: 38px; background: linear-gradient(135deg, #E8EEFF, #F5F7FB); }
.cls-thumb em { position: absolute; top: 6px; left: 6px; font-style: normal; font-size: 10px; font-weight: 800; padding: 2px 8px; border-radius: 999px; background: #F5C451; color: #5B4300; }
.cls-grid h4, .cls-mylisting h4 { font-size: 13px; font-weight: 700; margin: 10px 2px 2px; line-height: 1.3; }
.cls-price { font-size: 15px; font-weight: 800; margin: 0 2px; }
.cls-meta { font-size: 11px; color: #6B7280; margin: 4px 2px 0; display: flex; align-items: center; gap: 8px; }
.cls-ok { color: #15803D; font-weight: 700; }
.cls-mine { background: #E8EEFF; color: #2F5BEA; font-weight: 700; padding: 1px 7px; border-radius: 999px; }
.cls-card-move, .cls-card-enter-active, .cls-card-leave-active { transition: all .4s; }
.cls-card-enter-from, .cls-card-leave-to { opacity: 0; transform: scale(.94); }
.cls-card-leave-active { position: absolute; }
.cls-wallet { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
.cls-card-box { background: #fff; border: 1px solid #E5E9F2; border-radius: 16px; padding: 18px; overflow: auto; }
.cls-amounts, .cls-actions { display: flex; gap: 10px; margin-bottom: 14px; }
.cls-amounts button, .cls-actions button { flex: 1; padding: 10px; border-radius: 12px; border: 1px solid #D5DBEA; background: #F5F7FB; font-weight: 800; font-size: 14px; transition: background .2s, color .2s; }
.cls-amounts button:hover, .cls-actions button:hover:not(:disabled) { background: #2F5BEA; color: #fff; border-color: #2F5BEA; }
.cls-actions button:disabled { opacity: .45; cursor: default; }
.cls-actions button span { margin-left: 6px; font-weight: 600; opacity: .7; }
.cls-hint { font-size: 12px; color: #6B7280; line-height: 1.5; }
.cls-invoice { border: 1px dashed #B8C3E0; border-radius: 12px; padding: 12px 14px; font-size: 12px; }
.cls-invoice.paid { border-color: #86EFAC; background: #F0FDF4; }
.cls-steps { margin: 10px 0; display: grid; gap: 6px; }
.cls-steps li { position: relative; padding-left: 22px; color: #9CA3AF; }
.cls-steps li::before { content: ''; position: absolute; left: 2px; top: 3px; width: 10px; height: 10px; border-radius: 50%; border: 2px solid #CBD2E3; }
.cls-steps li.done { color: #111827; font-weight: 700; }
.cls-steps li.done::before { background: #22C55E; border-color: #22C55E; }
.cls-log { font-family: ui-monospace, Consolas, monospace; font-size: 11px; color: #4B5563; display: grid; gap: 3px; }
.cls-ghost { margin-top: 10px; padding: 6px 12px; border-radius: 999px; border: 1px solid #B8C3E0; background: #fff; font-size: 11px; font-weight: 700; }
.cls-mylisting { display: flex; gap: 12px; align-items: center; margin-bottom: 12px; }
.cls-mylisting > span { font-size: 30px; }
.cls-mylisting h4 { margin: 0; }
.cls-ledger { display: grid; gap: 8px; font-size: 13px; }
.cls-ledger li { display: flex; justify-content: space-between; padding-bottom: 8px; border-bottom: 1px solid #EEF1F8; }
.cls-ledger b { color: #15803D; }
.cls-ledger b.neg { color: #B91C1C; }
.cls-notice { position: absolute; left: 50%; bottom: 18px; transform: translateX(-50%); padding: 9px 18px; border-radius: 999px; background: #111827; color: #fff; font-size: 12px; font-weight: 700; animation: clsPop .3s; }
@keyframes clsPop { from { opacity: 0; transform: translate(-50%, 10px); } }
</style>
