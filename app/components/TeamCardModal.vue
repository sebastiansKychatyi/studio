<script setup lang="ts">
// Kanban card editor: title, description, assignee, column, delete
import type { TeamCard, TeamColumn, TeamUser } from '~/composables/useTeam'

const props = defineProps<{ card: TeamCard; columns: TeamColumn[]; users: TeamUser[] }>()
const emit = defineEmits<{ close: []; save: [patch: Partial<TeamCard>]; delete: [] }>()

const { t } = useSite()
const p = computed(() => t.value.panel)
const k = computed(() => t.value.panel.kanban)

const form = reactive({
  title: props.card.title,
  description: props.card.description,
  assignee_id: props.card.assignee_id,
  column_id: props.card.column_id,
})
const sure = ref(false)

function save() {
  const title = form.title.trim()
  if (!title) return
  const patch: Partial<TeamCard> = {}
  if (title !== props.card.title) patch.title = title
  if (form.description !== props.card.description) patch.description = form.description
  if (form.assignee_id !== props.card.assignee_id) patch.assignee_id = form.assignee_id
  if (form.column_id !== props.card.column_id) patch.column_id = form.column_id
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
        <textarea v-model="form.description" rows="5" maxlength="10000" :placeholder="k.descriptionPh" />
      </label>
      <div class="tm-row">
        <label class="tp-field">
          <span>{{ k.column }}</span>
          <select v-model="form.column_id">
            <option v-for="c in columns" :key="c.id" :value="c.id">{{ c.title }}</option>
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
.tm-overlay {
  position: fixed; inset: 0; z-index: 200; display: grid; place-items: center; padding: 16px;
  background: rgba(18, 18, 22, .35); -webkit-backdrop-filter: blur(6px); backdrop-filter: blur(6px);
  animation: tpFade .25s both;
}
.tm {
  width: min(560px, 100%); max-height: calc(100svh - 32px); overflow-y: auto; padding: 24px;
  border-radius: var(--radius); background: var(--surface); box-shadow: var(--shadow-lg);
  animation: tmIn .4s var(--ease) both;
}
@keyframes tmIn { from { opacity: 0; transform: translateY(20px) scale(.97); } }
.tm-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.tm-head h2 { font-size: 1.15rem; font-weight: 800; }
.tm textarea { resize: vertical; min-height: 110px; font: inherit; }
.tm-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.tm-foot { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px; margin-top: 8px; }
.tm-foot-right { display: flex; gap: 8px; }
.tm-delete { background: transparent; color: #C93A3F; padding-inline: 12px; }
.tm-delete:hover, .tm-delete.sure { background: #E5484D; color: #fff; }
@media (max-width: 520px) { .tm-row { grid-template-columns: 1fr; } }
</style>
