<script setup lang="ts">
const props = defineProps<{ min: number; max: number; label: string }>()
const value = defineModel<number>({ required: true })

const clamp = (n: number) => Math.min(props.max, Math.max(props.min, Math.round(n) || props.min))
const step = (delta: number) => {
  value.value = clamp(value.value + delta)
}
const commit = (event: Event) => {
  const input = event.target as HTMLInputElement
  value.value = clamp(Number(input.value))
  input.value = String(value.value)
}
</script>

<template>
  <div class="ck-stepper" @click.stop>
    <button type="button" :aria-label="`Decrease ${label}`" :disabled="value <= min" @click="step(-1)">
      <svg viewBox="0 0 16 16" width="16" height="16"><path d="M3 8h10" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" /></svg>
    </button>
    <input type="number" :value="value" :min="min" :max="max" :aria-label="label" @change="commit">
    <button type="button" :aria-label="`Increase ${label}`" :disabled="value >= max" @click="step(1)">
      <svg viewBox="0 0 16 16" width="16" height="16"><path d="M3 8h10M8 3v10" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" /></svg>
    </button>
  </div>
</template>

<style>
.ck-stepper { display: flex; gap: 8px; width: 100%; }
.ck-stepper button { flex: none; width: 42px; height: 42px; display: grid; place-items: center; border-radius: 12px; border: 1px solid rgba(255, 255, 255, .12); background: rgba(0, 0, 0, .42); color: #fff; cursor: pointer; transition: background .2s; }
.ck-stepper button:hover:not(:disabled) { background: rgba(0, 0, 0, .55); }
.ck-stepper button:disabled { opacity: .4; cursor: default; }
.ck-stepper input { flex: 1; min-width: 0; height: 42px; padding: 0 8px; text-align: center; font: inherit; font-size: 18px; color: #F2F4FC; border-radius: 12px; border: 1px solid rgba(255, 255, 255, .12); background: rgba(0, 0, 0, .42); outline: none; appearance: textfield; -moz-appearance: textfield; }
.ck-stepper input::-webkit-inner-spin-button, .ck-stepper input::-webkit-outer-spin-button { appearance: none; margin: 0; }
</style>
