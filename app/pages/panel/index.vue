<script setup lang="ts">
// Kanban: team or private boards and cards, drag & drop for cards, columns and boards, deadlines, @mentions
import { dueState, mentionParts, type TeamBoardFull, type TeamBoardItem, type TeamCard, type TeamColumn, type TeamMention } from '~/composables/useTeam'

const { t } = useSite()
const localePath = useLocalePath()
const { locale } = useI18n()
const { api, users, user, mentions, loadMentions } = useTeam()

const p = computed(() => t.value.panel)
const k = computed(() => t.value.panel.kanban)

const boards = ref<TeamBoardItem[]>([])
const board = ref<TeamBoardFull | null>(null)
const activeId = ref<number | null>(null)
const loading = ref(true)
const failed = ref('')

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
    const status = httpStatus(e)
    if (status === 401) return navigateTo(localePath('/login'))
    failed.value = status === 409 ? k.value.errorConflict : status === 403 ? k.value.errorOwner : p.value.errorServer
    setTimeout(() => (failed.value = ''), 3500)
    await reloadBoard().catch(() => {})
  }
}

// Board list (with column names for moving cards) + the open board
async function reloadBoard() {
  boards.value = await api<TeamBoardItem[]>('/boards')
  // The open board may be gone or made private by its author
  if (!boards.value.some((b) => b.id === activeId.value)) activeId.value = boards.value[0]?.id ?? null
  board.value = activeId.value ? await api<TeamBoardFull>(`/boards/${activeId.value}`) : null
  loadMentions().catch(() => {})
}

async function openBoard(id: number) {
  activeId.value = id
  remember(id)
  await run(reloadBoard)
}

onMounted(() =>
  run(async () => {
    activeId.value = stored()
    await reloadBoard()
  }).finally(() => (loading.value = false))
)

// Layout: columns in one scrolling row or wrapped into a grid; remembered per browser
const LAYOUT = 'team-kanban-layout'
const layout = ref<'grid' | 'row'>('grid')
onMounted(() => {
  try { if (localStorage.getItem(LAYOUT) === 'row') layout.value = 'row' } catch { /* private mode */ }
})
watch(layout, (v) => {
  try { localStorage.setItem(LAYOUT, v) } catch { /* private mode */ }
})

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

// Creator of a board/card (or no creator left) may change its visibility
const mine = (x: { created_by: number | null }) => x.created_by === null || x.created_by === user.value?.id

// Boards
const newBoardPrivate = ref(false)
async function createBoard() {
  const title = take('new-board')
  if (!title) return
  await run(async () => {
    const body = { title, columns: k.value.defaultColumns, is_private: newBoardPrivate.value }
    const b = await api<TeamBoardItem>('/boards', { method: 'POST', body })
    newBoardPrivate.value = false
    await openBoard(b.id)
  })
}

async function toggleBoardPrivate() {
  const b = board.value
  if (!b) return
  const is_private = !b.is_private
  await run(async () => {
    await api(`/boards/${b.id}`, { method: 'PATCH', body: { is_private } })
    await reloadBoard()
  })
}

// Board tabs: drag to reorder
const tabDrag = ref<number | null>(null)
async function onTabDrop(target: TeamBoardItem) {
  const id = tabDrag.value
  tabDrag.value = null
  const from = boards.value.findIndex((b) => b.id === id)
  const to = boards.value.indexOf(target)
  if (from < 0 || from === to) return
  const [moved] = boards.value.splice(from, 1)
  boards.value.splice(to, 0, moved!)
  await run(() => api(`/boards/${id}`, { method: 'PATCH', body: { position: to } }))
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

// Columns: drag the header to reorder
const colDrag = ref<TeamColumn | null>(null)
const colOver = ref<number | null>(null)
function onColDragStart(e: DragEvent, col: TeamColumn) {
  colDrag.value = col
  e.dataTransfer?.setData('text/plain', `col-${col.id}`)
  if (e.dataTransfer) e.dataTransfer.effectAllowed = 'move'
}
function onColDragEnd() {
  colDrag.value = null
  colOver.value = null
}
async function onColDrop(target: TeamColumn) {
  const col = colDrag.value
  onColDragEnd()
  const cols = board.value?.columns
  if (!col || !cols || col === target) return
  const to = cols.indexOf(target)
  cols.splice(cols.indexOf(col), 1)
  cols.splice(to, 0, col)
  await run(() => api(`/columns/${col.id}`, { method: 'PATCH', body: { position: to } }))
}

// Cards
const newCardPrivate = ref(false)
async function addCard(col: TeamColumn) {
  const title = editText.value.trim()
  if (!title) return stopEdit()
  editText.value = '' // keep the form open for the next task
  await run(async () => {
    const body = { title, is_private: newCardPrivate.value }
    col.cards.push(await api<TeamCard>(`/columns/${col.id}/cards`, { method: 'POST', body }))
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
  if (colDrag.value) {
    e.preventDefault()
    colOver.value = col.id
    return
  }
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
  if (colDrag.value) return onColDrop(col)
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

// Open a card from the "For me" list
async function openMention(m: TeamMention) {
  if (activeId.value !== m.board_id) await openBoard(m.board_id)
  editing.value = board.value?.columns.flatMap((c) => c.cards).find((c) => c.id === m.id) ?? null
}

// Deadline chip: Today / Tomorrow / short date; cards in the last column count as done
const isDone = (card: TeamCard) => board.value?.columns.at(-1)?.id === card.column_id
function dueLabel(due: string) {
  const state = dueState(due)
  if (state === 'today') return k.value.today
  const d = new Date(`${due}T12:00:00`)
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  if (d.toDateString() === tomorrow.toDateString()) return k.value.tomorrow
  return d.toLocaleDateString(locale.value, { day: 'numeric', month: 'short' })
}
const mentionsMe = (text: string) => mentionParts(text, users.value).some((x) => x.user?.id === user.value?.id)

const userById = (id: number | null) => users.value.find((u) => u.id === id)
const initial = (name = '') => name.trim().charAt(0).toUpperCase() || '?'

// Pick up changes made by the teammate
let poll: ReturnType<typeof setInterval> | undefined
const idle = () => !drag.value && !colDrag.value && !editing.value && !editKey.value && document.visibilityState === 'visible'
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

    <!-- For me: open cards that mention me or are assigned to me -->
    <section v-if="!loading" class="kb-forme">
      <h2><AppIcon name="at" /> {{ k.forMe }} <span class="kb-count">{{ mentions.length }}</span> <small>{{ k.forMeHint }}</small></h2>
      <TransitionGroup v-if="mentions.length" tag="ul" name="kb-card" class="kb-forme-list">
        <li v-for="m in mentions" :key="m.id">
          <button type="button" class="kb-forme-item" @click="openMention(m)">
            <b>{{ m.title }}</b>
            <small>{{ m.board_title }} · {{ m.column_title }}</small>
            <span class="kb-forme-meta">
              <span v-if="m.due_date" class="kb-due" :class="dueState(m.due_date)"><AppIcon name="calendar" />{{ dueLabel(m.due_date) }}</span>
              <span v-if="mentionsMe(`${m.title}\n${m.description}`)" class="kb-at me">@{{ user?.username }}</span>
            </span>
          </button>
        </li>
      </TransitionGroup>
      <p v-else class="kb-forme-empty">{{ k.forMeEmpty }}</p>
    </section>

    <!-- Board tabs -->
    <div class="kb-boards" role="tablist" :aria-label="k.boards">
      <button
        v-for="b in boards"
        :key="b.id"
        type="button"
        role="tab"
        class="kb-tab"
        :class="{ active: b.id === activeId, dragging: tabDrag === b.id }"
        :aria-selected="b.id === activeId"
        :title="`${b.is_private ? k.privateHint : k.teamHint} · ${k.drag}`"
        draggable="true"
        @click="openBoard(b.id)"
        @dragstart="tabDrag = b.id"
        @dragend="tabDrag = null"
        @dragover="tabDrag !== null && $event.preventDefault()"
        @drop.prevent="onTabDrop(b)"
      >
        <AppIcon v-if="b.is_private" name="lock" />{{ b.title }}
      </button>
      <form v-if="editKey === 'new-board'" class="kb-inline kb-new-board" @submit.prevent="createBoard">
        <input v-model="editText" v-focus class="tp-input" :placeholder="k.boardName" maxlength="120" @keydown.esc="stopEdit">
        <button
          type="button"
          class="kb-lock"
          :class="{ on: newBoardPrivate }"
          :aria-pressed="newBoardPrivate"
          :title="newBoardPrivate ? k.privateHint : k.teamHint"
          @mousedown.prevent
          @click="newBoardPrivate = !newBoardPrivate"
        >
          <AppIcon :name="newBoardPrivate ? 'lock' : 'users'" />{{ newBoardPrivate ? k.private : k.team }}
        </button>
        <button class="btn btn-primary btn-sm">{{ p.add }}</button>
        <button type="button" class="tp-icon-btn sm" :aria-label="p.cancel" @click="stopEdit"><AppIcon name="close" /></button>
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
        <button
          type="button"
          class="kb-lock"
          :class="{ on: board.is_private }"
          :disabled="!mine(board)"
          :title="mine(board) ? (board.is_private ? k.privateHint : k.teamHint) : k.errorOwner"
          @click="toggleBoardPrivate"
        >
          <AppIcon :name="board.is_private ? 'lock' : 'users'" />{{ board.is_private ? k.private : k.team }}
        </button>
        <div class="ex-seg kb-layout" role="radiogroup" :aria-label="k.layout">
          <button type="button" role="radio" :aria-checked="layout === 'grid'" :class="{ on: layout === 'grid' }" :title="k.grid" @click="layout = 'grid'">
            <AppIcon name="grid" /><span>{{ k.grid }}</span>
          </button>
          <button type="button" role="radio" :aria-checked="layout === 'row'" :class="{ on: layout === 'row' }" :title="k.row" @click="layout = 'row'">
            <AppIcon name="tasks" /><span>{{ k.row }}</span>
          </button>
        </div>
      </div>

      <!-- Columns -->
      <TransitionGroup tag="div" name="kb-col" class="kb-columns" :class="{ grid: layout === 'grid' }">
        <section
          v-for="(col, ci) in board.columns"
          :key="col.id"
          class="kb-col"
          :class="{ over: drop?.col === col.id || (colOver === col.id && colDrag !== col), moving: colDrag === col }"
          @dragover="onDragOver($event, col)"
          @dragleave="onDragLeave($event, col)"
          @drop.prevent="onDrop(col)"
        >
          <header class="kb-col-head" draggable="true" :title="k.drag" @dragstart="onColDragStart($event, col)" @dragend="onColDragEnd">
            <form v-if="editKey === `col-${col.id}`" class="kb-inline" @submit.prevent="renameColumn(col)">
              <input v-model="editText" v-focus class="tp-input" maxlength="120" @keydown.esc="stopEdit" @blur="renameColumn(col)">
            </form>
            <h3 v-else @dblclick="startEdit(`col-${col.id}`, col.title)">
              <AppIcon name="grip" class="kb-grip" />{{ col.title }} <span class="kb-count">{{ col.cards.length }}</span>
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
                <p class="kb-card-title">
                  <AppIcon v-if="it.card.is_private && !board.is_private" name="lock" class="kb-card-lock" />
                  <template v-for="(part, pi) in mentionParts(it.card.title, users)" :key="pi">
                    <span v-if="part.user" class="kb-at" :class="{ me: part.user.id === user?.id }">{{ part.text }}</span>
                    <template v-else>{{ part.text }}</template>
                  </template>
                </p>
                <p v-if="it.card.description" class="kb-card-desc">
                  <template v-for="(part, pi) in mentionParts(it.card.description, users)" :key="pi">
                    <span v-if="part.user" class="kb-at" :class="{ me: part.user.id === user?.id }">{{ part.text }}</span>
                    <template v-else>{{ part.text }}</template>
                  </template>
                </p>
                <div v-if="it.card.assignee_id || it.card.description || it.card.due_date" class="kb-card-foot">
                  <span
                    v-if="it.card.due_date"
                    class="kb-due"
                    :class="isDone(it.card) ? 'done' : dueState(it.card.due_date)"
                    :title="`${k.due}: ${it.card.due_date}${!isDone(it.card) && dueState(it.card.due_date) === 'overdue' ? ` · ${k.overdue}` : ''}`"
                  >
                    <AppIcon name="calendar" />{{ dueLabel(it.card.due_date) }}
                  </span>
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
              <button
                v-if="!board.is_private"
                type="button"
                class="kb-lock"
                :class="{ on: newCardPrivate }"
                :aria-pressed="newCardPrivate"
                :title="newCardPrivate ? k.privateHint : k.teamHint"
                @click="newCardPrivate = !newCardPrivate"
              >
                <AppIcon :name="newCardPrivate ? 'lock' : 'users'" />{{ newCardPrivate ? k.private : k.team }}
              </button>
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
      :board-id="board.id"
      :boards="boards"
      :users="users"
      :me-id="user?.id ?? null"
      @close="editing = null"
      @save="saveCard"
      @delete="deleteCard"
    />

    <Transition name="toast"><div v-if="failed" class="tp-toast" role="status">{{ failed }}</div></Transition>
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

.kb-columns {
  display: grid; grid-auto-flow: column; grid-auto-columns: minmax(270px, 300px); gap: 16px; align-items: start;
  overflow-x: auto; padding: 4px 4px 20px; margin: 0 -4px; scroll-snap-type: x proximity;
}
/* Grid layout: columns wrap into rows */
.kb-columns.grid { grid-auto-flow: row; grid-template-columns: repeat(auto-fill, minmax(270px, 1fr)); overflow-x: visible; scroll-snap-type: none; }
.kb-layout { margin-left: auto; }
.kb-layout button { display: inline-flex; align-items: center; gap: 6px; }
.kb-layout .ico { width: 15px; height: 15px; }
@media (max-width: 640px) { .kb-layout span { display: none; } }
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
.kb-at { padding: 0 4px; border-radius: 6px; background: #EEEBFF; color: var(--accent); font-weight: 800; }
.kb-at.me { background: var(--accent); color: #fff; }
.kb-due {
  display: inline-flex; align-items: center; gap: 4px; margin-right: auto; padding: 2px 8px; border-radius: 999px;
  background: var(--bg-2); color: var(--ink-2); font-size: .75rem; font-weight: 800; white-space: nowrap;
}
.kb-card-foot .kb-due .ico, .kb-due .ico { width: 13px; height: 13px; margin: 0; }
.kb-due + .ico { margin-right: 0; }
.kb-due.soon { background: #FFF1D6; color: #A15C00; }
.kb-due.today { background: #FFE2D6; color: #C2410C; }
.kb-due.overdue { background: #E5484D; color: #fff; animation: kbPulse 2s ease-in-out infinite; }
.kb-due.done { text-decoration: line-through; opacity: .6; }
@keyframes kbPulse { 50% { box-shadow: 0 0 0 4px rgba(229, 72, 77, .18); } }

.kb-forme { margin-bottom: 22px; padding: 16px; border-radius: 22px; background: var(--surface); border: 1px solid var(--line); animation: tpUp .6s var(--ease) both; }
.kb-forme h2 { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; font-size: .95rem; font-weight: 800; }
.kb-forme h2 .ico { width: 17px; height: 17px; color: var(--accent); }
.kb-forme h2 .kb-count { background: var(--bg-2); }
.kb-forme h2 small { color: var(--muted); font-weight: 600; font-size: .8rem; }
.kb-forme-list { display: flex; gap: 10px; overflow-x: auto; padding: 12px 2px 2px; }
.kb-forme-list li { flex: none; width: 240px; }
.kb-forme-item {
  display: grid; gap: 4px; width: 100%; height: 100%; padding: 12px 14px; border-radius: 16px; text-align: left; cursor: pointer;
  border: 1px solid var(--line); background: var(--bg); transition: transform .3s var(--ease), box-shadow .3s, border-color .2s;
}
.kb-forme-item:hover { transform: translateY(-2px); box-shadow: var(--shadow); border-color: rgba(91, 75, 255, .35); }
.kb-forme-item b { font-size: .9rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.kb-forme-item small { color: var(--muted); font-weight: 600; font-size: .78rem; }
.kb-forme-meta { display: flex; align-items: center; gap: 6px; margin-top: 4px; min-height: 20px; }
.kb-forme-meta .kb-due { margin-right: 0; }
.kb-forme-meta .kb-at { font-size: .75rem; }
.kb-forme-empty { margin-top: 8px; color: var(--muted); font-size: .88rem; }
.kb-tab .ico { color: inherit; }
.kb-tab.dragging { opacity: .4; }
.kb-new-board { display: flex; align-items: center; gap: 6px; }
.kb-new-board .tp-input { width: 200px; }
.kb-lock {
  display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 999px; cursor: pointer; white-space: nowrap;
  border: 1px solid var(--line-2); background: var(--surface); color: var(--ink-2); font-weight: 700; font-size: .8rem;
  transition: background .2s, color .2s, border-color .2s;
}
.kb-lock .ico { width: 15px; height: 15px; transition: transform .35s var(--ease); }
.kb-lock:hover:not(:disabled) { border-color: var(--ink); }
.kb-lock.on { background: var(--ink); border-color: var(--ink); color: #fff; }
.kb-lock.on .ico { transform: rotate(-8deg) scale(1.1); }
.kb-lock:disabled { cursor: not-allowed; opacity: .55; }
.kb-bar .kb-lock { margin-left: 8px; }
.kb-col-head { cursor: grab; }
.kb-col-head:active { cursor: grabbing; }
.kb-grip { width: 14px; height: 14px; color: var(--muted); opacity: 0; margin-right: -4px; transition: opacity .2s; }
.kb-col:hover .kb-grip { opacity: 1; }
.kb-col.moving { opacity: .4; transform: rotate(-1deg); }
.kb-col.over:not(.moving) { border-style: dashed; }
.kb-card-lock { display: inline-block; width: 13px; height: 13px; margin: 0 4px 2px 0; vertical-align: middle; color: var(--accent); }
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
