<script setup lang="ts">
// Card actions without drag & drop (main way on a phone): open, move to board → column → top/bottom, assign.
import type { TeamBoard, TeamBoardItem, TeamCard, TeamUser } from '~/composables/useTeam'

const props = defineProps<{
  card: TeamCard
  boardId: number
  boards: TeamBoardItem[]
  users: TeamUser[] // people with access to the card's board
  meId: number | null
}>()
const emit = defineEmits<{ close: []; open: []; move: [columnId: number, where: 'top' | 'bottom']; assign: [userId: number | null] }>()

const { t } = useSite()
const p = computed(() => t.value.panel)
const k = computed(() => t.value.panel.kanban)

const step = ref<'menu' | 'move' | 'where' | 'assign'>('menu')
const target = ref<{ board: TeamBoardItem; column: { id: number; title: string } } | null>(null)

// The card's author must have access to the target board (server rule)
const authorSees = (b: TeamBoard) =>
  props.card.created_by === null || b.created_by === props.card.created_by || b.member_ids.includes(props.card.created_by)
  || (b.created_by === null && !b.member_ids.length)
const sorted = computed(() => [...props.boards].sort((a, b) => Number(b.id === props.boardId) - Number(a.id === props.boardId)))

function pick(board: TeamBoardItem, column: { id: number; title: string }) {
  target.value = { board, column }
  step.value = 'where'
}

const onKey = (e: KeyboardEvent) => e.key === 'Escape' && emit('close')
onMounted(() => addEventListener('keydown', onKey))
onBeforeUnmount(() => removeEventListener('keydown', onKey))
</script>

<template>
  <div class="tm-overlay" @click.self="emit('close')">
    <div class="tm tm-sm km" role="dialog" aria-modal="true" :aria-label="k.menu">
      <header class="tm-head">
        <button v-if="step !== 'menu'" type="button" class="tp-icon-btn sm" :aria-label="k.back" @click="step = step === 'where' ? 'move' : 'menu'">
          <AppIcon name="left" />
        </button>
        <h2>{{ step === 'move' ? k.moveTo : step === 'where' ? k.pickPosition : step === 'assign' ? k.assignTo : card.title }}</h2>
        <button type="button" class="tp-icon-btn sm" :aria-label="p.close" @click="emit('close')"><AppIcon name="close" /></button>
      </header>

      <div v-if="step === 'menu'" class="km-list">
        <button type="button" class="km-item" @click="emit('open')"><AppIcon name="edit" />{{ k.open }}</button>
        <button type="button" class="km-item" @click="step = 'move'"><AppIcon name="right" />{{ k.moveTo }}</button>
        <button type="button" class="km-item" @click="step = 'assign'">
          <AppIcon name="user" />{{ k.assignTo }}
          <small v-if="card.assignee_id">{{ users.find((u) => u.id === card.assignee_id)?.name }}</small>
        </button>
      </div>

      <!-- Board → column -->
      <div v-else-if="step === 'move'" class="km-boards">
        <section v-for="b in sorted" :key="b.id" class="km-board" :class="{ off: !authorSees(b) }">
          <h3><AppIcon :name="b.is_private ? 'lock' : 'users'" />{{ b.title }}<small v-if="!authorSees(b)">{{ k.errorAuthor }}</small></h3>
          <div class="km-cols">
            <button
              v-for="c in b.columns"
              :key="c.id"
              type="button"
              :class="{ here: c.id === card.column_id }"
              :disabled="!authorSees(b)"
              @click="pick(b, c)"
            >
              {{ c.title }}<small v-if="c.id === card.column_id">{{ k.here }}</small>
            </button>
          </div>
        </section>
      </div>

      <!-- Position -->
      <div v-else-if="step === 'where' && target" class="km-list">
        <p class="km-path">{{ target.board.title }} · <b>{{ target.column.title }}</b></p>
        <button type="button" class="km-item" @click="emit('move', target.column.id, 'top')"><AppIcon name="arrow" />{{ k.top }}</button>
        <button type="button" class="km-item" @click="emit('move', target.column.id, 'bottom')"><AppIcon name="download" />{{ k.bottom }}</button>
      </div>

      <!-- Assignee -->
      <div v-else-if="step === 'assign'" class="km-list">
        <button type="button" class="km-item" :class="{ on: card.assignee_id === null }" @click="emit('assign', null)">
          <AppIcon name="close" />{{ k.nobody }}
        </button>
        <button v-for="u in users" :key="u.id" type="button" class="km-item" :class="{ on: card.assignee_id === u.id }" @click="emit('assign', u.id)">
          <span class="tp-avatar sm" :data-c="u.id % 3">{{ (u.name || u.username).charAt(0).toUpperCase() }}</span>
          {{ u.name || u.username }}<small v-if="u.id === meId">{{ k.me }}</small>
        </button>
        <p class="km-path">{{ k.assignHint }}</p>
      </div>
    </div>
  </div>
</template>

<style>
.tm.tm-sm { width: min(420px, 100%); }
.km .tm-head { gap: 8px; }
.km .tm-head h2 { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.km-list { display: grid; gap: 4px; padding-bottom: calc(12px + env(safe-area-inset-bottom)); }
.km-item {
  display: flex; align-items: center; gap: 12px; min-height: 48px; padding: 10px 12px; border: 0; border-radius: 14px; cursor: pointer;
  background: none; color: var(--ink); font-weight: 700; font-size: .95rem; text-align: left; transition: background .2s;
}
.km-item:hover { background: var(--bg-2); }
.km-item > .ico { width: 18px; height: 18px; color: var(--muted); }
.km-item small { margin-left: auto; color: var(--muted); font-weight: 600; font-size: .8rem; }
.km-item.on { background: rgba(91, 75, 255, .1); color: var(--accent); }
.km-path { padding: 4px 12px; color: var(--muted); font-size: .82rem; font-weight: 600; }
.km-path b { color: var(--ink); }
.km-boards { display: grid; gap: 14px; padding-bottom: calc(14px + env(safe-area-inset-bottom)); }
.km-board h3 { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin-bottom: 8px; font-size: .9rem; font-weight: 800; }
.km-board h3 .ico { width: 15px; height: 15px; color: var(--muted); }
.km-board h3 small { flex-basis: 100%; color: var(--muted); font-weight: 600; font-size: .75rem; }
.km-board.off { opacity: .5; }
.km-cols { display: flex; flex-wrap: wrap; gap: 6px; }
.km-cols button {
  display: inline-flex; align-items: center; gap: 6px; min-height: 44px; padding: 0 16px; border-radius: 999px; cursor: pointer;
  border: 1px solid var(--line-2); background: var(--field, #fff); color: var(--ink); font-weight: 700; font-size: .88rem; transition: border-color .2s, background .2s;
}
.km-cols button:hover:not(:disabled) { border-color: var(--accent); }
.km-cols button.here { border-style: dashed; }
.km-cols button small { color: var(--muted); font-size: .72rem; font-weight: 700; }
.km-cols button:disabled { cursor: not-allowed; }
</style>
