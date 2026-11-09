<script setup lang="ts">
// Assistant chat: the same history as the Telegram chat. Short lines are saved by the quick parser
// at once (no AI); the rest goes to Claude, which can only use the panel tools on the server.
// Created entries get "Undo"; changes to existing entries wait for "Yes".

interface Action { label: string; kind: 'undo' | 'confirm'; method: string; path: string; done?: boolean | 'declined' }
interface Message { id: number; at: string; role: 'user' | 'assistant'; via: string; engine: string; text: string; actions: Action[] }
interface Status { telegram: boolean; telegram_linked: boolean; bot: string | null; parser: boolean; claude: boolean; model: string }

const { t } = useSite()
const { locale } = useI18n()
const localePath = useLocalePath()
const { api } = useTeam()
const p = computed(() => t.value.panel)
const a = computed(() => t.value.panel.assistant)

const messages = ref<Message[]>([])
const status = ref<Status | null>(null)
const text = ref('')
const busy = ref(false)
const loading = ref(true)
const note = ref('')
const list = ref<HTMLElement | null>(null)
const input = ref<HTMLTextAreaElement | null>(null)
const helpOpen = ref(false)  // phones only; wide screens always show the help
const flash = (s: string) => {
  note.value = s
  setTimeout(() => (note.value = ''), 3500)
}

async function scrollDown() {
  await nextTick()
  // The list scrolls on wide screens, the page on phones
  list.value?.scrollTo({ top: list.value.scrollHeight, behavior: 'smooth' })
  list.value?.lastElementChild?.scrollIntoView({ block: 'end', behavior: 'smooth' })
}
async function load() {
  try {
    messages.value = await api<Message[]>('/assistant/messages', { query: { limit: 100 } })
  } catch (e) {
    flash(isOffline(e) ? p.value.offlineOnly : p.value.errorServer)
  } finally {
    loading.value = false
    scrollDown()
  }
}
onMounted(() => {
  load()
  api<Status>('/assistant').then((s) => (status.value = s)).catch(() => {})
})

async function send(line = text.value) {
  const q = line.trim()
  if (!q || busy.value) return
  busy.value = true
  text.value = ''
  // Shown at once; the stored copy comes with the reload
  messages.value.push({ id: -Date.now(), at: new Date().toISOString(), role: 'user', via: 'panel', engine: '', text: q, actions: [] })
  scrollDown()
  try {
    await api('/assistant/messages', { method: 'POST', body: { text: q } })
    await load()
  } catch (e) {
    messages.value.pop()
    text.value = q
    flash(isOffline(e) ? p.value.offlineOnly : p.value.errorServer)
  } finally {
    busy.value = false
  }
}
// Help examples go into the input to be edited, not sent
function fill(line: string) {
  text.value = line
  helpOpen.value = false
  nextTick(() => input.value?.focus())
}
function onKey(e: KeyboardEvent) {
  // Enter sends, Shift+Enter is a new line
  if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) {
    e.preventDefault()
    send()
  }
}

async function act(m: Message, i: number, accept: boolean) {
  try {
    const r = await api<{ message: Message | null; result: string }>(`/assistant/messages/${m.id}/actions/${i}`, { method: 'POST', body: { accept } })
    if (r.message) messages.value = messages.value.map((x) => (x.id === m.id ? r.message! : x))
    flash(r.result)
  } catch (e) {
    flash(isOffline(e) ? p.value.offlineOnly : p.value.errorServer)
  }
}

const sure = ref(false)
async function clear() {
  if (!sure.value) {
    sure.value = true
    setTimeout(() => (sure.value = false), 3000)
    return
  }
  sure.value = false
  await api('/assistant/messages', { method: 'DELETE' }).catch(() => flash(p.value.errorServer))
  messages.value = []
}

const time = (iso: string) => new Date(iso).toLocaleTimeString(locale.value, { hour: '2-digit', minute: '2-digit' })
const doneLabel = (x: Action) => (x.done === 'declined' ? a.value.declined : x.kind === 'undo' ? a.value.undone : a.value.applied)
</script>

<template>
  <div class="as">
    <header class="tp-head">
      <div>
        <h1>{{ a.title }}</h1>
        <p>{{ a.subtitle }}</p>
      </div>
      <div class="as-tools">
        <button type="button" class="btn btn-ghost btn-sm as-help-btn" :aria-expanded="helpOpen" @click="helpOpen = !helpOpen">
          <AppIcon name="note" /> {{ a.help.title }}
        </button>
        <button v-if="messages.length" type="button" class="btn btn-ghost btn-sm" :class="{ 'tm-delete sure': sure }" @click="clear">
          <AppIcon name="trash" /> {{ sure ? p.sure : a.clear }}
        </button>
      </div>
    </header>

    <!-- Short guide: right column on wide screens, toggled on phones -->
    <aside class="as-help sd-card" :class="{ open: helpOpen }">
      <h2>{{ a.help.title }}</h2>
      <ol class="as-steps">
        <li v-for="s in a.help.steps" :key="s">{{ s }}</li>
      </ol>
      <p v-if="status && !status.claude" class="as-warn">{{ a.help.claudeOff }}</p>

      <h3><AppIcon name="spark" /> {{ a.help.quickTitle }}</h3>
      <ul class="as-ex">
        <li v-for="[kind, ex] in a.help.quick" :key="ex">
          <span>{{ p.quick.kinds[kind as keyof typeof p.quick.kinds] }}</span>
          <button type="button" @click="fill(ex)">{{ ex }}</button>
        </li>
      </ul>

      <h3><AppIcon name="bot" /> {{ a.help.claudeTitle }}</h3>
      <ul class="as-ex">
        <li v-for="ex in a.help.claude" :key="ex"><button type="button" @click="fill(ex)">{{ ex }}</button></li>
      </ul>
      <small class="as-fill">{{ a.help.fill }}</small>

      <h3>{{ a.help.tipsTitle }}</h3>
      <ul class="as-tips">
        <li v-for="tip in a.help.tips" :key="tip">{{ tip }}</li>
      </ul>
    </aside>

    <!-- What works on this server -->
    <div v-if="status" class="as-status">
      <span class="as-chip" :class="{ on: status.parser }"><AppIcon name="spark" /> {{ a.parser }}</span>
      <span class="as-chip" :class="{ on: status.claude }"><AppIcon name="bot" /> Claude {{ status.claude ? `(${status.model})` : `— ${a.claudeOff}` }}</span>
      <NuxtLink v-if="status.telegram" :to="localePath('/panel/settings')" class="as-chip" :class="{ on: status.telegram_linked }">
        <AppIcon name="telegram" /> {{ status.telegram_linked ? a.tgLinked : a.tgConnect }}
      </NuxtLink>
    </div>

    <section ref="list" class="as-list sd-card" aria-live="polite">
      <div v-if="loading" class="kb-loading"><span class="spinner" /></div>
      <div v-else-if="!messages.length" class="as-empty">
        <p>{{ a.empty }}</p>
        <div class="as-examples">
          <button v-for="ex in a.examples" :key="ex" type="button" class="as-example" @click="send(ex)">{{ ex }}</button>
        </div>
      </div>
      <div v-for="m in messages" :key="m.id" class="as-msg" :class="m.role">
        <div class="as-bubble">
          <p>{{ m.text }}</p>
          <div v-if="m.actions.length" class="as-actions">
            <template v-for="(x, i) in m.actions" :key="i">
              <span v-if="x.done" class="as-done"><AppIcon name="check" /> {{ doneLabel(x) }}<template v-if="x.label !== 'undo'">: {{ x.label }}</template></span>
              <button v-else-if="x.kind === 'undo'" type="button" class="btn btn-ghost btn-sm" @click="act(m, i, true)">↩ {{ a.undo }}<template v-if="x.label !== 'undo'">: {{ x.label }}</template></button>
              <span v-else class="as-confirm">
                <span>{{ x.label }}</span>
                <button type="button" class="btn btn-primary btn-sm" @click="act(m, i, true)">{{ a.yes }}</button>
                <button type="button" class="btn btn-ghost btn-sm" @click="act(m, i, false)">{{ a.no }}</button>
              </span>
            </template>
          </div>
        </div>
        <small class="as-meta">
          {{ time(m.at) }}
          <template v-if="m.via === 'telegram'"> · Telegram</template>
          <template v-if="m.engine === 'parser'"> · {{ a.fast }}</template>
          <template v-else-if="m.engine === 'claude'"> · Claude</template>
        </small>
      </div>
      <div v-if="busy" class="as-msg assistant"><div class="as-bubble as-typing"><span /><span /><span /></div></div>
    </section>

    <form class="as-form" @submit.prevent="send()">
      <textarea ref="input" v-model="text" class="tp-input" rows="2" maxlength="2000" :placeholder="a.placeholder" :aria-label="a.placeholder" @keydown="onKey" />
      <button class="btn btn-primary" :disabled="busy || !text.trim()" :aria-label="a.send"><AppIcon name="send" /></button>
    </form>

    <Transition name="toast"><div v-if="note" class="tp-toast" role="status">{{ note }}</div></Transition>
  </div>
</template>

<style>
/* ===== Assistant ===== */
.as { display: grid; grid-template-columns: minmax(0, 1fr); gap: 12px; max-width: 860px; }
.as-tools { display: flex; flex-wrap: wrap; gap: 6px; }
/* Help: hidden on phones until toggled, a sticky right column on wide screens */
.as-help { display: none; gap: 8px; align-content: start; font-size: .86rem; }
.as-help.open { display: grid; }
.as-help h2 { font-size: 1.05rem; }
.as-help h3 { display: flex; align-items: center; gap: 6px; margin-top: 6px; font-size: .84rem; text-transform: uppercase; letter-spacing: .04em; color: var(--muted); }
.as-help h3 .ico { width: 14px; height: 14px; }
.as-steps { display: grid; gap: 6px; padding-left: 18px; line-height: 1.45; }
.as-warn { padding: 8px 10px; border-radius: 10px; background: rgba(255, 170, 0, .12); color: var(--ink); font-size: .82rem; }
.as-ex { list-style: none; display: grid; gap: 4px; padding: 0; }
.as-ex li { display: flex; align-items: center; gap: 8px; }
.as-ex li span { flex: none; width: 92px; color: var(--muted); font-size: .78rem; font-weight: 700; }
.as-ex button { min-width: 0; padding: 5px 10px; border-radius: 8px; border: 1px solid var(--line-2); background: var(--bg); color: var(--ink); font: inherit; text-align: left; cursor: pointer; overflow-wrap: anywhere; }
.as-ex button:hover { border-color: var(--accent); }
.as-fill { color: var(--muted); font-size: .76rem; }
.as-tips { display: grid; gap: 6px; padding-left: 18px; color: var(--muted); line-height: 1.45; }
@media (min-width: 1180px) {
  /* The last 1fr row takes the help's extra height, so the chat rows stay tight */
  .as { max-width: 1240px; grid-template-columns: minmax(0, 1fr) 320px; grid-template-rows: auto auto auto auto 1fr; column-gap: 20px; }
  .as > :not(.as-help) { grid-column: 1; }
  .as-help { display: grid; grid-column: 2; grid-row: 1 / 6; position: sticky; top: 16px; align-self: start; max-height: calc(100dvh - 32px); overflow-y: auto; }
  .as-help-btn { display: none; }
}
.as .btn .ico { width: 16px; height: 16px; }
.as-status { display: flex; flex-wrap: wrap; gap: 6px; }
.as-chip { display: inline-flex; align-items: center; gap: 6px; padding: 5px 10px; border-radius: 999px; background: var(--bg-2); color: var(--muted); font-size: .78rem; font-weight: 700; text-decoration: none; }
.as-chip .ico { width: 14px; height: 14px; }
.as-chip.on { background: rgba(25, 195, 166, .14); color: #12927C; }
.as-list { display: flex; flex-direction: column; gap: 10px; min-height: 280px; max-height: calc(100dvh - 330px); overflow-y: auto; }
.as-empty { margin: auto; text-align: center; color: var(--muted); display: grid; gap: 12px; }
.as-examples { display: flex; flex-wrap: wrap; justify-content: center; gap: 6px; }
.as-example { padding: 8px 12px; border-radius: 999px; border: 1px solid var(--line-2); background: var(--bg); color: var(--ink); font-size: .84rem; cursor: pointer; }
.as-msg { display: grid; gap: 2px; max-width: min(85%, 620px); }
.as-msg.user { align-self: flex-end; justify-items: end; }
.as-bubble { padding: 10px 14px; border-radius: 18px; background: var(--bg-2); color: var(--ink); }
.as-msg.user .as-bubble { background: var(--accent); color: #fff; border-bottom-right-radius: 6px; }
.as-msg.assistant .as-bubble { border-bottom-left-radius: 6px; }
.as-bubble p { white-space: pre-wrap; overflow-wrap: anywhere; font-size: .92rem; line-height: 1.45; }
.as-actions { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.as-confirm { display: inline-flex; flex-wrap: wrap; align-items: center; gap: 6px; font-size: .84rem; font-weight: 700; }
.as-done { display: inline-flex; align-items: center; gap: 4px; color: var(--muted); font-size: .8rem; font-weight: 700; }
.as-done .ico { width: 14px; height: 14px; }
.as-meta { color: var(--muted); font-size: .72rem; font-weight: 600; padding: 0 6px; }
.as-typing { display: inline-flex; gap: 4px; padding: 14px 16px; }
.as-typing span { width: 7px; height: 7px; border-radius: 50%; background: var(--muted); animation: asDot 1.2s infinite ease-in-out; }
.as-typing span:nth-child(2) { animation-delay: .15s; }
.as-typing span:nth-child(3) { animation-delay: .3s; }
@keyframes asDot { 0%, 80%, 100% { opacity: .3; transform: translateY(0); } 40% { opacity: 1; transform: translateY(-3px); } }
.as-form { display: flex; gap: 8px; align-items: flex-end; }
.as-form textarea { flex: 1; min-width: 0; resize: none; min-height: 52px; }
.as-form .btn { flex: none; width: 52px; height: 52px; padding: 0; justify-content: center; }
/* Phone: the input stays visible right above the tab bar */
@media (max-width: 860px) {
  .as-form { position: sticky; bottom: calc(80px + env(safe-area-inset-bottom)); z-index: 5; padding: 8px 0; background: var(--bg); }
}
@media (max-width: 640px) {
  .as-list { max-height: none; min-height: 200px; }
  .as-msg { scroll-margin-bottom: 180px; }  /* above the input and the tab bar */
  .as-msg { max-width: 92%; }
}
</style>
