<script setup lang="ts" generic="T extends string">
import type { RvOption } from '~~/data/reservations'

defineProps<{ options: RvOption<T>[]; label: string }>()
const model = defineModel<T>({ required: true })
</script>

<template>
  <div class="rv-seg" role="group" :aria-label="label">
    <button v-for="option in options" :key="option.id" type="button" :class="{ on: option.id === model }" @click="model = option.id">
      {{ option.label }}
    </button>
  </div>
</template>

<style>
.rv-seg { display: flex; gap: 2px; padding: 3px; border-radius: 999px; background: rgba(255, 255, 255, .08); }
.rv-seg button { border: 0; background: none; color: #A3A3B0; padding: 5px 14px; border-radius: 999px; font: inherit; font-size: 12px; font-weight: 600; cursor: pointer; transition: background .2s, color .2s; }
.rv-seg button:hover { color: #fff; }
.rv-seg button.on { background: #4F46E5; color: #fff; }
</style>
