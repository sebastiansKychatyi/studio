<script setup lang="ts">
// "Nordic Living" prototype: furniture e-shop (900×560) with UI kit
const props = defineProps<{ preview?: boolean }>()
useHead({ link: [{ rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Lora:wght@500&display=swap' }] })

const c = useConceptCopy({
  sk: { cats: ['Pohovky', 'Stoličky', 'Lampy'], hero: 'Pokoj v každom detaile.', heroSub: 'Ručne vyrábaný nábytok zo severského dreva.', shop: 'Nakupovať', color: 'Farba', add: 'Do košíka', added: 'Pridané do košíka ✓', back: '← Späť', delivery: 'Doručenie do 5 dní · 2 roky záruka', proto: 'Prototyp', kit: 'UI kit', palette: 'Paleta', type: 'Typografia', buttons: 'Tlačidlá', primary: 'Primárne', secondary: 'Sekundárne', cart: 'Košík' },
  cs: { cats: ['Pohovky', 'Židle', 'Lampy'], hero: 'Klid v každém detailu.', heroSub: 'Ručně vyráběný nábytek ze severského dřeva.', shop: 'Nakupovat', color: 'Barva', add: 'Do košíku', added: 'Přidáno do košíku ✓', back: '← Zpět', delivery: 'Doručení do 5 dnů · 2 roky záruka', proto: 'Prototyp', kit: 'UI kit', palette: 'Paleta', type: 'Typografie', buttons: 'Tlačítka', primary: 'Primární', secondary: 'Sekundární', cart: 'Košík' },
  uk: { cats: ['Дивани', 'Стільці', 'Лампи'], hero: 'Спокій у кожній деталі.', heroSub: 'Меблі ручної роботи з північного дерева.', shop: 'До покупок', color: 'Колір', add: 'У кошик', added: 'Додано в кошик ✓', back: '← Назад', delivery: 'Доставка до 5 днів · гарантія 2 роки', proto: 'Прототип', kit: 'UI kit', palette: 'Палітра', type: 'Типографіка', buttons: 'Кнопки', primary: 'Основна', secondary: 'Другорядна', cart: 'Кошик' },
  en: {
    "cats": [
      "Sofas",
      "Chairs",
      "Lamps"
    ],
    "hero": "Calm in every detail.",
    "heroSub": "Handmade furniture from Nordic wood.",
    "shop": "Shop now",
    "color": "Colour",
    "add": "Add to cart",
    "added": "Added to cart ✓",
    "back": "← Back",
    "delivery": "Delivery within 5 days · 2-year warranty",
    "proto": "Prototype",
    "kit": "UI kit",
    "palette": "Palette",
    "type": "Typography",
    "buttons": "Buttons",
    "primary": "Primary",
    "secondary": "Secondary",
    "cart": "Cart"
  },
})

type Kind = 'sofa' | 'chair' | 'lamp'
const items: { name: string; price: number; kind: Kind }[][] = [
  [{ name: 'Fjord', price: 1290, kind: 'sofa' }, { name: 'Oslo', price: 990, kind: 'sofa' }, { name: 'Lund', price: 1490, kind: 'sofa' }],
  [{ name: 'Birk', price: 189, kind: 'chair' }, { name: 'Aska', price: 229, kind: 'chair' }, { name: 'Tove', price: 159, kind: 'chair' }],
  [{ name: 'Lys', price: 119, kind: 'lamp' }, { name: 'Nord', price: 149, kind: 'lamp' }, { name: 'Hav', price: 99, kind: 'lamp' }],
]
const colors = ['#9AA5B1', '#C9B79C', '#5F7161', '#D7CFC4']
const shapes: Record<Kind, string> = {
  sofa: 'M20 60 Q20 40 40 40 H160 Q180 40 180 60 V90 H20 Z M10 70 Q10 60 22 60 V100 H10 Z M178 60 Q190 60 190 70 V100 H178 Z M15 100 H185 V112 H15 Z M30 112 V126 M170 112 V126',
  chair: 'M60 20 Q100 10 140 20 V80 H60 Z M50 80 H150 V96 H50 Z M60 96 L52 140 M140 96 L148 140 M80 96 V130 M120 96 V130',
  lamp: 'M70 20 H130 L150 70 H50 Z M100 70 V130 M70 130 H130',
}

const tab = ref<'proto' | 'kit'>('proto')
const view = ref<'home' | 'product'>('home')
const cat = ref(0)
const sel = ref(items[0]![0]!)
const color = ref(0)
const cart = ref(1)
const toast = ref(false)

function open(p: (typeof items)[number][number]) {
  sel.value = p
  color.value = 0
  view.value = 'product'
}
function add() {
  cart.value++
  toast.value = true
  setTimeout(() => (toast.value = false), 1600)
}
const fmt = (n: number) => `${n.toLocaleString('sk-SK')} €`
</script>

<template>
  <div class="pn" :class="{ 'is-preview': props.preview }" :inert="props.preview || undefined">
    <div class="pn-bar"><i /><i /><i /><span>nordicliving.sk</span>
      <div class="pn-tabs">
        <button type="button" :class="{ on: tab === 'proto' }" @click="tab = 'proto'">{{ c.proto }}</button>
        <button type="button" :class="{ on: tab === 'kit' }" @click="tab = 'kit'">{{ c.kit }}</button>
      </div>
    </div>

    <div v-if="tab === 'proto'" class="pn-site">
      <header class="pn-nav">
        <b class="pn-logo" @click="view = 'home'">nordic<span>.</span></b>
        <nav><button v-for="(cName, i) in c.cats" :key="cName" type="button" :class="{ on: cat === i && view === 'home' }" @click="cat = i; view = 'home'">{{ cName }}</button></nav>
        <span class="pn-cart">{{ c.cart }} <b :key="cart">{{ cart }}</b></span>
      </header>

      <Transition name="pn-slide" mode="out-in">
        <div v-if="view === 'home'" key="home" class="pn-home">
          <div class="pn-hero">
            <div>
              <h3>{{ c.hero }}</h3>
              <p>{{ c.heroSub }}</p>
              <button type="button" class="pn-btn" @click="open(items[cat]![0]!)">{{ c.shop }} →</button>
            </div>
            <svg viewBox="0 0 200 140" class="pn-hero-art" aria-hidden="true"><path :d="shapes.sofa" fill="#C9B79C" stroke="#2B2B2B" stroke-width="2" /></svg>
          </div>
          <div class="pn-grid">
            <button v-for="(p, i) in items[cat]" :key="p.name" type="button" class="pn-card" @click="open(p)">
              <svg viewBox="0 0 200 140" aria-hidden="true"><path :d="shapes[p.kind]" :fill="colors[i % colors.length]" stroke="#2B2B2B" stroke-width="2" /></svg>
              <span>{{ p.name }}</span><b>{{ fmt(p.price) }}</b>
            </button>
          </div>
        </div>

        <div v-else key="product" class="pn-product">
          <button type="button" class="pn-back" @click="view = 'home'">{{ c.back }}</button>
          <div class="pn-product-grid">
            <div class="pn-stage">
              <svg viewBox="0 0 200 140" aria-hidden="true"><path :d="shapes[sel.kind]" :fill="colors[color]" stroke="#2B2B2B" stroke-width="2" style="transition: fill .4s" /></svg>
            </div>
            <div>
              <h3>{{ sel.name }}</h3>
              <p class="pn-price">{{ fmt(sel.price) }}</p>
              <p class="pn-label">{{ c.color }}</p>
              <div class="pn-swatches">
                <button v-for="(col, i) in colors" :key="col" type="button" :class="{ on: color === i }" :style="{ background: col }" :aria-label="col" @click="color = i" />
              </div>
              <button type="button" class="pn-btn pn-add" @click="add">{{ c.add }}</button>
              <p class="pn-note">{{ c.delivery }}</p>
            </div>
          </div>
          <Transition name="pn-toast"><p v-if="toast" class="pn-toast">{{ c.added }}</p></Transition>
        </div>
      </Transition>
    </div>

    <div v-else class="pn-kit">
      <section>
        <h4>{{ c.palette }}</h4>
        <div class="pn-palette">
          <div v-for="col in ['#2B2B2B', '#F7F4EE', ...colors]" :key="col"><i :style="{ background: col }" /><code>{{ col }}</code></div>
        </div>
      </section>
      <section>
        <h4>{{ c.type }}</h4>
        <p class="pn-type-1">Aa — Lora Display</p>
        <p class="pn-type-2">Aa — Manrope Text 16 / 24</p>
      </section>
      <section>
        <h4>{{ c.buttons }}</h4>
        <div class="pn-btns"><button type="button" class="pn-btn">{{ c.primary }}</button><button type="button" class="pn-btn ghost">{{ c.secondary }}</button></div>
      </section>
    </div>
  </div>
</template>

<style>
.pn { width: 900px; height: 560px; border-radius: 16px; overflow: hidden; background: #F7F4EE; color: #2B2B2B; font-family: 'Manrope', system-ui, sans-serif; box-shadow: 0 30px 70px -30px rgba(0, 0, 0, .45); display: flex; flex-direction: column; text-align: left; }
.pn button { font: inherit; color: inherit; cursor: pointer; }
.pn-bar { display: flex; align-items: center; gap: 6px; padding: 10px 14px; background: #fff; border-bottom: 1px solid #E8E2D8; }
.pn-bar > i { width: 10px; height: 10px; border-radius: 50%; background: #E5DED2; }
.pn-bar > span { margin-left: 10px; font-size: 12px; color: #8A8478; background: #F7F4EE; padding: 3px 12px; border-radius: 999px; }
.pn-tabs { margin-left: auto; display: flex; background: #F1ECE3; border-radius: 999px; padding: 3px; }
.pn-tabs button { border: 0; background: none; padding: 5px 14px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.pn-tabs button.on { background: #2B2B2B; color: #fff; }
.pn-site { flex: 1; display: flex; flex-direction: column; min-height: 0; }
.pn-nav { display: flex; align-items: center; gap: 24px; padding: 16px 28px; }
.pn-logo { font-family: 'Lora', Georgia, serif; font-size: 22px; cursor: pointer; }
.pn-logo span { color: #5F7161; }
.pn-nav nav { display: flex; gap: 4px; }
.pn-nav nav button { border: 0; background: none; padding: 6px 12px; border-radius: 999px; font-size: 13px; font-weight: 600; }
.pn-nav nav button.on, .pn-nav nav button:hover { background: #EAE3D7; }
.pn-cart { margin-left: auto; font-size: 13px; font-weight: 700; display: flex; align-items: center; gap: 6px; }
.pn-cart b { display: grid; place-items: center; min-width: 22px; height: 22px; border-radius: 50%; background: #5F7161; color: #fff; font-size: 11px; animation: knBump .4s; }
.pn-home { padding: 0 28px 24px; }
.pn-hero { display: grid; grid-template-columns: 1fr 260px; align-items: center; gap: 20px; padding: 20px 28px; border-radius: 16px; background: #EAE3D7; }
.pn-hero h3 { font-family: 'Lora', Georgia, serif; font-weight: 500; font-size: 32px; line-height: 1.1; }
.pn-hero p { font-size: 14px; color: #6B655B; margin: 6px 0 14px; }
.pn-hero-art { width: 100%; animation: bob 5s ease-in-out infinite; }
.pn-btn { border: 0; background: #2B2B2B; color: #fff !important; padding: 10px 20px; border-radius: 999px; font-size: 13px; font-weight: 700; transition: background .3s, transform .2s; }
.pn-btn:hover { background: #5F7161; transform: translateY(-1px); }
.pn-btn.ghost { background: transparent; color: #2B2B2B !important; box-shadow: inset 0 0 0 1.5px #2B2B2B; }
.pn-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-top: 16px; }
.pn-card { border: 0; background: #fff; border-radius: 14px; padding: 12px; display: grid; grid-template-columns: 1fr auto; gap: 4px; text-align: left; transition: transform .3s, box-shadow .3s; }
.pn-card:hover { transform: translateY(-4px); box-shadow: 0 16px 30px -18px rgba(0, 0, 0, .35); }
.pn-card svg { grid-column: 1 / -1; width: 100%; height: 92px; background: #F7F4EE; border-radius: 10px; padding: 8px; }
.pn-card span { font-weight: 700; font-size: 14px; }
.pn-card b { font-size: 13px; color: #5F7161; }
.pn-product { position: relative; padding: 4px 28px 24px; flex: 1; }
.pn-back { border: 0; background: none; font-size: 13px; font-weight: 700; padding: 0; margin-bottom: 10px; }
.pn-product-grid { display: grid; grid-template-columns: 1.2fr 1fr; gap: 28px; align-items: center; }
.pn-stage { background: #EAE3D7; border-radius: 18px; padding: 40px 30px; }
.pn-stage svg { width: 100%; }
.pn-product h3 { font-family: 'Lora', Georgia, serif; font-weight: 500; font-size: 36px; }
.pn-price { font-size: 20px; font-weight: 700; color: #5F7161; margin: 4px 0 16px; }
.pn-label { font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: .1em; color: #8A8478; }
.pn-swatches { display: flex; gap: 10px; margin: 8px 0 20px; }
.pn-swatches button { width: 34px; height: 34px; border-radius: 50%; border: 3px solid #F7F4EE; box-shadow: 0 0 0 1px #D9D1C4; transition: box-shadow .2s, transform .2s; }
.pn-swatches button.on { box-shadow: 0 0 0 2px #2B2B2B; transform: scale(1.1); }
.pn-add { padding: 14px 30px; font-size: 14px; }
.pn-note { font-size: 12px; color: #8A8478; margin-top: 12px; }
.pn-toast { position: absolute; right: 28px; bottom: 20px; background: #5F7161; color: #fff; padding: 10px 16px; border-radius: 12px; font-size: 13px; font-weight: 700; }
.pn-toast-enter-active, .pn-toast-leave-active { transition: all .3s; }
.pn-toast-enter-from, .pn-toast-leave-to { opacity: 0; transform: translateY(10px); }
.pn-slide-enter-active, .pn-slide-leave-active { transition: opacity .25s, transform .25s; }
.pn-slide-enter-from { opacity: 0; transform: translateX(20px); }
.pn-slide-leave-to { opacity: 0; transform: translateX(-20px); }
.pn-kit { flex: 1; display: grid; grid-template-columns: 1.3fr 1fr; grid-template-rows: auto auto; gap: 18px; padding: 24px 28px; }
.pn-kit section { background: #fff; border-radius: 16px; padding: 18px; }
.pn-kit section:first-child { grid-row: span 2; }
.pn-kit h4 { font-size: 12px; text-transform: uppercase; letter-spacing: .12em; color: #8A8478; margin-bottom: 14px; }
.pn-palette { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.pn-palette i { display: block; height: 70px; border-radius: 12px; border: 1px solid #E8E2D8; }
.pn-palette code { font-size: 11px; color: #6B655B; }
.pn-type-1 { font-family: 'Lora', Georgia, serif; font-size: 34px; }
.pn-type-2 { font-size: 16px; color: #6B655B; }
.pn-btns { display: flex; gap: 10px; }
.pn.is-preview { pointer-events: none; }
</style>
