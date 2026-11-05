<script setup lang="ts">
// Invoice as a printable page: the browser's Print → "Save as PDF" makes the PDF (no PDF library).
// Seller details come from Settings → Invoices; the document language is the client's (if supported).
// Fields are configurable; legal correctness (Slovak invoices, VAT) is not guaranteed.
import type { TeamClient, TeamInvoice } from '~/composables/useTeam'

const { t, all } = useSite()
const { locale } = useI18n()
const localePath = useLocalePath()
const route = useRoute()
const { api } = useTeam()
const { pref } = usePrefs()

const seller = pref<Record<string, string>>('invoice', {})
const invoice = ref<TeamInvoice | null>(null)
const client = ref<TeamClient | null>(null)
const failed = ref(false)
onMounted(async () => {
  try {
    invoice.value = (await api<TeamInvoice[]>('/invoices')).find((x) => x.id === Number(route.query.id)) ?? null
    if (invoice.value) client.value = (await api<{ client: TeamClient }>(`/clients/${invoice.value.client_id}`)).client
  } catch {
    failed.value = true
  }
})

// Document language: the client's if the panel has it, else the panel's
const lang = computed(() => (client.value && all[client.value.lang] ? client.value.lang : locale.value))
const d = computed(() => (all[lang.value] ?? t.value).panel.invoiceDoc)
const date = (s: string) => new Date(`${s}T12:00:00`).toLocaleDateString(lang.value === 'en' ? 'en-GB' : lang.value)
const money = (n: number) => {
  try {
    return new Intl.NumberFormat(lang.value, { style: 'currency', currency: invoice.value?.currency ?? 'EUR' }).format(n)
  } catch {
    return n.toFixed(2)
  }
}
const items = computed(() => (invoice.value?.items.length ? invoice.value.items : invoice.value ? [{ title: invoice.value.title, hours: null, rate: null, amount: invoice.value.amount }] : []))
const vs = computed(() => (invoice.value?.number ?? '').replace(/\D/g, ''))
const print = () => window.print()
useHead(() => ({ title: invoice.value ? `${d.value.title} ${invoice.value.number}` : d.value.title }))
</script>

<template>
  <div class="iv">
    <div class="iv-bar no-print">
      <NuxtLink :to="localePath(invoice ? `/panel/clients?id=${invoice.client_id}` : '/panel/clients')" class="cr-back"><AppIcon name="left" /> {{ t.panel.clients.title }}</NuxtLink>
      <button type="button" class="btn btn-primary btn-sm" :disabled="!invoice" @click="print"><AppIcon name="download" /> {{ t.panel.clients.savePdf }}</button>
    </div>
    <p v-if="!seller.name" class="iv-warn no-print">{{ t.panel.clients.noSeller }} <NuxtLink :to="localePath('/panel/settings')">{{ t.panel.nav.settings }}</NuxtLink></p>
    <p v-if="failed" class="al-empty">{{ t.panel.errorServer }}</p>
    <div v-else-if="!invoice" class="kb-loading"><span class="spinner" /></div>

    <article v-else class="iv-doc">
      <header class="iv-top">
        <h1>{{ d.title }} <span>{{ invoice.number }}</span></h1>
        <dl>
          <div><dt>{{ d.issued }}</dt><dd>{{ date(invoice.issued) }}</dd></div>
          <div><dt>{{ d.due }}</dt><dd>{{ date(invoice.due) }}</dd></div>
          <div v-if="vs"><dt>{{ d.vs }}</dt><dd>{{ vs }}</dd></div>
        </dl>
      </header>

      <div class="iv-parties">
        <section>
          <h2>{{ d.seller }}</h2>
          <p><b>{{ seller.name || '—' }}</b></p>
          <p v-if="seller.address" class="iv-pre">{{ seller.address }}</p>
          <p v-if="seller.ico">{{ d.ico }}: {{ seller.ico }}</p>
          <p v-if="seller.dic">{{ d.dic }}: {{ seller.dic }}</p>
          <p v-if="seller.icdph">{{ d.icdph }}: {{ seller.icdph }}</p>
          <p v-if="seller.register" class="iv-small">{{ seller.register }}</p>
          <p v-if="seller.email || seller.phone">{{ [seller.email, seller.phone].filter(Boolean).join(' · ') }}</p>
        </section>
        <section>
          <h2>{{ d.buyer }}</h2>
          <p><b>{{ client?.company || client?.name }}</b></p>
          <p v-if="client?.company && client?.name">{{ client.name }}</p>
          <p v-if="client?.email">{{ client.email }}</p>
        </section>
      </div>

      <table class="iv-items">
        <thead><tr><th>{{ d.item }}</th><th>{{ d.qty }}</th><th>{{ d.price }}</th><th>{{ d.sum }}</th></tr></thead>
        <tbody>
          <tr v-for="(x, i) in items" :key="i">
            <td>{{ x.title }}</td>
            <td>{{ x.hours !== null ? `${x.hours} h` : '1' }}</td>
            <td>{{ x.rate !== null ? money(x.rate) : money(x.amount) }}</td>
            <td>{{ money(x.amount) }}</td>
          </tr>
        </tbody>
        <tfoot><tr><td colspan="3">{{ d.total }}</td><td>{{ money(invoice.amount) }}</td></tr></tfoot>
      </table>

      <section class="iv-pay">
        <h2>{{ d.payment }}</h2>
        <p>{{ d.transfer }}</p>
        <p v-if="seller.iban"><b>IBAN:</b> {{ seller.iban }}<template v-if="seller.swift"> · <b>SWIFT:</b> {{ seller.swift }}</template></p>
        <p v-if="seller.bank">{{ seller.bank }}</p>
      </section>
      <p v-if="invoice.note || seller.note" class="iv-note iv-pre">{{ [invoice.note, seller.note].filter(Boolean).join('\n') }}</p>
      <p v-if="invoice.status === 'paid'" class="iv-paid">{{ d.paid }} {{ date(invoice.paid_on!) }}</p>
    </article>
  </div>
</template>

<style>
/* ===== Invoice (printable) ===== */
.iv { display: grid; gap: 12px; max-width: 820px; }
.iv-bar { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px; }
.iv-bar .btn .ico { width: 16px; height: 16px; }
.iv-warn { padding: 10px 14px; border-radius: 14px; background: #FFF1D6; color: #7A4500; font-weight: 700; font-size: .88rem; }
.iv-warn a { text-decoration: underline; }
.iv-doc { padding: clamp(18px, 5vw, 44px); border-radius: 18px; background: #fff; color: #111; border: 1px solid var(--line); font-size: .92rem; line-height: 1.5; }
.iv-top { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 16px; padding-bottom: 18px; border-bottom: 2px solid #111; }
.iv-top h1 { font-family: var(--font-display); font-weight: 600; font-size: 1.6rem; }
.iv-top h1 span { color: #5B4BFF; }
.iv-top dl { display: grid; gap: 2px; }
.iv-top dl div { display: flex; gap: 10px; justify-content: space-between; }
.iv-top dt { color: #666; }
.iv-top dd { font-weight: 700; }
.iv-parties { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; padding: 18px 0; }
.iv-doc h2 { margin-bottom: 6px; font-size: .74rem; font-weight: 800; color: #666; text-transform: uppercase; letter-spacing: .05em; }
.iv-pre { white-space: pre-line; }
.iv-small { color: #666; font-size: .8rem; }
.iv-items { width: 100%; border-collapse: collapse; margin: 8px 0 18px; }
.iv-items th { text-align: left; padding: 8px 6px; font-size: .74rem; color: #666; text-transform: uppercase; border-bottom: 1px solid #ccc; }
.iv-items td { padding: 8px 6px; border-bottom: 1px solid #eee; vertical-align: top; }
.iv-items th:not(:first-child), .iv-items td:not(:first-child) { text-align: right; white-space: nowrap; }
.iv-items tfoot td { padding-top: 12px; border: 0; font-weight: 800; font-size: 1.1rem; }
.iv-note { margin-top: 14px; padding: 10px 12px; border-radius: 10px; background: #f5f5f2; font-size: .85rem; }
.iv-paid { margin-top: 12px; color: #0E9F85; font-weight: 800; }
@media (max-width: 560px) { .iv-parties { grid-template-columns: 1fr; gap: 14px; } }
@media print {
  .iv .no-print { display: none !important; }
  .iv-doc { border: 0; border-radius: 0; padding: 0; font-size: 11pt; }
  @page { size: A4; margin: 16mm; }
}
</style>
