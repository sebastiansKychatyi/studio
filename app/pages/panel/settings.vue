<script setup lang="ts">
// Account settings: appearance (stored on the server), who sees my calendar, who has access to my boards.
import { CURRENCIES, type Currency, type TeamBoardItem, type TeamUser } from '~/composables/useTeam'

const { t } = useSite()
const localePath = useLocalePath()
const { api, user, users } = useTeam()
const { pref } = usePrefs()

const p = computed(() => t.value.panel)
const st = computed(() => t.value.panel.settings)

const theme = pref<'light' | 'dark' | 'system'>('theme', 'system')
const layout = pref<'grid' | 'row'>('kanbanLayout', 'grid')
const calendarView = pref<'week' | 'month'>('calendarView', 'week')
const currency = pref<Currency>('currency', 'EUR')
const openBoards = pref<number[]>('kanbanBoards', [])
const SYMBOLS: Record<Currency, string> = { EUR: '€', UAH: '₴', USD: '$' }

const others = computed(() => users.value.filter((u) => u.id !== user.value?.id))
const initial = (u?: TeamUser) => (u?.name || u?.username || '?').charAt(0).toUpperCase()
const nameOf = (id: number | null) => users.value.find((u) => u.id === id)

// Calendar access
const sharedWith = ref<number[]>([])
const sharedToMe = ref<TeamUser[]>([])
const calShared = ref(true) // sharing switched on on the server
const boards = ref<TeamBoardItem[]>([])
const loading = ref(true)
const saved = ref(false)
const failed = ref(false)

function flash(ok: boolean) {
  const r = ok ? saved : failed
  r.value = true
  setTimeout(() => (r.value = false), 2000)
}

onMounted(async () => {
  try {
    const [access, list] = await Promise.all([
      api<{ shared_with: number[]; shared_to_me: TeamUser[]; enabled?: boolean }>('/calendar/access'),
      api<TeamBoardItem[]>('/boards'),
    ])
    sharedWith.value = access.shared_with
    sharedToMe.value = access.shared_to_me
    calShared.value = access.enabled !== false
    boards.value = list
  } catch (err) {
    if (httpStatus(err) === 401) navigateTo(localePath('/login'))
    else flash(false)
  } finally {
    loading.value = false
  }
})

async function toggleCalendar(uid: number) {
  const ids = sharedWith.value.includes(uid) ? sharedWith.value.filter((x) => x !== uid) : [...sharedWith.value, uid]
  sharedWith.value = ids
  try {
    await api('/calendar/access', { method: 'PUT', body: { user_ids: ids } })
    flash(true)
  } catch {
    flash(false)
  }
}

// Installed app
const { canInstall, standalone, ios, updateReady, install, update } = usePwa()
const version = useRuntimeConfig().public.appVersion

// Notifications: this device's subscription + account-wide types and quiet hours (read by the server)
const { permission, subscribed, serverReady, check, enable, disable, test } = usePush()
const KINDS = ['alarms', 'events', 'due', 'mentions', 'assign', 'bills'] as const
interface NotifyPrefs { quiet?: boolean; quietFrom?: string; quietTo?: string; summaryAt?: string; eveningAt?: string; [kind: string]: boolean | string | undefined }
// Daily summaries: morning on by default, evening ("what is tomorrow") off
const SUMMARIES = [
  { key: 'summary', at: 'summaryAt', def: '07:30', on: (n: NotifyPrefs) => n.summary !== false },
  { key: 'evening', at: 'eveningAt', def: '20:00', on: (n: NotifyPrefs) => n.evening === true },
] as const
const notify = pref<NotifyPrefs>('notify', {})
const setNotify = (patch: NotifyPrefs) => (notify.value = { ...notify.value, ...patch })
const pushBusy = ref(false)
const pushText = ref('')
onMounted(check)
async function togglePush() {
  pushBusy.value = true
  try {
    if (subscribed.value) await disable()
    else await enable()
  } catch {
    flash(false)
  } finally {
    pushBusy.value = false
  }
}
async function sendTest() {
  try {
    const { sent } = await test()
    pushText.value = sent ? `${st.value.notify.testSent}: ${sent}` : st.value.notify.testNone
  } catch {
    pushText.value = p.value.errorServer
  }
  setTimeout(() => (pushText.value = ''), 4000)
}

const myBoards = computed(() => boards.value.filter((b) => b.created_by === user.value?.id))
const sharedBoards = computed(() => boards.value.filter((b) => b.created_by !== user.value?.id))
function openBoard(id: number) {
  openBoards.value = [id]
  navigateTo(localePath('/panel'))
}
</script>

<template>
  <div class="st">
    <header class="tp-head">
      <div>
        <h1>{{ st.title }}</h1>
        <p>{{ st.subtitle }}</p>
      </div>
    </header>

    <div class="st-grid">
      <!-- Appearance -->
      <section class="st-card">
        <h2><AppIcon name="spark" /> {{ st.look }}</h2>
        <div class="st-row">
          <span>{{ st.theme }}</span>
          <div class="ex-seg" role="radiogroup" :aria-label="st.theme">
            <button v-for="v in (['light', 'dark', 'system'] as const)" :key="v" type="button" role="radio" :aria-checked="theme === v" :class="{ on: theme === v }" @click="theme = v">
              <AppIcon :name="v === 'light' ? 'sun' : v === 'dark' ? 'moon' : 'laptop'" />{{ st.themes[v] }}
            </button>
          </div>
        </div>
        <div class="st-row">
          <span>{{ st.kanban }}</span>
          <div class="ex-seg" role="radiogroup" :aria-label="st.kanban">
            <button type="button" role="radio" :aria-checked="layout === 'grid'" :class="{ on: layout === 'grid' }" @click="layout = 'grid'"><AppIcon name="grid" />{{ p.kanban.grid }}</button>
            <button type="button" role="radio" :aria-checked="layout === 'row'" :class="{ on: layout === 'row' }" @click="layout = 'row'"><AppIcon name="tasks" />{{ p.kanban.row }}</button>
          </div>
        </div>
        <div class="st-row">
          <span>{{ st.calendar }}</span>
          <div class="ex-seg" role="radiogroup" :aria-label="st.calendar">
            <button type="button" role="radio" :aria-checked="calendarView === 'week'" :class="{ on: calendarView === 'week' }" @click="calendarView = 'week'">{{ p.calendar.week }}</button>
            <button type="button" role="radio" :aria-checked="calendarView === 'month'" :class="{ on: calendarView === 'month' }" @click="calendarView = 'month'">{{ p.calendar.month }}</button>
          </div>
        </div>
        <div class="st-row">
          <span>{{ st.currency }}</span>
          <div class="ex-seg" role="radiogroup" :aria-label="st.currency">
            <button v-for="c in CURRENCIES" :key="c" type="button" role="radio" :aria-checked="currency === c" :class="{ on: currency === c }" @click="currency = c">{{ SYMBOLS[c] }} {{ c }}</button>
          </div>
        </div>
        <p class="st-note">{{ st.synced }}</p>
      </section>

      <!-- Installed app -->
      <section class="st-card">
        <h2><AppIcon name="phone" /> {{ p.app.title }}</h2>
        <div class="st-row">
          <span>{{ p.app.status }}</span>
          <b v-if="standalone" class="st-ok">✓ {{ p.app.installed }}</b>
          <button v-else-if="canInstall" type="button" class="btn btn-primary btn-sm" @click="install"><AppIcon name="download" /> {{ p.app.install }}</button>
          <span v-else class="st-muted">{{ p.app.notInstalled }}</span>
        </div>
        <p v-if="ios && !standalone" class="st-note">{{ p.app.iosHint }}</p>
        <p v-else-if="!standalone && !canInstall" class="st-note">{{ p.app.androidHint }}</p>
        <div class="st-row">
          <span>{{ p.app.version }}</span>
          <span class="st-version">{{ version }}</span>
        </div>
        <button v-if="updateReady" type="button" class="btn btn-ghost btn-sm st-update" @click="update"><AppIcon name="spark" /> {{ p.app.update }}</button>
      </section>

      <!-- Notifications -->
      <section class="st-card st-wide">
        <h2><AppIcon name="bell" /> {{ st.notify.title }}</h2>
        <div class="st-row">
          <span>{{ st.notify.device }}</span>
          <span v-if="permission === 'unsupported'" class="st-muted">{{ st.notify.unsupported }}</span>
          <span v-else-if="permission === 'denied'" class="st-muted">{{ st.notify.blocked }}</span>
          <button v-else type="button" class="btn btn-sm" :class="subscribed ? 'btn-ghost' : 'btn-primary'" :disabled="pushBusy" @click="togglePush">
            <AppIcon name="bell" /> {{ subscribed ? st.notify.disable : st.notify.enable }}
          </button>
        </div>
        <p v-if="!serverReady" class="st-note st-warn">{{ st.notify.serverOff }}</p>
        <div class="st-kinds">
          <label v-for="kind in KINDS" :key="kind" class="st-kind">
            <input type="checkbox" class="kb-check" :checked="notify[kind] !== false" @change="setNotify({ [kind]: ($event.target as HTMLInputElement).checked })">
            <span>{{ st.notify.kinds[kind] }}</span>
          </label>
        </div>
        <div v-for="s in SUMMARIES" :key="s.key" class="st-row">
          <label class="st-kind">
            <input type="checkbox" class="kb-check" :checked="s.on(notify)" @change="setNotify({ [s.key]: ($event.target as HTMLInputElement).checked })">
            <span>{{ st.notify[s.key] }}</span>
          </label>
          <input type="time" class="tp-input st-at" :value="notify[s.at] || s.def" :disabled="!s.on(notify)" :aria-label="st.notify[s.key]" @change="setNotify({ [s.at]: ($event.target as HTMLInputElement).value })">
        </div>
        <div class="st-row">
          <label class="st-kind">
            <input type="checkbox" class="kb-check" :checked="!!notify.quiet" @change="setNotify({ quiet: ($event.target as HTMLInputElement).checked })">
            <span>{{ st.notify.quiet }}</span>
          </label>
          <span class="st-quiet">
            <input type="time" class="tp-input" :value="notify.quietFrom || '22:00'" :disabled="!notify.quiet" :aria-label="st.notify.quiet" @change="setNotify({ quietFrom: ($event.target as HTMLInputElement).value })">
            –
            <input type="time" class="tp-input" :value="notify.quietTo || '07:00'" :disabled="!notify.quiet" :aria-label="st.notify.quiet" @change="setNotify({ quietTo: ($event.target as HTMLInputElement).value })">
          </span>
        </div>
        <div class="st-row">
          <button type="button" class="btn btn-ghost btn-sm" :disabled="!subscribed" @click="sendTest"><AppIcon name="send" /> {{ st.notify.test }}</button>
          <span v-if="pushText" class="st-muted">{{ pushText }}</span>
        </div>
        <!-- Honest limits of web notifications -->
        <details class="st-limits">
          <summary>{{ st.notify.limitsTitle }}</summary>
          <p v-for="(line, i) in st.notify.limits" :key="i">{{ line }}</p>
        </details>
      </section>

      <!-- Calendar access -->
      <section class="st-card">
        <h2><AppIcon name="calendar" /> {{ st.calAccess }}</h2>
        <p class="st-note">{{ calShared ? st.calAccessHint : st.calPrivate }}</p>
        <div v-if="loading" class="kb-loading"><span class="spinner" /></div>
        <template v-else-if="calShared">
          <label v-for="u in others" :key="u.id" class="kb-access-row">
            <span class="tp-avatar sm" :data-c="u.id % 3">{{ initial(u) }}</span>
            <span class="kb-access-name"><b>{{ u.name || u.username }}</b><small>@{{ u.username }}</small></span>
            <input type="checkbox" class="kb-check" :checked="sharedWith.includes(u.id)" @change="toggleCalendar(u.id)">
          </label>
          <p v-if="!others.length" class="st-note">{{ st.nobody }}</p>
          <h3>{{ st.sharedToMe }}</h3>
          <p v-if="!sharedToMe.length" class="st-note">{{ st.noneToMe }}</p>
          <ul v-else class="st-people">
            <li v-for="u in sharedToMe" :key="u.id"><span class="tp-avatar sm" :data-c="u.id % 3">{{ initial(u) }}</span>{{ u.name || u.username }}</li>
          </ul>
        </template>
      </section>

      <!-- Board access overview -->
      <section class="st-card st-wide">
        <h2><AppIcon name="users" /> {{ st.boards }}</h2>
        <p class="st-note">{{ st.boardsHint }}</p>
        <div v-if="loading" class="kb-loading"><span class="spinner" /></div>
        <template v-else>
          <ul class="st-boards">
            <li v-for="b in myBoards" :key="b.id">
              <button type="button" class="st-board" @click="openBoard(b.id)">
                <b><AppIcon :name="b.is_private ? 'lock' : 'users'" />{{ b.title }}</b>
                <span v-if="b.is_private" class="st-muted">{{ p.kanban.private }}</span>
                <span v-else class="kb-faces">
                  <span v-for="id in b.member_ids" :key="id" class="tp-avatar sm" :data-c="id % 3" :title="nameOf(id)?.name">{{ initial(nameOf(id)) }}</span>
                </span>
              </button>
            </li>
          </ul>
          <template v-if="sharedBoards.length">
            <h3>{{ st.boardsToMe }}</h3>
            <ul class="st-boards">
              <li v-for="b in sharedBoards" :key="b.id">
                <button type="button" class="st-board" @click="openBoard(b.id)">
                  <b><AppIcon name="users" />{{ b.title }}</b>
                  <span class="st-muted">{{ p.kanban.owner }}: {{ nameOf(b.created_by)?.name || nameOf(b.created_by)?.username }}</span>
                </button>
              </li>
            </ul>
          </template>
        </template>
      </section>
    </div>

    <Transition name="toast"><div v-if="saved || failed" class="tp-toast" role="status">{{ failed ? p.errorServer : st.saved }}</div></Transition>
  </div>
</template>

<style>
/* ===== Settings ===== */
.st-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }
.st-card { padding: 22px; border-radius: var(--radius); background: var(--surface); border: 1px solid var(--line); box-shadow: var(--shadow); animation: tpUp .6s var(--ease) both; }
.st-card:nth-child(2) { animation-delay: .06s; }
.st-card:nth-child(3) { animation-delay: .12s; }
.st-wide { grid-column: 1 / -1; }
.st-card h2 { display: flex; align-items: center; gap: 8px; font-size: 1rem; font-weight: 800; margin-bottom: 6px; }
.st-card h2 .ico { width: 18px; height: 18px; color: var(--accent); }
.st-card h3 { margin: 16px 0 6px; font-size: .88rem; font-weight: 800; }
.st-row { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px; padding: 12px 0; border-bottom: 1px solid var(--line); }
.st-row > span { font-weight: 700; font-size: .9rem; color: var(--ink-2); }
.st-row .ex-seg button { display: inline-flex; align-items: center; gap: 6px; }
.st-row .ex-seg .ico { width: 15px; height: 15px; }
.st-note { margin: 6px 0 10px; color: var(--muted); font-size: .82rem; font-weight: 600; }
.st-muted { color: var(--muted); font-size: .8rem; font-weight: 700; }
.st-ok { color: #0E9F85; font-size: .9rem; }
.st-version { font-family: ui-monospace, monospace; font-size: .82rem; color: var(--muted); }
.st-update { margin-top: 12px; }
.st-warn { color: #C2410C; }
.st-kinds { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 4px 12px; padding: 12px 0; border-bottom: 1px solid var(--line); }
.st-kind { display: flex; align-items: center; gap: 10px; min-height: 44px; font-weight: 700; font-size: .9rem; color: var(--ink-2); cursor: pointer; }
.st-quiet { display: inline-flex; align-items: center; gap: 6px; }
.st-quiet .tp-input, .st-at { width: 120px; }
.st-at:disabled { opacity: .5; }
.st-quiet .tp-input:disabled { opacity: .5; }
.st-limits { margin-top: 12px; font-size: .84rem; color: var(--ink-2); }
.st-limits summary { min-height: 44px; display: flex; align-items: center; cursor: pointer; font-weight: 800; color: var(--accent); }
.st-limits p { margin-top: 8px; line-height: 1.5; }
.tp.dark .st-quiet .tp-input { background: var(--field); color: var(--ink); }
.st-card .btn .ico { width: 16px; height: 16px; }
.st-people { display: flex; flex-wrap: wrap; gap: 8px; }
.st-people li { display: inline-flex; align-items: center; gap: 7px; padding: 5px 12px 5px 5px; border-radius: 999px; background: var(--bg-2); font-weight: 700; font-size: .85rem; }
.st-boards { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 8px; }
.st-board {
  width: 100%; display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 12px 14px; border-radius: 16px; cursor: pointer;
  border: 1px solid var(--line); background: var(--bg); color: var(--ink); text-align: left; transition: border-color .2s, transform .3s var(--ease);
}
.st-board:hover { border-color: var(--accent); transform: translateY(-2px); }
.st-board b { display: flex; align-items: center; gap: 7px; font-size: .9rem; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.st-board b .ico { flex: none; width: 15px; height: 15px; color: var(--muted); }
@media (max-width: 860px) { .st-grid { grid-template-columns: 1fr; } }
@media (max-width: 640px) {
  .st-card { padding: 18px 16px; }
  .st-row { flex-direction: column; align-items: stretch; }
  .st-row .ex-seg { justify-content: space-between; }
  .st-row .ex-seg button { flex: 1; justify-content: center; white-space: nowrap; padding: 0 6px; }
}
</style>
