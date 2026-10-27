<script setup lang="ts">
// Личная страница в стиле «разработчик»: терминал, моноширинный шрифт, сетка активности, превью проектов за курсором
import type { PersonView } from '~/composables/useSite'

const props = defineProps<{ person: PersonView }>()
const { t, cfg, people, projects } = useSite()
const localePath = useLocalePath()
const { $motion } = useNuxtApp()

useHead({
  link: [{ rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&display=swap' }],
})

const p = computed(() => props.person)
const page = computed(() => p.value.page)
const myProjects = computed(() => projects.value.filter((x) => x.author === p.value.id))
const other = computed(() => people.value.find((x) => x.id !== p.value.id))
const email = computed(() => p.value.email || cfg.email)
const year = new Date().getFullYear()

// --- Имя «расшифровывается» из случайных символов
const display = ref(p.value.name)
function scramble() {
  if ($motion.reduce) return
  const target = p.value.name
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#%&*+<>/'
  const total = 36
  let frame = 0
  // setInterval, а не requestAnimationFrame: rAF замирает в фоновой вкладке и имя осталось бы «зашифрованным»
  const id = setInterval(() => {
    frame++
    const done = (frame / total) * target.length
    display.value = target
      .split('')
      .map((c, i) => (c === ' ' || i < done ? c : chars[Math.floor(Math.random() * chars.length)]))
      .join('')
    if (frame >= total) {
      clearInterval(id)
      display.value = target
    }
  }, 40)
}

// --- Терминал с печатью команд
const lines = computed(() => {
  const out: { cmd: boolean; text: string }[] = []
  for (let i = 0; i < p.value.terminal.length; i += 2) {
    out.push({ cmd: true, text: p.value.terminal[i]! }, { cmd: false, text: p.value.terminal[i + 1] ?? '' })
  }
  return out
})
const lineIdx = ref(lines.value.length) // на сервере терминал показан целиком
const charIdx = ref(0)
let timer: ReturnType<typeof setTimeout> | undefined
function typeNext() {
  const line = lines.value[lineIdx.value]
  if (!line) return
  if (line.cmd && charIdx.value < line.text.length) {
    charIdx.value++
    timer = setTimeout(typeNext, 55 + Math.random() * 50)
  } else {
    timer = setTimeout(() => {
      lineIdx.value++
      charIdx.value = 0
      typeNext()
    }, line.cmd ? 260 : 380)
  }
}
const visibleText = (i: number, text: string) => (i < lineIdx.value ? text : i === lineIdx.value ? text.slice(0, charIdx.value) : '')

// --- Сетка активности (детерминированная, чтобы SSR и клиент совпадали)
const cells = Array.from({ length: 7 * 52 }, (_, i) => {
  const col = Math.floor(i / 7)
  const v = (Math.sin(i * 12.9898 + col * 4.1414) * 43758.5453) % 1
  const lvl = Math.abs(v)
  return { col, level: lvl > 0.82 ? 4 : lvl > 0.6 ? 3 : lvl > 0.38 ? 2 : lvl > 0.18 ? 1 : 0 }
})

// --- Превью проекта, которое следует за курсором
const preview = reactive({ active: -1, x: 0, y: 0 })
function onRowMove(e: PointerEvent, i: number) {
  if (!$motion.fine) return
  preview.active = i
  preview.x = e.clientX
  preview.y = e.clientY
}

// --- Копирование e-mail
const copied = ref(false)
async function copyEmail() {
  try {
    await navigator.clipboard.writeText(email.value)
    copied.value = true
    setTimeout(() => (copied.value = false), 2000)
  } catch {
    location.href = `mailto:${email.value}`
  }
}

onMounted(() => {
  scramble()
  if (!$motion.reduce) {
    lineIdx.value = 0
    charIdx.value = 0
    timer = setTimeout(typeNext, 700)
  }
})
onBeforeUnmount(() => clearTimeout(timer))
</script>

<template>
  <div class="pd" :style="{ '--pd-accent': p.colors[0], '--pd-accent-2': p.colors[1] }">
    <a class="skip-link" href="#pd-main">{{ t.skip }}</a>

    <header class="pd-top">
      <div class="container pd-top-inner">
        <NuxtLink class="pd-back" :to="localePath('/')"><AppIcon name="back" /> {{ cfg.brand }}</NuxtLink>
        <span class="pd-path" aria-hidden="true">~/{{ p.slug }}</span>
        <LangSwitch />
      </div>
    </header>

    <main id="pd-main">
      <section class="pd-hero container">
        <div class="pd-hero-copy">
          <p class="pd-status fade-in"><span class="pd-dot" />{{ t.personal.available }}</p>
          <p class="pd-hello fade-in" style="--d: 100ms">{{ t.personal.hello }}</p>
          <h1 class="pd-name fade-in" style="--d: 150ms" :aria-label="p.name">
            <span aria-hidden="true">{{ display }}</span><span class="pd-caret" aria-hidden="true">_</span>
          </h1>
          <p class="pd-headline fade-in" style="--d: 350ms">{{ page.headline }}</p>
          <p class="pd-intro fade-in" style="--d: 450ms">{{ page.intro }}</p>
          <div class="pd-cta fade-in" style="--d: 550ms">
            <a v-magnetic class="btn btn-primary" href="#pd-contact">{{ t.personal.contact }} <AppIcon name="arrow" /></a>
            <a v-if="p.links.github" v-magnetic class="btn btn-ghost" :href="p.links.github" target="_blank" rel="noopener">
              <AppIcon name="github" /> GitHub
            </a>
          </div>
        </div>

        <div v-if="lines.length" class="pd-terminal fade-in" style="--d: 300ms" aria-hidden="true">
          <div class="pd-term-bar"><i /><i /><i /><span>zsh — {{ p.slug }}</span></div>
          <div class="pd-term-body">
            <p v-for="(l, i) in lines" :key="i" :class="l.cmd ? 'cmd' : 'out'">
              <template v-if="l.cmd"><b>➜</b> <em>~</em> </template>{{ visibleText(i, l.text) }}<span v-if="i === lineIdx" class="pd-cursor" />
            </p>
            <p v-if="lineIdx >= lines.length" class="cmd"><b>➜</b> <em>~</em> <span class="pd-cursor" /></p>
          </div>
        </div>
      </section>

      <section class="container pd-activity" aria-hidden="true">
        <p class="pd-label">$ git log --since={{ year - 1 }}</p>
        <div class="pd-grid">
          <i v-for="(c, i) in cells" :key="i" :class="`l${c.level}`" :style="{ '--c': c.col }" />
        </div>
      </section>

      <section class="container pd-section pd-about">
        <h2 v-reveal class="pd-h2"><span>01.</span> {{ t.personal.about }}</h2>
        <div class="pd-about-grid">
          <div class="pd-bio">
            <p v-for="(b, i) in page.bio" :key="i" v-reveal :style="{ '--d': `${i * 100}ms` }">{{ b }}</p>
          </div>
          <dl v-reveal class="pd-facts" style="--d: 150ms">
            <div v-for="f in page.facts" :key="f.k">
              <dt>{{ f.k }}</dt>
              <dd>{{ f.v }}</dd>
            </div>
          </dl>
        </div>
      </section>

      <section class="container pd-section">
        <h2 v-reveal class="pd-h2"><span>02.</span> {{ t.personal.stack }}</h2>
        <ul class="pd-stack">
          <li v-for="(s, i) in p.skills" :key="s" v-reveal :style="{ '--d': `${i * 50}ms` }">
            <span>{{ String(i + 1).padStart(2, '0') }}</span>{{ s }}
          </li>
        </ul>
      </section>

      <section class="container pd-section">
        <h2 v-reveal class="pd-h2"><span>03.</span> {{ t.personal.projects }}</h2>
        <ol class="pd-projects" @pointerleave="preview.active = -1">
          <li
            v-for="(pr, i) in myProjects"
            :key="pr.id"
            v-reveal
            class="pd-row"
            :style="{ '--d': `${i * 60}ms` }"
            @pointermove="onRowMove($event, i)"
          >
            <span class="pd-idx">{{ String(i + 1).padStart(2, '0') }}</span>
            <div class="pd-row-thumb">
              <ProjectMock :image="pr.image" :title="pr.title" :layout="pr.layout" :tags="pr.tags" :style="{ '--c1': pr.colors[0], '--c2': pr.colors[1] }" />
            </div>
            <div class="pd-row-main">
              <h3>{{ pr.title }}</h3>
              <p>{{ pr.desc }}</p>
              <ul class="pd-tags"><li v-for="tag in pr.tags" :key="tag">{{ tag }}</li></ul>
            </div>
            <div class="pd-row-side">
              <span class="pd-year">{{ pr.year }}</span>
              <a v-if="pr.url" :href="pr.url" target="_blank" rel="noopener">{{ t.work.live }} ↗</a>
              <a v-if="pr.repo" :href="pr.repo" target="_blank" rel="noopener">{{ t.work.code }} ↗</a>
            </div>
          </li>
        </ol>
      </section>

      <section class="container pd-section">
        <h2 v-reveal class="pd-h2"><span>04.</span> {{ t.personal.journey }}</h2>
        <ol v-reveal class="pd-timeline">
          <li v-for="(item, i) in page.timeline" :key="i" :style="{ '--d': `${i * 150}ms` }">
            <span class="pd-when">{{ item.year }}</span>
            <h3>{{ item.title }}</h3>
            <p>{{ item.text }}</p>
          </li>
        </ol>
      </section>

      <section id="pd-contact" class="container pd-section pd-contact">
        <div v-reveal class="pd-contact-card">
          <p class="pd-label">$ mail --to {{ p.shortName.toLowerCase() }}</p>
          <h2>{{ t.personal.contact }}</h2>
          <p class="pd-intro">{{ t.personal.contactText }}</p>
          <div class="pd-mail">
            <a :href="`mailto:${email}`">{{ email }}</a>
            <button type="button" class="btn btn-ghost btn-sm" @click="copyEmail">
              <AppIcon name="copy" /> {{ copied ? t.personal.copied : t.personal.copy }}
            </button>
          </div>
        </div>
      </section>
    </main>

    <footer class="container pd-footer">
      <p>© {{ year }} {{ p.name }} · <NuxtLink :to="localePath('/')">{{ cfg.brand }}</NuxtLink></p>
      <NuxtLink v-if="other" class="pd-other" :to="localePath(`/${other.slug}`)">
        {{ t.personal.also }} {{ other.shortName }} →
      </NuxtLink>
    </footer>

    <!-- Превью проекта за курсором (только мышь) -->
    <div
      class="pd-preview"
      :class="{ on: preview.active > -1 }"
      :style="{ transform: `translate(${preview.x + 24}px, ${preview.y - 90}px)` }"
      aria-hidden="true"
    >
      <template v-for="(pr, i) in myProjects" :key="pr.id">
        <ProjectMock
          v-show="preview.active === i"
          :image="pr.image"
          :title="pr.title"
          :layout="pr.layout"
          :tags="pr.tags"
          :style="{ '--c1': pr.colors[0], '--c2': pr.colors[1] }"
        />
      </template>
    </div>
  </div>
</template>

<style>
.pd {
  --mono: 'JetBrains Mono', ui-monospace, Consolas, monospace;
  min-height: 100vh; background-color: #F7F8FB; color: var(--ink);
  background-image: radial-gradient(rgba(18, 18, 22, .09) 1px, transparent 1px);
  background-size: 22px 22px;
}
.pd-top { position: sticky; top: 0; z-index: 40; background: rgba(247, 248, 251, .8); -webkit-backdrop-filter: blur(12px); backdrop-filter: blur(12px); border-bottom: 1px solid var(--line); }
.pd-top-inner { display: flex; align-items: center; justify-content: space-between; gap: 16px; height: 64px; }
.pd-back { display: inline-flex; align-items: center; gap: 8px; font-weight: 700; padding: 8px 14px 8px 10px; border-radius: 999px; transition: background .25s; }
.pd-back:hover { background: var(--bg-2); }
.pd-path { font-family: var(--mono); font-size: .85rem; color: var(--muted); }

.pd-hero { display: grid; grid-template-columns: 1.1fr .9fr; gap: 48px; align-items: center; padding-block: clamp(56px, 9vw, 110px) 40px; }
.pd-status { display: inline-flex; align-items: center; gap: 10px; font-family: var(--mono); font-size: .85rem; color: #15803D; background: #DCFCE7; padding: 6px 14px; border-radius: 999px; }
.pd-dot { width: 8px; height: 8px; border-radius: 50%; background: #22C55E; animation: pulse 2s infinite; }
.pd-hello { margin-top: 28px; font-family: var(--mono); color: var(--muted); }
.pd-name {
  font-family: var(--font-display); font-weight: 600; font-size: clamp(2.4rem, 6.4vw, 5.2rem); line-height: 1.02; letter-spacing: -.04em;
  margin: 6px 0 22px; overflow-wrap: anywhere;
}
.pd-caret { color: var(--pd-accent); animation: blink 1s steps(1) infinite; }
@keyframes blink { 50% { opacity: 0; } }
.pd-headline { font-size: clamp(1.2rem, 2vw, 1.5rem); font-weight: 700; max-width: 560px; line-height: 1.35; }
.pd-intro { color: var(--ink-2); margin-top: 14px; max-width: 560px; }
.pd-cta { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 30px; }
.pd .btn-primary:hover { background: var(--pd-accent); }

.pd-terminal { border-radius: 18px; background: #fff; border: 1px solid var(--line-2); box-shadow: var(--shadow-lg); overflow: hidden; font-family: var(--mono); font-size: .92rem; }
.pd-term-bar { display: flex; align-items: center; gap: 6px; padding: 12px 14px; background: #F3F4F6; border-bottom: 1px solid var(--line); }
.pd-term-bar i { width: 11px; height: 11px; border-radius: 50%; background: #FF8A7A; }
.pd-term-bar i:nth-child(2) { background: #FFC960; }
.pd-term-bar i:nth-child(3) { background: #5ED39A; }
.pd-term-bar span { margin: 0 auto; font-size: .75rem; color: var(--muted); transform: translateX(-20px); }
.pd-term-body { padding: 20px 22px 24px; min-height: 290px; line-height: 1.9; }
.pd-term-body .cmd b { color: #16A34A; }
.pd-term-body .cmd em { color: var(--pd-accent); font-style: normal; font-weight: 700; }
.pd-term-body .out { color: var(--ink-2); padding-left: 1.6em; }
.pd-cursor { display: inline-block; width: .6em; height: 1.1em; margin-left: 2px; vertical-align: -3px; background: var(--pd-accent); animation: blink 1s steps(1) infinite; }

.pd-activity { padding-bottom: 20px; }
.pd-label { font-family: var(--mono); font-size: .82rem; color: var(--muted); margin-bottom: 12px; }
.pd-grid {
  display: grid; grid-auto-flow: column; grid-template-rows: repeat(7, 14px); grid-auto-columns: 14px; gap: 4px;
  overflow: hidden; padding: 18px; border-radius: 16px; background: #fff; border: 1px solid var(--line); width: max-content; max-width: 100%;
}
.pd-grid i { border-radius: 3px; background: #E8EAEF; animation: cell 3.6s ease-in-out infinite; animation-delay: calc(var(--c) * 90ms); }
.pd-grid i.l1 { background: color-mix(in srgb, var(--pd-accent) 22%, #fff); }
.pd-grid i.l2 { background: color-mix(in srgb, var(--pd-accent) 45%, #fff); }
.pd-grid i.l3 { background: color-mix(in srgb, var(--pd-accent) 70%, #fff); }
.pd-grid i.l4 { background: var(--pd-accent); }
@keyframes cell { 0%, 70%, 100% { transform: none; } 80% { transform: scale(.6); } 90% { transform: scale(1.1); } }

.pd-section { padding-block: clamp(56px, 8vw, 96px) 0; }
.pd-h2 { font-family: var(--font-display); font-weight: 600; font-size: clamp(1.7rem, 3.6vw, 2.6rem); letter-spacing: -.03em; margin-bottom: 32px; display: flex; align-items: baseline; gap: 14px; }
.pd-h2 span { font-family: var(--mono); font-size: .5em; color: var(--pd-accent); letter-spacing: 0; }

.pd-about-grid { display: grid; grid-template-columns: 1.4fr 1fr; gap: 40px; align-items: start; }
.pd-bio p { font-size: 1.08rem; color: var(--ink-2); }
.pd-bio p + p { margin-top: 16px; }
.pd-facts { border-radius: 18px; background: #fff; border: 1px solid var(--line); overflow: hidden; font-family: var(--mono); font-size: .9rem; }
.pd-facts div { display: grid; grid-template-columns: 120px 1fr; gap: 12px; padding: 14px 18px; }
.pd-facts div + div { border-top: 1px dashed var(--line-2); }
.pd-facts dt { color: var(--muted); }
.pd-facts dd { font-weight: 600; }

.pd-stack { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 10px; }
.pd-stack li {
  display: flex; align-items: center; gap: 12px; padding: 16px 18px; border-radius: 14px; background: #fff; border: 1px solid var(--line);
  font-weight: 700; transition: transform .3s var(--ease), border-color .3s, box-shadow .3s;
}
.pd-stack li span { font-family: var(--mono); font-size: .75rem; color: var(--pd-accent); }
.pd-stack li:hover { transform: translateY(-4px); border-color: var(--pd-accent); box-shadow: 0 10px 30px -14px var(--pd-accent); }

.pd-projects { border-top: 1px solid var(--line-2); }
.pd-row {
  position: relative; display: grid; grid-template-columns: 48px 1fr auto; gap: 20px; align-items: start; padding: 26px 8px;
  border-bottom: 1px solid var(--line-2); transition: background .3s, padding .4s var(--ease);
}
.pd-row:hover { background: #fff; padding-left: 18px; }
.pd-row-thumb { display: none; }
.pd-idx { font-family: var(--mono); color: var(--muted); padding-top: 4px; }
.pd-row-main h3 { font-family: var(--font-display); font-weight: 600; font-size: clamp(1.2rem, 2.4vw, 1.7rem); letter-spacing: -.02em; transition: color .3s; }
.pd-row:hover .pd-row-main h3 { color: var(--pd-accent); }
.pd-row-main p { color: var(--ink-2); margin-top: 6px; max-width: 640px; }
.pd-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; }
.pd-tags li { font-family: var(--mono); font-size: .75rem; padding: 3px 9px; border-radius: 6px; background: var(--bg-2); color: var(--ink-2); }
.pd-row-side { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; font-family: var(--mono); font-size: .85rem; }
.pd-year { color: var(--muted); }
.pd-row-side a { font-weight: 700; padding: 4px 10px; border-radius: 8px; transition: background .25s, color .25s; }
.pd-row-side a:hover { background: var(--ink); color: #fff; }

.pd-preview {
  position: fixed; top: 0; left: 0; z-index: 60; width: 340px; pointer-events: none; border-radius: 16px; overflow: hidden;
  box-shadow: 0 30px 70px -20px rgba(18, 18, 22, .45); opacity: 0; scale: .85; rotate: -3deg;
  transition: opacity .3s, scale .4s var(--ease), rotate .4s var(--ease), transform .18s linear;
}
.pd-preview.on { opacity: 1; scale: 1; rotate: 0deg; }
.pd-preview .mock { border-radius: 0; }

.pd-timeline { position: relative; display: grid; gap: 28px; padding-left: 28px; }
.pd-timeline::before {
  content: ''; position: absolute; left: 6px; top: 6px; bottom: 6px; width: 2px; background: linear-gradient(var(--pd-accent), var(--pd-accent-2));
  transform-origin: top; transform: scaleY(0); transition: transform 1.4s var(--ease);
}
.js .pd-timeline[data-reveal] { opacity: 1; transform: none; }
.pd-timeline.is-in::before, html:not(.js) .pd-timeline::before { transform: none; }
.pd-timeline li { position: relative; }
.js .pd-timeline[data-reveal] li { opacity: 0; transform: translateX(-16px); transition: opacity .7s var(--ease), transform .7s var(--ease); transition-delay: calc(var(--d) + 300ms); }
.js .pd-timeline.is-in li { opacity: 1; transform: none; }
.pd-timeline li::before { content: ''; position: absolute; left: -28px; top: 6px; width: 14px; height: 14px; border-radius: 50%; background: #fff; border: 3px solid var(--pd-accent); }
.pd-when { font-family: var(--mono); font-size: .82rem; color: var(--pd-accent); font-weight: 700; }
.pd-timeline h3 { margin: 2px 0 4px; }
.pd-timeline p { color: var(--ink-2); max-width: 680px; }

.pd-contact { padding-bottom: 40px; }
.pd-contact-card { padding: clamp(28px, 5vw, 56px); border-radius: 28px; background: #fff; border: 1px solid var(--line); box-shadow: var(--shadow-lg); }
.pd-contact-card h2 { font-family: var(--font-display); font-weight: 600; font-size: clamp(2rem, 5vw, 3.6rem); letter-spacing: -.04em; }
.pd-mail { display: flex; flex-wrap: wrap; align-items: center; gap: 14px; margin-top: 26px; }
.pd-mail a { font-family: var(--mono); font-weight: 700; font-size: clamp(1rem, 2.6vw, 1.6rem); color: var(--pd-accent); border-bottom: 2px solid currentColor; overflow-wrap: anywhere; }

.pd-footer { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 12px; padding-block: 32px 40px; font-family: var(--mono); font-size: .85rem; color: var(--muted); }
.pd-footer a:hover, .pd-other { color: var(--ink); font-weight: 700; }
.pd-other:hover { color: var(--pd-accent); }

@media (max-width: 960px) {
  .pd-hero, .pd-about-grid { grid-template-columns: 1fr; }
  .pd-path { display: none; }
}
@media (hover: none), (max-width: 720px) {
  .pd-preview { display: none; }
  .pd-row { grid-template-columns: 1fr; gap: 12px; }
  .pd-idx { display: none; }
  .pd-row-thumb { display: block; }
  .pd-row-side { flex-direction: row; align-items: center; }
}
</style>
