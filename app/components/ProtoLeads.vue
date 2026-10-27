<script setup lang="ts">
defineProps<{ preview?: boolean }>()

type EnrichStatus = 'idle' | 'running' | 'done'

interface Lead {
  id: number
  company: string
  domain: string
  employees: number
  email: string
  stack: string[]
  score: number
}

interface Column {
  id: 'domain' | 'employees' | 'email' | 'stack' | 'score'
  label: string
}

const ENRICH_STEP_MS = 650
const SCORE_HIGH = 80
const SCORE_MEDIUM = 60
const MIN_SCORE_FILTER = 0
const MAX_SCORE_FILTER = 100
const SCORE_FILTER_STEP = 10

const COLUMNS: Column[] = [
  { id: 'domain', label: 'Domain' },
  { id: 'employees', label: 'Employees' },
  { id: 'email', label: 'Work email' },
  { id: 'stack', label: 'Tech stack' },
  { id: 'score', label: 'Fit score' },
]

const leads: Lead[] = [
  { id: 1, company: 'Northwind Labs', domain: 'northwindlabs.io', employees: 84, email: 'maria@northwindlabs.io', stack: ['Next.js', 'Stripe'], score: 91 },
  { id: 2, company: 'Brightloop', domain: 'brightloop.co', employees: 36, email: 'tomas@brightloop.co', stack: ['React', 'Segment'], score: 78 },
  { id: 3, company: 'Kestrel Pay', domain: 'kestrelpay.com', employees: 212, email: 'ivan@kestrelpay.com', stack: ['Python', 'Kafka'], score: 86 },
  { id: 4, company: 'Fernhill Studio', domain: 'fernhill.studio', employees: 12, email: 'eva@fernhill.studio', stack: ['Webflow'], score: 52 },
  { id: 5, company: 'Quarry Systems', domain: 'quarry.systems', employees: 540, email: 'peter@quarry.systems', stack: ['Java', 'Snowflake'], score: 67 },
  { id: 6, company: 'Lumen Retail', domain: 'lumenretail.eu', employees: 150, email: 'sofia@lumenretail.eu', stack: ['Shopify', 'Klaviyo'], score: 74 },
]

const status = ref<EnrichStatus>('idle')
const enrichedCount = ref(0)
const minScore = ref(MIN_SCORE_FILTER)
let timer: ReturnType<typeof setInterval> | undefined

const isEnriched = (lead: Lead) => leads.indexOf(lead) < enrichedCount.value
const visibleLeads = computed(() => leads.filter((l) => !isEnriched(l) || l.score >= minScore.value))
const progressPercent = computed(() => Math.round((enrichedCount.value / leads.length) * 100))
const scoreTone = (score: number) => (score >= SCORE_HIGH ? 'high' : score >= SCORE_MEDIUM ? 'mid' : 'low')

function stopTimer() {
  clearInterval(timer)
  timer = undefined
}

function enrich() {
  if (status.value === 'running') return
  stopTimer()
  enrichedCount.value = 0
  status.value = 'running'
  timer = setInterval(() => {
    enrichedCount.value += 1
    if (enrichedCount.value >= leads.length) {
      status.value = 'done'
      stopTimer()
    }
  }, ENRICH_STEP_MS)
}

function reset() {
  stopTimer()
  enrichedCount.value = 0
  status.value = 'idle'
  minScore.value = MIN_SCORE_FILTER
}

onBeforeUnmount(stopTimer)
</script>

<template>
  <div class="lds" :class="{ 'is-preview': preview }" :inert="preview || undefined">
    <header class="lds-top">
      <div class="lds-crumbs"><b>Leads</b> / EU SaaS prospects</div>
      <label class="lds-filter">
        Min score
        <input v-model.number="minScore" type="range" :min="MIN_SCORE_FILTER" :max="MAX_SCORE_FILTER" :step="SCORE_FILTER_STEP" :disabled="status !== 'done'">
        <span>{{ minScore }}</span>
      </label>
      <button v-if="status === 'done'" type="button" class="lds-ghost" @click="reset">Reset</button>
      <button type="button" class="lds-run" :disabled="status === 'running'" @click="enrich">
        {{ status === 'running' ? `Enriching… ${progressPercent}%` : status === 'done' ? 'Enrich again' : '✦ Enrich 6 rows' }}
      </button>
    </header>

    <div v-if="status !== 'idle'" class="lds-progress"><i :style="{ width: `${progressPercent}%` }" /></div>

    <div class="lds-wrap">
      <table>
        <thead>
          <tr>
            <th>Company</th>
            <th v-for="c in COLUMNS" :key="c.id" class="lds-enrich">{{ c.label }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="l in visibleLeads" :key="l.id">
            <td class="lds-company"><span>{{ l.company[0] }}</span>{{ l.company }}</td>
            <template v-if="isEnriched(l)">
              <td class="lds-in">{{ l.domain }}</td>
              <td class="lds-in">{{ l.employees }}</td>
              <td class="lds-in lds-mono">{{ l.email }}</td>
              <td class="lds-in"><em v-for="s in l.stack" :key="s">{{ s }}</em></td>
              <td class="lds-in"><b class="lds-score" :class="scoreTone(l.score)">{{ l.score }}</b></td>
            </template>
            <template v-else>
              <td v-for="c in COLUMNS" :key="c.id" class="lds-empty"><i :class="{ spin: status === 'running' }" /></td>
            </template>
          </tr>
        </tbody>
      </table>
      <p v-if="status === 'idle'" class="lds-hint">Each row is a company with only a name. Run the enrichment to fill in the domain, headcount, a verified email, the tech stack and a fit score.</p>
    </div>
  </div>
</template>

<style>
.lds { width: 960px; height: 600px; border-radius: 14px; overflow: hidden; display: flex; flex-direction: column; background: #FFFCF8; color: #1F1A17; font-family: 'Manrope', system-ui, sans-serif; text-align: left; box-shadow: 0 30px 70px -30px rgba(0, 0, 0, .45); }
.lds button { font: inherit; color: inherit; cursor: pointer; }
.lds.is-preview { pointer-events: none; }
.lds-top { display: flex; align-items: center; gap: 18px; padding: 14px 22px; border-bottom: 1px solid #EFE6DB; background: #fff; }
.lds-crumbs { font-size: 14px; color: #8A7B6E; margin-right: auto; }
.lds-crumbs b { color: #1F1A17; }
.lds-filter { display: flex; align-items: center; gap: 10px; font-size: 12px; font-weight: 700; color: #8A7B6E; }
.lds-filter input { accent-color: #F97316; width: 120px; }
.lds-filter span { width: 24px; color: #1F1A17; }
.lds-run { padding: 9px 18px; border-radius: 999px; border: 0; background: #F97316; color: #fff; font-size: 13px; font-weight: 800; transition: filter .2s; }
.lds-run:hover:not(:disabled) { filter: brightness(1.08); }
.lds-run:disabled { opacity: .75; cursor: default; }
.lds-ghost { padding: 8px 14px; border-radius: 999px; border: 1px solid #E6D9CA; background: #fff; font-size: 12px; font-weight: 700; }
.lds-progress { height: 3px; background: #FDE5D0; }
.lds-progress i { display: block; height: 100%; background: #F97316; transition: width .5s; }
.lds-wrap { flex: 1; overflow: auto; padding: 18px 22px; }
.lds table { width: 100%; border-collapse: separate; border-spacing: 0; font-size: 13px; background: #fff; border: 1px solid #EFE6DB; border-radius: 14px; overflow: hidden; }
.lds th { text-align: left; font-size: 11px; font-weight: 800; letter-spacing: .06em; text-transform: uppercase; color: #8A7B6E; padding: 12px 14px; background: #FBF5EE; border-bottom: 1px solid #EFE6DB; }
.lds th.lds-enrich::before { content: '✦ '; color: #F97316; }
.lds td { padding: 12px 14px; border-bottom: 1px solid #F6EEE4; height: 50px; }
.lds tr:last-child td { border-bottom: 0; }
.lds-company { font-weight: 800; display: flex; align-items: center; gap: 10px; }
.lds-company span { display: grid; place-items: center; width: 26px; height: 26px; border-radius: 8px; background: #FDE5D0; color: #C2410C; font-size: 12px; }
.lds-in { animation: ldsFill .45s; }
.lds-mono { font-family: ui-monospace, Consolas, monospace; font-size: 12px; }
.lds-in em { font-style: normal; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 6px; background: #F3EEE8; margin-right: 4px; }
.lds-score { display: inline-block; min-width: 34px; text-align: center; padding: 3px 8px; border-radius: 999px; font-size: 12px; }
.lds-score.high { background: #DCFCE7; color: #166534; }
.lds-score.mid { background: #FEF3C7; color: #92400E; }
.lds-score.low { background: #FEE2E2; color: #991B1B; }
.lds-empty i { display: block; width: 70%; height: 10px; border-radius: 6px; background: #F3EEE8; }
.lds-empty i.spin { background: linear-gradient(90deg, #F3EEE8 0%, #FDE5D0 50%, #F3EEE8 100%); background-size: 200% 100%; animation: ldsShimmer 1s linear infinite; }
.lds-hint { margin-top: 16px; font-size: 12px; color: #8A7B6E; line-height: 1.5; max-width: 560px; }
@keyframes ldsFill { from { opacity: 0; transform: translateY(6px); } }
@keyframes ldsShimmer { to { background-position: -200% 0; } }
</style>
