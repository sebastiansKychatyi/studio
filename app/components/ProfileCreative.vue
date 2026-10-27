<script setup lang="ts">
// Личная страница в «креативном» стиле: крупная антиква, стикеры, плавающие фигуры, курсор-капля
import type { PersonView } from '~/composables/useSite'

const props = defineProps<{ person: PersonView }>()
const { t, cfg, people, projects } = useSite()
const localePath = useLocalePath()
const { $motion } = useNuxtApp()
const { show } = useDesignModal()

useHead({
  link: [{ rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,800;1,600;1,800&display=swap' }],
})

const p = computed(() => props.person)
const page = computed(() => p.value.page)
const myProjects = computed(() => projects.value.filter((x) => x.author === p.value.id))
const other = computed(() => people.value.find((x) => x.id !== p.value.id))
const email = computed(() => p.value.email || cfg.email)
const letters = computed(() => p.value.shortName.split(''))
const year = new Date().getFullYear()
const palette = ['#FF7A59', '#FFC94A', '#B9A8FF', '#9BE7C4']

// Параллакс фигур и курсор-капля
const mouse = reactive({ x: 0, y: 0, px: 0, py: 0, on: false })
function onMove(e: PointerEvent) {
  if (!$motion.fine) return
  mouse.on = true
  mouse.x = e.clientX
  mouse.y = e.clientY
  mouse.px = e.clientX / innerWidth - 0.5
  mouse.py = e.clientY / innerHeight - 0.5
}
const shift = (k: number) => ({ translate: `${mouse.px * k}px ${mouse.py * k}px` })

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
</script>

<template>
  <div class="pc" @pointermove="onMove" @pointerleave="mouse.on = false">
    <a class="skip-link" href="#pc-main">{{ t.skip }}</a>

    <header class="pc-top container">
      <NuxtLink class="pc-back" :to="localePath('/')"><AppIcon name="back" /> {{ cfg.brand }}</NuxtLink>
      <span class="pc-mark" aria-hidden="true">{{ p.shortName }}<i>.</i></span>
      <LangSwitch />
    </header>

    <main id="pc-main">
      <section class="pc-hero container">
        <div class="pc-shapes" aria-hidden="true">
          <span class="pc-shape s-circle" :style="shift(40)" />
          <span class="pc-shape s-pill" :style="shift(-30)" />
          <svg class="pc-shape s-star" :style="shift(60)" viewBox="0 0 100 100"><path d="M50 0 61 39 100 50 61 61 50 100 39 61 0 50 39 39Z" /></svg>
          <svg class="pc-shape s-squiggle" :style="shift(-50)" viewBox="0 0 200 40"><path d="M2 20 Q 27 0 52 20 T 102 20 T 152 20 T 198 20" /></svg>
        </div>

        <p class="pc-hello fade-in">{{ t.personal.hello }}</p>
        <h1 class="pc-name" :aria-label="p.name">
          <span v-for="(ch, i) in letters" :key="i" class="pc-letter" :style="{ '--i': i }" aria-hidden="true">{{ ch }}</span>
        </h1>
        <p class="pc-headline fade-in" style="--d: 500ms">{{ page.headline }}</p>
        <NuxtLink class="pc-cv fade-in" style="--d: 650ms" :to="localePath(`/${p.slug}/cv`)"><AppIcon name="doc" /> {{ t.personal.cv.open }}</NuxtLink>

        <a href="#pc-contact" class="pc-sticker fade-in" style="--d: 700ms" :aria-label="t.personal.sayHi">
          <svg viewBox="0 0 200 200" aria-hidden="true">
            <defs><path id="pc-circle" d="M100,100 m-78,0 a78,78 0 1,1 156,0 a78,78 0 1,1 -156,0" /></defs>
            <text><textPath href="#pc-circle">{{ t.personal.sticker.repeat(2) }}</textPath></text>
          </svg>
          <span>✺</span>
        </a>
      </section>

      <div class="pc-band" aria-hidden="true">
        <div class="pc-band-track">
          <template v-for="n in 2" :key="n">
            <template v-for="s in p.skills" :key="`${n}-${s}`"><span>{{ s }}</span><i>✦</i></template>
          </template>
        </div>
      </div>

      <section class="container pc-section pc-about">
        <p v-reveal class="pc-kicker">{{ t.personal.about }}</p>
        <p v-reveal class="pc-statement" style="--d: 80ms"><mark>{{ page.intro }}</mark></p>
        <div class="pc-about-grid">
          <div class="pc-bio">
            <p v-for="(b, i) in page.bio" :key="i" v-reveal :style="{ '--d': `${i * 100}ms` }">{{ b }}</p>
          </div>
          <ul class="pc-facts">
            <li
              v-for="(f, i) in page.facts"
              :key="f.k"
              v-reveal
              :style="{ '--d': `${i * 120}ms`, '--bg': palette[i % palette.length], '--rot': `${i % 2 ? 3 : -3}deg` }"
            >
              <small>{{ f.k }}</small>
              <strong>{{ f.v }}</strong>
            </li>
          </ul>
        </div>
      </section>

      <section class="container pc-section">
        <p v-reveal class="pc-kicker">{{ t.personal.projects }}</p>
        <div class="pc-projects">
          <article
            v-for="(pr, i) in myProjects"
            :key="pr.id"
            v-reveal
            class="pc-project"
            :style="{ '--d': `${(i % 2) * 120}ms`, '--rot': `${i % 2 ? 2 : -2}deg`, '--tag': palette[i % palette.length] }"
          >
            <component
              :is="pr.prototype ? 'button' : pr.url || pr.repo ? 'a' : 'div'"
              v-bind="pr.prototype ? { type: 'button', 'aria-label': `${t.work.proto.open}: ${pr.title}` } : pr.url || pr.repo ? { href: pr.url || pr.repo, target: '_blank', rel: 'noopener' } : {}"
              class="pc-project-inner"
              @click="pr.prototype && show(pr.id)"
            >
              <div class="pc-cover" :style="{ '--c1': pr.colors[0], '--c2': pr.colors[1] }">
                <ProjectMock :image="pr.image" :title="pr.title" :layout="pr.layout" :tags="pr.tags" :prototype="pr.prototype" />
                <span v-if="pr.prototype" class="pc-play">▶ {{ t.work.proto.open }}</span>
                <span v-if="pr.placeholder" class="pc-demo">{{ t.work.demo }}</span>
              </div>
              <div class="pc-project-info">
                <span class="pc-year">{{ pr.year }}</span>
                <h3>{{ pr.title }}</h3>
                <p>{{ pr.desc }}</p>
                <ul><li v-for="tag in pr.tags" :key="tag">{{ tag }}</li></ul>
              </div>
            </component>
          </article>
        </div>
      </section>

      <section class="container pc-section">
        <p v-reveal class="pc-kicker">{{ t.personal.journey }}</p>
        <ol class="pc-chapters">
          <li v-for="(item, i) in page.timeline" :key="i" v-reveal :style="{ '--d': `${i * 120}ms` }">
            <span class="pc-num">{{ String(i + 1).padStart(2, '0') }}</span>
            <div>
              <small>{{ item.year }}</small>
              <h3>{{ item.title }}</h3>
              <p>{{ item.text }}</p>
            </div>
          </li>
        </ol>
      </section>

      <section id="pc-contact" class="container pc-section pc-contact">
        <h2 v-reveal class="pc-big">{{ t.personal.sayHi }}<em>!</em></h2>
        <p v-reveal class="pc-contact-text" style="--d: 100ms">{{ t.personal.contactText }}</p>
        <div v-reveal class="pc-contact-actions" style="--d: 200ms">
          <a v-magnetic class="pc-blob-btn" :href="`mailto:${email}`">{{ email }}</a>
          <button type="button" class="pc-copy" @click="copyEmail"><AppIcon name="copy" /> {{ copied ? t.personal.copied : t.personal.copy }}</button>
        </div>
      </section>
    </main>

    <footer class="container pc-footer">
      <p>© {{ year }} {{ p.name }} · <NuxtLink :to="localePath('/')">{{ cfg.brand }}</NuxtLink></p>
      <NuxtLink v-if="other" class="pc-other" :to="localePath(`/${other.slug}`)">{{ t.personal.also }} {{ other.shortName }} →</NuxtLink>
    </footer>

    <div class="pc-cursor" :class="{ on: mouse.on }" :style="{ transform: `translate(${mouse.x}px, ${mouse.y}px)` }" aria-hidden="true" />
  </div>
</template>

<style>
.pc {
  --serif: 'Playfair Display', Georgia, 'Times New Roman', serif;
  --cream: #FFF7EE; --coral: #FF7A59; --sun: #FFC94A; --lilac: #B9A8FF; --mint: #9BE7C4;
  min-height: 100vh; background: var(--cream); color: #1B1B1B; overflow-x: clip; position: relative;
}
.pc-top { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding-block: 18px; position: relative; z-index: 5; }
.pc-back { display: inline-flex; align-items: center; gap: 8px; font-weight: 700; padding: 8px 16px 8px 12px; border-radius: 999px; border: 1.5px solid #1B1B1B; transition: background .25s, color .25s; }
.pc-back:hover { background: #1B1B1B; color: var(--cream); }
.pc-mark { font-family: var(--serif); font-style: italic; font-weight: 800; font-size: 1.5rem; }
.pc-mark i { color: var(--coral); }
.pc .lang-switch { background: #fff; border: 1.5px solid #1B1B1B; }

.pc-hero { position: relative; padding-block: clamp(48px, 9vw, 120px) clamp(60px, 9vw, 120px); }
.pc-hello { font-family: var(--serif); font-style: italic; font-size: clamp(1.3rem, 2.4vw, 2rem); }
.pc-name {
  font-family: var(--serif); font-weight: 800; font-style: italic; line-height: .9; letter-spacing: -.04em;
  font-size: clamp(4.5rem, 17vw, 13.5rem); margin: 8px 0 26px; position: relative; z-index: 2;
}
.pc-letter { display: inline-block; }
.js .pc-letter { opacity: 0; transform: translateY(60%) rotate(8deg); animation: letterIn .9s cubic-bezier(.34, 1.56, .64, 1) forwards; animation-delay: calc(var(--i) * 70ms + 150ms); }
.pc-letter:nth-child(4n + 1) { color: #1B1B1B; }
.pc-letter:nth-child(4n + 2) { color: var(--coral); }
.pc-letter:hover { animation: wiggle .5s; }
@keyframes letterIn { to { opacity: 1; transform: none; } }
@keyframes wiggle { 30% { transform: rotate(-10deg) scale(1.1); } 60% { transform: rotate(6deg); } }
.pc-headline { font-family: var(--serif); font-size: clamp(1.4rem, 3vw, 2.4rem); line-height: 1.2; max-width: 760px; position: relative; z-index: 2; }

.pc-cv {
  position: relative; z-index: 2; display: inline-flex; align-items: center; gap: 8px; margin-top: 28px; padding: 14px 24px;
  border-radius: 999px; background: #fff; border: 2px solid #1B1B1B; box-shadow: 4px 4px 0 #1B1B1B; font-weight: 800;
  transition: transform .3s cubic-bezier(.34, 1.56, .64, 1), box-shadow .3s, background .3s;
}
.pc-cv:hover { transform: translate(-2px, -2px); box-shadow: 6px 6px 0 #1B1B1B; background: var(--sun); }
.pc-shapes { position: absolute; inset: 0; pointer-events: none; }
.pc-shape { position: absolute; transition: translate .6s cubic-bezier(.2, .8, .2, 1); }
.s-circle { width: clamp(120px, 18vw, 240px); aspect-ratio: 1; border-radius: 50%; background: var(--sun); right: 6%; top: 8%; animation: spinSlow 30s linear infinite; }
.s-circle::after { content: ''; position: absolute; inset: 22%; border-radius: 50%; border: 2px dashed #1B1B1B; }
.s-pill { width: clamp(90px, 12vw, 160px); height: clamp(40px, 5vw, 64px); border-radius: 999px; background: var(--lilac); right: 26%; bottom: 14%; rotate: -18deg; animation: bob 7s ease-in-out infinite; }
.s-star { width: clamp(50px, 7vw, 90px); fill: var(--coral); right: 30%; top: 4%; animation: spinSlow 14s linear infinite reverse; }
.s-squiggle { width: clamp(120px, 16vw, 200px); fill: none; stroke: var(--mint); stroke-width: 7; stroke-linecap: round; left: 52%; bottom: 4%; }
@keyframes spinSlow { to { rotate: 360deg; } }

.pc-sticker {
  position: absolute; right: 8%; bottom: 6%; z-index: 3; width: clamp(120px, 14vw, 170px); aspect-ratio: 1; display: grid; place-items: center;
  border-radius: 50%; background: #1B1B1B; color: var(--cream); transition: transform .5s cubic-bezier(.34, 1.56, .64, 1), background .3s;
}
.pc-sticker:hover { transform: scale(1.1) rotate(-8deg); background: var(--coral); }
.pc-sticker svg { position: absolute; inset: 0; width: 100%; height: 100%; animation: spinSlow 16s linear infinite; }
.pc-sticker text { font: 700 15px/1 var(--font); letter-spacing: 3px; fill: currentColor; }
.pc-sticker > span { font-size: 2.2rem; color: var(--sun); }

.pc-band { background: var(--coral); color: #1B1B1B; rotate: -2deg; margin: 0 -20px; padding: 18px 0; overflow: hidden; border-block: 2px solid #1B1B1B; }
.pc-band-track { display: flex; width: max-content; gap: 28px; align-items: center; animation: marquee 30s linear infinite; }
.pc-band span { font-family: var(--serif); font-style: italic; font-weight: 800; font-size: clamp(1.6rem, 3.5vw, 2.8rem); }
.pc-band i { font-style: normal; font-size: 1.4rem; }

.pc-section { padding-block: clamp(70px, 10vw, 130px) 0; }
.pc-kicker { display: inline-block; padding: 6px 16px; border-radius: 999px; background: #1B1B1B; color: var(--cream); font-weight: 800; font-size: .85rem; letter-spacing: .1em; text-transform: uppercase; margin-bottom: 26px; }
.pc-statement { font-family: var(--serif); font-size: clamp(1.7rem, 4vw, 3.2rem); line-height: 1.2; max-width: 1000px; }
.pc-statement mark {
  background: linear-gradient(transparent 62%, var(--sun) 62%) no-repeat 0 0 / 0% 100%; color: inherit;
  transition: background-size 1.4s cubic-bezier(.2, .8, .2, 1) .4s;
}
.pc-statement.is-in mark, html:not(.js) .pc-statement mark { background-size: 100% 100%; }
.pc-about-grid { display: grid; grid-template-columns: 1.3fr 1fr; gap: 48px; margin-top: 48px; align-items: start; }
.pc-bio p { font-size: 1.1rem; }
.pc-bio p + p { margin-top: 16px; }
.pc-facts { display: grid; gap: 16px; }
.pc-facts li { padding: 18px 22px; border-radius: 20px; background: var(--bg); border: 2px solid #1B1B1B; box-shadow: 5px 5px 0 #1B1B1B; }
.js .pc-facts li[data-reveal].is-in, html:not(.js) .pc-facts li { transform: rotate(var(--rot)); }
.pc-facts li:hover { transform: rotate(0) scale(1.03) !important; }
.pc-facts li { transition: transform .5s cubic-bezier(.34, 1.56, .64, 1), opacity .9s; }
.pc-facts small { display: block; font-weight: 800; text-transform: uppercase; letter-spacing: .08em; font-size: .75rem; }
.pc-facts strong { font-family: var(--serif); font-size: 1.5rem; }

.pc-projects { display: grid; grid-template-columns: repeat(2, 1fr); gap: 40px 32px; }
.pc-project-inner { display: block; border-radius: 28px; background: #fff; border: 2px solid #1B1B1B; box-shadow: 8px 8px 0 #1B1B1B; overflow: hidden; transition: transform .5s cubic-bezier(.34, 1.56, .64, 1), box-shadow .4s; }
.js .pc-project[data-reveal].is-in .pc-project-inner, html:not(.js) .pc-project-inner { transform: rotate(var(--rot)); }
.pc-project:hover .pc-project-inner { transform: rotate(0) translateY(-6px) !important; box-shadow: 12px 14px 0 #1B1B1B; }
.pc-project:nth-child(even) { margin-top: 60px; }
.pc-cover { position: relative; border-bottom: 2px solid #1B1B1B; }
.pc-cover .mock { border-radius: 0; }
.pc-project-inner { width: 100%; padding: 0; font: inherit; color: inherit; text-align: left; cursor: pointer; }
.pc-play { position: absolute; right: 14px; bottom: 14px; padding: 8px 14px; border-radius: 999px; background: #1B1B1B; color: var(--cream); font-weight: 800; font-size: .85rem; transition: background .3s, transform .3s; }
.pc-project:hover .pc-play { background: var(--coral); transform: scale(1.05); }
.pc-demo { position: absolute; top: 14px; left: 14px; padding: 4px 12px; border-radius: 999px; background: var(--sun); border: 2px solid #1B1B1B; font-weight: 800; font-size: .75rem; text-transform: uppercase; }
.pc-project-info { padding: 22px 24px 26px; }
.pc-year { display: inline-block; padding: 2px 10px; border-radius: 999px; background: var(--tag); border: 1.5px solid #1B1B1B; font-weight: 800; font-size: .8rem; }
.pc-project-info h3 { font-family: var(--serif); font-style: italic; font-weight: 800; font-size: 1.9rem; margin: 10px 0 6px; }
.pc-project-info ul { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 14px; }
.pc-project-info li { padding: 4px 10px; border-radius: 999px; border: 1.5px solid #1B1B1B; font-size: .78rem; font-weight: 700; }

.pc-chapters { display: grid; gap: 0; border-top: 2px solid #1B1B1B; }
.pc-chapters li { display: grid; grid-template-columns: 140px 1fr; gap: 24px; padding: 28px 0; border-bottom: 2px solid #1B1B1B; }
.pc-num { font-family: var(--serif); font-style: italic; font-weight: 800; font-size: clamp(3rem, 7vw, 5.5rem); line-height: .9; color: transparent; -webkit-text-stroke: 2px #1B1B1B; transition: color .4s; }
.pc-chapters li:hover .pc-num { color: var(--coral); }
.pc-chapters small { font-weight: 800; letter-spacing: .08em; }
.pc-chapters h3 { font-family: var(--serif); font-size: 1.7rem; margin: 4px 0; }

.pc-contact { text-align: center; padding-bottom: 60px; }
.pc-big { font-family: var(--serif); font-style: italic; font-weight: 800; font-size: clamp(3rem, 10vw, 8rem); line-height: .95; letter-spacing: -.04em; }
.pc-big em { color: var(--coral); }
.pc-contact-text { font-size: 1.15rem; max-width: 560px; margin: 20px auto 0; }
.pc-contact-actions { display: flex; flex-direction: column; align-items: center; gap: 14px; margin-top: 36px; }
.pc-blob-btn {
  --mx: 0px; --my: 0px;
  display: inline-block; padding: 26px 40px; border-radius: 60% 40% 55% 45% / 50% 60% 40% 50%; background: var(--coral); border: 2px solid #1B1B1B;
  font-weight: 800; font-size: clamp(1rem, 2.6vw, 1.5rem); overflow-wrap: anywhere;
  transform: translate(var(--mx), var(--my)); transition: transform .35s cubic-bezier(.2, .8, .2, 1), border-radius .8s, background .3s;
  animation: morph 8s ease-in-out infinite;
}
.pc-blob-btn:hover { background: var(--sun); }
@keyframes morph { 50% { border-radius: 40% 60% 45% 55% / 60% 40% 60% 40%; } }
.pc-copy { display: inline-flex; align-items: center; gap: 8px; border: 0; background: none; font-weight: 700; cursor: pointer; text-decoration: underline; text-underline-offset: 4px; }

.pc-footer { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 12px; padding-block: 28px 40px; border-top: 2px solid #1B1B1B; font-weight: 600; }
.pc-other { font-family: var(--serif); font-style: italic; font-weight: 800; font-size: 1.2rem; }
.pc-other:hover { color: var(--coral); }

.pc-cursor {
  position: fixed; top: -20px; left: -20px; z-index: 70; width: 40px; height: 40px; border-radius: 50%; pointer-events: none;
  background: var(--coral); mix-blend-mode: multiply; opacity: 0; transition: opacity .3s, transform .12s linear;
}
.pc-cursor.on { opacity: .8; }

@media (max-width: 860px) {
  .pc-about-grid, .pc-projects { grid-template-columns: 1fr; }
  .pc-project:nth-child(even) { margin-top: 0; }
  .pc-chapters li { grid-template-columns: 1fr; gap: 6px; }
  .pc-mark { display: none; }
  .pc-sticker { position: relative; right: auto; bottom: auto; margin-top: 32px; }
}
@media (hover: none) { .pc-cursor { display: none; } }
</style>
