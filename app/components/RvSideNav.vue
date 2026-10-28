<script setup lang="ts" generic="T extends string">
import type { RvOption } from '~~/data/reservations'

defineProps<{ items: RvOption<T>[]; heading: string }>()
const page = defineModel<T>({ required: true })
</script>

<template>
  <nav class="rv-side" :aria-label="heading">
    <p>{{ heading }}</p>
    <button v-for="item in items" :key="item.id" type="button" :class="{ on: item.id === page }" @click="page = item.id">{{ item.label }}</button>
  </nav>
</template>

<style>
.rv-side { display: flex; flex-direction: column; gap: 4px; width: 200px; flex: none; padding-right: 20px; border-right: 1px solid var(--line); }
.rv-side p { margin: 0 0 6px 12px; font-size: 11px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }
.rv-side button { text-align: left; padding: 11px 14px; border: 0; border-left: 3px solid transparent; border-radius: 0 10px 10px 0; background: none; color: var(--muted); font: inherit; font-size: 14px; font-weight: 500; cursor: pointer; transition: background .2s, color .2s; }
.rv-side button:hover { color: var(--text); }
.rv-side button.on { color: var(--accent-text); border-left-color: var(--accent); background: var(--accent-soft); }
@container rv (max-width: 700px) {
  .rv-side { width: auto; flex-direction: row; padding: 0 0 8px; border-right: 0; overflow-x: auto; }
  .rv-side p { display: none; }
  .rv-side button { flex: none; border-left: 0; border-bottom: 2px solid transparent; border-radius: 8px; padding: 8px 12px; font-size: 13px; }
  .rv-side button.on { border-bottom-color: var(--accent); }
}
</style>
