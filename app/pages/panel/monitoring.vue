<script setup lang="ts">
// Project monitoring (admins): environment cards per project, checks / metrics / scheduler jobs / containers,
// state history, errors with filters, logs (fetched by our server), settings (projects, environments, recipients).
// Only status, time and checks are required by the contract; missing blocks are simply not shown.
// Tokens and webhook secrets are write-only here: the API never returns them.

interface Check { ok: boolean; detail?: string; latency_ms?: number | null }
interface Job { id: string; name: string; next_run_at: string | null; last_run_at: string | null; last_status: string | null; last_duration_ms: number | null; last_error: string | null; runs: number; failures: number; stale: boolean }
interface Snapshot {
  status: string; environment?: string; time?: string; version?: string; uptime_seconds?: number
  checks?: Record<string, Check>; errors?: { open: number; last_1h: number; last_24h: number }
  bookings?: Record<string, number>; scheduler?: { running: boolean; jobs: Job[] }
  containers?: { service: string; state: string; health: string | null; status: string; image: string }[] | null
}
interface Env {
  id: number; project_id: number; name: string; kind: 'production' | 'test'; base_url: string; enabled: boolean; poll_interval_seconds: number
  has_token: boolean; has_webhook: boolean; state: string; status: string; fail_count: number; last_poll_at: string | null; last_ok_at: string | null
  last_error: string; down_since: string | null; degraded_since: string | null; token_invalid: boolean; snapshot: Snapshot | null
}
interface Project { id: number; name: string; description: string; enabled: boolean; envs: Env[] }
interface ErrorRow { id: number; env_id: number; remote_id: number; source: string; level: string; logger_name: string; message: string; traceback: string; path: string; method: string; user_id: number | null; count: number; first_seen_at: string | null; last_seen_at: string | null; resolved: boolean; via: string }

const { t } = useSite()
const { locale } = useI18n()
const { api } = useTeam()
const p = computed(() => t.value.panel)
const m = computed(() => t.value.panel.monitoring)

const tab = ref<'overview' | 'errors' | 'logs' | 'settings'>('overview')
const projects = ref<Project[]>([])
const envs = computed(() => projects.value.flatMap((x) => x.envs))
const selected = ref<number | null>(null)
const env = computed(() => envs.value.find((e) => e.id === selected.value) ?? envs.value.find((e) => e.enabled) ?? envs.value[0])
const loading = ref(true)
const denied = ref(false)
const failed = ref('')
const toast = (text: string) => {
  failed.value = text
  setTimeout(() => (failed.value = ''), 4000)
}
const now = ref(Date.now())
let timer: ReturnType<typeof setInterval> | undefined

async function load() {
  try {
    projects.value = await api<Project[]>('/monitoring/projects')
    denied.value = false
  } catch (e) {
    if (httpStatus(e) === 403) denied.value = true
    else toast(p.value.errorServer)
  } finally {
    loading.value = false
  }
}
onMounted(() => {
  load()
  loadSettings()
  timer = setInterval(() => {
    now.value = Date.now()
    if (document.visibilityState === 'visible') load()
  }, 30000)
})
onBeforeUnmount(() => clearInterval(timer))

// Formatting
const ago = (iso: string | null) => {
  if (!iso) return '—'
  const s = Math.max(Math.round((now.value - Date.parse(iso)) / 1000), 0)
  return s < 60 ? `${s} s` : s < 3600 ? `${Math.floor(s / 60)} min` : s < 86400 ? `${Math.floor(s / 3600)} h ${Math.floor((s % 3600) / 60)} min` : `${Math.floor(s / 86400)} d`
}
const span = (seconds?: number) => {
  if (seconds === undefined) return ''
  const d = Math.floor(seconds / 86400)
  const h = Math.floor((seconds % 86400) / 3600)
  const min = Math.floor((seconds % 3600) / 60)
  return [d && `${d} d`, h && `${h} h`, `${min} min`].filter(Boolean).join(' ')
}
const when = (iso: string | null) => (iso ? new Date(iso).toLocaleString(locale.value, { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) : '—')
// Known metric names get a label, others are shown as they come
const metricLabel = (k: string) => (m.value.metricLabels as Record<string, string>)[k] ?? k.replace(/_/g, ' ')
const projectName = (id: number) => projects.value.find((x) => x.id === id)?.name ?? ''
const envName = (id: number) => {
  const e = envs.value.find((x) => x.id === id)
  return e ? `${projectName(e.project_id)} · ${e.name}` : ''
}

// Actions
const checking = ref<number | null>(null)
async function checkNow(e: Env) {
  checking.value = e.id
  try {
    const fresh = await api<Env>(`/monitoring/envs/${e.id}/check`, { method: 'POST' })
    projects.value = projects.value.map((x) => ({ ...x, envs: x.envs.map((y) => (y.id === fresh.id ? fresh : y)) }))
    loadEvents()
  } catch {
    toast(p.value.errorServer)
  } finally {
    checking.value = null
  }
}
const events = ref<{ id: number; at: string; kind: string; text: string }[]>([])
async function loadEvents() {
  if (!env.value) return
  events.value = await api<typeof events.value>(`/monitoring/envs/${env.value.id}/events`, { query: { limit: 30 } }).catch(() => [])
}
watch(() => env.value?.id, loadEvents)

// ===== Errors =====
const errFilter = reactive({ project: null as number | null, env: null as number | null, source: '', open: true })
const errors = ref<ErrorRow[]>([])
const sources = ref<string[]>([])
const openError = ref<number | null>(null)
async function loadErrors() {
  const query = { ...(errFilter.project ? { project: errFilter.project } : {}), ...(errFilter.env ? { env: errFilter.env } : {}), open: errFilter.open }
  errors.value = await api<ErrorRow[]>('/monitoring/errors', { query: { ...query, ...(errFilter.source ? { source: errFilter.source } : {}) } }).catch(() => [])
  // Sources differ per project: offer the ones that occur
  sources.value = [...new Set([...sources.value, ...errors.value.map((x) => x.source).filter(Boolean)])].sort()
}
watch(() => errFilter.project, () => (errFilter.env = null))
watch([tab, () => errFilter.project, () => errFilter.env, () => errFilter.source, () => errFilter.open], () => tab.value === 'errors' && loadErrors())
const errEnvs = computed(() => envs.value.filter((e) => !errFilter.project || e.project_id === errFilter.project))

// ===== Logs =====
const logForm = reactive({ env: null as number | null, service: 'backend', tail: 300, q: '' })
const logEnv = computed(() => envs.value.find((x) => x.id === logForm.env) ?? env.value)
// Service names come from /status containers; without them only "backend"
const services = computed(() => {
  const list = logEnv.value?.snapshot?.containers?.map((c) => c.service) ?? []
  return list.length ? list : ['backend']
})
watch(services, (list) => {
  if (!list.includes(logForm.service)) logForm.service = list.includes('backend') ? 'backend' : list[0] ?? 'backend'
})
const logs = ref<{ service: string; origin: string; lines: string[] } | null>(null)
const logsBusy = ref(false)
async function loadLogs() {
  const id = logEnv.value?.id
  if (!id) return
  logsBusy.value = true
  try {
    logs.value = await api(`/monitoring/envs/${id}/logs`, { query: { service: logForm.service, tail: Math.min(Math.max(Number(logForm.tail) || 300, 10), 2000), q: logForm.q.trim() } })
  } catch {
    toast(m.value.logsFailed)
  } finally {
    logsBusy.value = false
  }
}

// ===== Settings =====
const settings = ref<{ recipients: string; default_recipients: string; smtp: boolean; encrypted: boolean; errors_interval: number } | null>(null)
const recipients = ref('')
async function loadSettings() {
  settings.value = await api<NonNullable<typeof settings.value>>('/monitoring/settings').catch(() => null)
  recipients.value = settings.value?.recipients ?? ''
}
async function saveRecipients() {
  settings.value = await api<NonNullable<typeof settings.value>>('/monitoring/settings', { method: 'PUT', body: { recipients: recipients.value } }).catch(() => settings.value)
  toast(m.value.saved)
}
async function testMail() {
  const r = await api<{ sent: boolean; to: string[]; smtp: boolean }>('/monitoring/test-mail', { method: 'POST' }).catch(() => null)
  toast(!r ? p.value.errorServer : r.sent ? `${m.value.mailSent}: ${r.to.join(', ')}` : r.smtp ? m.value.mailFailed : m.value.noSmtp)
}
const saveError = (e: unknown) => toast(httpStatus(e) === 409 ? m.value.nameUsed : httpStatus(e) === 400 ? m.value.needToken : httpStatus(e) === 422 ? m.value.invalid : p.value.errorServer)

// Two-click delete shared by both forms
const sure = ref(false)
function confirmed() {
  if (sure.value) {
    sure.value = false
    return true
  }
  sure.value = true
  setTimeout(() => (sure.value = false), 3000)
  return false
}

// Project form
const pform = ref<{ id: number | null; name: string; description: string; enabled: boolean } | null>(null)
const openProject = (x?: Project) => (pform.value = x ? { id: x.id, name: x.name, description: x.description, enabled: x.enabled } : { id: null, name: '', description: '', enabled: true })
async function saveProject() {
  const f = pform.value
  if (!f) return
  try {
    const body = { name: f.name.trim(), description: f.description, enabled: f.enabled }
    await api(f.id ? `/monitoring/projects/${f.id}` : '/monitoring/projects', { method: f.id ? 'PATCH' : 'POST', body })
    pform.value = null
    await load()
  } catch (e) {
    saveError(e)
  }
}
async function deleteProject() {
  if (!confirmed()) return
  const id = pform.value?.id
  pform.value = null
  if (id) await api(`/monitoring/projects/${id}`, { method: 'DELETE' }).catch(() => toast(p.value.errorServer))
  await load()
}

// Environment form
const form = ref<{ id: number | null; project_id: number; name: string; kind: 'production' | 'test'; base_url: string; api_token: string; webhook_secret: string; clear_webhook: boolean; enabled: boolean; poll_interval_seconds: number; has_token: boolean; has_webhook: boolean } | null>(null)
function openForm(projectId: number, e?: Env) {
  form.value = e
    ? { id: e.id, project_id: e.project_id, name: e.name, kind: e.kind, base_url: e.base_url, api_token: '', webhook_secret: '', clear_webhook: false, enabled: e.enabled, poll_interval_seconds: e.poll_interval_seconds, has_token: e.has_token, has_webhook: e.has_webhook }
    : { id: null, project_id: projectId, name: '', kind: 'production', base_url: 'https://', api_token: '', webhook_secret: '', clear_webhook: false, enabled: true, poll_interval_seconds: 60, has_token: false, has_webhook: false }
}
// Enabling needs a token (saved or typed now)
const canEnable = computed(() => !!form.value && (form.value.has_token || !!form.value.api_token))
async function saveForm() {
  const f = form.value
  if (!f) return
  const common = { name: f.name.trim(), kind: f.kind, base_url: f.base_url.trim(), enabled: f.enabled && canEnable.value, poll_interval_seconds: Number(f.poll_interval_seconds) || 60 }
  try {
    if (f.id) await api(`/monitoring/envs/${f.id}`, { method: 'PATCH', body: { ...common, api_token: f.api_token || null, webhook_secret: f.webhook_secret || null, clear_webhook: f.clear_webhook } })
    else await api('/monitoring/envs', { method: 'POST', body: { ...common, project_id: f.project_id, api_token: f.api_token, webhook_secret: f.webhook_secret } })
    form.value = null
    await load()
  } catch (e) {
    saveError(e)
  }
}
async function deleteEnv() {
  if (!confirmed()) return
  const id = form.value?.id
  form.value = null
  if (id) await api(`/monitoring/envs/${id}`, { method: 'DELETE' }).catch(() => toast(p.value.errorServer))
  await load()
}
const webhookUrl = (e: Env) => `${location.origin}/api/team/monitoring/webhook/${e.id}`
async function copy(text: string) {
  await navigator.clipboard?.writeText(text).catch(() => {})
  toast(m.value.copied)
}
</script>

<template>
  <div class="mo">
    <header class="tp-head">
      <div>
        <h1>{{ m.title }}</h1>
        <p>{{ m.subtitle }}</p>
      </div>
      <div class="ex-seg mo-tabs" role="tablist">
        <button v-for="k in (['overview', 'errors', 'logs', 'settings'] as const)" :key="k" type="button" role="tab" :aria-selected="tab === k" :class="{ on: tab === k }" @click="tab = k">{{ m.tabs[k] }}</button>
      </div>
    </header>

    <div v-if="loading" class="kb-loading"><span class="spinner" /></div>
    <p v-else-if="denied" class="al-empty">{{ m.denied }}</p>

    <template v-else>
      <!-- Environment cards, grouped by project -->
      <template v-if="tab !== 'settings'">
        <div v-for="pr in projects" :key="pr.id" class="mo-project" :class="{ off: !pr.enabled }">
          <h2 class="mo-project-name">{{ pr.name }} <small v-if="!pr.enabled">{{ m.disabled }}</small></h2>
          <div class="mo-envs">
            <button v-for="e in pr.envs" :key="e.id" type="button" class="mo-env" :class="[e.enabled && pr.enabled ? e.state : 'idle', { on: env?.id === e.id, off: !e.enabled || !pr.enabled }]" @click="selected = e.id">
              <span class="mo-dot" :class="e.enabled && pr.enabled ? e.state : 'idle'" aria-hidden="true" />
              <span class="mo-env-main">
                <b>{{ e.name }} <small>{{ e.enabled && pr.enabled ? m.states[e.state as keyof typeof m.states] ?? e.state : m.disabled }}</small></b>
                <small><span class="mo-kind" :class="e.kind">{{ m.kinds[e.kind] }}</span>{{ e.snapshot?.version ? ` v${e.snapshot.version}` : '' }}<template v-if="e.snapshot?.uptime_seconds !== undefined"> · {{ m.uptime }} {{ span(e.snapshot.uptime_seconds) }}</template></small>
                <small v-if="!e.has_token" class="mo-bad">{{ m.noToken }}</small>
                <template v-else>
                  <small>{{ m.lastOk }} {{ ago(e.last_ok_at) }}<template v-if="e.state === 'down' && e.down_since"> · <em>{{ m.downFor }} {{ ago(e.down_since) }}</em></template></small>
                  <small v-if="e.token_invalid" class="mo-bad">{{ m.badToken }}</small>
                  <small v-else-if="e.last_error" class="mo-bad">{{ e.last_error }}</small>
                </template>
              </span>
              <span v-if="e.snapshot?.errors" class="mo-err-count" :title="m.errorsOpen">{{ e.snapshot.errors.open }}</span>
            </button>
            <p v-if="!pr.envs.length" class="sd-muted">{{ m.noEnvs }}</p>
          </div>
        </div>
        <p v-if="!projects.length" class="al-empty">{{ m.noProjects }} <button type="button" class="btn btn-primary btn-sm" @click="tab = 'settings'; openProject()">{{ m.addProject }}</button></p>
      </template>

      <!-- Overview of the chosen environment -->
      <template v-if="tab === 'overview' && env">
        <div class="mo-bar">
          <h2>{{ envName(env.id) }} <small>{{ env.base_url }}</small></h2>
          <button type="button" class="btn btn-ghost btn-sm" :disabled="checking === env.id || !env.has_token" @click="checkNow(env)"><AppIcon name="repeat" /> {{ m.checkNow }}</button>
        </div>
        <p v-if="!env.snapshot" class="sd-muted">{{ env.has_token ? m.noSnapshot : m.noToken }}</p>
        <template v-else>
          <div class="mo-grid">
            <section class="sd-card">
              <h2><AppIcon name="shield" /> {{ m.checks }}</h2>
              <ul class="mo-checks">
                <li v-for="(c, name) in env.snapshot.checks" :key="name" :class="{ bad: !c.ok }">
                  <span class="mo-dot" :class="c.ok ? 'up' : 'down'" /><b>{{ name }}</b>
                  <small>{{ c.detail }}<template v-if="c.latency_ms !== null && c.latency_ms !== undefined"> · {{ c.latency_ms }} ms</template></small>
                </li>
              </ul>
            </section>
            <section v-if="env.snapshot.bookings || env.snapshot.errors" class="sd-card">
              <h2><AppIcon name="chart" /> {{ m.metrics }}</h2>
              <dl class="mo-nums">
                <div v-for="(v, k) in env.snapshot.bookings" :key="k" :class="{ warn: k === 'lessons_next_7d_without_car' && v > 0 }"><dt>{{ metricLabel(String(k)) }}</dt><dd>{{ v }}</dd></div>
                <template v-if="env.snapshot.errors">
                  <div><dt>{{ m.errorsOpen }}</dt><dd>{{ env.snapshot.errors.open }}</dd></div>
                  <div><dt>{{ m.errors1h }}</dt><dd>{{ env.snapshot.errors.last_1h }}</dd></div>
                  <div><dt>{{ m.errors24h }}</dt><dd>{{ env.snapshot.errors.last_24h }}</dd></div>
                </template>
              </dl>
            </section>
          </div>
          <section v-if="env.snapshot.scheduler" class="sd-card">
            <h2><AppIcon name="clock" /> {{ m.scheduler }} <small :class="{ 'mo-bad': !env.snapshot.scheduler.running }">{{ env.snapshot.scheduler.running ? m.running : m.stopped }}</small></h2>
            <div class="mo-scroll">
              <table class="mo-table">
                <thead><tr><th>{{ m.job }}</th><th>{{ m.lastRun }}</th><th>{{ m.nextRun }}</th><th>{{ m.result }}</th><th>{{ m.runs }}</th></tr></thead>
                <tbody>
                  <tr v-for="j in env.snapshot.scheduler.jobs ?? []" :key="j.id" :class="{ bad: j.stale || j.last_status === 'error' }">
                    <td><b>{{ j.name || j.id }}</b><small v-if="j.last_error">{{ j.last_error }}</small></td>
                    <td>{{ when(j.last_run_at) }}<small v-if="j.last_duration_ms !== null && j.last_duration_ms !== undefined">{{ j.last_duration_ms }} ms</small></td>
                    <td>{{ when(j.next_run_at) }}</td>
                    <td>{{ j.stale ? m.stale : j.last_status ?? '—' }}</td>
                    <td>{{ j.runs ?? '—' }} / {{ j.failures ?? '—' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>
          <section v-if="env.snapshot.containers?.length" class="sd-card">
            <h2><AppIcon name="grid" /> {{ m.containers }}</h2>
            <div class="mo-scroll">
              <table class="mo-table">
                <thead><tr><th>{{ m.service }}</th><th>{{ m.state }}</th><th>{{ m.health }}</th><th>{{ m.image }}</th></tr></thead>
                <tbody>
                  <tr v-for="c in env.snapshot.containers" :key="c.service" :class="{ bad: c.state !== 'running' || c.health === 'unhealthy' }">
                    <td><b>{{ c.service }}</b><small>{{ c.status }}</small></td><td>{{ c.state }}</td><td>{{ c.health ?? '—' }}</td><td class="mo-mono">{{ c.image }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>
        </template>
        <section class="sd-card">
          <h2><AppIcon name="note" /> {{ m.history }}</h2>
          <p v-if="!events.length" class="sd-muted">—</p>
          <ul class="mo-events">
            <li v-for="x in events" :key="x.id" :class="x.kind"><time>{{ when(x.at) }}</time><span>{{ x.text }}</span></li>
          </ul>
        </section>
      </template>

      <!-- Errors -->
      <section v-if="tab === 'errors'" class="sd-card">
        <div class="mo-filters">
          <select v-model="errFilter.project" class="tp-input" :aria-label="m.project"><option :value="null">{{ m.allProjects }}</option><option v-for="x in projects" :key="x.id" :value="x.id">{{ x.name }}</option></select>
          <select v-model="errFilter.env" class="tp-input" :aria-label="m.environment"><option :value="null">{{ m.allEnvs }}</option><option v-for="e in errEnvs" :key="e.id" :value="e.id">{{ envName(e.id) }}</option></select>
          <select v-model="errFilter.source" class="tp-input" :aria-label="m.source"><option value="">{{ m.allSources }}</option><option v-for="s in sources" :key="s" :value="s">{{ s }}</option></select>
          <label class="mo-check"><input v-model="errFilter.open" type="checkbox" class="kb-check">{{ m.openOnly }}</label>
        </div>
        <p v-if="!errors.length" class="sd-muted">{{ m.noErrors }}</p>
        <ul class="mo-errors">
          <li v-for="x in errors" :key="x.id" :class="{ resolved: x.resolved }">
            <button type="button" class="mo-error" :aria-expanded="openError === x.id" @click="openError = openError === x.id ? null : x.id">
              <span class="mo-count">×{{ x.count }}</span>
              <span class="cr-inv-text"><b>{{ x.message }}</b><small>{{ envName(x.env_id) }} · {{ x.source }} · {{ x.level }} · {{ when(x.last_seen_at) }}<template v-if="x.path"> · {{ x.method }} {{ x.path }}</template></small></span>
            </button>
            <div v-if="openError === x.id" class="mo-detail">
              <p>#{{ x.remote_id }}<template v-if="x.logger_name"> · {{ x.logger_name }}</template> · {{ m.first }} {{ when(x.first_seen_at) }} · {{ x.via }}<template v-if="x.user_id"> · user {{ x.user_id }}</template><template v-if="x.resolved"> · {{ m.resolved }}</template></p>
              <pre v-if="x.traceback">{{ x.traceback }}</pre>
            </div>
          </li>
        </ul>
      </section>

      <!-- Logs -->
      <section v-if="tab === 'logs'" class="sd-card">
        <form class="mo-filters" @submit.prevent="loadLogs">
          <select v-model="logForm.env" class="tp-input" :aria-label="m.environment"><option :value="null">{{ env ? envName(env.id) : '—' }}</option><option v-for="e in envs" :key="e.id" :value="e.id">{{ envName(e.id) }}</option></select>
          <select v-model="logForm.service" class="tp-input" :aria-label="m.service"><option v-for="s in services" :key="s">{{ s }}</option></select>
          <input v-model.number="logForm.tail" type="number" min="10" max="2000" class="tp-input mo-tail" :aria-label="m.tail">
          <input v-model="logForm.q" class="tp-input" maxlength="200" :placeholder="m.search" :aria-label="m.search">
          <button class="btn btn-primary btn-sm" :disabled="logsBusy || !logEnv?.has_token">{{ m.loadLogs }}</button>
        </form>
        <p v-if="logs" class="sd-muted">{{ logs.service }} · {{ logs.origin }} · {{ logs.lines.length }} {{ m.lines }}</p>
        <pre v-if="logs" class="mo-logs">{{ logs.lines.join('\n') }}</pre>
      </section>

      <!-- Settings -->
      <template v-if="tab === 'settings'">
        <section class="sd-card">
          <div class="sd-bar"><h2><AppIcon name="globe" /> {{ m.projects }}</h2><button type="button" class="btn btn-ghost btn-sm" @click="openProject()"><AppIcon name="plus" /> {{ m.addProject }}</button></div>
          <p v-if="!projects.length" class="sd-muted">{{ m.noProjects }}</p>
          <div v-for="pr in projects" :key="pr.id" class="mo-set-project">
            <div class="mo-envrow mo-project-row">
              <span class="cr-inv-text"><b>{{ pr.name }} <small>{{ pr.enabled ? '' : m.disabled }}</small></b><small v-if="pr.description">{{ pr.description }}</small></span>
              <button type="button" class="tp-icon-btn sm" :aria-label="p.cats.edit" @click="openProject(pr)"><AppIcon name="edit" /></button>
            </div>
            <ul class="cr-list">
              <li v-for="e in pr.envs" :key="e.id" class="mo-envrow">
                <span class="cr-inv-text"><b>{{ e.name }} <span class="mo-kind" :class="e.kind">{{ m.kinds[e.kind] }}</span> <small>{{ e.enabled ? '' : m.disabled }}</small></b><small>{{ e.base_url }}</small>
                  <small>{{ m.token }}: {{ e.has_token ? m.set : m.notSet }} · {{ m.webhook }}: {{ e.has_webhook ? m.set : m.notSet }} · {{ m.every }} {{ e.poll_interval_seconds }} s</small></span>
                <button type="button" class="tp-icon-btn sm" :aria-label="p.cats.edit" @click="openForm(pr.id, e)"><AppIcon name="edit" /></button>
              </li>
            </ul>
            <button type="button" class="btn btn-ghost btn-sm" @click="openForm(pr.id)"><AppIcon name="plus" /> {{ m.addEnv }}</button>
            <div v-for="e in pr.envs.filter((x) => x.has_webhook)" :key="`w${e.id}`" class="mo-webhook">
              <small>MONITORING_WEBHOOK_URL ({{ e.name }})</small>
              <code>{{ webhookUrl(e) }}</code>
              <button type="button" class="tp-icon-btn sm" :aria-label="m.copy" @click="copy(webhookUrl(e))"><AppIcon name="copy" /></button>
            </div>
          </div>
        </section>
        <section v-if="settings" class="sd-card">
          <h2><AppIcon name="mail" /> {{ m.alerts }}</h2>
          <label class="tp-field"><span>{{ m.recipients }}</span><input v-model="recipients" maxlength="2000" :placeholder="settings.default_recipients"></label>
          <p class="sd-muted">{{ settings.smtp ? m.smtpOk : m.noSmtp }} · {{ settings.encrypted ? m.encrypted : m.notEncrypted }} · /errors {{ m.every }} {{ settings.errors_interval }} s</p>
          <div class="rc-form-actions">
            <button type="button" class="btn btn-primary btn-sm" @click="saveRecipients">{{ p.save }}</button>
            <button type="button" class="btn btn-ghost btn-sm" @click="testMail"><AppIcon name="send" /> {{ m.testMail }}</button>
          </div>
        </section>
      </template>
    </template>

    <!-- Project form -->
    <div v-if="pform" class="tm-overlay" @click.self="pform = null">
      <form class="tm" role="dialog" aria-modal="true" :aria-label="m.project" @submit.prevent="saveProject">
        <header class="tm-head"><h2>{{ pform.id ? pform.name : m.addProject }}</h2><button type="button" class="tp-icon-btn sm" :aria-label="p.close" @click="pform = null"><AppIcon name="close" /></button></header>
        <div class="tm-row">
          <label class="tp-field"><span>{{ m.name }}</span><input v-model="pform.name" required maxlength="80"></label>
          <label class="tp-field mo-enabled"><span>{{ m.enabled }}</span><input v-model="pform.enabled" type="checkbox" class="kb-check"></label>
        </div>
        <label class="tp-field"><span>{{ m.description }}</span><textarea v-model="pform.description" maxlength="2000" rows="2" /></label>
        <footer class="tm-foot">
          <button v-if="pform.id" type="button" class="btn btn-sm tm-delete" :class="{ sure }" @click="deleteProject"><AppIcon name="trash" /> {{ sure ? p.sure : p.delete }}</button>
          <div class="tm-foot-right">
            <button type="button" class="btn btn-ghost btn-sm" @click="pform = null">{{ p.cancel }}</button>
            <button class="btn btn-primary btn-sm">{{ p.save }}</button>
          </div>
        </footer>
      </form>
    </div>

    <!-- Environment form -->
    <div v-if="form" class="tm-overlay" @click.self="form = null">
      <form class="tm" role="dialog" aria-modal="true" :aria-label="m.environment" @submit.prevent="saveForm">
        <header class="tm-head"><h2>{{ form.id ? form.name : `${projectName(form.project_id)} · ${m.addEnv}` }}</h2><button type="button" class="tp-icon-btn sm" :aria-label="p.close" @click="form = null"><AppIcon name="close" /></button></header>
        <div class="tm-row">
          <label class="tp-field"><span>{{ m.envName }}</span><input v-model="form.name" required maxlength="80"></label>
          <label class="tp-field"><span>{{ m.kind }}</span><select v-model="form.kind" class="tp-input"><option value="production">{{ m.kinds.production }}</option><option value="test">{{ m.kinds.test }}</option></select></label>
        </div>
        <label class="tp-field"><span>base_url</span><input v-model="form.base_url" type="url" required maxlength="300"></label>
        <label class="tp-field"><span>api_token</span><input v-model="form.api_token" type="password" autocomplete="off" :placeholder="form.has_token ? m.keep : m.tokenLater"></label>
        <label class="tp-field"><span>webhook_secret</span><input v-model="form.webhook_secret" type="password" autocomplete="off" :placeholder="form.has_webhook ? m.keep : m.optional"></label>
        <label v-if="form.has_webhook" class="mo-check"><input v-model="form.clear_webhook" type="checkbox" class="kb-check">{{ m.clearWebhook }}</label>
        <div class="tm-row">
          <label class="tp-field"><span>{{ m.pollInterval }}</span><input v-model.number="form.poll_interval_seconds" type="number" min="15" max="3600" required></label>
          <label class="tp-field mo-enabled"><span>{{ m.enabled }}</span><input v-model="form.enabled" type="checkbox" class="kb-check" :disabled="!canEnable"></label>
        </div>
        <p class="sd-muted">{{ canEnable ? m.secretsHint : m.needToken }}</p>
        <footer class="tm-foot">
          <button v-if="form.id" type="button" class="btn btn-sm tm-delete" :class="{ sure }" @click="deleteEnv"><AppIcon name="trash" /> {{ sure ? p.sure : p.delete }}</button>
          <div class="tm-foot-right">
            <button type="button" class="btn btn-ghost btn-sm" @click="form = null">{{ p.cancel }}</button>
            <button class="btn btn-primary btn-sm">{{ p.save }}</button>
          </div>
        </footer>
      </form>
    </div>

    <Transition name="toast"><div v-if="failed" class="tp-toast" role="status">{{ failed }}</div></Transition>
  </div>
</template>

<style>
/* ===== Project monitoring ===== */
.mo { display: grid; gap: 12px; max-width: 1100px; }
.mo .btn .ico { width: 16px; height: 16px; }
.mo-tabs { flex-wrap: wrap; }
.mo-project { display: grid; gap: 8px; }
.mo-project.off { opacity: .7; }
.mo-project-name { font-size: .86rem; font-weight: 800; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }
.mo-project-name small { font-weight: 700; text-transform: none; }
.mo-envs { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 10px; }
.mo-env {
  display: flex; align-items: flex-start; gap: 10px; padding: 14px; border-radius: 18px; cursor: pointer; text-align: left;
  background: var(--surface); border: 1px solid var(--line); border-left: 5px solid #9CA3AF; color: var(--ink);
}
.mo-env.up { border-left-color: #19C3A6; }
.mo-env.degraded { border-left-color: #F59E0B; }
.mo-env.down { border-left-color: #E5484D; background: color-mix(in srgb, #E5484D 7%, var(--surface)); }
.mo-env.on { box-shadow: 0 0 0 3px rgba(91, 75, 255, .2); }
.mo-env.off { opacity: .6; }
.mo-env-main { flex: 1; min-width: 0; display: grid; gap: 2px; }
.mo-env-main b { font-size: 1rem; overflow-wrap: anywhere; }
.mo-env-main b small { color: var(--muted); font-weight: 700; font-size: .78rem; text-transform: uppercase; }
.mo-env-main small { color: var(--muted); font-weight: 600; font-size: .78rem; overflow: hidden; text-overflow: ellipsis; }
.mo-env-main em { color: #E5484D; font-style: normal; font-weight: 800; }
.mo-kind { display: inline-block; padding: 0 7px; border-radius: 999px; background: var(--bg-2); color: var(--muted); font-size: .68rem; font-weight: 800; text-transform: uppercase; vertical-align: 1px; }
.mo-kind.production { background: rgba(91, 75, 255, .14); color: var(--accent); }
.mo-bad { color: #E5484D !important; }
.mo-dot { flex: none; width: 12px; height: 12px; margin-top: 4px; border-radius: 50%; background: #9CA3AF; }
.mo-dot.up { background: #19C3A6; }
.mo-dot.degraded { background: #F59E0B; }
.mo-dot.down { background: #E5484D; animation: tpPulse 1.6s ease-in-out infinite; }
.mo-err-count { flex: none; min-width: 28px; padding: 2px 8px; border-radius: 999px; background: var(--bg-2); text-align: center; font-weight: 800; font-size: .8rem; }
.mo-bar { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px; }
.mo-bar h2 { font-size: 1.05rem; font-weight: 800; overflow-wrap: anywhere; }
.mo-bar h2 small { color: var(--muted); font-weight: 600; font-size: .78rem; overflow-wrap: anywhere; }
.mo-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 12px; }
.mo-checks { display: grid; gap: 6px; margin-top: 8px; }
.mo-checks li { display: grid; grid-template-columns: auto auto 1fr; align-items: center; gap: 8px; font-size: .9rem; }
.mo-checks .mo-dot { margin: 0; }
.mo-checks small { color: var(--muted); font-weight: 600; overflow-wrap: anywhere; }
.mo-checks li.bad small { color: #E5484D; }
.mo-nums { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 8px; margin-top: 8px; }
.mo-nums div { padding: 8px 10px; border-radius: 12px; background: var(--bg); border: 1px solid var(--line); }
.mo-nums div.warn { border-color: rgba(245, 158, 11, .6); }
.mo-nums dt { color: var(--muted); font-size: .72rem; font-weight: 700; }
.mo-nums dd { font-family: var(--font-display); font-weight: 600; font-size: 1.2rem; }
.mo-scroll { overflow-x: auto; margin-top: 8px; }
.mo-table { width: 100%; min-width: 560px; border-collapse: collapse; font-size: .85rem; }
.mo-table th { text-align: left; padding: 6px 8px; color: var(--muted); font-size: .72rem; text-transform: uppercase; border-bottom: 1px solid var(--line-2); }
.mo-table td { padding: 8px; border-bottom: 1px solid var(--line); vertical-align: top; }
.mo-table td small { display: block; color: var(--muted); font-size: .74rem; overflow-wrap: anywhere; }
.mo-table tr.bad td { background: rgba(229, 72, 77, .07); }
.mo-mono, .mo-webhook code { font-family: ui-monospace, monospace; font-size: .78rem; overflow-wrap: anywhere; }
.mo-events { display: grid; gap: 4px; margin-top: 8px; font-size: .84rem; }
.mo-events li { display: grid; grid-template-columns: 110px 1fr; gap: 8px; }
.mo-events li span { overflow-wrap: anywhere; }
.mo-events time { color: var(--muted); font-weight: 700; }
.mo-events li.mail span { color: var(--accent); }
.mo-filters { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin-bottom: 10px; }
.mo-filters .tp-input { flex: 1 1 140px; min-width: 0; }
.mo-filters .mo-tail { flex: 0 0 90px; }
.mo-check { display: inline-flex; align-items: center; gap: 8px; min-height: 44px; font-weight: 700; font-size: .88rem; cursor: pointer; }
.mo-errors { display: grid; gap: 6px; }
.mo-errors li.resolved { opacity: .6; }
.mo-error { display: flex; align-items: center; gap: 10px; width: 100%; min-height: 52px; padding: 8px 12px; border-radius: 14px; cursor: pointer; text-align: left; background: var(--bg); border: 1px solid var(--line); color: var(--ink); }
.mo-count { flex: none; padding: 2px 8px; border-radius: 999px; background: rgba(229, 72, 77, .14); color: #E5484D; font-weight: 800; font-size: .76rem; }
.mo-detail { padding: 8px 12px; font-size: .8rem; color: var(--muted); }
.mo-detail pre, .mo-logs {
  max-height: 60vh; overflow: auto; margin-top: 6px; padding: 12px; border-radius: 12px; background: #0E0E13; color: #D7D7E0;
  font: .74rem/1.5 ui-monospace, monospace; white-space: pre-wrap; overflow-wrap: anywhere;
}
.mo-set-project { display: grid; gap: 8px; margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--line); justify-items: start; }
.mo-set-project > * { width: 100%; }
.mo-set-project > .btn { width: auto; }
.mo-envrow { display: flex; align-items: center; gap: 10px; padding: 8px 8px 8px 12px; border-radius: 14px; background: var(--bg); border: 1px solid var(--line); }
.mo-project-row { background: var(--bg-2); }
.mo-webhook { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; padding: 10px 12px; border-radius: 14px; background: var(--bg-2); }
.mo-webhook small { flex-basis: 100%; color: var(--muted); font-weight: 800; font-size: .74rem; }
.mo-webhook code { flex: 1; min-width: 0; }
.mo-enabled input { width: 22px !important; height: 22px; }
@media (max-width: 640px) {
  .mo-events li { grid-template-columns: 1fr; gap: 0; }
}
</style>
