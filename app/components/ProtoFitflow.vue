<script setup lang="ts">
// "FitFlow" prototype: fitness app (320×640) with light/dark theme
const props = defineProps<{ preview?: boolean }>()

const c = useConceptCopy({
  sk: { hi: 'Ahoj 👋', today: 'Dnešná aktivita', rings: ['Pohyb', 'Cvičenie', 'Státie'], workouts: 'Tréningy pre teba', min: 'min', start: 'Začať', next: 'Ďalší cvik', pause: 'Pauza', play: 'Pokračovať', of: 'z', doneTitle: 'Skvelá práca! 🔥', kcal: 'kcal', time: 'čas', back: 'Späť na prehľad', names: [['HIIT 12', ['Drepy', 'Kliky', 'Burpees']], ['Jóga flow', ['Pes hlavou dole', 'Bojovník', 'Strom']], ['Core', ['Plank', 'Brušáky', 'Horolezec']]] },
  cs: { hi: 'Ahoj 👋', today: 'Dnešní aktivita', rings: ['Pohyb', 'Cvičení', 'Stání'], workouts: 'Tréninky pro tebe', min: 'min', start: 'Začít', next: 'Další cvik', pause: 'Pauza', play: 'Pokračovat', of: 'z', doneTitle: 'Skvělá práce! 🔥', kcal: 'kcal', time: 'čas', back: 'Zpět na přehled', names: [['HIIT 12', ['Dřepy', 'Kliky', 'Angličáky']], ['Jóga flow', ['Pes hlavou dolů', 'Bojovník', 'Strom']], ['Core', ['Plank', 'Sklapovačky', 'Horolezec']]] },
  uk: { hi: 'Привіт 👋', today: 'Активність сьогодні', rings: ['Рух', 'Вправи', 'Стояння'], workouts: 'Тренування для тебе', min: 'хв', start: 'Почати', next: 'Наступна вправа', pause: 'Пауза', play: 'Продовжити', of: 'з', doneTitle: 'Чудова робота! 🔥', kcal: 'ккал', time: 'час', back: 'До огляду', names: [['HIIT 12', ['Присідання', 'Віджимання', 'Берпі']], ['Йога flow', ['Собака мордою вниз', 'Воїн', 'Дерево']], ['Core', ['Планка', 'Скручування', 'Скелелаз']]] },
  en: {
    "hi": "Hi 👋",
    "today": "Today’s activity",
    "rings": [
      "Move",
      "Exercise",
      "Stand"
    ],
    "workouts": "Workouts for you",
    "min": "min",
    "start": "Start",
    "next": "Next exercise",
    "pause": "Pause",
    "play": "Resume",
    "of": "of",
    "doneTitle": "Great job! 🔥",
    "kcal": "kcal",
    "time": "time",
    "back": "Back to overview",
    "names": [
      [
        "HIIT 12",
        [
          "Squats",
          "Push-ups",
          "Burpees"
        ]
      ],
      [
        "Yoga flow",
        [
          "Downward dog",
          "Warrior",
          "Tree"
        ]
      ],
      [
        "Core",
        [
          "Plank",
          "Crunches",
          "Mountain climbers"
        ]
      ]
    ]
  },
})

const meta = [{ min: 12, kcal: 180, color: '#FF5A36' }, { min: 15, kcal: 90, color: '#8B5CF6' }, { min: 10, kcal: 120, color: '#10B981' }]
const ringColors = ['#FF5A36', '#A3E635', '#22D3EE']
const rings = ref([0.72, 0.45, 0.9])
const shown = ref([0, 0, 0]) // animate from zero
const dark = ref(false)
const screen = ref<'home' | 'run' | 'done'>('home')
const w = ref(0)
const step = ref(0)
const left = ref(10)
const running = ref(false)
const STEP = 10 // seconds per exercise (demo)
let timer: ReturnType<typeof setInterval> | undefined

const workout = computed(() => c.value.names[w.value]! as [string, string[]])
const exercises = computed(() => workout.value[1])
const circ = 2 * Math.PI * 40

function start(i: number) {
  w.value = i
  step.value = 0
  left.value = STEP
  screen.value = 'run'
  running.value = true
  tick()
}
function tick() {
  clearInterval(timer)
  timer = setInterval(() => {
    if (!running.value) return
    left.value--
    if (left.value <= 0) next()
  }, 1000)
}
function next() {
  if (step.value < exercises.value.length - 1) {
    step.value++
    left.value = STEP
  } else {
    clearInterval(timer)
    running.value = false
    screen.value = 'done'
    rings.value = rings.value.map((r, i) => Math.min(1, r + (i === 1 ? 0.3 : 0.08)))
    shown.value = [...rings.value]
  }
}
function home() {
  screen.value = 'home'
  clearInterval(timer)
}

onMounted(() => setTimeout(() => (shown.value = [...rings.value]), props.preview ? 0 : 300))
onBeforeUnmount(() => clearInterval(timer))
</script>

<template>
  <div class="ff-phone" :class="{ dark, 'is-preview': props.preview }" :inert="props.preview || undefined">
    <div class="ff-notch" />
    <div class="ff-status"><b>9:41</b><button type="button" class="ff-theme" :aria-label="dark ? 'light' : 'dark'" @click="dark = !dark">{{ dark ? '☀' : '☾' }}</button></div>

    <Transition name="pb-push" mode="out-in">
      <div v-if="screen === 'home'" key="home" class="ff-screen">
        <p class="ff-muted">{{ c.hi }}</p>
        <h3>{{ c.today }}</h3>
        <div class="ff-rings-card">
          <svg viewBox="0 0 120 120" class="ff-rings" aria-hidden="true">
            <g v-for="(r, i) in shown" :key="i" :style="{ '--rc': ringColors[i] }">
              <circle cx="60" cy="60" :r="50 - i * 14" class="bg" />
              <circle cx="60" cy="60" :r="50 - i * 14" class="fg" :stroke-dasharray="2 * Math.PI * (50 - i * 14)" :stroke-dashoffset="2 * Math.PI * (50 - i * 14) * (1 - r)" />
            </g>
          </svg>
          <ul>
            <li v-for="(name, i) in c.rings" :key="name"><i :style="{ background: ringColors[i] }" />{{ name }} <b>{{ Math.round(rings[i]! * 100) }}%</b></li>
          </ul>
        </div>
        <p class="ff-label">{{ c.workouts }}</p>
        <button v-for="(wk, i) in c.names" :key="wk[0] as string" type="button" class="ff-work" @click="start(i)">
          <span class="ff-dot" :style="{ background: meta[i]!.color }">▶</span>
          <span><b>{{ wk[0] }}</b><small>{{ meta[i]!.min }} {{ c.min }} · {{ meta[i]!.kcal }} {{ c.kcal }}</small></span>
          <em>{{ c.start }} →</em>
        </button>
      </div>

      <div v-else-if="screen === 'run'" key="run" class="ff-screen ff-run" :style="{ '--wc': meta[w]!.color }">
        <button type="button" class="ff-x" @click="home">✕</button>
        <p class="ff-muted">{{ workout[0] }} · {{ step + 1 }} {{ c.of }} {{ exercises.length }}</p>
        <h3>{{ exercises[step] }}</h3>
        <div class="ff-timer">
          <svg viewBox="0 0 100 100" aria-hidden="true">
            <circle cx="50" cy="50" r="40" class="bg" />
            <circle cx="50" cy="50" r="40" class="fg" :stroke-dasharray="circ" :stroke-dashoffset="circ * (1 - left / STEP)" />
          </svg>
          <b>{{ left }}</b>
        </div>
        <div class="ff-progress"><i v-for="(e, i) in exercises" :key="e" :class="{ on: i <= step }" /></div>
        <div class="ff-controls">
          <button type="button" class="ff-btn" @click="running = !running">{{ running ? `❚❚ ${c.pause}` : `▶ ${c.play}` }}</button>
          <button type="button" class="ff-btn ghost" @click="next">{{ c.next }} →</button>
        </div>
      </div>

      <div v-else key="done" class="ff-screen ff-done">
        <div class="ff-burst">🏆</div>
        <h3>{{ c.doneTitle }}</h3>
        <div class="ff-stats">
          <div><b>{{ meta[w]!.kcal }}</b><small>{{ c.kcal }}</small></div>
          <div><b>{{ meta[w]!.min }}</b><small>{{ c.min }}</small></div>
          <div><b>{{ exercises.length }}</b><small>✓</small></div>
        </div>
        <button type="button" class="ff-btn" @click="home">{{ c.back }}</button>
      </div>
    </Transition>
  </div>
</template>

<style>
.ff-phone { --bg: #F8F7FF; --card: #fff; --ink: #14121F; --muted: #7C7894; position: relative; width: 320px; height: 640px; border-radius: 44px; border: 10px solid #14121F; background: var(--bg); color: var(--ink); overflow: hidden; font-family: 'Manrope', system-ui, sans-serif; text-align: left; display: flex; flex-direction: column; box-shadow: 0 40px 80px -30px rgba(0, 0, 0, .5); transition: background .4s, color .4s; }
.ff-phone.dark { --bg: #0E0C17; --card: #1A1727; --ink: #F5F3FF; --muted: #8E89A8; }
.ff-phone button { font: inherit; color: inherit; cursor: pointer; border: 0; background: none; }
.ff-notch { position: absolute; top: 8px; left: 50%; translate: -50% 0; width: 90px; height: 24px; border-radius: 20px; background: #14121F; z-index: 5; }
.ff-status { display: flex; justify-content: space-between; align-items: center; padding: 12px 18px 4px 22px; font-size: 12px; }
.ff-theme { width: 30px; height: 30px; border-radius: 50%; background: var(--card) !important; box-shadow: 0 4px 12px -6px rgba(0, 0, 0, .3); }
.ff-screen { flex: 1; padding: 8px 18px 18px; overflow-y: auto; scrollbar-width: none; position: relative; }
.ff-screen h3 { font-size: 22px; font-weight: 800; letter-spacing: -.02em; margin: 2px 0 12px; }
.ff-muted { color: var(--muted); font-size: 13px; }
.ff-rings-card { display: grid; grid-template-columns: 120px 1fr; gap: 12px; align-items: center; padding: 14px; border-radius: 22px; background: var(--card); transition: background .4s; }
.ff-rings circle { fill: none; stroke-width: 11; stroke-linecap: round; transform: rotate(-90deg); transform-origin: 60px 60px; }
.ff-rings .bg { stroke: var(--rc); opacity: .15; }
.ff-rings .fg { stroke: var(--rc); transition: stroke-dashoffset 1.4s cubic-bezier(.2, .8, .2, 1); }
.ff-rings-card ul { display: grid; gap: 8px; font-size: 12px; font-weight: 700; }
.ff-rings-card li { display: flex; align-items: center; gap: 6px; }
.ff-rings-card i { width: 8px; height: 8px; border-radius: 50%; }
.ff-rings-card b { margin-left: auto; }
.ff-label { font-size: 11px; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); margin: 16px 0 8px; }
.ff-work { width: 100%; display: grid; grid-template-columns: 40px 1fr auto; gap: 10px; align-items: center; padding: 10px; margin-bottom: 8px; border-radius: 18px; background: var(--card) !important; text-align: left; transition: transform .2s, box-shadow .2s; }
.ff-work:hover { transform: translateX(4px); box-shadow: 0 10px 20px -14px rgba(0, 0, 0, .4); }
.ff-dot { width: 40px; height: 40px; border-radius: 14px; display: grid; place-items: center; color: #fff; font-size: 12px; }
.ff-work b { display: block; font-size: 14px; }
.ff-work small { color: var(--muted); font-size: 11px; }
.ff-work em { font-style: normal; font-size: 12px; font-weight: 800; }
.ff-run { display: flex; flex-direction: column; align-items: center; text-align: center; }
.ff-x { align-self: flex-start; width: 32px; height: 32px; border-radius: 50%; background: var(--card) !important; }
.ff-timer { position: relative; width: 190px; height: 190px; margin: 6px 0 14px; }
.ff-timer svg { width: 100%; height: 100%; transform: rotate(-90deg); }
.ff-timer circle { fill: none; stroke-width: 8; stroke-linecap: round; }
.ff-timer .bg { stroke: var(--wc); opacity: .15; }
.ff-timer .fg { stroke: var(--wc); transition: stroke-dashoffset 1s linear; }
.ff-timer b { position: absolute; inset: 0; display: grid; place-items: center; font-size: 56px; font-weight: 800; letter-spacing: -.04em; }
.ff-progress { display: flex; gap: 6px; width: 100%; margin-bottom: 18px; }
.ff-progress i { flex: 1; height: 6px; border-radius: 3px; background: var(--card); transition: background .3s; }
.ff-progress i.on { background: var(--wc); }
.ff-controls { display: grid; gap: 8px; width: 100%; }
.ff-btn { width: 100%; padding: 14px; border-radius: 16px; background: var(--ink) !important; color: var(--bg) !important; font-weight: 800; font-size: 14px; transition: transform .15s; }
.ff-btn:active { transform: scale(.97); }
.ff-btn.ghost { background: var(--card) !important; color: var(--ink) !important; }
.ff-done { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
.ff-burst { font-size: 64px; animation: knDrop .8s cubic-bezier(.34, 1.56, .64, 1); }
.ff-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; width: 100%; margin: 6px 0 20px; }
.ff-stats div { padding: 12px 6px; border-radius: 16px; background: var(--card); }
.ff-stats b { display: block; font-size: 22px; }
.ff-stats small { color: var(--muted); font-size: 11px; }
.ff-phone.is-preview { pointer-events: none; }
</style>
