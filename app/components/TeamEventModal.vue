<script setup lang="ts">
// Calendar event editor: title, day, time, weekly repeat (weekdays + end date), color, note.
// Repeating events can be removed for one day only or as a whole series.
import { CATEGORY_COLORS, type EventDraft, type TeamEvent } from '~/composables/useTeam'

const props = defineProps<{
  event: TeamEvent | null // null = new
  draft: EventDraft // initial values
  occurrence: string | null // clicked day of a repeating event
}>()
const emit = defineEmits<{ close: []; save: [body: EventDraft]; skip: [date: string]; delete: [] }>()

const { t } = useSite()
const p = computed(() => t.value.panel)
const c = computed(() => t.value.panel.calendar)
const WEEK = [1, 2, 3, 4, 5, 6, 0] // Monday first, JS weekday numbers

const form = reactive<EventDraft>({ ...props.draft, days: [...props.draft.days] })

// Reminder: presets or own number of minutes
const PRESETS = [5, 10, 15, 30, 60, 1440]
const custom = ref(form.remind !== null && !PRESETS.includes(form.remind))
const remindLabel = (m: number) =>
  m % 1440 === 0 ? `${m / 1440} ${c.value.d}` : m % 60 === 0 ? `${m / 60} ${c.value.h}` : `${m} ${c.value.m}`
function pickRemind(m: number | null) {
  custom.value = false
  form.remind = m
}
function pickCustom() {
  custom.value = true
  if (form.remind === null || PRESETS.includes(form.remind)) form.remind = 20
}
const error = ref(false)
const sure = ref<'one' | 'all' | null>(null)

const weekdayOf = (d: string) => new Date(`${d}T12:00:00`).getDay()
watch(() => form.repeat, (r) => {
  if (r === 'weekly' && !form.days.length) form.days = [weekdayOf(form.date)]
})

function toggleDay(d: number) {
  const i = form.days.indexOf(d)
  if (i >= 0) form.days.splice(i, 1)
  else form.days.push(d)
}

function save() {
  error.value = !form.title.trim() || form.end <= form.start
  if (error.value) return
  emit('save', {
    ...form,
    title: form.title.trim(),
    days: form.repeat === 'weekly' ? [...form.days].sort() : [],
    until: form.repeat === 'weekly' ? form.until || null : null,
    remind: form.remind === null ? null : Math.min(Math.max(Math.round(Number(form.remind) || 0), 0), 10080),
  })
}

function confirm(kind: 'one' | 'all') {
  if (sure.value !== kind) {
    sure.value = kind
    setTimeout(() => sure.value === kind && (sure.value = null), 3000)
    return
  }
  if (kind === 'one' && props.occurrence) emit('skip', props.occurrence)
  else emit('delete')
}

const vFocus = { mounted: (el: HTMLInputElement) => el.focus() }
const onKey = (e: KeyboardEvent) => e.key === 'Escape' && emit('close')
onMounted(() => addEventListener('keydown', onKey))
onBeforeUnmount(() => removeEventListener('keydown', onKey))
</script>

<template>
  <div class="tm-overlay" @click.self="emit('close')">
    <form class="tm ev" role="dialog" aria-modal="true" :aria-label="event ? c.edit : c.newEvent" :style="{ '--c': form.color }" @submit.prevent="save">
      <header class="tm-head">
        <h2><span class="ev-swatch" />{{ event ? c.edit : c.newEvent }}</h2>
        <button type="button" class="tp-icon-btn sm" :aria-label="p.close" @click="emit('close')"><AppIcon name="close" /></button>
      </header>

      <label class="tp-field">
        <span>{{ c.name }}</span>
        <input v-model="form.title" v-focus required maxlength="200" :placeholder="c.namePh">
      </label>
      <div class="ev-row">
        <label class="tp-field">
          <span>{{ form.repeat === 'weekly' ? c.from : c.date }}</span>
          <input v-model="form.date" type="date" required>
        </label>
        <label class="tp-field">
          <span>{{ c.start }}</span>
          <input v-model="form.start" type="time" required>
        </label>
        <label class="tp-field">
          <span>{{ c.end }}</span>
          <input v-model="form.end" type="time" required :class="{ invalid: error && form.end <= form.start }">
        </label>
      </div>

      <div class="tp-field">
        <span>{{ c.repeat }}</span>
        <div class="ev-repeat">
          <div class="ex-seg" role="radiogroup" :aria-label="c.repeat">
            <button type="button" role="radio" :aria-checked="form.repeat === 'none'" :class="{ on: form.repeat === 'none' }" @click="form.repeat = 'none'">{{ c.once }}</button>
            <button type="button" role="radio" :aria-checked="form.repeat === 'weekly'" :class="{ on: form.repeat === 'weekly' }" @click="form.repeat = 'weekly'">{{ c.weekly }}</button>
          </div>
          <div v-if="form.repeat === 'weekly'" class="al-days ev-days" role="group" :aria-label="c.repeat">
            <button
              v-for="(d, i) in WEEK"
              :key="d"
              type="button"
              class="al-day"
              :class="{ on: form.days.includes(d) }"
              :aria-pressed="form.days.includes(d)"
              @click="toggleDay(d)"
            >
              {{ p.alarms.days[i] }}
            </button>
          </div>
        </div>
      </div>
      <label v-if="form.repeat === 'weekly'" class="tp-field">
        <span>{{ c.until }}</span>
        <input v-model="form.until" type="date" :min="form.date">
        <small class="rc-hint">{{ c.untilHint }}</small>
      </label>

      <div class="tp-field">
        <span>{{ c.remind }}</span>
        <div class="ev-remind" role="radiogroup" :aria-label="c.remind">
          <button type="button" role="radio" :aria-checked="form.remind === null" :class="{ on: form.remind === null }" @click="pickRemind(null)">{{ c.remindNone }}</button>
          <button
            v-for="m in PRESETS"
            :key="m"
            type="button"
            role="radio"
            :aria-checked="!custom && form.remind === m"
            :class="{ on: !custom && form.remind === m }"
            @click="pickRemind(m)"
          >
            <AppIcon name="bell" />{{ remindLabel(m) }}
          </button>
          <button type="button" role="radio" :aria-checked="custom" :class="{ on: custom }" @click="pickCustom">{{ c.remindCustom }}</button>
        </div>
        <label v-if="custom" class="ev-remind-custom">
          <input v-model.number="form.remind" type="number" min="0" max="10080" step="1" inputmode="numeric">
          <span>{{ c.remindMinutes }}</span>
        </label>
        <small v-if="form.remind !== null" class="rc-hint">{{ c.remindHint }}</small>
      </div>

      <div class="tp-field">
        <span>{{ c.color }}</span>
        <div class="ex-catform-colors">
          <button
            v-for="col in CATEGORY_COLORS"
            :key="col"
            type="button"
            :aria-label="col"
            :class="{ on: form.color === col }"
            :style="{ background: col }"
            @click="form.color = col"
          />
        </div>
      </div>
      <label class="tp-field">
        <span>{{ c.note }}</span>
        <textarea v-model="form.note" rows="2" maxlength="5000" :placeholder="c.notePh" />
      </label>

      <footer class="tm-foot">
        <div v-if="event" class="ev-del">
          <button v-if="event.repeat === 'weekly' && occurrence" type="button" class="btn btn-sm tm-delete" :class="{ sure: sure === 'one' }" @click="confirm('one')">
            <AppIcon name="trash" /> {{ sure === 'one' ? p.sure : c.deleteOne }}
          </button>
          <button type="button" class="btn btn-sm tm-delete" :class="{ sure: sure === 'all' }" @click="confirm('all')">
            <AppIcon name="trash" /> {{ sure === 'all' ? p.sure : event.repeat === 'weekly' ? c.deleteAll : p.delete }}
          </button>
        </div>
        <div class="tm-foot-right">
          <button type="button" class="btn btn-ghost btn-sm" @click="emit('close')">{{ p.cancel }}</button>
          <button class="btn btn-primary btn-sm">{{ p.save }}</button>
        </div>
      </footer>
    </form>
  </div>
</template>

<style>
.ev h2 { display: flex; align-items: center; gap: 10px; }
.ev-swatch { width: 14px; height: 14px; border-radius: 5px; background: var(--c); transition: background .25s; }
.ev-row { display: grid; grid-template-columns: 1.3fr 1fr 1fr; gap: 10px; }
.ev input.invalid { border-color: #E5484D; }
.ev-repeat { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; }
.ev-days { margin: 0; }
.ev-days .al-day { width: 36px; height: 36px; font-size: .75rem; }
.ev-days .al-day.on { background: var(--c); border-color: var(--c); }
.ev textarea { resize: vertical; font: inherit; }
.ev-del { display: flex; flex-wrap: wrap; gap: 6px; }
.ev-remind { display: flex; flex-wrap: wrap; gap: 6px; }
.ev-remind button {
  display: inline-flex; align-items: center; gap: 5px; padding: 7px 11px; border-radius: 999px; cursor: pointer;
  border: 1px solid var(--line-2); background: var(--field, #fff); color: var(--ink-2); font-weight: 700; font-size: .8rem;
  transition: background .2s, color .2s, border-color .2s;
}
.ev-remind button .ico { width: 13px; height: 13px; }
.ev-remind button:hover { border-color: var(--c); }
.ev-remind button.on { background: var(--c); border-color: var(--c); color: #fff; }
.ev-remind-custom { display: flex; align-items: center; gap: 8px; margin-top: 4px; }
.ev-remind-custom input { width: 110px; }
.ev-remind-custom span { color: var(--muted); font-weight: 700; font-size: .85rem; }
@media (max-width: 520px) { .ev-row { grid-template-columns: 1fr 1fr; } .ev-row .tp-field:first-child { grid-column: 1 / -1; } }
</style>
