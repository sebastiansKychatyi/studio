<script setup lang="ts">
// Kanban card editor: title, description with @mentions, deadline, assignee, visibility, column (any board), delete
import type { TeamBoardItem, TeamCard, TeamColumn, TeamUser } from '~/composables/useTeam'

const props = defineProps<{
  card: TeamCard
  columns: TeamColumn[] // current board (fresh)
  boardId: number
  boards: TeamBoardItem[]
  users: TeamUser[]
  meId: number | null
}>()
const emit = defineEmits<{ close: []; save: [patch: Partial<TeamCard>]; delete: [] }>()

const { t } = useSite()
const p = computed(() => t.value.panel)
const k = computed(() => t.value.panel.kanban)

const form = reactive({
  title: props.card.title,
  description: props.card.description,
  assignee_id: props.card.assignee_id,
  column_id: props.card.column_id,
  due_date: props.card.due_date ?? '',
  is_private: props.card.is_private,
})

// Only the author changes visibility; someone else's card cannot go to a private board
const mine = computed(() => props.card.created_by === null || props.card.created_by === props.meId)
// `users` = people with access to the board; names of the others
const viewers = computed(() => props.users.filter((u) => u.id !== props.meId).map((u) => u.name || u.username))
const targets = computed(() =>
  props.boards
    .filter((b) => b.id === props.boardId || !b.is_private || mine.value)
    .map((b) => ({ ...b, columns: b.id === props.boardId ? props.columns : b.columns }))
)

// Insert "@username " at the cursor of the description
const descEl = ref<HTMLTextAreaElement>()
function mention(u: TeamUser) {
  const el = descEl.value
  const at = el?.selectionStart ?? form.description.length
  const before = form.description.slice(0, at)
  const tag = `${before && !/\s$/.test(before) ? ' ' : ''}@${u.username} `
  form.description = before + tag + form.description.slice(at)
  nextTick(() => {
    el?.focus()
    el?.setSelectionRange(at + tag.length, at + tag.length)
  })
}
const sure = ref(false)

function save() {
  const title = form.title.trim()
  if (!title) return
  const patch: Partial<TeamCard> = {}
  if (title !== props.card.title) patch.title = title
  if (form.description !== props.card.description) patch.description = form.description
  if (form.assignee_id !== props.card.assignee_id) patch.assignee_id = form.assignee_id
  if (form.column_id !== props.card.column_id) patch.column_id = form.column_id
  if ((form.due_date || null) !== props.card.due_date) patch.due_date = form.due_date || null
  if (form.is_private !== props.card.is_private) patch.is_private = form.is_private
  if (Object.keys(patch).length) emit('save', patch)
  else emit('close')
}

function remove() {
  if (sure.value) return emit('delete')
  sure.value = true
  setTimeout(() => (sure.value = false), 3000)
}

const onKey = (e: KeyboardEvent) => e.key === 'Escape' && emit('close')
onMounted(() => addEventListener('keydown', onKey))
onBeforeUnmount(() => removeEventListener('keydown', onKey))
</script>

<template>
  <div class="tm-overlay" @click.self="emit('close')">
    <form class="tm" role="dialog" aria-modal="true" :aria-label="k.edit" @submit.prevent="save">
      <header class="tm-head">
        <h2>{{ k.edit }}</h2>
        <button type="button" class="tp-icon-btn sm" :aria-label="p.close" @click="emit('close')"><AppIcon name="close" /></button>
      </header>

      <label class="tp-field">
        <span>{{ k.cardTitle }}</span>
        <input v-model="form.title" required maxlength="300">
      </label>
      <label class="tp-field">
        <span>{{ k.description }}</span>
        <textarea ref="descEl" v-model="form.description" rows="5" maxlength="10000" :placeholder="k.descriptionPh" />
      </label>
      <div class="tm-mention">
        <span><AppIcon name="at" /> {{ k.mention }}:</span>
        <button v-for="u in users" :key="u.id" type="button" class="tm-chip" @click="mention(u)">@{{ u.username }}</button>
        <small>{{ k.mentionHint }}</small>
      </div>
      <div class="tm-row">
        <label class="tp-field">
          <span>{{ k.column }}</span>
          <select v-model="form.column_id">
            <optgroup v-for="b in targets" :key="b.id" :label="`${k.board}: ${b.title}${b.is_private ? ' 🔒' : ''}`">
              <option v-for="c in b.columns" :key="c.id" :value="c.id">{{ c.title }}</option>
            </optgroup>
          </select>
        </label>
        <label class="tp-field">
          <span>{{ k.assignee }}</span>
          <select v-model="form.assignee_id">
            <option :value="null">{{ k.nobody }}</option>
            <option v-for="u in users" :key="u.id" :value="u.id">{{ u.name || u.username }}</option>
          </select>
        </label>
      </div>
      <div class="tp-field">
        <span>{{ k.visibility }}</span>
        <div class="tm-vis" role="radiogroup" :aria-label="k.visibility">
          <button
            v-for="v in [false, true]"
            :key="String(v)"
            type="button"
            role="radio"
            :aria-checked="form.is_private === v"
            :class="{ on: form.is_private === v }"
            :disabled="!mine"
            :title="mine ? '' : k.errorOwner"
            @click="form.is_private = v"
          >
            <AppIcon :name="v ? 'lock' : 'users'" />
            <span><b>{{ v ? k.private : k.team }}</b><small>{{ v ? k.privateHint : k.teamHint }}</small></span>
          </button>
        </div>
        <!-- Who actually sees a non-private card: everyone with access to the board -->
        <small v-if="!form.is_private" class="tm-who" :class="{ warn: !viewers.length }">
          <AppIcon :name="viewers.length ? 'users' : 'lock'" />
          {{ viewers.length ? `${k.seenBy}: ${viewers.join(', ')}` : k.boardNotShared }}
        </small>
      </div>
      <div class="tp-field">
        <span>{{ k.due }}</span>
        <div class="tm-due">
          <input v-model="form.due_date" type="date" :aria-label="k.due">
          <button v-if="form.due_date" type="button" class="btn btn-ghost btn-sm" @click="form.due_date = ''">{{ k.dueClear }}</button>
        </div>
      </div>

      <footer class="tm-foot">
        <button type="button" class="btn btn-sm tm-delete" :class="{ sure }" @click="remove">
          <AppIcon name="trash" /> {{ sure ? p.sure : p.delete }}
        </button>
        <div class="tm-foot-right">
          <button type="button" class="btn btn-ghost btn-sm" @click="emit('close')">{{ p.cancel }}</button>
          <button class="btn btn-primary btn-sm">{{ p.save }}</button>
        </div>
      </footer>
    </form>
  </div>
</template>

<style>
.tm-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.tm-mention { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin: -6px 0 16px; font-size: .82rem; font-weight: 700; color: var(--muted); }
.tm-mention > span { display: inline-flex; align-items: center; gap: 5px; }
.tm-mention .ico { width: 15px; height: 15px; }
.tm-mention small { flex-basis: 100%; font-weight: 600; }
.tm-chip {
  padding: 4px 10px; border-radius: 999px; border: 1px solid var(--line-2); background: #fff; cursor: pointer;
  font-weight: 700; font-size: .82rem; color: var(--accent); transition: background .2s, color .2s, border-color .2s;
}
.tm-chip:hover { background: var(--accent); border-color: var(--accent); color: #fff; }
.tm-vis { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.tm-vis button {
  display: flex; align-items: center; gap: 10px; padding: 10px 12px; border-radius: 14px; cursor: pointer; text-align: left;
  border: 1px solid var(--line-2); background: #fff; color: var(--ink-2); transition: border-color .2s, background .2s, box-shadow .2s;
}
.tm-vis button .ico { flex: none; width: 18px; height: 18px; color: var(--muted); transition: color .2s, transform .35s var(--ease); }
.tm-vis button span { display: grid; line-height: 1.25; }
.tm-vis button b { font-size: .88rem; }
.tm-vis button small { font-size: .75rem; color: var(--muted); font-weight: 600; }
.tm-vis button:hover:not(:disabled) { border-color: var(--accent); }
.tm-vis button.on { border-color: var(--accent); background: #F4F2FF; box-shadow: 0 0 0 3px rgba(91, 75, 255, .12); }
.tm-vis button.on .ico { color: var(--accent); transform: scale(1.1); }
.tm-vis button:disabled { cursor: not-allowed; opacity: .55; }
.tm-who { display: flex; align-items: center; gap: 6px; margin-top: 2px; color: var(--muted); font-size: .78rem; font-weight: 700; }
.tm-who .ico { flex: none; width: 14px; height: 14px; }
.tm-who.warn { color: #C2410C; }
.tm-due { display: flex; align-items: center; gap: 8px; }
.tm-due input { flex: 1; }
@media (max-width: 520px) { .tm-row { grid-template-columns: 1fr; } }
</style>
