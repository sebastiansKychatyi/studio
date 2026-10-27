<script setup lang="ts">
import { formatUsd, newId } from '~/utils/prototype'

defineProps<{ preview?: boolean }>()

type Period = 'monthly' | 'yearly'
type InvoiceStatus = 'pending' | 'paid'

interface Plan {
  id: string
  name: string
  monthlyCents: number
  seats: number
}

interface Product {
  id: string
  name: string
  color: string
  mrrCents: number
  licenses: number
}

interface Invoice {
  id: string
  productId: string
  planName: string
  amountCents: number
  status: InvoiceStatus
  licenseKey: string
}

const YEARLY_DISCOUNT = 0.2
const MONTHS_PER_YEAR = 12
const PAYMENT_DELAY_MS = 2400
const LICENSE_GROUPS = 3
const LICENSE_GROUP_LENGTH = 4

const PLANS: Plan[] = [
  { id: 'starter', name: 'Starter', monthlyCents: 1900, seats: 1 },
  { id: 'pro', name: 'Pro', monthlyCents: 4900, seats: 5 },
  { id: 'team', name: 'Team', monthlyCents: 12900, seats: 25 },
]

const products = ref<Product[]>([
  { id: 'atlas', name: 'Atlas', color: '#7C3AED', mrrCents: 412000, licenses: 118 },
  { id: 'beacon', name: 'Beacon', color: '#0EA5E9', mrrCents: 318500, licenses: 96 },
  { id: 'cobalt', name: 'Cobalt', color: '#F97316', mrrCents: 287000, licenses: 74 },
  { id: 'delta', name: 'Delta', color: '#10B981', mrrCents: 301500, licenses: 88 },
  { id: 'ember', name: 'Ember', color: '#EF4444', mrrCents: 224000, licenses: 61 },
])

const productId = ref(products.value[0]!.id)
const period = ref<Period>('monthly')
const invoices = ref<Invoice[]>([])
const paymentTimers = new Set<ReturnType<typeof setTimeout>>()

const product = computed(() => products.value.find((p) => p.id === productId.value)!)
const totalMrrCents = computed(() => products.value.reduce((sum, p) => sum + p.mrrCents, 0))
const productInvoices = computed(() => invoices.value.filter((i) => i.productId === productId.value))
const hasPendingInvoice = computed(() => productInvoices.value.some((i) => i.status === 'pending'))

const priceCents = (plan: Plan) =>
  period.value === 'monthly' ? plan.monthlyCents : Math.round(plan.monthlyCents * MONTHS_PER_YEAR * (1 - YEARLY_DISCOUNT))
const monthlyEquivalentCents = (plan: Plan) =>
  period.value === 'monthly' ? plan.monthlyCents : Math.round(plan.monthlyCents * (1 - YEARLY_DISCOUNT))

function generateLicenseKey(): string {
  return Array.from({ length: LICENSE_GROUPS }, () => newId().padEnd(LICENSE_GROUP_LENGTH, '0').slice(0, LICENSE_GROUP_LENGTH).toUpperCase()).join('-')
}

function settle(invoiceId: string, plan: Plan) {
  const invoice = invoices.value.find((i) => i.id === invoiceId)
  if (!invoice || invoice.status === 'paid') return
  invoice.status = 'paid'
  invoice.licenseKey = generateLicenseKey()
  const target = products.value.find((p) => p.id === invoice.productId)!
  target.mrrCents += monthlyEquivalentCents(plan)
  target.licenses += 1
}

function createInvoice(plan: Plan) {
  if (hasPendingInvoice.value) return
  const invoice: Invoice = {
    id: `INV-${newId().toUpperCase()}`,
    productId: productId.value,
    planName: plan.name,
    amountCents: priceCents(plan),
    status: 'pending',
    licenseKey: '',
  }
  invoices.value.unshift(invoice)
  const timer = setTimeout(() => {
    paymentTimers.delete(timer)
    settle(invoice.id, plan)
  }, PAYMENT_DELAY_MS)
  paymentTimers.add(timer)
}

onBeforeUnmount(() => paymentTimers.forEach(clearTimeout))
</script>

<template>
  <div class="pb" :class="{ 'is-preview': preview }" :inert="preview || undefined">
    <header class="pb-top">
      <div class="pb-brand"><b>◆</b> Billing console</div>
      <div class="pb-total"><span>Total MRR</span><strong>{{ formatUsd(totalMrrCents) }}</strong></div>
      <div class="pb-period" role="group" aria-label="Billing period">
        <button type="button" :class="{ on: period === 'monthly' }" @click="period = 'monthly'">Monthly</button>
        <button type="button" :class="{ on: period === 'yearly' }" @click="period = 'yearly'">Yearly −20%</button>
      </div>
    </header>

    <div class="pb-body">
      <aside>
        <p class="pb-cap">Products</p>
        <button v-for="p in products" :key="p.id" type="button" :class="{ on: p.id === productId }" :style="{ '--pc': p.color }" @click="productId = p.id">
          <i /> <span>{{ p.name }}</span> <em>{{ formatUsd(p.mrrCents) }}</em>
        </button>
      </aside>

      <main>
        <div class="pb-head" :style="{ '--pc': product.color }">
          <h3><i /> {{ product.name }}</h3>
          <p>{{ formatUsd(product.mrrCents) }} MRR · {{ product.licenses }} active licenses</p>
        </div>

        <ul class="pb-plans">
          <li v-for="plan in PLANS" :key="plan.id">
            <h4>{{ plan.name }}</h4>
            <p class="pb-price">{{ formatUsd(priceCents(plan)) }}<span>/{{ period === 'monthly' ? 'mo' : 'yr' }}</span></p>
            <p class="pb-seats">{{ plan.seats }} {{ plan.seats === 1 ? 'seat' : 'seats' }}</p>
            <button type="button" :disabled="hasPendingInvoice" :style="{ '--pc': product.color }" @click="createInvoice(plan)">Invoice in USDT</button>
          </li>
        </ul>

        <p class="pb-cap">Invoices and licenses</p>
        <table v-if="productInvoices.length" class="pb-table">
          <tbody>
            <tr v-for="i in productInvoices" :key="i.id">
              <td>{{ i.id }}</td>
              <td>{{ i.planName }}</td>
              <td>{{ formatUsd(i.amountCents) }}</td>
              <td><span class="pb-chip" :class="i.status">{{ i.status === 'paid' ? 'Paid' : 'Waiting for payment…' }}</span></td>
              <td class="pb-key">{{ i.licenseKey || '—' }}</td>
            </tr>
          </tbody>
        </table>
        <p v-else class="pb-empty">No invoices yet. Create one: once the payment confirms, a license key is issued and MRR updates.</p>
      </main>
    </div>
  </div>
</template>

<style>
.pb { width: 960px; height: 600px; border-radius: 16px; overflow: hidden; display: flex; flex-direction: column; background: #FAFAFC; color: #14121F; font-family: 'Manrope', system-ui, sans-serif; text-align: left; box-shadow: 0 30px 70px -30px rgba(0, 0, 0, .45); }
.pb button { font: inherit; color: inherit; cursor: pointer; }
.pb.is-preview { pointer-events: none; }
.pb-top { display: flex; align-items: center; gap: 24px; padding: 14px 22px; background: #14121F; color: #fff; }
.pb-brand { font-weight: 800; font-size: 15px; }
.pb-brand b { color: #A78BFA; margin-right: 6px; }
.pb-total { margin-left: auto; display: grid; text-align: right; }
.pb-total span { font-size: 10px; letter-spacing: .08em; text-transform: uppercase; color: #A5A1B8; }
.pb-total strong { font-size: 20px; letter-spacing: -.02em; }
.pb-period { display: flex; background: #2A2740; border-radius: 999px; padding: 3px; }
.pb-period button { border: 0; background: none; color: #C9C5DD; padding: 6px 14px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.pb-period button.on { background: #7C3AED; color: #fff; }
.pb-body { flex: 1; min-height: 0; display: grid; grid-template-columns: 220px 1fr; }
.pb-body aside { padding: 18px 12px; border-right: 1px solid #E8E6F0; background: #fff; display: flex; flex-direction: column; gap: 4px; }
.pb-cap { font-size: 11px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; color: #77738A; margin: 0 8px 8px; }
.pb-body aside button { display: grid; grid-template-columns: 12px 1fr auto; align-items: center; gap: 10px; border: 0; background: none; padding: 10px; border-radius: 10px; text-align: left; font-size: 13px; font-weight: 700; }
.pb-body aside button i, .pb-head i { width: 10px; height: 10px; border-radius: 50%; background: var(--pc); display: inline-block; }
.pb-body aside button em { font-style: normal; font-size: 11px; color: #77738A; font-weight: 600; }
.pb-body aside button.on, .pb-body aside button:hover { background: #F1ECFE; }
.pb-body main { padding: 20px 24px; overflow: auto; }
.pb-head h3 { font-size: 22px; letter-spacing: -.02em; display: flex; align-items: center; gap: 10px; }
.pb-head p { font-size: 13px; color: #77738A; margin: 4px 0 16px; }
.pb-plans { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px; }
.pb-plans li { background: #fff; border: 1px solid #E8E6F0; border-radius: 14px; padding: 14px; }
.pb-plans h4 { font-size: 13px; font-weight: 800; }
.pb-price { font-size: 24px; font-weight: 800; letter-spacing: -.02em; margin: 6px 0 2px; }
.pb-price span { font-size: 12px; font-weight: 600; color: #77738A; margin-left: 2px; }
.pb-seats { font-size: 12px; color: #77738A; margin-bottom: 12px; }
.pb-plans button { width: 100%; padding: 9px; border-radius: 10px; border: 0; background: var(--pc); color: #fff; font-weight: 700; font-size: 12px; transition: filter .2s; }
.pb-plans button:hover:not(:disabled) { filter: brightness(1.1); }
.pb-plans button:disabled { opacity: .4; cursor: default; }
.pb-table { width: 100%; border-collapse: collapse; font-size: 12px; background: #fff; border: 1px solid #E8E6F0; border-radius: 12px; overflow: hidden; }
.pb-table td { padding: 10px 12px; border-bottom: 1px solid #F0EEF6; }
.pb-table tr:last-child td { border-bottom: 0; }
.pb-key { font-family: ui-monospace, Consolas, monospace; font-weight: 700; }
.pb-chip { padding: 3px 10px; border-radius: 999px; font-weight: 700; font-size: 11px; }
.pb-chip.pending { background: #FEF3C7; color: #92400E; }
.pb-chip.paid { background: #DCFCE7; color: #166534; }
.pb-empty { font-size: 12px; color: #77738A; line-height: 1.5; padding: 0 8px; }
</style>
