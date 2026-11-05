<script setup lang="ts">
// Mini CRM: client list (search, status and tag filters) and one client (?id=): contacts, money and hours,
// invoices (paid → income), contact history with "contact again", projects, open tasks, meetings.
import { hm, type ClientDetail, type ClientLogItem, type ClientStatus, type TeamClient, type TeamInvoice, type TeamProject } from '~/composables/useTeam'

const { t } = useSite()
const { locale } = useI18n()
const localePath = useLocalePath()
const route = useRoute()
const { api, clients, loadClients, loadProjects, synced } = useTeam()
const timer = useTimer()

const p = computed(() => t.value.panel)
const c = computed(() => t.value.panel.clients)
const STATUSES: ClientStatus[] = ['lead', 'active', 'paused', 'former']
const pad = (n: number) => String(n).padStart(2, '0')
const today = (() => {
  const d = new Date()
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
})()
const fmtDay = (s: string) => new Date(`${s}T12:00:00`).toLocaleDateString(locale.value, { day: 'numeric', month: 'short', year: 'numeric' })
const money = (n: number, cur = 'EUR') => {
  try {
    return new Intl.NumberFormat(locale.value, { style: 'currency', currency: cur, currencyDisplay: 'narrowSymbol' }).format(n)
  } catch {
    return `${n.toFixed(2)} ${cur}`
  }
}
const failed = ref('')
const toast = (e: unknown) => {
  failed.value = isOffline(e) ? p.value.offlineOnly : p.value.errorServer
  setTimeout(() => (failed.value = ''), 3500)
}
const confirmKey = ref('')
function sure(key: string, action: () => unknown) {
  if (confirmKey.value === key) {
    confirmKey.value = ''
    return action()
  }
  confirmKey.value = key
  setTimeout(() => confirmKey.value === key && (confirmKey.value = ''), 3000)
}

// ===== List =====
const loading = ref(true)
onMounted(() => loadClients().catch(toast).finally(() => (loading.value = false)))
const search = ref('')
const status = ref<ClientStatus | ''>('')
const tag = ref('')
const allTags = computed(() => [...new Set(clients.value.flatMap((x) => x.tags))].sort())
const shown = computed(() => {
  const q = search.value.trim().toLowerCase()
  return clients.value.filter((x) =>
    (!status.value || x.status === status.value) && (!tag.value || x.tags.includes(tag.value))
    && (!q || [x.name, x.company, x.email, x.phone, x.tags.join(' ')].some((v) => v.toLowerCase().includes(q))))
})

// ===== One client =====
const id = computed(() => Number(route.query.id) || null)
const detail = ref<ClientDetail | null>(null)
async function loadDetail() {
  if (!id.value) return (detail.value = null)
  try {
    detail.value = await api<ClientDetail>(`/clients/${id.value}`)
  } catch (e) {
    toast(e)
  }
}
watch(id, loadDetail, { immediate: true })
watch(synced, () => {
  loadClients().catch(() => {})
  loadDetail()
})
async function reload() {
  await Promise.all([loadDetail(), loadClients().catch(() => {}), loadProjects().catch(() => {})])
}

// Client form (new / edit)
const form = ref<(Omit<TeamClient, 'id' | 'tags' | 'rate'> & { id: number | null; tags: string; rate: string }) | null>(null)
function openForm(x?: TeamClient) {
  form.value = x
    ? { ...x, tags: x.tags.join(', '), rate: x.rate === null ? '' : String(x.rate) }
    : { id: null, name: '', company: '', email: '', phone: '', telegram: '', website: '', lang: locale.value, currency: 'EUR', rate: '', tags: '', note: '', status: 'active' }
}
async function saveForm() {
  const f = form.value
  if (!f?.name.trim()) return
  const { id: fid, open_invoices: _o, late_invoices: _l, ...rest } = f as typeof f & { open_invoices?: number; late_invoices?: number }
  const rate = rest.rate.trim() ? Number(rest.rate.replace(',', '.')) : null
  const body = { ...rest, name: rest.name.trim(), rate: rate !== null && Number.isFinite(rate) ? rate : null, tags: rest.tags.split(',').map((x) => x.trim()).filter(Boolean) }
  try {
    const saved = fid
      ? await api<TeamClient>(`/clients/${fid}`, { method: 'PATCH', body })
      : await api<TeamClient>('/clients', { method: 'POST', body })
    form.value = null
    await loadClients()
    if (!fid) navigateTo({ query: { id: saved.id } })
    else await loadDetail()
  } catch (e) {
    toast(e)
  }
}
async function removeClient() {
  const fid = form.value?.id
  if (!fid) return
  form.value = null
  await api(`/clients/${fid}`, { method: 'DELETE' }).catch(toast)
  await loadClients().catch(() => {})
  navigateTo({ query: {} })
}
async function setStatus(s: ClientStatus) {
  if (!detail.value) return
  detail.value.client.status = s
  await api(`/clients/${detail.value.client.id}`, { method: 'PATCH', body: { status: s } }).catch(toast)
  loadClients().catch(() => {})
}

// Contacts as links
const contacts = computed(() => {
  const x = detail.value?.client
  if (!x) return []
  const web = x.website && (/^https?:\/\//.test(x.website) ? x.website : `https://${x.website}`)
  return [
    x.email && { icon: 'mail', label: x.email, href: `mailto:${x.email}` },
    x.phone && { icon: 'phone', label: x.phone, href: `tel:${x.phone.replace(/\s/g, '')}` },
    x.telegram && { icon: 'telegram', label: x.telegram, href: `https://t.me/${x.telegram.replace(/^@/, '')}` },
    web && { icon: 'globe', label: x.website, href: web },
  ].filter(Boolean) as { icon: string; label: string; href: string }[]
})

// Invoices
const invForm = reactive({ open: false, title: '', amount: '', due: '', project_id: null as number | null })
async function addInvoice() {
  const amount = Number(invForm.amount.replace(',', '.'))
  if (!id.value || !invForm.title.trim() || !(amount > 0)) return
  try {
    await api(`/clients/${id.value}/invoices`, { method: 'POST', body: { title: invForm.title.trim(), amount, due: invForm.due || null, project_id: invForm.project_id } })
    Object.assign(invForm, { open: false, title: '', amount: '', due: '' })
    await reload()
  } catch (e) {
    toast(e)
  }
}
async function payInvoice(i: TeamInvoice, paid: boolean) {
  try {
    await api(`/invoices/${i.id}/${paid ? 'pay' : 'unpay'}`, { method: 'POST', body: {} })
    await reload()
  } catch (e) {
    toast(e)
  }
}
async function deleteInvoice(i: TeamInvoice) {
  await api(`/invoices/${i.id}`, { method: 'DELETE' }).catch(toast)
  await reload()
}

// Contact history (+ "contact again in N days")
const LOG_KINDS = ['call', 'email', 'meeting', 'message'] as const
const logForm = reactive({ kind: 'call' as ClientLogItem['kind'], day: today, text: '', again: null as number | null })
const AGAIN = [null, 3, 7, 14, 30]
async function addLog() {
  if (!id.value || !logForm.text.trim()) return
  let followup: string | null = null
  if (logForm.again) {
    const d = new Date(`${logForm.day}T12:00:00`)
    d.setDate(d.getDate() + logForm.again)
    followup = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
  }
  try {
    const item = await api<ClientLogItem>(`/clients/${id.value}/log`, { method: 'POST', body: { kind: logForm.kind, day: logForm.day, text: logForm.text.trim(), followup } })
    detail.value?.log.unshift(item)
    Object.assign(logForm, { text: '', again: null })
  } catch (e) {
    toast(e)
  }
}
async function followupDone(x: ClientLogItem) {
  x.followup_done = true
  await api(`/client-log/${x.id}`, { method: 'PATCH', body: { followup_done: true } }).catch(toast)
}
async function deleteLog(x: ClientLogItem) {
  if (detail.value) detail.value.log = detail.value.log.filter((l) => l !== x)
  await api(`/client-log/${x.id}`, { method: 'DELETE' }).catch(toast)
}

// Projects
const projForm = reactive({ open: false, title: '', rate: '', budget: '' })
const num = (s: string) => (s.trim() ? Number(s.replace(',', '.')) : null)
async function addProject() {
  if (!id.value || !projForm.title.trim()) return
  try {
    await api(`/clients/${id.value}/projects`, { method: 'POST', body: { title: projForm.title.trim(), rate: num(projForm.rate), budget: num(projForm.budget) } })
    Object.assign(projForm, { open: false, title: '', rate: '', budget: '' })
    await reload()
  } catch (e) {
    toast(e)
  }
}
const NEXT = { active: 'paused', paused: 'done', done: 'active' } as const
async function cycleProject(x: TeamProject) {
  x.status = NEXT[x.status]
  await api(`/projects/${x.id}`, { method: 'PATCH', body: { status: x.status } }).catch(toast)
  loadProjects().catch(() => {})
}
async function deleteProject(x: TeamProject) {
  await api(`/projects/${x.id}`, { method: 'DELETE' }).catch(toast)
  await reload()
}
const rateOf = (x: TeamProject) => x.rate ?? detail.value?.client.rate ?? null
async function startTimer(project?: TeamProject) {
  if (!detail.value) return
  await timer.start({ client_id: detail.value.client.id, project_id: project?.id ?? null, note: project?.title ?? '' }).catch(toast)
}
</script>

<template>
  <div class="cr">
    <!-- ===== One client ===== -->
    <template v-if="id">
      <NuxtLink :to="{ query: {} }" class="cr-back"><AppIcon name="left" /> {{ c.title }}</NuxtLink>
      <div v-if="!detail" class="kb-loading"><span class="spinner" /></div>
      <template v-else>
        <header class="cr-head">
          <div>
            <h1>{{ detail.client.name }}</h1>
            <p v-if="detail.client.company">{{ detail.client.company }}</p>
          </div>
          <button type="button" class="btn btn-ghost btn-sm" @click="openForm(detail.client)"><AppIcon name="edit" /> {{ p.cats.edit }}</button>
        </header>
        <div class="ex-seg cr-status" role="radiogroup" :aria-label="c.status">
          <button v-for="s in STATUSES" :key="s" type="button" role="radio" :aria-checked="detail.client.status === s" :class="{ on: detail.client.status === s }" @click="setStatus(s)">{{ c.statuses[s] }}</button>
        </div>
        <div v-if="contacts.length || detail.client.tags.length" class="cr-contacts">
          <a v-for="x in contacts" :key="x.href" :href="x.href" target="_blank" rel="noopener"><AppIcon :name="x.icon" />{{ x.label }}</a>
          <span v-for="g in detail.client.tags" :key="g" class="cr-tag">#{{ g }}</span>
        </div>
        <p v-if="detail.client.note" class="cr-note">{{ detail.client.note }}</p>

        <div class="cr-stats">
          <div><small>{{ c.earnedTotal }}</small><b>{{ money(detail.earned_total) }}</b></div>
          <div><small>{{ c.earnedMonth }}</small><b>{{ money(detail.earned_month) }}</b></div>
          <div><small>{{ c.hoursTotal }}</small><b>{{ hm(detail.minutes_total) }}</b></div>
          <div><small>{{ c.hoursMonth }}</small><b>{{ hm(detail.minutes_month) }}</b></div>
        </div>
        <button v-if="!timer.running.value || timer.running.value.client_id !== detail.client.id" type="button" class="btn btn-ghost btn-sm cr-timer" @click="startTimer()">
          <AppIcon name="play" /> {{ c.startTimer }}<template v-if="detail.client.rate"> · {{ money(detail.client.rate, detail.client.currency) }}/h</template>
        </button>
        <button v-else type="button" class="btn btn-sm cr-timer running" @click="timer.stop().catch(toast)"><AppIcon name="stop" /> {{ timer.clock.value }}</button>

        <!-- Invoices -->
        <section class="sd-card">
          <div class="sd-bar">
            <h2><AppIcon name="cash" /> {{ c.invoices }}</h2>
            <button type="button" class="btn btn-ghost btn-sm" @click="invForm.open = !invForm.open"><AppIcon name="plus" /> {{ c.addInvoice }}</button>
          </div>
          <form v-if="invForm.open" class="sd-workform" @submit.prevent="addInvoice">
            <label class="tp-field"><span>{{ c.invoiceTitle }}</span><input v-model="invForm.title" required maxlength="200"></label>
            <div class="sd-grid3">
              <label class="tp-field"><span>{{ c.amount }} ({{ detail.client.currency }})</span><input v-model="invForm.amount" inputmode="decimal" required placeholder="0,00"></label>
              <label class="tp-field"><span>{{ c.dueDate }}</span><input v-model="invForm.due" type="date"></label>
              <label class="tp-field">
                <span>{{ c.project }}</span>
                <select v-model="invForm.project_id"><option :value="null">—</option><option v-for="x in detail.projects" :key="x.id" :value="x.id">{{ x.title }}</option></select>
              </label>
            </div>
            <div class="rc-form-actions">
              <button class="btn btn-primary btn-sm">{{ p.add }}</button>
              <button type="button" class="btn btn-ghost btn-sm" @click="invForm.open = false">{{ p.cancel }}</button>
            </div>
          </form>
          <p v-if="!detail.invoices.length" class="sd-muted">{{ c.noInvoices }}</p>
          <ul class="cr-list">
            <li v-for="i in detail.invoices" :key="i.id" class="cr-inv" :class="i.status">
              <span class="cr-inv-text">
                <b>{{ i.number ? `${i.number} · ` : '' }}{{ i.title }}</b>
                <small>{{ c.invStatus[i.status] }} · {{ i.status === 'paid' ? fmtDay(i.paid_on!) : `${c.due} ${fmtDay(i.due)}` }}</small>
              </span>
              <b class="cr-amount">{{ money(i.amount, i.currency) }}</b>
              <span class="cr-actions">
                <button v-if="i.status !== 'paid'" type="button" class="rc-pay" @click="payInvoice(i, true)"><AppIcon name="check" />{{ c.paid }}</button>
                <button v-else type="button" class="tp-icon-btn sm" :title="c.unpay" :aria-label="c.unpay" @click="payInvoice(i, false)"><AppIcon name="back" /></button>
                <NuxtLink :to="localePath(`/panel/invoice?id=${i.id}`)" class="tp-icon-btn sm" :title="c.pdf" :aria-label="c.pdf"><AppIcon name="doc" /></NuxtLink>
                <button type="button" class="tp-icon-btn sm danger" :class="{ confirm: confirmKey === `i${i.id}` }" :aria-label="p.delete" @click="sure(`i${i.id}`, () => deleteInvoice(i))"><AppIcon name="trash" /></button>
              </span>
            </li>
          </ul>
        </section>

        <!-- Contact history -->
        <section class="sd-card">
          <h2><AppIcon name="note" /> {{ c.history }}</h2>
          <form class="cr-logform" @submit.prevent="addLog">
            <div class="ev-remind" role="radiogroup" :aria-label="c.history">
              <button v-for="k in LOG_KINDS" :key="k" type="button" role="radio" :aria-checked="logForm.kind === k" :class="{ on: logForm.kind === k }" style="--c: var(--accent)" @click="logForm.kind = k">{{ c.kinds[k] }}</button>
            </div>
            <textarea v-model="logForm.text" class="tp-input" rows="2" maxlength="10000" :placeholder="c.logPh" />
            <div class="cr-logrow">
              <input v-model="logForm.day" type="date" class="tp-input" :aria-label="c.date">
              <select v-model="logForm.again" class="tp-input" :aria-label="c.again">
                <option v-for="n in AGAIN" :key="String(n)" :value="n">{{ n ? `${c.again} ${n} ${c.days}` : c.noAgain }}</option>
              </select>
              <button class="btn btn-primary btn-sm">{{ p.add }}</button>
            </div>
          </form>
          <ul class="cr-list">
            <li v-for="x in detail.log" :key="x.id" class="cr-log">
              <span class="cr-log-kind">{{ c.kinds[x.kind] }}<small>{{ fmtDay(x.day) }}</small></span>
              <p>{{ x.text }}</p>
              <span v-if="x.followup && !x.followup_done" class="cr-follow" :class="{ due: x.followup <= today }">
                {{ c.contactOn }} {{ fmtDay(x.followup) }}
                <button type="button" class="rc-pay" @click="followupDone(x)"><AppIcon name="check" />{{ c.done }}</button>
              </span>
              <button type="button" class="tp-icon-btn sm danger cr-log-del" :class="{ confirm: confirmKey === `l${x.id}` }" :aria-label="p.delete" @click="sure(`l${x.id}`, () => deleteLog(x))"><AppIcon name="trash" /></button>
            </li>
          </ul>
        </section>

        <!-- Projects -->
        <section class="sd-card">
          <div class="sd-bar">
            <h2><AppIcon name="briefcase" /> {{ c.projects }}</h2>
            <button type="button" class="btn btn-ghost btn-sm" @click="projForm.open = !projForm.open"><AppIcon name="plus" /> {{ c.addProject }}</button>
          </div>
          <form v-if="projForm.open" class="sd-workform" @submit.prevent="addProject">
            <div class="sd-grid3">
              <label class="tp-field"><span>{{ c.projectTitle }}</span><input v-model="projForm.title" required maxlength="160"></label>
              <label class="tp-field"><span>{{ c.rate }}</span><input v-model="projForm.rate" inputmode="decimal" :placeholder="detail.client.rate ? String(detail.client.rate) : '0'"></label>
              <label class="tp-field"><span>{{ c.budget }}</span><input v-model="projForm.budget" inputmode="decimal" placeholder="—"></label>
            </div>
            <div class="rc-form-actions">
              <button class="btn btn-primary btn-sm">{{ p.add }}</button>
              <button type="button" class="btn btn-ghost btn-sm" @click="projForm.open = false">{{ p.cancel }}</button>
            </div>
          </form>
          <p v-if="!detail.projects.length" class="sd-muted">{{ c.noProjects }}</p>
          <ul class="cr-list">
            <li v-for="x in detail.projects" :key="x.id" class="cr-proj" :class="x.status">
              <button type="button" class="cr-badge" :title="c.projectStatus" @click="cycleProject(x)">{{ c.projStatus[x.status] }}</button>
              <span class="cr-inv-text">
                <b>{{ x.title }}</b>
                <small>{{ rateOf(x) !== null ? `${money(rateOf(x)!, detail.client.currency)}/h` : c.noRate }}<template v-if="x.budget"> · {{ c.budget }} {{ money(x.budget, detail.client.currency) }}</template></small>
              </span>
              <span class="cr-actions">
                <button type="button" class="tp-icon-btn sm" :title="c.startTimer" :aria-label="c.startTimer" @click="startTimer(x)"><AppIcon name="play" /></button>
                <button type="button" class="tp-icon-btn sm danger" :class="{ confirm: confirmKey === `p${x.id}` }" :aria-label="p.delete" @click="sure(`p${x.id}`, () => deleteProject(x))"><AppIcon name="trash" /></button>
              </span>
            </li>
          </ul>
        </section>

        <!-- Tasks and meetings -->
        <section class="sd-card">
          <h2><AppIcon name="tasks" /> {{ c.tasks }}</h2>
          <p v-if="!detail.cards.length" class="sd-muted">{{ c.noTasks }}</p>
          <ul class="cr-list">
            <li v-for="x in detail.cards" :key="x.id">
              <NuxtLink :to="localePath(`/panel?board=${x.board_id}&card=${x.id}`)" class="cr-link">
                <b>{{ x.title }}</b><small>{{ x.board_title }} · {{ x.column_title }}<template v-if="x.due_date"> · {{ fmtDay(x.due_date) }}</template></small>
              </NuxtLink>
            </li>
          </ul>
          <h2 class="cr-sub"><AppIcon name="calendar" /> {{ c.meetings }}</h2>
          <p v-if="!detail.meetings.length" class="sd-muted">{{ c.noMeetings }}</p>
          <ul class="cr-list">
            <li v-for="x in detail.meetings" :key="x.id">
              <NuxtLink :to="localePath(`/panel/calendar?date=${x.date}&event=${x.id}`)" class="cr-link">
                <b>{{ x.title }}</b><small>{{ fmtDay(x.date) }} · {{ x.start }}–{{ x.end }}</small>
              </NuxtLink>
            </li>
          </ul>
        </section>
      </template>
    </template>

    <!-- ===== List ===== -->
    <template v-else>
      <header class="tp-head">
        <div>
          <h1>{{ c.title }}</h1>
          <p>{{ c.subtitle }}</p>
        </div>
        <button type="button" class="btn btn-primary btn-sm" @click="openForm()"><AppIcon name="plus" /> {{ c.newClient }}</button>
      </header>
      <input v-model="search" class="tp-input cr-search" type="search" :placeholder="c.search" :aria-label="c.search">
      <div class="cr-filters">
        <button type="button" :class="{ on: !status }" @click="status = ''">{{ c.all }}</button>
        <button v-for="s in STATUSES" :key="s" type="button" :class="{ on: status === s }" @click="status = status === s ? '' : s">{{ c.statuses[s] }}</button>
        <button v-for="g in allTags" :key="g" type="button" class="tag" :class="{ on: tag === g }" @click="tag = tag === g ? '' : g">#{{ g }}</button>
      </div>
      <div v-if="loading && !clients.length" class="kb-loading"><span class="spinner" /></div>
      <p v-else-if="!shown.length" class="al-empty">{{ clients.length ? c.nothingFound : c.empty }}</p>
      <ul class="cr-clients">
        <li v-for="x in shown" :key="x.id">
          <NuxtLink :to="{ query: { id: x.id } }" class="cr-client" :class="x.status">
            <span class="tp-avatar" :data-c="x.id % 3">{{ x.name.charAt(0).toUpperCase() }}</span>
            <span class="cr-inv-text">
              <b>{{ x.name }}</b>
              <small>{{ [x.company, c.statuses[x.status], ...x.tags.map((g) => `#${g}`)].filter(Boolean).join(' · ') }}</small>
            </span>
            <span v-if="x.late_invoices" class="cr-pill late">{{ x.late_invoices }} {{ c.lateShort }}</span>
            <span v-else-if="x.open_invoices" class="cr-pill">{{ x.open_invoices }} {{ c.openShort }}</span>
          </NuxtLink>
        </li>
      </ul>
    </template>

    <!-- Client form -->
    <div v-if="form" class="tm-overlay" @click.self="form = null">
      <form class="tm" role="dialog" aria-modal="true" :aria-label="c.client" @submit.prevent="saveForm">
        <header class="tm-head">
          <h2>{{ form.id ? form.name : c.newClient }}</h2>
          <button type="button" class="tp-icon-btn sm" :aria-label="p.close" @click="form = null"><AppIcon name="close" /></button>
        </header>
        <div class="tm-row">
          <label class="tp-field"><span>{{ c.name }}</span><input v-model="form.name" required maxlength="120"></label>
          <label class="tp-field"><span>{{ c.company }}</span><input v-model="form.company" maxlength="120"></label>
        </div>
        <div class="tm-row">
          <label class="tp-field"><span>E-mail</span><input v-model="form.email" type="email" maxlength="200" autocomplete="off"></label>
          <label class="tp-field"><span>{{ c.phone }}</span><input v-model="form.phone" type="tel" maxlength="60"></label>
        </div>
        <div class="tm-row">
          <label class="tp-field"><span>Telegram</span><input v-model="form.telegram" maxlength="60" placeholder="@username"></label>
          <label class="tp-field"><span>{{ c.website }}</span><input v-model="form.website" maxlength="200" placeholder="example.com"></label>
        </div>
        <div class="sd-grid3">
          <label class="tp-field"><span>{{ c.rate }}</span><input v-model="form.rate" inputmode="decimal" placeholder="0"></label>
          <label class="tp-field"><span>{{ c.currency }}</span><select v-model="form.currency"><option v-for="cur in ['EUR', 'CZK', 'UAH', 'USD']" :key="cur">{{ cur }}</option></select></label>
          <label class="tp-field"><span>{{ c.lang }}</span><select v-model="form.lang"><option v-for="l in ['sk', 'cs', 'uk', 'en', 'ru', 'de']" :key="l">{{ l }}</option></select></label>
        </div>
        <label class="tp-field"><span>{{ c.tags }}</span><input v-model="form.tags" maxlength="300" :placeholder="c.tagsPh"></label>
        <label class="tp-field">
          <span>{{ c.status }}</span>
          <select v-model="form.status"><option v-for="s in STATUSES" :key="s" :value="s">{{ c.statuses[s] }}</option></select>
        </label>
        <label class="tp-field"><span>{{ p.calendar.note }}</span><textarea v-model="form.note" rows="3" maxlength="10000" /></label>
        <footer class="tm-foot">
          <button v-if="form.id" type="button" class="btn btn-sm tm-delete" :class="{ sure: confirmKey === 'client' }" @click="sure('client', removeClient)"><AppIcon name="trash" /> {{ confirmKey === 'client' ? p.sure : p.delete }}</button>
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
/* ===== Clients (shares .sd-* card styles of the Study page) ===== */
.cr { display: grid; gap: 12px; max-width: 980px; }
.cr .btn .ico { width: 16px; height: 16px; }
.cr-back { justify-self: start; display: inline-flex; align-items: center; gap: 6px; min-height: 40px; color: var(--muted); font-weight: 800; font-size: .9rem; }
.cr-back .ico { width: 16px; height: 16px; }
.cr-head { display: flex; flex-wrap: wrap; align-items: flex-end; justify-content: space-between; gap: 10px; }
.cr-head h1 { font-family: var(--font-display); font-weight: 600; font-size: clamp(1.5rem, 5vw, 2.1rem); letter-spacing: -.03em; line-height: 1.15; }
.cr-head p { color: var(--muted); font-weight: 700; }
.cr-status { justify-self: start; flex-wrap: wrap; }
.cr-contacts { display: flex; flex-wrap: wrap; gap: 6px; }
.cr-contacts a, .cr-tag {
  display: inline-flex; align-items: center; gap: 6px; min-height: 40px; padding: 0 12px; border-radius: 999px;
  background: var(--surface); border: 1px solid var(--line-2); font-weight: 700; font-size: .85rem; max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.cr-contacts .ico { width: 16px; height: 16px; color: var(--accent); flex: none; }
.cr-tag { background: var(--bg-2); border-color: transparent; color: var(--ink-2); }
.cr-note { padding: 12px 14px; border-radius: 16px; background: var(--surface); border: 1px solid var(--line); color: var(--ink-2); font-size: .9rem; white-space: pre-line; }
.cr-stats { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; }
.cr-stats div { display: grid; padding: 12px; border-radius: 16px; background: var(--surface); border: 1px solid var(--line); }
.cr-stats small { color: var(--muted); font-weight: 700; font-size: .76rem; }
.cr-stats b { font-family: var(--font-display); font-weight: 600; font-size: 1.15rem; font-variant-numeric: tabular-nums; }
.cr-timer { justify-self: start; min-height: 44px; }
.cr-timer.running { background: rgba(229, 72, 77, .12); color: #E5484D; font-variant-numeric: tabular-nums; }
.cr-list { display: grid; gap: 6px; margin-top: 8px; }
.cr-inv, .cr-proj, .cr-client, .cr-link {
  display: flex; align-items: center; gap: 10px; padding: 8px 8px 8px 12px; border-radius: 14px; background: var(--bg); border: 1px solid var(--line); min-height: 52px;
}
.cr-inv.overdue { border-color: rgba(229, 72, 77, .45); }
.cr-inv.paid { opacity: .7; }
.cr-inv-text { flex: 1; min-width: 0; display: grid; line-height: 1.3; }
.cr-inv-text b { font-size: .92rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cr-inv-text small { color: var(--muted); font-weight: 600; font-size: .76rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cr-inv.overdue small { color: #E5484D; }
.cr-amount { font-variant-numeric: tabular-nums; white-space: nowrap; font-size: .92rem; }
.cr-actions { display: flex; align-items: center; gap: 4px; flex: none; }
.cr-actions .rc-pay { min-height: 40px; }
.cr-link { display: grid; gap: 2px; line-height: 1.3; }
.cr-link b { font-size: .92rem; }
.cr-link small { color: var(--muted); font-weight: 600; font-size: .76rem; }
.cr-sub { margin-top: 14px; }
.cr-logform { display: grid; gap: 8px; margin-top: 10px; }
.cr-logform textarea { width: 100%; resize: vertical; font: inherit; }
.cr-logrow { display: grid; grid-template-columns: 1fr 1fr auto; gap: 6px; }
.cr-log { position: relative; display: grid; gap: 4px; padding: 10px 44px 10px 12px; border-radius: 14px; background: var(--bg); border: 1px solid var(--line); }
.cr-log-kind { display: flex; gap: 8px; align-items: baseline; font-weight: 800; font-size: .8rem; color: var(--accent); }
.cr-log-kind small { color: var(--muted); font-weight: 600; }
.cr-log p { font-size: .9rem; white-space: pre-line; overflow-wrap: anywhere; }
.cr-log-del { position: absolute; top: 6px; right: 6px; }
.cr-follow { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; color: var(--muted); font-weight: 700; font-size: .8rem; }
.cr-follow.due { color: #C27803; }
.cr-badge { flex: none; min-height: 32px; padding: 0 10px; border-radius: 999px; border: 0; cursor: pointer; background: rgba(25, 195, 166, .14); color: #0E9F85; font-weight: 800; font-size: .74rem; }
.cr-proj.paused .cr-badge { background: rgba(245, 158, 11, .14); color: #C27803; }
.cr-proj.done .cr-badge { background: var(--bg-2); color: var(--muted); }
.cr-search { width: 100%; }
.cr-filters { display: flex; flex-wrap: wrap; gap: 6px; }
.cr-filters button {
  min-height: 36px; padding: 0 12px; border-radius: 999px; cursor: pointer; border: 1px solid var(--line-2); background: none;
  color: var(--ink-2); font-weight: 700; font-size: .82rem;
}
.cr-filters button.on { background: var(--ink); border-color: var(--ink); color: #fff; }
.tp.dark .cr-filters button.on { background: var(--solid); border-color: var(--solid); }
.cr-clients { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 8px; }
.cr-client { background: var(--surface); }
.cr-client.former { opacity: .6; }
.cr-pill { flex: none; padding: 2px 10px; border-radius: 999px; background: rgba(91, 75, 255, .12); color: var(--accent); font-weight: 800; font-size: .74rem; }
.cr-pill.late { background: #E5484D; color: #fff; }
@media (max-width: 640px) {
  .cr-stats { grid-template-columns: 1fr 1fr; }
  .cr-clients { grid-template-columns: 1fr; }
  .cr-logrow { grid-template-columns: 1fr 1fr; }
  .cr-logrow .btn { grid-column: 1 / -1; min-height: 44px; }
  .cr-inv { flex-wrap: wrap; }
  .cr-inv .cr-actions { margin-left: auto; }
  .cr-filters { flex-wrap: nowrap; overflow-x: auto; margin-inline: -16px; padding-inline: 16px; scrollbar-width: none; }
  .cr-filters button { flex: none; }
}
</style>
