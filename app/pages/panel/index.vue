<script setup lang="ts">
// Team kanban: shared boards, editable columns, cards with drag & drop
import type { TeamBoard, TeamBoardFull, TeamCard, TeamColumn } from '~/composables/useTeam'

const { t } = useSite()
const localePath = useLocalePath()
const { api, users } = useTeam()

const p = computed(() => t.value.panel)
const k = computed(() => t.value.panel.kanban)

const boards = ref<TeamBoard[]>([])
const board = ref<TeamBoardFull | null>(null)
const activeId = ref<number | null>(null)
const loading = ref(true)
const failed = ref(false)

const STORE = 'team-board'
const stored = () => {
  try { return Number(localStorage.getItem(STORE)) || null } catch { return null }
}
const remember = (id: number) => {
  try { localStorage.setItem(STORE, String(id)) } catch { /* private mode */ }
}

// Runs an API action; on failure shows a toast and reloads the board
async function run(fn: () => Promise<unknown>) {
  try {
    await fn()
  } catch (e) {
    if (httpStatus(e) === 401) return navigateTo(localePath('/login'))
    failed.value = true
    setTimeout(() => (failed.value = false), 3000)
    await reloadBoard().catch(() => {})
  }
}

async function reloadBoard() {
  board.value = activeId.value ? await api<TeamBoardFull>(`/boards/${activeId.value}`) : null
}

async function openBoard(id: number) {
  activeId.value = id
  remember(id)
  await run(reloadBoard)
}

onMounted(() =>
  run(async () => {
    boards.value = await api<TeamBoard[]>('/boards')
    const saved = stored()
    activeId.value = boards.value.some((b) => b.id === saved) ? saved : (boards.value[0]?.id ?? null)
    await reloadBoard()
  }).finally(() => (loading.value = false))
)

// Inline editing / two-step delete
const vFocus = { mounted: (el: HTMLInputElement) => (el.focus(), el.select?.()) }
const editKey = ref('')
const editText = ref('')
function startEdit(key: string, text = '') {
  editKey.value = key
  editText.value = text
}
const stopEdit = () => (editKey.value = '')
// Text of an open inline form; null if it is not open (guards submit + blur)
function take(key: string) {
  if (editKey.value !== key) return null
  stopEdit()
  return editText.value.trim()
}

const confirmKey = ref('')
let confirmTimer: ReturnType<typeof setTimeout> | undefined
function confirmThen(key: string, action: () => unknown) {
  if (confirmKey.value === key) {
    confirmKey.value = ''
    return action()
  }
  confirmKey.value = key
  clearTimeout(confirmTimer)
  confirmTimer = setTimeout(() => (confirmKey.value = ''), 3000)
}

// Boards
async function createBoard() {
  const title = take('new-board')
  if (!title) return
  await run(async () => {
    const b = await api<TeamBoard>('/boards', { method: 'POST', body: { title, columns: k.value.defaultColumns } })
    boards.value.push(b)
    await openBoard(b.id)
  })
}

async function renameBoard() {
  const title = take('board')
  const b = board.value
  if (!b || !title || title === b.title) return
  b.title = title
  const item = boards.value.find((x) => x.id === b.id)
  if (item) item.title = title
  await run(() => api(`/boards/${b.id}`, { method: 'PATCH', body: { title } }))
}

async function deleteBoard() {
  const id = activeId.value
  if (!id) return
  await run(async () => {
    await api(`/boards/${id}`, { method: 'DELETE' })
    boards.value = boards.value.filter((b) => b.id !== id)
    activeId.value = boards.value[0]?.id ?? null
    if (activeId.value) remember(activeId.value)
    await reloadBoard()
  })
}

// Columns
async function addColumn() {
  const title = take('new-col')
  const b = board.value
  if (!b || !title) return
  await run(async () => {
    b.columns.push(await api<TeamColumn>(`/boards/${b.id}/columns`, { method: 'POST', body: { title } }))
  })
}

async function renameColumn(col: TeamColumn) {
  const title = take(`col-${col.id}`)
  if (!title || title === col.title) return
  col.title = title
  await run(() => api(`/columns/${col.id}`, { method: 'PATCH', body: { title } }))
}

async function moveColumn(col: TeamColumn, dir: -1 | 1) {
  const cols = board.value?.columns
  if (!cols) return
  const from = cols.indexOf(col)
  const to = from + dir
  if (to < 0 || to >= cols.length) return
  cols.splice(from, 1)
  cols.splice(to, 0, col)
  await run(() => api(`/columns/${col.id}`, { method: 'PATCH', body: { position: to } }))
}

async function deleteColumn(col: TeamColumn) {
  const b = board.value
  if (!b) return
  b.columns = b.columns.filter((c) => c !== col)
  await run(() => api(`/columns/${col.id}`, { method: 'DELETE' }))
}

// Cards
async function addCard(col: TeamColumn) {
  const title = editText.value.trim()
  if (!title) return stopEdit()
  editText.value = '' // keep the form open for the next task
  await run(async () => {
    col.cards.push(await api<TeamCard>(`/columns/${col.id}/cards`, { method: 'POST', body: { title } }))
  })
}

// Drag & drop (native HTML5)
const drag = ref<{ card: TeamCard; from: TeamColumn } | null>(null)
const drop = ref<{ col: number; index: number } | null>(null)

function onDragStart(e: DragEvent, card: TeamCard, from: TeamColumn) {
  drag.value = { card, from }
  e.dataTransfer?.setData('text/plain', String(card.id))
  if (e.dataTransfer) e.dataTransfer.effectAllowed = 'move'
}

function onDragOver(e: DragEvent, col: TeamColumn) {
  if (!drag.value) return
  e.preventDefault()
  // Index among the other cards, by vertical midpoints
  let index = 0
  ;(e.currentTarget as HTMLElement).querySelectorAll<HTMLElement>('[data-card]').forEach((el) => {
    if (el.dataset.card === String(drag.value!.card.id)) return
    const r = el.getBoundingClientRect()
    if (e.clientY > r.top + r.height / 2) index++
  })
  if (drop.value?.col !== col.id || drop.value.index !== index) drop.value = { col: col.id, index }
}

function onDragLeave(e: DragEvent, col: TeamColumn) {
  const inside = (e.currentTarget as HTMLElement).contains(e.relatedTarget as Node | null)
  if (!inside && drop.value?.col === col.id) drop.value = null
}

function onDragEnd() {
  drag.value = null
  drop.value = null
}

async function onDrop(col: TeamColumn) {
  const d = drag.value
  const target = drop.value
  onDragEnd()
  if (!d || !target) return
  const from = d.from.cards.indexOf(d.card)
  if (d.from === col && from === target.index) return
  d.from.cards.splice(from, 1)
  col.cards.splice(target.index, 0, d.card)
  d.card.column_id = col.id
  col.cards.forEach((c, i) => (c.position = i))
  await run(() => api(`/cards/${d.card.id}`, { method: 'PATCH', body: { column_id: col.id, position: target.index } }))
}

// Cards of a column with the drop placeholder inserted
function items(col: TeamColumn) {
  const out: ({ ghost: true; key: string } | { ghost: false; key: number; card: TeamCard })[] = []
  const ghostAt = drop.value?.col === col.id ? drop.value.index : -1
  let i = 0
  for (const card of col.cards) {
    const moving = drag.value?.card === card
    if (!moving && i === ghostAt) out.push({ ghost: true, key: 'ghost' })
    out.push({ ghost: false, key: card.id, card })
    if (!moving) i++
  }
  if (ghostAt >= i) out.push({ ghost: true, key: 'ghost' })
  return out
}

// Card editor
const editing = ref<TeamCard | null>(null)

async function saveCard(patch: Partial<TeamCard>) {
  const card = editing.value
  editing.value = null
  if (!card) return
  await run(async () => {
    await api(`/cards/${card.id}`, { method: 'PATCH', body: patch })
    await reloadBoard()
  })
}

async function deleteCard() {
  const card = editing.value
  editing.value = null
  if (!card || !board.value) return
  for (const col of board.value.columns) col.cards = col.cards.filter((c) => c.id !== card.id)
  await run(() => api(`/cards/${card.id}`, { method: 'DELETE' }))
}

const userById = (id: number | null) => users.value.find((u) => u.id === id)
const initial = (name = '') => name.trim().charAt(0).toUpperCase() || '?'

// Pick up changes made by the teammate
let poll: ReturnType<typeof setInterval> | undefined
const idle = () => !drag.value && !editing.value && !editKey.value && document.visibilityState === 'visible'
const sync = () => idle() && reloadBoard().catch(() => {})
onMounted(() => {
  addEventListener('focus', sync)
  poll = setInterval(sync, 30000)
})
onBeforeUnmount(() => {
  removeEventListener('focus', sync)
  clearInterval(poll)
  clearTimeout(confirmTimer)
})
</script>

<template>
  <div class="kb">
    <header class="tp-head">
      <div>
        <h1>{{ k.title }}</h1>
        <p>{{ k.subtitle }}</p>
      </div>
    </header>

    <!-- Board tabs -->
    <div class="kb-boards" role="tablist" :aria-label="k.boards">
      <button
        v-for="b in boards"
        :key="b.id"
        type="button"
        role="tab"
        class="kb-tab"
        :class="{ active: b.id === activeId }"
        :aria-selected="b.id === activeId"
        @click="openBoard(b.id)"
      >
        {{ b.title }}
      </button>
      <form v-if="editKey === 'new-board'" class="kb-inline" @submit.prevent="createBoard">
        <input v-model="editText" v-focus class="tp-input" :placeholder="k.boardName" maxlength="120" @keydown.esc="stopEdit" @blur="createBoard">
      </form>
      <button v-else type="button" class="kb-tab kb-tab-add" @click="startEdit('new-board')">
        <AppIcon name="plus" /> {{ k.newBoard }}
      </button>
    </div>

    <div v-if="loading" class="kb-loading"><span class="spinner" /></div>

    <section v-else-if="!board" class="kb-empty">
      <span class="kb-empty-icon" aria-hidden="true"><AppIcon name="tasks" /></span>
      <h2>{{ k.emptyTitle }}</h2>
      <p>{{ k.emptyText }}</p>
      <button type="button" class="btn btn-primary" @click="startEdit('new-board')"><AppIcon name="plus" /> {{ k.newBoard }}</button>
    </section>

    <template v-else>
      <!-- Board title + actions -->
      <div class="kb-bar">
        <form v-if="editKey === 'board'" class="kb-inline" @submit.prevent="renameBoard">
          <input v-model="editText" v-focus class="tp-input kb-title-input" maxlength="120" @keydown.esc="stopEdit" @blur="renameBoard">
        </form>
        <h2 v-else class="kb-title" @dblclick="startEdit('board', board.title)">{{ board.title }}</h2>
        <button type="button" class="tp-icon-btn sm" :title="p.rename" :aria-label="p.rename" @click="startEdit('board', board.title)"><AppIcon name="edit" /></button>
        <button
          type="button"
          class="tp-icon-btn sm danger"
          :class="{ confirm: confirmKey === 'board' }"
          :title="confirmKey === 'board' ? p.sure : p.delete"
          :aria-label="confirmKey === 'board' ? p.sure : p.delete"
          @click="confirmThen('board', deleteBoard)"
        >
          <AppIcon name="trash" />
        </button>
        <Transition name="fade-x"><span v-if="confirmKey === 'board'" class="kb-sure">{{ p.sure }}</span></Transition>
      </div>

      <!-- Columns -->
      <TransitionGroup tag="div" name="kb-col" class="kb-columns">
        <section
          v-for="(col, ci) in board.columns"
          :key="col.id"
          class="kb-col"
          :class="{ over: drop?.col === col.id }"
          @dragover="onDragOver($event, col)"
          @dragleave="onDragLeave($event, col)"
          @drop.prevent="onDrop(col)"
        >
          <header class="kb-col-head">
            <form v-if="editKey === `col-${col.id}`" class="kb-inline" @submit.prevent="renameColumn(col)">
              <input v-model="editText" v-focus class="tp-input" maxlength="120" @keydown.esc="stopEdit" @blur="renameColumn(col)">
            </form>
            <h3 v-else @dblclick="startEdit(`col-${col.id}`, col.title)">
              {{ col.title }} <span class="kb-count">{{ col.cards.length }}</span>
            </h3>
            <div class="kb-col-actions">
              <button type="button" class="tp-icon-btn sm" :disabled="ci === 0" :title="k.moveLeft" :aria-label="k.moveLeft" @click="moveColumn(col, -1)"><AppIcon name="left" /></button>
              <button type="button" class="tp-icon-btn sm" :disabled="ci === board.columns.length - 1" :title="k.moveRight" :aria-label="k.moveRight" @click="moveColumn(col, 1)"><AppIcon name="right" /></button>
              <button type="button" class="tp-icon-btn sm" :title="p.rename" :aria-label="p.rename" @click="startEdit(`col-${col.id}`, col.title)"><AppIcon name="edit" /></button>
              <button
                type="button"
                class="tp-icon-btn sm danger"
                :class="{ confirm: confirmKey === `col-${col.id}` }"
                :title="confirmKey === `col-${col.id}` ? p.sure : p.delete"
                :aria-label="confirmKey === `col-${col.id}` ? p.sure : p.delete"
                @click="confirmThen(`col-${col.id}`, () => deleteColumn(col))"
              >
                <AppIcon name="trash" />
              </button>
            </div>
          </header>

          <TransitionGroup tag="ul" name="kb-card" class="kb-cards">
            <template v-for="it in items(col)">
              <li v-if="it.ghost" :key="`g-${col.id}`" class="kb-ghost">{{ k.dropHere }}</li>
              <li
                v-else
                :key="it.key"
                class="kb-card"
                :class="{ dragging: drag?.card === it.card }"
                :data-card="it.card.id"
                draggable="true"
                role="button"
                tabindex="0"
                @dragstart="onDragStart($event, it.card, col)"
                @dragend="onDragEnd"
                @click="editing = it.card"
                @keydown.enter="editing = it.card"
              >
                <p class="kb-card-title">{{ it.card.title }}</p>
                <p v-if="it.card.description" class="kb-card-desc">{{ it.card.description }}</p>
                <div v-if="it.card.assignee_id || it.card.description" class="kb-card-foot">
                  <AppIcon v-if="it.card.description" name="note" />
                  <span
                    v-if="userById(it.card.assignee_id)"
                    class="tp-avatar sm"
                    :data-c="it.card.assignee_id! % 3"
                    :title="userById(it.card.assignee_id)!.name"
                  >{{ initial(userById(it.card.assignee_id)!.name || userById(it.card.assignee_id)!.username) }}</span>
                </div>
              </li>
            </template>
          </TransitionGroup>

          <form v-if="editKey === `card-${col.id}`" class="kb-add-form" @submit.prevent="addCard(col)">
            <textarea
              v-model="editText"
              v-focus
              class="tp-input"
              rows="2"
              maxlength="300"
              :placeholder="k.cardTitle"
              @keydown.enter.exact.prevent="addCard(col)"
              @keydown.esc="stopEdit"
            />
            <div class="kb-add-actions">
              <button class="btn btn-primary btn-sm">{{ p.add }}</button>
              <button type="button" class="tp-icon-btn sm" :aria-label="p.cancel" @click="stopEdit"><AppIcon name="close" /></button>
            </div>
          </form>
          <button v-else type="button" class="kb-add" @click="startEdit(`card-${col.id}`)"><AppIcon name="plus" /> {{ k.newCard }}</button>
        </section>

        <!-- New column -->
        <section key="add-col" class="kb-col kb-col-new">
          <form v-if="editKey === 'new-col'" class="kb-inline" @submit.prevent="addColumn">
            <input v-model="editText" v-focus class="tp-input" :placeholder="k.columnName" maxlength="120" @keydown.esc="stopEdit" @blur="addColumn">
          </form>
          <button v-else type="button" class="kb-add" @click="startEdit('new-col')"><AppIcon name="plus" /> {{ k.newColumn }}</button>
        </section>
      </TransitionGroup>
    </template>

    <TeamCardModal
      v-if="editing && board"
      :card="editing"
      :columns="board.columns"
      :users="users"
      @close="editing = null"
      @save="saveCard"
      @delete="deleteCard"
    />

    <Transition name="toast"><div v-if="failed" class="tp-toast" role="status">{{ p.errorServer }}</div></Transition>
  </div>
</template>

<style>
/* ===== Kanban ===== */
.kb-boards { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 22px; }
.kb-tab {
  display: inline-flex; align-items: center; gap: 8px; padding: 9px 16px; border-radius: 999px; cursor: pointer;
  border: 1px solid var(--line-2); background: var(--surface); font-weight: 700; font-size: .9rem; color: var(--ink-2);
  transition: background .25s, color .25s, border-color .25s, transform .3s var(--ease);
}
.kb-tab:hover { border-color: var(--ink); color: var(--ink); }
.kb-tab.active { background: var(--ink); border-color: var(--ink); color: #fff; }
.kb-tab-add { border-style: dashed; color: var(--muted); background: transparent; }
.kb-tab .ico { width: 16px; height: 16px; }
.kb-inline { display: flex; }
.kb-inline .tp-input { width: 100%; }

.kb-loading { display: grid; place-items: center; padding: 80px 0; }
.kb-loading .spinner { width: 28px; height: 28px; border-color: var(--line-2); border-top-color: var(--accent); }

.kb-empty {
  display: grid; justify-items: center; gap: 10px; max-width: 460px; margin: 40px auto; padding: 44px 28px; text-align: center;
  border-radius: var(--radius); background: var(--surface); border: 1px dashed var(--line-2); animation: tpUp .7s var(--ease) both;
}
.kb-empty-icon { display: grid; place-items: center; width: 60px; height: 60px; border-radius: 18px; background: #EEEBFF; color: var(--accent); margin-bottom: 6px; }
.kb-empty-icon .ico { width: 28px; height: 28px; }
.kb-empty h2 { font-family: var(--font-display); font-weight: 600; font-size: 1.3rem; }
.kb-empty p { color: var(--muted); margin-bottom: 10px; }

.kb-bar { display: flex; align-items: center; gap: 8px; margin-bottom: 18px; min-height: 42px; }
.kb-title { font-size: 1.25rem; font-weight: 800; letter-spacing: -.01em; margin-right: 6px; cursor: text; }
.kb-title-input { font-size: 1.1rem; font-weight: 800; }
.kb-sure { color: #E5484D; font-weight: 700; font-size: .85rem; }
.fade-x-enter-active, .fade-x-leave-active { transition: opacity .2s, transform .25s var(--ease); }
.fade-x-enter-from, .fade-x-leave-to { opacity: 0; transform: translateX(-6px); }

.kb-columns {
  display: grid; grid-auto-flow: column; grid-auto-columns: minmax(270px, 300px); gap: 16px; align-items: start;
  overflow-x: auto; padding: 4px 4px 20px; margin: 0 -4px; scroll-snap-type: x proximity;
}
.kb-col {
  display: grid; gap: 10px; padding: 12px; border-radius: 22px; background: var(--bg-2); border: 1px solid transparent;
  scroll-snap-align: start; transition: background .25s, border-color .25s, box-shadow .25s;
}
.kb-col.over { background: #ECE9FF; border-color: rgba(91, 75, 255, .35); box-shadow: 0 0 0 4px rgba(91, 75, 255, .08); }
.kb-col-new { background: transparent; border: 1px dashed var(--line-2); }
.kb-col-head { display: flex; align-items: center; justify-content: space-between; gap: 6px; min-height: 34px; padding: 0 2px 0 6px; }
.kb-col-head h3 { display: flex; align-items: center; gap: 8px; font-size: .95rem; font-weight: 800; cursor: text; min-width: 0; overflow-wrap: anywhere; }
.kb-count { padding: 1px 8px; border-radius: 999px; background: var(--surface); color: var(--muted); font-size: .75rem; font-weight: 800; }
.kb-col-actions { display: flex; gap: 2px; opacity: 0; transition: opacity .2s; }
.kb-col:hover .kb-col-actions, .kb-col:focus-within .kb-col-actions { opacity: 1; }
.kb-col-actions .tp-icon-btn { background: transparent; }
.kb-col-actions .tp-icon-btn:hover:not(:disabled) { background: var(--ink); }
.kb-col-actions .tp-icon-btn.confirm { background: #E5484D; }
.kb-col-actions .tp-icon-btn:disabled { opacity: .3; cursor: default; }
@media (hover: none) { .kb-col-actions { opacity: 1; } }

.kb-cards { display: grid; gap: 8px; min-height: 8px; }
.kb-card {
  padding: 12px 14px; border-radius: 16px; background: var(--surface); border: 1px solid var(--line);
  box-shadow: 0 1px 2px rgba(18, 18, 22, .04); cursor: grab; user-select: none;
  transition: transform .3s var(--ease), box-shadow .3s, border-color .2s, opacity .2s;
}
.kb-card:hover { transform: translateY(-2px); box-shadow: var(--shadow); border-color: var(--line-2); }
.kb-card:active { cursor: grabbing; }
.kb-card.dragging { opacity: .35; transform: rotate(-1.5deg) scale(.98); }
.kb-card-title { font-weight: 700; font-size: .95rem; line-height: 1.4; overflow-wrap: anywhere; }
.kb-card-desc {
  margin-top: 4px; color: var(--muted); font-size: .84rem; line-height: 1.45;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.kb-card-foot { display: flex; align-items: center; justify-content: flex-end; gap: 8px; margin-top: 10px; color: var(--muted); }
.kb-card-foot .ico { width: 15px; height: 15px; margin-right: auto; }
.kb-ghost {
  display: grid; place-items: center; height: 46px; border-radius: 16px; border: 2px dashed rgba(91, 75, 255, .45);
  background: rgba(91, 75, 255, .06); color: var(--accent); font-size: .8rem; font-weight: 700;
}

.kb-card-move, .kb-col-move { transition: transform .35s var(--ease); }
.kb-card-enter-active { transition: opacity .35s, transform .35s var(--ease); }
.kb-card-enter-from { opacity: 0; transform: translateY(8px) scale(.97); }
.kb-card-leave-active { display: none; }
.kb-col-enter-active { transition: opacity .4s, transform .4s var(--ease); }
.kb-col-enter-from { opacity: 0; transform: translateX(20px); }
.kb-col-leave-active { display: none; }

.kb-add {
  display: flex; align-items: center; gap: 8px; width: 100%; padding: 10px 12px; border-radius: 14px; border: 0; cursor: pointer;
  background: transparent; color: var(--muted); font-weight: 700; font-size: .9rem; transition: background .2s, color .2s;
}
.kb-add:hover { background: var(--surface); color: var(--ink); }
.kb-add .ico { width: 16px; height: 16px; }
.kb-add-form { display: grid; gap: 8px; }
.kb-add-form textarea { resize: none; width: 100%; font-weight: 600; }
.kb-add-actions { display: flex; align-items: center; gap: 6px; }
</style>
