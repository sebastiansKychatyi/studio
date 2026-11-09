<script setup lang="ts">
// Assistant and chats (the same chats as in Telegram).
// - Assistant: short lines are saved by the quick parser at once (no AI); the rest goes to Claude.
// - Regular chats: Claude with memory of the whole chat and its own model; with the sandbox it can also
//   write and run code in the user's own container. Long answers are polled, so the page can be left.
// Created entries get "Undo"; changes to existing entries wait for "Yes".

interface Action { label: string; kind: 'undo' | 'confirm'; method: string; path: string; done?: boolean | 'declined' }
interface Message { id: number; at: string; role: 'user' | 'assistant'; via: string; engine: string; text: string; actions: Action[] }
interface Chat { id: number; kind: 'assistant' | 'chat'; title: string; model: string; own_model: string; busy: boolean; updated_at: string }
interface Status { telegram: boolean; telegram_linked: boolean; bot: string | null; parser: boolean; claude: boolean; model: string; chat_model: string; models: string[]; sandbox: boolean }

const { t } = useSite()
const { locale } = useI18n()
const localePath = useLocalePath()
const route = useRoute()
const router = useRouter()
const { api } = useTeam()
const p = computed(() => t.value.panel)
const a = computed(() => t.value.panel.assistant)

const chats = ref<Chat[]>([])
const chatId = ref<number | null>(null)
const chat = computed(() => chats.value.find((c) => c.id === chatId.value) || null)
const isChat = computed(() => chat.value?.kind === 'chat')
const messages = ref<Message[]>([])
const status = ref<Status | null>(null)
const text = ref('')
const sending = ref(false)
const waiting = ref(false)  // the server is still writing an answer (also for messages from Telegram)
const busy = computed(() => sending.value || waiting.value)
const loading = ref(true)
const note = ref('')
const list = ref<HTMLElement | null>(null)
const input = ref<HTMLTextAreaElement | null>(null)
const helpOpen = ref(false)  // phones only; wide screens always show the help
const flash = (s: string) => {
  note.value = s
  setTimeout(() => (note.value = ''), 3500)
}
const fail = (e: unknown) => flash(isOffline(e) ? p.value.offlineOnly : p.value.errorServer)
const chatTitle = (c: Chat) => (c.kind === 'assistant' ? a.value.title : c.title || a.value.untitled)

async function scrollDown() {
  await nextTick()
  // The list scrolls on wide screens, the page on phones
  list.value?.scrollTo({ top: list.value.scrollHeight, behavior: 'smooth' })
  list.value?.lastElementChild?.scrollIntoView({ block: 'end', behavior: 'smooth' })
}

async function loadChats() {
  chats.value = await api<Chat[]>('/assistant/chats')
}

let poll: ReturnType<typeof setTimeout> | null = null
async function load(quiet = false) {
  const id = chatId.value
  if (id === null) return
  if (poll) clearTimeout(poll)
  try {
    const r = await api<{ busy: boolean; messages: Message[] }>(`/assistant/chats/${id}/messages`, { query: { limit: 150 } })
    if (id !== chatId.value) return  // switched meanwhile
    const grew = r.messages.length !== messages.value.length
    messages.value = r.messages
    waiting.value = r.busy
    if (r.busy) poll = setTimeout(() => load(true), 3000)
    if (!quiet || grew) scrollDown()
  } catch (e) {
    if (!quiet) fail(e)
    else poll = setTimeout(() => load(true), 6000)
  } finally {
    loading.value = false
  }
}

async function open(id: number) {
  if (id === chatId.value) return
  chatId.value = id
  messages.value = []
  loading.value = true
  helpOpen.value = false
  router.replace({ query: { ...route.query, chat: chats.value[0]?.id === id ? undefined : String(id) } })
  await load()
}

onMounted(async () => {
  api<Status>('/assistant').then((s) => (status.value = s)).catch(() => {})
  try {
    await loadChats()
  } catch (e) {
    loading.value = false
    return fail(e)
  }
  const wanted = Number(route.query.chat)
  chatId.value = chats.value.find((c) => c.id === wanted)?.id ?? chats.value[0]?.id ?? null
  // Phones: the open chat may be outside the strip
  nextTick(() => document.querySelector('.as-tab.on')?.scrollIntoView({ block: 'nearest', inline: 'nearest' }))
  await load()
})
onBeforeUnmount(() => poll && clearTimeout(poll))

async function send(line = text.value) {
  const q = line.trim()
  const id = chatId.value
  if (!q || busy.value || id === null) return
  sending.value = true
  text.value = ''
  // Shown at once; the stored copy comes with the reload
  messages.value.push({ id: -Date.now(), at: new Date().toISOString(), role: 'user', via: 'panel', engine: '', text: q, actions: [] })
  scrollDown()
  try {
    const r = await api<{ question: Message; answer: Message | null }>(`/assistant/chats/${id}/messages`, { method: 'POST', body: { text: q } })
    if (!r.answer) waiting.value = true  // a long answer: keep polling, the page may be left
    await load(!!r.answer)
    if (isChat.value) loadChats().catch(() => {})  // the first message names the chat
  } catch (e) {
    messages.value.pop()
    text.value = q
    fail(e)
  } finally {
    sending.value = false
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
    fail(e)
  }
}

// ===== Chats =====
async function newChat() {
  try {
    const c = await api<Chat>('/assistant/chats', { method: 'POST', body: {} })
    chats.value.splice(1, 0, c)
    await open(c.id)
    nextTick(() => input.value?.focus())
  } catch (e) {
    fail(e)
  }
}
async function patch(body: { title?: string; model?: string }) {
  const c = chat.value
  if (!c) return
  try {
    const r = await api<Chat>(`/assistant/chats/${c.id}`, { method: 'PATCH', body })
    chats.value = chats.value.map((x) => (x.id === r.id ? r : x))
  } catch (e) {
    fail(e)
  }
}
const renaming = ref(false)
const newTitle = ref('')
function rename() {
  newTitle.value = chat.value?.title || ''
  renaming.value = true
}
async function saveTitle() {
  if (!renaming.value) return
  renaming.value = false
  if (newTitle.value.trim() !== (chat.value?.title || '')) await patch({ title: newTitle.value.trim() })
}

// Two clicks: "Clear" then "Sure?"
const sure = ref<'' | 'clear' | 'delete'>('')
function confirmFirst(what: 'clear' | 'delete') {
  if (sure.value === what) return true
  sure.value = what
  setTimeout(() => (sure.value = ''), 3000)
  return false
}
async function clear() {
  const c = chat.value
  if (!c || !confirmFirst('clear')) return
  sure.value = ''
  try {
    await api(`/assistant/chats/${c.id}/messages`, { method: 'DELETE' })
    messages.value = []
  } catch (e) {
    fail(e)
  }
}
async function remove() {
  const c = chat.value
  if (!c || c.kind !== 'chat' || !confirmFirst('delete')) return
  sure.value = ''
  try {
    await api(`/assistant/chats/${c.id}`, { method: 'DELETE' })
    chats.value = chats.value.filter((x) => x.id !== c.id)
    chatId.value = null
    await open(chats.value[0]!.id)
  } catch (e) {
    fail(e)
  }
}

const modelName = (m: string) => a.value.models[m as keyof typeof a.value.models] || m
const defaultModel = computed(() => (isChat.value ? status.value?.chat_model : status.value?.model) || '')
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
      </div>
    </header>

    <!-- Chats: the assistant first, then regular chats -->
    <nav class="as-chats" :aria-label="a.chats">
      <button v-for="c in chats" :key="c.id" type="button" class="as-tab" :class="{ on: c.id === chatId, quick: c.kind === 'assistant' }"
              :aria-current="c.id === chatId ? 'true' : undefined" @click="open(c.id)">
        <AppIcon :name="c.kind === 'assistant' ? 'spark' : 'bot'" />
        <span>{{ chatTitle(c) }}</span>
        <i v-if="c.busy || (c.id === chatId && busy)" class="as-dot" />
      </button>
      <button type="button" class="as-tab as-new" @click="newChat"><AppIcon name="plus" /> {{ a.newChat }}</button>
    </nav>

    <!-- Active chat: what works here, model, name -->
    <div v-if="chat" class="as-bar">
      <template v-if="renaming">
        <input v-model="newTitle" class="tp-input as-rename" maxlength="120" :aria-label="a.rename" @keydown.enter.prevent="saveTitle" @keydown.esc="renaming = false" @blur="saveTitle">
      </template>
      <div v-else class="as-status">
        <span v-if="!isChat && status" class="as-chip" :class="{ on: status.parser }"><AppIcon name="spark" /> {{ a.parser }}</span>
        <span v-if="status" class="as-chip" :class="{ on: status.claude }"><AppIcon name="bot" /> Claude{{ status.claude ? '' : ` — ${a.claudeOff}` }}</span>
        <span v-if="isChat && status" class="as-chip" :class="{ on: status.sandbox }"><AppIcon name="code" /> {{ status.sandbox ? a.sandboxOn : a.sandboxOff }}</span>
        <NuxtLink v-if="status?.telegram" :to="localePath('/panel/settings')" class="as-chip" :class="{ on: status.telegram_linked }">
          <AppIcon name="telegram" /> {{ status.telegram_linked ? a.tgLinked : a.tgConnect }}
        </NuxtLink>
      </div>
      <div class="as-actions-bar">
        <label v-if="status" class="as-model">
          <span>{{ a.model }}</span>
          <select :value="chat.own_model" class="tp-input" @change="patch({ model: ($event.target as HTMLSelectElement).value })">
            <option value="">{{ a.modelDefault }} ({{ modelName(defaultModel) }})</option>
            <option v-for="m in status.models" :key="m" :value="m">{{ modelName(m) }}</option>
          </select>
        </label>
        <button v-if="isChat && !renaming" type="button" class="btn btn-ghost btn-sm" :aria-label="a.rename" :title="a.rename" @click="rename"><AppIcon name="edit" /></button>
        <button v-if="messages.length" type="button" class="btn btn-ghost btn-sm" :class="{ 'tm-delete sure': sure === 'clear' }" @click="clear">
          <AppIcon name="close" /> {{ sure === 'clear' ? p.sure : a.clear }}
        </button>
        <button v-if="isChat" type="button" class="btn btn-ghost btn-sm" :class="{ 'tm-delete sure': sure === 'delete' }" @click="remove">
          <AppIcon name="trash" /> {{ sure === 'delete' ? p.sure : a.deleteChat }}
        </button>
      </div>
    </div>

    <!-- Short guide: right column on wide screens, toggled on phones -->
    <aside class="as-help sd-card" :class="{ open: helpOpen }">
      <template v-if="isChat">
        <h2>{{ a.help.chatTitle }}</h2>
        <ol class="as-steps">
          <li v-for="s in a.help.chatSteps" :key="s">{{ s }}</li>
        </ol>
        <p v-if="status" class="as-warn" :class="{ ok: status.sandbox }">{{ status.sandbox ? a.help.sandboxOn : a.help.sandboxOff }}</p>
        <h3><AppIcon name="bot" /> {{ a.help.chatExamplesTitle }}</h3>
        <ul class="as-ex">
          <li v-for="ex in a.help.chatExamples" :key="ex"><button type="button" @click="fill(ex)">{{ ex }}</button></li>
        </ul>
        <h3>{{ a.model }}</h3>
        <ul class="as-tips">
          <li v-for="m in a.help.modelTips" :key="m">{{ m }}</li>
        </ul>
      </template>
      <template v-else>
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
      </template>
    </aside>

    <section ref="list" class="as-list sd-card" aria-live="polite">
      <div v-if="loading" class="kb-loading"><span class="spinner" /></div>
      <div v-else-if="!messages.length" class="as-empty">
        <p>{{ isChat ? a.chatEmpty : a.empty }}</p>
        <div v-if="!isChat" class="as-examples">
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
      <div v-if="busy" class="as-msg assistant">
        <div class="as-bubble as-typing"><span /><span /><span /></div>
        <small v-if="waiting && isChat" class="as-meta">{{ a.working }}</small>
      </div>
    </section>

    <form class="as-form" @submit.prevent="send()">
      <textarea ref="input" v-model="text" class="tp-input" rows="2" maxlength="2000" :placeholder="isChat ? a.chatPlaceholder : a.placeholder"
                :aria-label="isChat ? a.chatPlaceholder : a.placeholder" @keydown="onKey" />
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
  .as { max-width: 1240px; grid-template-columns: minmax(0, 1fr) 320px; grid-template-rows: auto auto auto auto auto 1fr; column-gap: 20px; }
  .as > :not(.as-help) { grid-column: 1; }
  .as-help { display: grid; grid-column: 2; grid-row: 1 / 7; position: sticky; top: 16px; align-self: start; max-height: calc(100dvh - 32px); overflow-y: auto; }
  .as-help-btn { display: none; }
}
.as .btn .ico { width: 16px; height: 16px; }
/* Chats strip: scrolls sideways when there are many */
.as-chats { display: flex; gap: 6px; overflow-x: auto; padding-bottom: 2px; scrollbar-width: thin; }
.as-tab { flex: none; display: inline-flex; align-items: center; gap: 6px; max-width: 220px; padding: 8px 12px; border-radius: 12px; border: 1px solid var(--line-2); background: var(--bg); color: var(--ink); font: inherit; font-size: .86rem; font-weight: 700; cursor: pointer; }
.as-tab span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.as-tab .ico { flex: none; width: 15px; height: 15px; }
.as-tab.on { border-color: var(--accent); background: var(--accent); color: #fff; }
.as-tab.as-new { border-style: dashed; color: var(--muted); }
.as-dot { flex: none; width: 7px; height: 7px; border-radius: 50%; background: #19C3A6; animation: asDot 1.2s infinite ease-in-out; }
.as-bar { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 8px; }
.as-actions-bar { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; }
.as-model { display: inline-flex; align-items: center; gap: 6px; color: var(--muted); font-size: .78rem; font-weight: 700; }
.as-model select { width: auto; min-height: 0; padding: 6px 10px; font-size: .82rem; }
.as-rename { flex: 1; min-width: 180px; max-width: 420px; }
.as-warn.ok { background: rgba(25, 195, 166, .14); }

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
