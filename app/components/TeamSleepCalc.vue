<script setup lang="ts">
// Sleep calculator: wake-up times for a bedtime, or bedtimes for a wake-up time.
// Sleep = time to fall asleep + whole ~90 min cycles, so the alarm hits light sleep.
// Click an option to set the alarm(s) right away.
const props = defineProps<{ setTimes: string[] }>() // times of enabled alarms
const emit = defineEmits<{ alarm: [alarms: { time: string; label: string }[]] }>()

const { t } = useSite()
const s = computed(() => t.value.panel.alarms.sleep)

const CYCLE = 90
const CYCLES = [6, 5, 4, 3]
const LATENCIES = [5, 10, 15, 20, 30]

const pad = (n: number) => String(n).padStart(2, '0')
const toMin = (hhmm: string) => {
  const [h, m] = hhmm.split(':').map(Number)
  return (h ?? 0) * 60 + (m ?? 0)
}
const toTime = (min: number) => {
  const m = ((Math.round(min) % 1440) + 1440) % 1440
  return `${pad(Math.floor(m / 60))}:${pad(m % 60)}`
}
// Now, rounded up to 5 minutes
const nowTime = () => {
  const d = new Date()
  return toTime(Math.ceil((d.getHours() * 60 + d.getMinutes()) / 5) * 5)
}

const mode = ref<'wake' | 'bed'>('wake') // wake: I go to bed at…, bed: I want to wake up at…
const bedTime = ref('23:00')
const wakeTime = ref('07:00')
const latency = ref(15)
onMounted(() => (bedTime.value = nowTime()))

const options = computed(() => {
  const list = CYCLES.map((n) => {
    const sleep = n * CYCLE
    const time = mode.value === 'wake'
      ? toTime(toMin(bedTime.value) + latency.value + sleep)
      : toTime(toMin(wakeTime.value) - sleep - latency.value)
    return { n, sleep, time, level: n >= 5 ? 'best' : n === 4 ? 'ok' : 'short' }
  })
  // Chronological: earliest wake-up first / earliest bedtime first
  return mode.value === 'wake' ? list.reverse() : list
})

const duration = (min: number) => `${Math.floor(min / 60)} ${s.value.h}${min % 60 ? ` ${min % 60} ${s.value.m}` : ''}`

// Wake mode: wake-up alarm. Bed mode: bedtime reminder + the wake-up alarm itself.
const isSet = (time: string) =>
  props.setTimes.includes(time) && (mode.value === 'wake' || props.setTimes.includes(wakeTime.value))

function addAlarm(o: { n: number; time: string }) {
  if (isSet(o.time)) return
  const wake = mode.value === 'wake'
    ? { time: o.time, label: `${s.value.wakeLabel} · ${duration(o.n * CYCLE)}` }
    : { time: wakeTime.value, label: `${s.value.wakeLabel} · ${duration(o.n * CYCLE)}` }
  const list = mode.value === 'wake' ? [wake] : [{ time: o.time, label: `${s.value.bedLabel} · ${s.value.wakeLabel} ${wakeTime.value}` }, wake]
  emit('alarm', list.filter((x) => !props.setTimes.includes(x.time)))
}
</script>

<template>
  <section class="sc">
    <header class="sc-head">
      <div>
        <h2><span class="sc-moon" aria-hidden="true" />{{ s.title }}</h2>
        <p>{{ s.subtitle }}</p>
      </div>
      <div class="sc-modes" role="tablist" :aria-label="s.title">
        <button type="button" role="tab" :aria-selected="mode === 'wake'" :class="{ on: mode === 'wake' }" @click="mode = 'wake'">{{ s.modeWake }}</button>
        <button type="button" role="tab" :aria-selected="mode === 'bed'" :class="{ on: mode === 'bed' }" @click="mode = 'bed'">{{ s.modeBed }}</button>
      </div>
    </header>

    <div class="sc-inputs">
      <label class="tp-field sc-time">
        <span>{{ mode === 'wake' ? s.bedInput : s.wakeInput }}</span>
        <span class="sc-time-row">
          <input v-if="mode === 'wake'" v-model="bedTime" type="time" required>
          <input v-else v-model="wakeTime" type="time" required>
          <button v-if="mode === 'wake'" type="button" class="btn btn-ghost btn-sm" @click="bedTime = nowTime()">{{ s.now }}</button>
        </span>
      </label>
      <div class="tp-field">
        <span>{{ s.latency }}</span>
        <div class="sc-chips" role="radiogroup" :aria-label="s.latency">
          <button
            v-for="l in LATENCIES"
            :key="l"
            type="button"
            role="radio"
            :aria-checked="latency === l"
            :class="{ on: latency === l }"
            @click="latency = l"
          >
            {{ l }} {{ s.m }}
          </button>
        </div>
      </div>
    </div>

    <p class="sc-lead">{{ mode === 'wake' ? s.wakeAt : s.bedAt }}</p>
    <TransitionGroup tag="ul" name="sc-opt" class="sc-options">
      <li
        v-for="(o, i) in options"
        :key="`${mode}-${o.n}`"
        class="sc-opt"
        :class="[o.level, { done: isSet(o.time) }]"
        :style="{ '--i': i }"
        role="button"
        tabindex="0"
        @click="addAlarm(o)"
        @keydown.enter="addAlarm(o)"
      >
        <span v-if="o.level !== 'short'" class="sc-badge">{{ o.level === 'best' ? s.best : s.ok }}</span>
        <span v-else class="sc-badge">{{ s.short }}</span>
        <p class="sc-opt-time">{{ o.time }}</p>
        <p class="sc-opt-meta">{{ duration(o.sleep) }} · {{ o.n }} × {{ CYCLE }} {{ s.m }}</p>
        <!-- One wave per sleep cycle -->
        <svg class="sc-waves" :viewBox="`0 0 ${o.n * 24} 12`" preserveAspectRatio="none" aria-hidden="true">
          <path :d="Array.from({ length: o.n }, (_, k) => `M${k * 24} 2 Q${k * 24 + 6} 12 ${k * 24 + 12} 10 T${k * 24 + 24} 2`).join(' ')" />
        </svg>
        <span class="sc-add">
          <template v-if="isSet(o.time)">✓ {{ s.isSet }}</template>
          <template v-else-if="mode === 'wake'"><AppIcon name="alarm" /> {{ s.setAlarm }} {{ o.time }}</template>
          <template v-else><AppIcon name="alarm" /> {{ s.setBoth }} {{ wakeTime }}</template>
        </span>
      </li>
    </TransitionGroup>
    <p class="sc-note">{{ s.note }}</p>
  </section>
</template>

<style>
/* ===== Sleep calculator ===== */
.sc {
  position: relative; overflow: hidden; margin-bottom: 22px; padding: 26px; border-radius: var(--radius);
  background: linear-gradient(140deg, #16142B, #23204A 60%, #2C2560); color: #fff; box-shadow: var(--shadow-lg);
  animation: tpUp .7s var(--ease) .12s both; isolation: isolate;
}
.sc::before, .sc::after {
  content: ''; position: absolute; border-radius: 50%; z-index: -1; pointer-events: none;
}
.sc::before { width: 320px; height: 320px; right: -90px; top: -120px; background: radial-gradient(circle, rgba(139, 127, 255, .45), transparent 70%); animation: float1 16s ease-in-out infinite; }
.sc::after {
  width: 3px; height: 3px; left: 12%; top: 18%; background: #fff;
  box-shadow: 120px 40px 0 #fff, 300px -6px 0 rgba(255, 255, 255, .6), 460px 70px 0 #fff, 620px 18px 0 rgba(255, 255, 255, .5), 760px 90px 0 #fff, 40px 140px 0 rgba(255, 255, 255, .4);
  animation: scTwinkle 4s ease-in-out infinite;
}
@keyframes scTwinkle { 50% { opacity: .35; } }
.sc-head { display: flex; flex-wrap: wrap; align-items: flex-start; justify-content: space-between; gap: 14px; margin-bottom: 18px; }
.sc-head h2 { display: flex; align-items: center; gap: 10px; font-family: var(--font-display); font-weight: 600; font-size: 1.35rem; letter-spacing: -.02em; }
.sc-head p { margin-top: 4px; color: rgba(255, 255, 255, .62); font-size: .9rem; max-width: 520px; }
.sc-moon { width: 22px; height: 22px; border-radius: 50%; box-shadow: inset -7px -3px 0 0 #FFD98A; transform: rotate(-20deg); animation: scMoon 6s ease-in-out infinite; }
@keyframes scMoon { 50% { transform: rotate(-5deg) scale(1.08); } }
.sc-modes { display: inline-flex; gap: 2px; padding: 4px; border-radius: 999px; background: rgba(255, 255, 255, .08); }
.sc-modes button {
  padding: 8px 14px; border: 0; border-radius: 999px; cursor: pointer; background: none; color: rgba(255, 255, 255, .7);
  font-weight: 800; font-size: .85rem; transition: background .25s, color .25s;
}
.sc-modes button:hover { color: #fff; }
.sc-modes button.on { background: #fff; color: #1B1838; }

.sc-inputs { display: grid; grid-template-columns: auto 1fr; gap: 18px; align-items: start; }
.sc .tp-field > span:first-child { color: rgba(255, 255, 255, .7); }
.sc-time-row { display: flex; align-items: center; gap: 8px; }
.sc-time input {
  width: 150px; background: rgba(255, 255, 255, .1); border-color: rgba(255, 255, 255, .18); color: #fff; color-scheme: dark;
  font-family: var(--font-display); font-weight: 600; font-size: 1.3rem; font-variant-numeric: tabular-nums;
}
.sc-time .btn { background: rgba(255, 255, 255, .1); color: #fff; border-color: rgba(255, 255, 255, .2); }
.sc-time .btn:hover { background: #fff; color: #1B1838; }
.sc-chips { display: flex; flex-wrap: wrap; gap: 6px; }
.sc-chips button {
  padding: 8px 12px; border-radius: 999px; cursor: pointer; border: 1px solid rgba(255, 255, 255, .18); background: none;
  color: rgba(255, 255, 255, .8); font-weight: 700; font-size: .82rem; transition: background .2s, color .2s, border-color .2s;
}
.sc-chips button:hover { border-color: #fff; }
.sc-chips button.on { background: #8B7FFF; border-color: #8B7FFF; color: #fff; }

.sc-lead { margin: 6px 0 10px; font-weight: 800; font-size: .9rem; color: rgba(255, 255, 255, .8); }
.sc-options { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
.sc-opt {
  position: relative; display: grid; gap: 4px; padding: 16px; border-radius: 20px;
  background: rgba(255, 255, 255, .06); border: 1px solid rgba(255, 255, 255, .1); transition: transform .35s var(--ease), background .25s, border-color .25s;
}
.sc-opt { cursor: pointer; }
.sc-opt:hover { transform: translateY(-3px); background: rgba(255, 255, 255, .1); }
.sc-opt:hover .sc-add { background: #fff; color: #1B1838; }
.sc-opt:focus-visible { outline: 2px solid #8B7FFF; outline-offset: 2px; }
.sc-opt.done { cursor: default; border-color: #7DEBD6; box-shadow: 0 0 0 3px rgba(125, 235, 214, .18); }
.sc-opt.done .sc-add, .sc-opt.done:hover .sc-add { background: #7DEBD6; color: #0B3B33; }
.sc-opt.best { background: rgba(125, 235, 214, .1); border-color: rgba(125, 235, 214, .35); }
.sc-opt.short { opacity: .7; }
.sc-badge { justify-self: start; padding: 2px 9px; border-radius: 999px; font-size: .7rem; font-weight: 800; background: rgba(255, 255, 255, .12); color: rgba(255, 255, 255, .8); }
.sc-opt.best .sc-badge { background: #7DEBD6; color: #0B3B33; }
.sc-opt.ok .sc-badge { background: #FFD98A; color: #4A3200; }
.sc-opt-time { font-family: var(--font-display); font-weight: 600; font-size: 2rem; letter-spacing: -.03em; line-height: 1.1; font-variant-numeric: tabular-nums; }
.sc-opt-meta { font-size: .8rem; color: rgba(255, 255, 255, .62); font-weight: 600; }
.sc-waves { width: 100%; height: 14px; margin: 6px 0 4px; overflow: visible; }
.sc-waves path { fill: none; stroke: rgba(255, 255, 255, .35); stroke-width: 1.6; stroke-linecap: round; vector-effect: non-scaling-stroke; stroke-dasharray: 400; stroke-dashoffset: 400; animation: scDraw 1.2s var(--ease) calc(var(--i) * .08s + .2s) forwards; }
.sc-opt.best .sc-waves path { stroke: #7DEBD6; }
@keyframes scDraw { to { stroke-dashoffset: 0; } }
.sc-add {
  justify-self: start; display: inline-flex; align-items: center; gap: 6px; margin-top: 2px; padding: 7px 12px; border-radius: 999px; background: rgba(255, 255, 255, .12); color: #fff; font-weight: 800; font-size: .8rem; transition: background .2s, color .2s;
}
.sc-add .ico { width: 15px; height: 15px; }
.sc-note { margin-top: 14px; font-size: .78rem; color: rgba(255, 255, 255, .5); }

.sc-opt-enter-active { transition: opacity .4s, transform .45s var(--ease); transition-delay: calc(var(--i) * .05s); }
.sc-opt-enter-from { opacity: 0; transform: translateY(10px); }
.sc-opt-leave-active { display: none; }

@media (max-width: 960px) { .sc-options { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 560px) {
  .sc { padding: 20px; }
  .sc-inputs { grid-template-columns: 1fr; }
  .sc-opt-time { font-size: 1.6rem; }
}
</style>
