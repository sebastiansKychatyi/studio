<script setup lang="ts">
// Концепт «Kinetic» — streetwear e-shop в стиле брутализм: гигантская типографика, рабочая корзина, «летящий» товар
useHead({
  link: [{ rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Dela+Gothic+One&display=swap' }],
})

const c = useConceptCopy({
  sk: {
    promo: ['Doprava zadarmo nad 60 €', 'Drop 07 je tu', 'Vrátenie do 30 dní'],
    nav: ['Novinky', 'Mikiny', 'Tričká', 'Doplnky'], cart: 'Košík',
    sub: 'Oblečenie pre ľudí, ktorí sa nezastavia. Limitovaná kolekcia — 300 kusov.', cta: 'Nakupovať drop',
    filters: ['Všetko', 'Mikiny', 'Tričká', 'Doplnky'], size: 'Vyber veľkosť', one: 'Univerzálna',
    cartTitle: 'Košík', empty: 'Košík je prázdny. Zatiaľ.', total: 'Spolu', checkout: 'Pokladňa (demo)', remove: 'Odstrániť', close: 'Zavrieť',
    look: 'Lookbook', drag: 'Potiahnite →', looks: ['Mesto v pohybe', 'Nočná linka', 'Betón & neón', 'Ráno po'],
  },
  cs: {
    promo: ['Doprava zdarma nad 1 500 Kč', 'Drop 07 je tady', 'Vrácení do 30 dní'],
    nav: ['Novinky', 'Mikiny', 'Trička', 'Doplňky'], cart: 'Košík',
    sub: 'Oblečení pro lidi, kteří se nezastaví. Limitovaná kolekce — 300 kusů.', cta: 'Nakupovat drop',
    filters: ['Vše', 'Mikiny', 'Trička', 'Doplňky'], size: 'Vyber velikost', one: 'Univerzální',
    cartTitle: 'Košík', empty: 'Košík je prázdný. Zatím.', total: 'Celkem', checkout: 'Pokladna (demo)', remove: 'Odebrat', close: 'Zavřít',
    look: 'Lookbook', drag: 'Táhněte →', looks: ['Město v pohybu', 'Noční linka', 'Beton & neon', 'Ráno poté'],
  },
  uk: {
    promo: ['Безкоштовна доставка від 60 €', 'Drop 07 вже тут', 'Повернення 30 днів'],
    nav: ['Новинки', 'Худі', 'Футболки', 'Аксесуари'], cart: 'Кошик',
    sub: 'Одяг для тих, хто не зупиняється. Лімітована колекція — 300 штук.', cta: 'До дропу',
    filters: ['Усе', 'Худі', 'Футболки', 'Аксесуари'], size: 'Обери розмір', one: 'Універсальний',
    cartTitle: 'Кошик', empty: 'Кошик порожній. Поки що.', total: 'Разом', checkout: 'Оформити (демо)', remove: 'Видалити', close: 'Закрити',
    look: 'Lookbook', drag: 'Тягніть →', looks: ['Місто в русі', 'Нічна лінія', 'Бетон & неон', 'Ранок після'],
  },
})

type Kind = 'hoodie' | 'tee' | 'cap' | 'tote'
const products: { id: number; name: string; cat: 1 | 2 | 3; price: number; color: string; kind: Kind }[] = [
  { id: 1, name: 'Orbit Hoodie', cat: 1, price: 79, color: '#D7FF3A', kind: 'hoodie' },
  { id: 2, name: 'Static Tee', cat: 2, price: 35, color: '#FF4D2E', kind: 'tee' },
  { id: 3, name: 'Flux Hoodie', cat: 1, price: 85, color: '#9B8CFF', kind: 'hoodie' },
  { id: 4, name: 'Grid Tee', cat: 2, price: 32, color: '#FFFFFF', kind: 'tee' },
  { id: 5, name: 'Signal Cap', cat: 3, price: 29, color: '#FFB800', kind: 'cap' },
  { id: 6, name: 'Drift Tote', cat: 3, price: 25, color: '#2EC4FF', kind: 'tote' },
]
const shapes: Record<Kind, string> = {
  hoodie: 'M62 48 Q64 8 100 8 Q136 8 138 48 L178 64 L194 152 L168 158 L160 114 L160 192 L40 192 L40 114 L32 158 L6 152 L22 64 Z',
  tee: 'M70 30 Q100 50 130 30 L180 55 L165 95 L145 85 L145 190 L55 190 L55 85 L35 95 L20 55 Z',
  cap: 'M30 130 Q30 60 100 55 Q170 60 170 130 Z M20 130 L190 130 Q195 145 175 148 L20 140 Z',
  tote: 'M40 80 L160 80 L170 190 L30 190 Z M70 80 Q70 30 100 30 Q130 30 130 80',
}
// Детали поверх силуэта (капюшон, шнурки, карман, швы)
const details: Record<Kind, string> = {
  hoodie: 'M76 50 Q100 84 124 50 M92 66 V100 M108 66 V100 M66 150 H134 L128 180 H72 Z',
  tee: 'M84 36 Q100 50 116 36',
  cap: 'M100 56 V130 M60 70 Q80 100 78 130 M140 70 Q120 100 122 130',
  tote: 'M60 125 H140',
}

const filter = ref(0)
const visible = computed(() => products.filter((p) => filter.value === 0 || p.cat === filter.value))

// --- Корзина
const cart = ref<{ key: string; id: number; size: string; qty: number }[]>([])
const cartOpen = ref(false)
const bump = ref(false)
const count = computed(() => cart.value.reduce((s, i) => s + i.qty, 0))
const total = computed(() => cart.value.reduce((s, i) => s + i.qty * products.find((p) => p.id === i.id)!.price, 0))
const cartBtn = ref<HTMLElement>()
const flyers = ref<{ id: number; x: number; y: number; dx: number; dy: number; color: string; go: boolean }[]>([])
let flyId = 0

function add(p: (typeof products)[number], size: string, e: MouseEvent) {
  const key = `${p.id}-${size}`
  const line = cart.value.find((i) => i.key === key)
  if (line) line.qty++
  else cart.value.push({ key, id: p.id, size, qty: 1 })
  // «Летящая» точка от кнопки к корзине
  const target = cartBtn.value?.getBoundingClientRect()
  if (target) {
    const f = { id: ++flyId, x: e.clientX, y: e.clientY, dx: target.left + target.width / 2 - e.clientX, dy: target.top + target.height / 2 - e.clientY, color: p.color, go: false }
    flyers.value.push(f)
    requestAnimationFrame(() => requestAnimationFrame(() => {
      // точка могла уже исчезнуть (rAF в фоновой вкладке срабатывает позже таймера)
      const fly = flyers.value.find((x) => x.id === f.id)
      if (fly) fly.go = true
    }))
    setTimeout(() => {
      flyers.value = flyers.value.filter((x) => x.id !== f.id)
      bump.value = true
      setTimeout(() => (bump.value = false), 400)
    }, 650)
  }
}
const remove = (key: string) => (cart.value = cart.value.filter((i) => i.key !== key))
const productOf = (id: number) => products.find((p) => p.id === id)!

// --- Наклон гигантского заголовка от скорости прокрутки
const skew = ref(0)
let lastY = 0
let raf = 0
function onScroll() {
  cancelAnimationFrame(raf)
  raf = requestAnimationFrame(() => {
    const v = scrollY - lastY
    lastY = scrollY
    skew.value = Math.max(-12, Math.min(12, v * 0.4))
    setTimeout(() => (skew.value = 0), 120)
  })
}

// --- Lookbook: перетаскивание мышью
const track = ref<HTMLElement>()
let drag: { x: number; left: number } | null = null
const down = (e: PointerEvent) => { drag = { x: e.clientX, left: track.value!.scrollLeft } }
const moveDrag = (e: PointerEvent) => { if (drag) track.value!.scrollLeft = drag.left - (e.clientX - drag.x) }
const up = () => { drag = null }

onMounted(() => addEventListener('scroll', onScroll, { passive: true }))
onBeforeUnmount(() => removeEventListener('scroll', onScroll))
</script>

<template>
  <div class="kinetic">
    <div class="kn-promo" aria-hidden="true">
      <div class="kn-promo-track"><template v-for="n in 4" :key="n"><span v-for="p in c.promo" :key="`${n}${p}`">{{ p }} ✦</span></template></div>
    </div>

    <header class="kn-nav">
      <span class="kn-logo">KNTC</span>
      <nav><a v-for="n in c.nav" :key="n" href="#kn-shop">{{ n }}</a></nav>
      <button ref="cartBtn" type="button" class="kn-cart-btn" :class="{ bump }" @click="cartOpen = true">
        {{ c.cart }} <b>{{ count }}</b>
      </button>
    </header>

    <section class="kn-hero">
      <h1 class="kn-title" :style="{ transform: `skewY(${skew}deg)` }">
        <span v-for="(ch, i) in 'KINETIC'.split('')" :key="i" :style="{ '--i': i }">{{ ch }}</span>
      </h1>
      <div class="kn-hero-row">
        <p class="kn-sub">{{ c.sub }}</p>
        <div class="kn-hero-art" aria-hidden="true">
          <svg viewBox="0 0 200 200"><path :d="shapes.hoodie" fill="#D7FF3A" stroke="#111" stroke-width="4" stroke-linejoin="round" /><path :d="details.hoodie" fill="none" stroke="#111" stroke-width="4" stroke-linecap="round" /></svg>
          <span class="kn-sticker">DROP<br>07</span>
        </div>
        <a href="#kn-shop" class="kn-cta">{{ c.cta }} ↓</a>
      </div>
    </section>

    <section id="kn-shop" class="kn-shop">
      <div class="kn-filters">
        <button v-for="(f, i) in c.filters" :key="f" type="button" :class="{ on: filter === i }" @click="filter = i">{{ f }}</button>
      </div>
      <TransitionGroup name="kn-grid" tag="div" class="kn-grid">
        <article v-for="p in visible" :key="p.id" class="kn-card" :style="{ '--pc': p.color }">
          <div class="kn-img">
            <svg viewBox="0 0 200 200" aria-hidden="true"><path :d="shapes[p.kind]" :fill="p.color" stroke="#111" stroke-width="4" stroke-linejoin="round" /><path :d="details[p.kind]" class="kn-detail" fill="none" stroke="#111" stroke-width="4" stroke-linecap="round" /></svg>
            <div class="kn-sizes">
              <small>{{ c.size }}</small>
              <div v-if="p.cat !== 3">
                <button v-for="s in ['S', 'M', 'L', 'XL']" :key="s" type="button" @click="add(p, s, $event)">{{ s }}</button>
              </div>
              <div v-else><button type="button" class="wide" @click="add(p, c.one, $event)">+ {{ c.one }}</button></div>
            </div>
          </div>
          <div class="kn-meta"><h3>{{ p.name }}</h3><span>{{ p.price }} €</span></div>
        </article>
      </TransitionGroup>
    </section>

    <section class="kn-look">
      <div class="kn-look-head"><h2>{{ c.look }}</h2><span>{{ c.drag }}</span></div>
      <div ref="track" class="kn-track" @pointerdown="down" @pointermove="moveDrag" @pointerup="up" @pointerleave="up">
        <figure v-for="(l, i) in c.looks" :key="l" :style="{ '--lc': products[i]!.color }">
          <svg viewBox="0 0 200 200" aria-hidden="true"><path :d="shapes[products[i]!.kind]" fill="var(--lc)" stroke="#111" stroke-width="4" /><path :d="details[products[i]!.kind]" fill="none" stroke="#111" stroke-width="4" /></svg>
          <figcaption>{{ String(i + 1).padStart(2, '0') }} — {{ l }}</figcaption>
        </figure>
      </div>
    </section>
    <footer class="kn-footer">KINETIC © DROP 07</footer>

    <!-- летящие товары -->
    <i
      v-for="f in flyers"
      :key="f.id"
      class="kn-flyer"
      :style="{ left: `${f.x}px`, top: `${f.y}px`, background: f.color, transform: f.go ? `translate(${f.dx}px, ${f.dy}px) scale(.3)` : 'none' }"
    />

    <!-- корзина -->
    <Transition name="kn-veil"><div v-if="cartOpen" class="kn-veil" @click="cartOpen = false" /></Transition>
    <Transition name="kn-drawer">
      <aside v-if="cartOpen" class="kn-drawer" role="dialog" :aria-label="c.cartTitle">
        <div class="kn-drawer-head"><h2>{{ c.cartTitle }} ({{ count }})</h2><button type="button" :aria-label="c.close" @click="cartOpen = false">✕</button></div>
        <p v-if="!cart.length" class="kn-empty">{{ c.empty }}</p>
        <TransitionGroup v-else name="kn-line" tag="ul" class="kn-lines">
          <li v-for="i in cart" :key="i.key">
            <svg viewBox="0 0 200 200"><path :d="shapes[productOf(i.id).kind]" :fill="productOf(i.id).color" stroke="#111" stroke-width="6" /></svg>
            <div><b>{{ productOf(i.id).name }}</b><small>{{ i.size }} · {{ i.qty }}×</small></div>
            <span>{{ productOf(i.id).price * i.qty }} €</span>
            <button type="button" :aria-label="c.remove" @click="remove(i.key)">✕</button>
          </li>
        </TransitionGroup>
        <div class="kn-total"><span>{{ c.total }}</span><b>{{ total }} €</b></div>
        <button type="button" class="kn-checkout">{{ c.checkout }}</button>
      </aside>
    </Transition>
  </div>
</template>

<style>
.kinetic { --kn-bg: #F2F0EA; --kn-acid: #D7FF3A; --kn-ink: #111; --kn-display: 'Dela Gothic One', 'Unbounded', Impact, sans-serif;
  background: var(--kn-bg); color: var(--kn-ink); min-height: 100vh; font-family: 'Manrope', system-ui, sans-serif; overflow-x: clip; }
.kn-promo { background: var(--kn-ink); color: var(--kn-acid); overflow: hidden; padding: 9px 0; font-weight: 800; font-size: .82rem; text-transform: uppercase; letter-spacing: .06em; }
.kn-promo-track { display: flex; gap: 32px; width: max-content; animation: marquee 22s linear infinite; }
.kn-nav { position: sticky; top: 0; z-index: 30; display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 14px clamp(16px, 3vw, 32px); background: var(--kn-bg); border-bottom: 3px solid var(--kn-ink); }
.kn-logo { font-family: var(--kn-display); font-size: 1.6rem; letter-spacing: -.02em; }
.kn-nav nav { display: flex; gap: 4px; }
.kn-nav nav a { padding: 8px 14px; font-weight: 800; text-transform: uppercase; font-size: .82rem; border: 2px solid transparent; transition: border-color .2s, background .2s; }
.kn-nav nav a:hover { border-color: var(--kn-ink); background: var(--kn-acid); }
.kn-cart-btn { display: inline-flex; align-items: center; gap: 10px; padding: 10px 16px; border: 3px solid var(--kn-ink); background: #fff; font-weight: 800; text-transform: uppercase; cursor: pointer; box-shadow: 4px 4px 0 var(--kn-ink); transition: transform .15s, box-shadow .15s; }
.kn-cart-btn:hover { transform: translate(-2px, -2px); box-shadow: 6px 6px 0 var(--kn-ink); }
.kn-cart-btn b { min-width: 26px; height: 26px; display: grid; place-items: center; background: var(--kn-acid); border: 2px solid var(--kn-ink); border-radius: 50%; }
.kn-cart-btn.bump b { animation: knBump .4s cubic-bezier(.34, 1.56, .64, 1); }
@keyframes knBump { 50% { transform: scale(1.6) rotate(-12deg); } }

.kn-hero { padding: 20px clamp(16px, 3vw, 32px) 40px; border-bottom: 3px solid var(--kn-ink); }
.kn-title { font-family: var(--kn-display); font-weight: 400; font-size: clamp(3.4rem, 16vw, 16rem); line-height: .85; letter-spacing: -.04em; transition: transform .25s ease-out; white-space: nowrap; text-align: center; }
.kn-title span { display: inline-block; }
.js .kn-title span { animation: knDrop .8s cubic-bezier(.34, 1.56, .64, 1) both; animation-delay: calc(var(--i) * 60ms + 100ms); }
.kn-title span:hover { color: var(--kn-acid); -webkit-text-stroke: 3px var(--kn-ink); }
@keyframes knDrop { from { transform: translateY(-120%) rotate(-10deg); opacity: 0; } }
.kn-hero-row { display: grid; grid-template-columns: 1fr auto 1fr; gap: 24px; align-items: center; margin-top: 20px; }
.kn-sub { font-weight: 700; font-size: 1.1rem; max-width: 360px; }
.kn-hero-art { position: relative; width: clamp(160px, 22vw, 260px); }
.kn-hero-art svg { animation: knSpin 9s ease-in-out infinite; }
@keyframes knSpin { 50% { transform: rotate(8deg) scale(1.05); } }
.kn-sticker { position: absolute; top: -6px; right: -18px; width: 82px; height: 82px; display: grid; place-items: center; text-align: center; border-radius: 50%; background: #FF4D2E; color: #fff; font-family: var(--kn-display); font-size: .9rem; line-height: 1; border: 3px solid var(--kn-ink); animation: spinSlow 12s linear infinite; }
.kn-cta { justify-self: end; padding: 18px 28px; background: var(--kn-ink); color: var(--kn-acid); font-weight: 800; text-transform: uppercase; font-size: 1rem; border: 3px solid var(--kn-ink); transition: background .2s, color .2s; }
.kn-cta:hover { background: var(--kn-acid); color: var(--kn-ink); }

.kn-shop { padding: 40px clamp(16px, 3vw, 32px); }
.kn-filters { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 24px; }
.kn-filters button { padding: 10px 18px; border: 3px solid var(--kn-ink); background: #fff; font-weight: 800; text-transform: uppercase; cursor: pointer; transition: background .2s; }
.kn-filters button.on { background: var(--kn-ink); color: var(--kn-acid); }
.kn-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0; border-left: 3px solid var(--kn-ink); border-top: 3px solid var(--kn-ink); }
.kn-card { border-right: 3px solid var(--kn-ink); border-bottom: 3px solid var(--kn-ink); background: #fff; }
.kn-img { position: relative; aspect-ratio: 1; display: grid; place-items: center; padding: 14%; overflow: hidden; transition: background .3s; }
.kn-card:hover .kn-img { background: var(--pc); }
.kn-img svg { width: 100%; transition: transform .5s cubic-bezier(.34, 1.56, .64, 1); }
.kn-card:hover .kn-img svg { transform: scale(1.08) rotate(-6deg); }
.kn-card:hover .kn-img svg path:not(.kn-detail) { fill: #fff; }
.kn-sizes { position: absolute; left: 0; right: 0; bottom: 0; padding: 12px; background: var(--kn-ink); color: #fff; transform: translateY(100%); transition: transform .3s cubic-bezier(.2, .8, .2, 1); }
.kn-card:hover .kn-sizes, .kn-card:focus-within .kn-sizes { transform: none; }
.kn-sizes small { display: block; font-weight: 700; text-transform: uppercase; font-size: .7rem; margin-bottom: 8px; color: var(--kn-acid); }
.kn-sizes div { display: flex; gap: 6px; }
.kn-sizes button { flex: 1; padding: 10px 0; background: #fff; border: 0; font-weight: 800; cursor: pointer; transition: background .2s; }
.kn-sizes button:hover { background: var(--kn-acid); }
.kn-meta { display: flex; justify-content: space-between; align-items: center; padding: 14px 16px; border-top: 3px solid var(--kn-ink); }
.kn-meta h3 { font-family: var(--kn-display); font-weight: 400; font-size: 1.15rem; }
.kn-meta span { font-weight: 800; padding: 4px 10px; background: var(--kn-acid); border: 2px solid var(--kn-ink); }
.kn-grid-enter-active { transition: opacity .4s, transform .4s cubic-bezier(.34, 1.56, .64, 1); }
.kn-grid-enter-from { opacity: 0; transform: scale(.9); }
.kn-grid-leave-active { display: none; }

.kn-look { padding: 40px 0 20px; border-top: 3px solid var(--kn-ink); }
.kn-look-head { display: flex; justify-content: space-between; align-items: baseline; padding: 0 clamp(16px, 3vw, 32px); }
.kn-look h2 { font-family: var(--kn-display); font-weight: 400; font-size: clamp(2.4rem, 7vw, 5rem); }
.kn-look-head span { font-weight: 800; text-transform: uppercase; }
.kn-track { display: flex; gap: 20px; overflow-x: auto; padding: 20px clamp(16px, 3vw, 32px) 30px; cursor: grab; scrollbar-width: none; user-select: none; }
.kn-track:active { cursor: grabbing; }
.kn-track figure { flex: 0 0 clamp(240px, 32vw, 380px); aspect-ratio: 3 / 4; display: grid; place-items: center; padding: 18%; background: var(--kn-ink); border: 3px solid var(--kn-ink); position: relative; box-shadow: 8px 8px 0 var(--lc); transition: transform .3s; }
.kn-track figure:nth-child(even) { transform: rotate(2deg); }
.kn-track figure:nth-child(odd) { transform: rotate(-2deg); }
.kn-track figure:hover { transform: rotate(0) scale(1.02); }
.kn-track svg { width: 100%; pointer-events: none; }
.kn-track figcaption { position: absolute; left: 14px; bottom: 12px; color: #fff; font-weight: 800; text-transform: uppercase; font-size: .85rem; }
.kn-footer { padding: 30px 16px 110px; text-align: center; font-family: var(--kn-display); font-size: 1.2rem; border-top: 3px solid var(--kn-ink); }

.kn-flyer { position: fixed; z-index: 95; width: 34px; height: 34px; margin: -17px 0 0 -17px; border-radius: 50%; border: 3px solid var(--kn-ink); pointer-events: none; transition: transform .65s cubic-bezier(.6, -0.3, .7, 1); }
.kn-veil { position: fixed; inset: 0; z-index: 90; background: rgba(17, 17, 17, .5); }
.kn-drawer { position: fixed; z-index: 91; top: 0; right: 0; bottom: 0; width: min(420px, 100%); background: var(--kn-bg); border-left: 3px solid var(--kn-ink); display: flex; flex-direction: column; padding: 20px; }
.kn-drawer-head { display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid var(--kn-ink); padding-bottom: 14px; }
.kn-drawer-head h2 { font-family: var(--kn-display); font-weight: 400; font-size: 1.6rem; }
.kn-drawer-head button { width: 40px; height: 40px; border: 3px solid var(--kn-ink); background: #fff; font-weight: 800; cursor: pointer; }
.kn-empty { margin: 30px 0; font-weight: 700; }
.kn-lines { flex: 1; overflow-y: auto; padding: 10px 0; }
.kn-lines li { display: grid; grid-template-columns: 56px 1fr auto auto; gap: 12px; align-items: center; padding: 12px 0; border-bottom: 2px dashed var(--kn-ink); }
.kn-lines svg { background: #fff; border: 2px solid var(--kn-ink); padding: 6px; }
.kn-lines small { display: block; }
.kn-lines button { border: 0; background: none; cursor: pointer; font-weight: 800; }
.kn-line-enter-active, .kn-line-leave-active { transition: all .3s; }
.kn-line-enter-from, .kn-line-leave-to { opacity: 0; transform: translateX(30px); }
.kn-total { display: flex; justify-content: space-between; padding: 16px 0; font-weight: 800; font-size: 1.2rem; border-top: 3px solid var(--kn-ink); margin-top: auto; }
.kn-checkout { padding: 18px; background: var(--kn-acid); border: 3px solid var(--kn-ink); font-weight: 800; text-transform: uppercase; cursor: pointer; box-shadow: 5px 5px 0 var(--kn-ink); }
.kn-veil-enter-active, .kn-veil-leave-active { transition: opacity .3s; }
.kn-veil-enter-from, .kn-veil-leave-to { opacity: 0; }
.kn-drawer-enter-active, .kn-drawer-leave-active { transition: transform .4s cubic-bezier(.2, .8, .2, 1); }
.kn-drawer-enter-from, .kn-drawer-leave-to { transform: translateX(100%); }

@media (max-width: 860px) {
  .kn-nav nav { display: none; }
  .kn-grid { grid-template-columns: repeat(2, 1fr); }
  .kn-hero-row { grid-template-columns: 1fr; justify-items: center; text-align: center; }
  .kn-cta { justify-self: center; }
}
@media (hover: none) { .kn-sizes { transform: none; position: static; } }
</style>
