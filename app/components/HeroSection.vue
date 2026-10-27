<script setup lang="ts">
const { t } = useSite()
const { $motion } = useNuxtApp()

// Split title into words; *word* gets the gradient
const words = computed(() =>
  t.value.hero.title.split(' ').map((w) => {
    const m = w.match(/^\*(.+)\*(.*)$/)
    return m ? { grad: m[1], rest: m[2], text: '' } : { grad: '', rest: '', text: w }
  })
)

// Animated counters
const counts = ref(t.value.hero.stats.map((s) => s.value))
onMounted(() => {
  if ($motion.reduce) return
  const targets = t.value.hero.stats.map((s) => s.value)
  counts.value = targets.map(() => 0)
  setTimeout(() => {
    const start = performance.now()
    const step = (now: number) => {
      const p = Math.min((now - start) / 1600, 1)
      const ease = 1 - Math.pow(1 - p, 3)
      counts.value = targets.map((v) => Math.round(v * ease))
      if (p < 1) requestAnimationFrame(step)
    }
    requestAnimationFrame(step)
  }, 900)
})

// Subtle blob parallax
const blobShift = ref({ x: 0, y: 0 })
function onPointer(e: PointerEvent) {
  if (!$motion.fine) return
  blobShift.value = { x: e.clientX / innerWidth - 0.5, y: e.clientY / innerHeight - 0.5 }
}
const blobStyle = (i: number) => ({ translate: `${blobShift.value.x * (i + 1) * 30}px ${blobShift.value.y * (i + 1) * 30}px` })
</script>

<template>
  <section id="top" class="hero" @pointermove="onPointer">
    <div class="hero-bg" aria-hidden="true">
      <div class="grid-bg" />
      <div v-for="i in 3" :key="i" :class="['blob', `blob-${i}`]" :style="blobStyle(i - 1)" />
    </div>

    <div class="container hero-grid">
      <div class="hero-copy">
        <p class="badge fade-in" style="--d: 0ms"><span class="dot" />{{ t.hero.badge }}</p>
        <h1>
          <template v-for="(w, i) in words" :key="i">
            <span class="word"><span :style="{ '--i': i }"><template v-if="w.grad"><span class="grad">{{ w.grad }}</span>{{ w.rest }}</template><template v-else>{{ w.text }}</template></span></span>{{ ' ' }}
          </template>
        </h1>
        <p class="lead fade-in" style="--d: 600ms">{{ t.hero.subtitle }}</p>
        <div class="hero-cta fade-in" style="--d: 750ms">
          <a v-magnetic class="btn btn-primary" href="#contact">{{ t.hero.ctaPrimary }} <AppIcon name="arrow" /></a>
          <a v-magnetic class="btn btn-ghost" href="#work">{{ t.hero.ctaSecondary }}</a>
        </div>
        <dl class="stats fade-in" style="--d: 900ms">
          <div v-for="(s, i) in t.hero.stats" :key="s.label">
            <dt>{{ counts[i] }}{{ s.suffix }}</dt>
            <dd>{{ s.label }}</dd>
          </div>
        </dl>
      </div>

      <div class="hero-visual fade-in" style="--d: 400ms" aria-hidden="true">
        <div v-tilt class="browser tilt" data-tilt="8">
          <div class="browser-bar"><i /><i /><i /><span>{{ t.hero.visual.url }}</span></div>
          <div class="browser-body">
            <div class="sk-hero"><i class="sk w70" /><i class="sk w90" /><i class="sk w50" /><i class="sk-btn" /></div>
            <div class="sk-chart">
              <svg viewBox="0 0 300 110" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="cg" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="0" stop-color="#5B4BFF" stop-opacity=".35" />
                    <stop offset="1" stop-color="#5B4BFF" stop-opacity="0" />
                  </linearGradient>
                </defs>
                <path class="chart-area" d="M0 95 C40 90 60 70 90 72 S140 50 170 48 220 22 250 25 290 8 300 6 V110 H0Z" fill="url(#cg)" />
                <path class="chart-line" d="M0 95 C40 90 60 70 90 72 S140 50 170 48 220 22 250 25 290 8 300 6" fill="none" stroke="#5B4BFF" stroke-width="3" stroke-linecap="round" />
              </svg>
            </div>
            <div class="sk-row"><span /><span /><span /></div>
          </div>
        </div>
        <div class="chip-float c1"><b>●</b> {{ t.hero.visual.chip1 }}</div>
        <div class="chip-float c2">⚡ {{ t.hero.visual.chip2 }}</div>
        <div class="chip-float c3">✦ {{ t.hero.visual.chip3 }}</div>
      </div>
    </div>
  </section>
</template>
