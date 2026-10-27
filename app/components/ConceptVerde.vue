<script setup lang="ts">
// Концепт «Verde» — эко-жильё: параллакс-иллюстрация, «липкая» история, интерактивный выбор квартир на фасаде
useHead({
  link: [{ rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,500;0,600;1,500&display=swap' }],
})

const c = useConceptCopy({
  sk: {
    nav: ['Projekt', 'Byty', 'Lokalita'], cta: 'Mám záujem',
    kicker: 'Rezidencia Verde · Nitra', title: 'Bývanie v rytme prírody.',
    sub: '48 bytov v energetickej triede A0, so zelenými strechami a parkom pred dverami. Kolaudácia na jar 2028.',
    steps: [['Slnko', 'Fotovoltika na streche pokryje spoločné priestory aj nabíjačky pre elektromobily.'], ['Voda', 'Dažďová voda sa zbiera a polieva záhrady a strešné terasy.'], ['Zeleň', '40 % pozemku tvorí park s ovocným sadom, ihriskom a lavičkami.']],
    pickTitle: 'Vyberte si byt.', hint: 'Kliknite na byt na fasáde', filters: ['Všetky', '1-izb.', '2-izb.', '3-izb.'],
    status: ['Voľný', 'Rezervovaný', 'Predaný'], statusLabel: 'Stav', floor: 'Poschodie', rooms: 'Izby', area: 'Plocha', price: 'Cena', book: 'Dohodnúť obhliadku',
    stats: [['A0', 'energetická trieda'], ['48', 'bytov'], ['2028', 'kolaudácia']],
    footer: 'Rezidencia Verde — fiktívny projekt na ukážku dizajnu',
  },
  cs: {
    nav: ['Projekt', 'Byty', 'Lokalita'], cta: 'Mám zájem',
    kicker: 'Rezidence Verde · Brno', title: 'Bydlení v rytmu přírody.',
    sub: '48 bytů v energetické třídě A, se zelenými střechami a parkem přede dveřmi. Kolaudace na jaře 2028.',
    steps: [['Slunce', 'Fotovoltaika na střeše pokryje společné prostory i nabíječky pro elektromobily.'], ['Voda', 'Dešťová voda se sbírá a zalévá zahrady a střešní terasy.'], ['Zeleň', '40 % pozemku tvoří park s ovocným sadem, hřištěm a lavičkami.']],
    pickTitle: 'Vyberte si byt.', hint: 'Klikněte na byt na fasádě', filters: ['Všechny', '1+kk', '2+kk', '3+kk'],
    status: ['Volný', 'Rezervovaný', 'Prodaný'], statusLabel: 'Stav', floor: 'Patro', rooms: 'Pokoje', area: 'Plocha', price: 'Cena', book: 'Domluvit prohlídku',
    stats: [['A', 'energetická třída'], ['48', 'bytů'], ['2028', 'kolaudace']],
    footer: 'Rezidence Verde — fiktivní projekt pro ukázku designu',
  },
  uk: {
    nav: ['Проєкт', 'Квартири', 'Локація'], cta: 'Цікавить',
    kicker: 'Резиденція Verde · Львів', title: 'Життя в ритмі природи.',
    sub: '48 квартир класу енергоефективності A, із зеленими дахами та парком біля дверей. Здача навесні 2028.',
    steps: [['Сонце', 'Сонячні панелі на даху живлять спільні простори та зарядки для електромобілів.'], ['Вода', 'Дощова вода збирається та поливає сади й терасу на даху.'], ['Зелень', '40 % ділянки — парк із фруктовим садом, майданчиком і лавками.']],
    pickTitle: 'Оберіть квартиру.', hint: 'Натисніть на квартиру на фасаді', filters: ['Усі', '1-кімн.', '2-кімн.', '3-кімн.'],
    status: ['Вільна', 'Заброньована', 'Продана'], statusLabel: 'Статус', floor: 'Поверх', rooms: 'Кімнати', area: 'Площа', price: 'Ціна', book: 'Домовитися про перегляд',
    stats: [['A', 'клас енергоефективності'], ['48', 'квартир'], ['2028', 'здача']],
    footer: 'Резиденція Verde — вигаданий проєкт для демонстрації дизайну',
  },
})

// --- Параллакс слоёв иллюстрации
const y = ref(0)
let raf = 0
const onScroll = () => {
  cancelAnimationFrame(raf)
  raf = requestAnimationFrame(() => (y.value = Math.min(scrollY, 900)))
}
const layer = (k: number) => ({ transform: `translateY(${y.value * k}px)` })

// --- «Липкая» история: активный шаг по прокрутке
const active = ref(0)
const stepEls = ref<HTMLElement[]>([])
let io: IntersectionObserver | undefined

// --- Квартиры (детерминированные данные)
const units = Array.from({ length: 24 }, (_, i) => {
  const floor = 4 - Math.floor(i / 6)
  const rooms = [1, 2, 3, 2, 3, 1][i % 6]!
  const area = [38, 56, 78, 61, 84, 41][i % 6]! + floor
  const status = (i * 7) % 5 === 0 ? 2 : (i * 3) % 7 === 0 ? 1 : 0
  return { id: `${floor}.${(i % 6) + 1}`, floor, rooms, area, status, price: Math.round((area * 3150 + floor * 4000) / 1000) * 1000 }
})
const roomFilter = ref(0)
const selected = ref(units.find((u) => u.status === 0)!)
const fmt = (n: number) => `${n.toLocaleString('sk-SK')} €`

onMounted(() => {
  addEventListener('scroll', onScroll, { passive: true })
  io = new IntersectionObserver(
    (entries) => entries.forEach((e) => e.isIntersecting && (active.value = Number((e.target as HTMLElement).dataset.i))),
    { rootMargin: '-45% 0px -45% 0px' }
  )
  stepEls.value.forEach((el) => io!.observe(el))
})
onBeforeUnmount(() => {
  removeEventListener('scroll', onScroll)
  io?.disconnect()
})
</script>

<template>
  <div class="verde">
    <header class="vd-nav">
      <span class="vd-logo"><i>❦</i> Verde</span>
      <nav><a href="#vd-story">{{ c.nav[0] }}</a><a href="#vd-pick">{{ c.nav[1] }}</a><a href="#vd-stats">{{ c.nav[2] }}</a></nav>
      <a href="#vd-pick" class="vd-btn">{{ c.cta }}</a>
    </header>

    <section class="vd-hero">
      <div class="vd-copy">
        <p class="vd-kicker fade-in">{{ c.kicker }}</p>
        <h1 class="fade-in" style="--d: 150ms">{{ c.title }}</h1>
        <p class="vd-sub fade-in" style="--d: 300ms">{{ c.sub }}</p>
      </div>
      <svg class="vd-scene" viewBox="0 0 1200 560" preserveAspectRatio="xMidYMax slice" aria-hidden="true">
        <defs>
          <linearGradient id="vdsky" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#F8E7C9" /><stop offset="1" stop-color="#F4F1EA" /></linearGradient>
        </defs>
        <rect width="1200" height="560" fill="url(#vdsky)" />
        <g :style="layer(0.05)"><circle cx="920" cy="150" r="70" fill="#F2B880" class="vd-sun" /></g>
        <g :style="layer(0.12)"><path d="M0 380 Q200 280 420 340 T860 320 T1200 330 V560 H0Z" fill="#C9D8BF" /></g>
        <g :style="layer(0.2)">
          <path d="M0 430 Q300 360 600 410 T1200 400 V560 H0Z" fill="#A8C3A0" />
          <g class="vd-building">
            <rect x="470" y="200" width="300" height="250" fill="#FBF8F2" stroke="#1F3D2B" stroke-width="3" />
            <rect x="460" y="188" width="320" height="16" fill="#5E8C61" />
            <g fill="#2F5A3E"><circle cx="490" cy="182" r="14" /><circle cx="530" cy="178" r="18" /><circle cx="700" cy="180" r="16" /><circle cx="745" cy="183" r="12" /></g>
            <g fill="#C8775A" opacity=".85">
              <template v-for="r in 4" :key="r"><rect v-for="col in 6" :key="col" :x="484 + (col - 1) * 47" :y="216 + (r - 1) * 56" width="32" height="38" rx="3" class="vd-win" :style="{ '--w': r * 6 + col }" /></template>
            </g>
          </g>
        </g>
        <g :style="layer(0.32)">
          <path d="M0 480 Q240 440 520 470 T1200 460 V560 H0Z" fill="#5E8C61" />
          <g fill="#1F3D2B"><circle cx="160" cy="430" r="40" /><rect x="156" y="440" width="8" height="50" /><circle cx="1010" cy="420" r="52" /><rect x="1006" y="430" width="8" height="60" /><circle cx="360" cy="450" r="28" /><circle cx="880" cy="452" r="30" /></g>
        </g>
      </svg>
    </section>

    <section id="vd-story" class="vd-story">
      <div class="vd-sticky" aria-hidden="true">
        <div class="vd-orb" :class="`s${active}`">
          <svg v-if="active === 0" viewBox="0 0 100 100"><circle cx="50" cy="50" r="20" /><path d="M50 10v12M50 78v12M10 50h12M78 50h12M22 22l8 8M70 70l8 8M22 78l8-8M70 30l8-8" /></svg>
          <svg v-else-if="active === 1" viewBox="0 0 100 100"><path d="M50 12 Q78 48 78 64 A28 28 0 0 1 22 64 Q22 48 50 12Z" /></svg>
          <svg v-else viewBox="0 0 100 100"><path d="M20 80 Q20 24 82 18 Q80 76 20 80Z M20 80 L60 40" /></svg>
        </div>
        <ol class="vd-dots"><li v-for="(s, i) in c.steps" :key="i" :class="{ on: active === i }" /></ol>
      </div>
      <div class="vd-steps">
        <article v-for="(s, i) in c.steps" :key="s[0]" ref="stepEls" :data-i="i" class="vd-step" :class="{ on: active === i }">
          <span>0{{ i + 1 }}</span>
          <h2>{{ s[0] }}</h2>
          <p>{{ s[1] }}</p>
        </article>
      </div>
    </section>

    <section id="vd-pick" class="vd-pick">
      <div class="vd-pick-head">
        <h2 v-reveal>{{ c.pickTitle }}</h2>
        <div class="vd-filters">
          <button v-for="(f, i) in c.filters" :key="f" type="button" :class="{ on: roomFilter === i }" @click="roomFilter = i">{{ f }}</button>
        </div>
      </div>
      <div class="vd-pick-grid">
        <div class="vd-facade">
          <div class="vd-roof" />
          <div class="vd-units">
            <button
              v-for="u in units"
              :key="u.id"
              type="button"
              class="vd-unit"
              :class="[`st${u.status}`, { dim: roomFilter && u.rooms !== roomFilter, sel: selected.id === u.id }]"
              :aria-label="`${c.floor} ${u.floor}, ${u.id}, ${c.status[u.status]}`"
              @click="selected = u"
            >{{ u.id }}</button>
          </div>
          <p class="vd-hint">{{ c.hint }}</p>
          <ul class="vd-legend"><li v-for="(s, i) in c.status" :key="s"><i :class="`st${i}`" />{{ s }}</li></ul>
        </div>
        <Transition name="vd-card" mode="out-in">
          <aside :key="selected.id" class="vd-card">
            <p class="vd-kicker">{{ c.floor }} {{ selected.floor }} · {{ selected.id }}</p>
            <h3>{{ selected.rooms }} {{ c.rooms.toLowerCase() }} · {{ selected.area }} m²</h3>
            <svg class="vd-plan" viewBox="0 0 200 130" aria-hidden="true">
              <rect x="4" y="4" width="192" height="122" />
              <path v-if="selected.rooms >= 2" d="M110 4 V80" />
              <path v-if="selected.rooms >= 3" d="M110 80 H196 M60 126 V80 H4" />
              <path d="M150 126 V100 H196" class="thin" />
            </svg>
            <dl>
              <div><dt>{{ c.area }}</dt><dd>{{ selected.area }} m²</dd></div>
              <div><dt>{{ c.price }}</dt><dd>{{ fmt(selected.price) }}</dd></div>
              <div><dt>{{ c.statusLabel }}</dt><dd :class="`st${selected.status}`">{{ c.status[selected.status] }}</dd></div>
            </dl>
            <button type="button" class="vd-btn" :disabled="selected.status === 2">{{ c.book }}</button>
          </aside>
        </Transition>
      </div>
    </section>

    <section id="vd-stats" class="vd-stats">
      <div v-for="(s, i) in c.stats" :key="s[1]" v-reveal :style="{ '--d': `${i * 120}ms` }"><b>{{ s[0] }}</b><span>{{ s[1] }}</span></div>
    </section>
    <footer class="vd-footer">{{ c.footer }}</footer>
  </div>
</template>

<style>
.verde { --vd-bg: #F4F1EA; --vd-green: #1F3D2B; --vd-sage: #A8C3A0; --vd-terra: #C8775A; --vd-serif: 'Lora', Georgia, serif;
  background: var(--vd-bg); color: var(--vd-green); min-height: 100vh; font-family: 'Manrope', system-ui, sans-serif; overflow-x: clip; }
.vd-nav { position: sticky; top: 0; z-index: 20; display: flex; justify-content: space-between; align-items: center; gap: 16px; padding: 16px clamp(16px, 4vw, 48px); background: rgba(244, 241, 234, .85); -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px); }
.vd-logo { font-family: var(--vd-serif); font-size: 1.6rem; font-weight: 600; }
.vd-logo i { font-style: normal; color: var(--vd-terra); }
.vd-nav nav { display: flex; gap: 28px; font-weight: 600; }
.vd-nav nav a:hover { color: var(--vd-terra); }
.vd-btn { display: inline-block; padding: 12px 22px; border-radius: 999px; background: var(--vd-green); color: var(--vd-bg); border: 0; font-weight: 700; cursor: pointer; transition: background .3s, transform .3s var(--ease); }
.vd-btn:hover:not(:disabled) { background: var(--vd-terra); transform: translateY(-2px); }
.vd-btn:disabled { opacity: .4; cursor: not-allowed; }

.vd-hero { position: relative; min-height: 100vh; display: flex; flex-direction: column; }
.vd-copy { position: relative; z-index: 2; text-align: center; padding: clamp(40px, 8vw, 90px) 16px 0; max-width: 820px; margin: 0 auto; }
.vd-kicker { font-weight: 700; letter-spacing: .14em; text-transform: uppercase; font-size: .78rem; color: var(--vd-terra); }
.vd-hero h1 { font-family: var(--vd-serif); font-weight: 500; font-size: clamp(2.8rem, 7.5vw, 6rem); line-height: 1.02; letter-spacing: -.02em; margin: 14px 0; }
.vd-sub { font-size: 1.12rem; max-width: 580px; margin: 0 auto; opacity: .85; }
.vd-scene { width: 100%; height: clamp(320px, 52vw, 600px); margin-top: auto; display: block; }
.vd-scene g { transition: transform .1s linear; }
.vd-sun { animation: vdSun 6s ease-in-out infinite; transform-origin: 920px 150px; }
@keyframes vdSun { 50% { transform: scale(1.08); } }
.vd-win { animation: vdWin 4s ease-in-out infinite; animation-delay: calc(var(--w) * 170ms); }
@keyframes vdWin { 50% { fill: #F2B880; } }

.vd-story { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; max-width: 1100px; margin: 0 auto; padding: 60px 16px; }
.vd-sticky { position: sticky; top: 120px; height: 60vh; display: grid; place-items: center; align-self: start; }
.vd-orb { width: min(340px, 70vw); aspect-ratio: 1; border-radius: 50%; display: grid; place-items: center; transition: background .8s; }
.vd-orb.s0 { background: #F8E1BC; }
.vd-orb.s1 { background: #CFE3E6; }
.vd-orb.s2 { background: #D6E5CF; }
.vd-orb svg { width: 50%; fill: none; stroke: var(--vd-green); stroke-width: 3.5; stroke-linecap: round; animation: vdPop .7s cubic-bezier(.34, 1.56, .64, 1); }
@keyframes vdPop { from { transform: scale(.6) rotate(-20deg); opacity: 0; } }
.vd-dots { display: flex; gap: 8px; margin-top: 20px; }
.vd-dots li { width: 10px; height: 10px; border-radius: 50%; background: var(--vd-sage); transition: width .4s, background .4s; }
.vd-dots li.on { width: 30px; border-radius: 6px; background: var(--vd-green); }
.vd-step { min-height: 70vh; display: flex; flex-direction: column; justify-content: center; opacity: .25; transition: opacity .6s; }
.vd-step.on { opacity: 1; }
.vd-step span { font-family: var(--vd-serif); font-style: italic; color: var(--vd-terra); font-size: 1.3rem; }
.vd-step h2 { font-family: var(--vd-serif); font-weight: 500; font-size: clamp(2.6rem, 6vw, 4.4rem); }
.vd-step p { font-size: 1.15rem; max-width: 420px; }

.vd-pick { max-width: 1100px; margin: 0 auto; padding: 60px 16px; }
.vd-pick-head { display: flex; justify-content: space-between; align-items: flex-end; gap: 20px; flex-wrap: wrap; margin-bottom: 30px; }
.vd-pick h2 { font-family: var(--vd-serif); font-weight: 500; font-size: clamp(2.4rem, 5vw, 3.8rem); }
.vd-filters { display: flex; gap: 6px; flex-wrap: wrap; }
.vd-filters button { padding: 10px 16px; border-radius: 999px; border: 1.5px solid var(--vd-green); background: none; color: var(--vd-green); font-weight: 700; cursor: pointer; transition: all .3s; }
.vd-filters button.on { background: var(--vd-green); color: var(--vd-bg); }
.vd-pick-grid { display: grid; grid-template-columns: 1.3fr 1fr; gap: 30px; align-items: start; }
.vd-facade { padding: 24px; border-radius: 24px; background: #FBF8F2; border: 1.5px solid rgba(31, 61, 43, .15); }
.vd-roof { height: 18px; border-radius: 8px 8px 0 0; background: #5E8C61; margin-bottom: 10px; }
.vd-units { display: grid; grid-template-columns: repeat(6, 1fr); gap: 8px; }
.vd-unit { aspect-ratio: 1 / 1.1; border-radius: 8px; border: 2px solid transparent; font-weight: 800; font-size: .8rem; cursor: pointer; transition: transform .3s var(--ease), opacity .3s, border-color .3s, box-shadow .3s; }
.vd-unit.st0 { background: #CFE5C6; color: var(--vd-green); }
.vd-unit.st1 { background: #F6D9A8; color: #7A4B12; }
.vd-unit.st2 { background: #E6DFD3; color: #9A9285; }
.vd-unit:hover { transform: translateY(-3px); box-shadow: 0 10px 20px -10px rgba(31, 61, 43, .5); }
.vd-unit.dim { opacity: .25; }
.vd-unit.sel { border-color: var(--vd-green); transform: scale(1.08); box-shadow: 0 10px 24px -10px rgba(31, 61, 43, .6); }
.vd-hint { margin-top: 14px; font-size: .9rem; opacity: .7; }
.vd-legend { display: flex; gap: 16px; flex-wrap: wrap; margin-top: 10px; font-size: .85rem; font-weight: 700; }
.vd-legend i { display: inline-block; width: 12px; height: 12px; border-radius: 3px; margin-right: 6px; vertical-align: -1px; }
.vd-legend .st0 { background: #CFE5C6; } .vd-legend .st1 { background: #F6D9A8; } .vd-legend .st2 { background: #E6DFD3; }
.vd-card { padding: 28px; border-radius: 24px; background: var(--vd-green); color: var(--vd-bg); display: grid; gap: 16px; }
.vd-card h3 { font-family: var(--vd-serif); font-weight: 500; font-size: 1.8rem; }
.vd-plan { width: 100%; fill: none; stroke: var(--vd-bg); stroke-width: 3; }
.vd-plan .thin { stroke-width: 1.5; stroke-dasharray: 4 4; }
.vd-card dl { display: grid; gap: 8px; }
.vd-card dl div { display: flex; justify-content: space-between; border-bottom: 1px solid rgba(244, 241, 234, .2); padding-bottom: 8px; }
.vd-card dt { opacity: .7; }
.vd-card dd { font-weight: 800; }
.vd-card dd.st0 { color: #A6E39A; } .vd-card dd.st1 { color: #F6C77A; } .vd-card dd.st2 { color: #C9C1B3; }
.vd-card .vd-btn { background: var(--vd-bg); color: var(--vd-green); justify-self: start; }
.vd-card-enter-active, .vd-card-leave-active { transition: opacity .25s, transform .25s; }
.vd-card-enter-from { opacity: 0; transform: translateX(16px); }
.vd-card-leave-to { opacity: 0; transform: translateX(-16px); }

.vd-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; max-width: 1100px; margin: 0 auto; padding: 40px 16px 60px; text-align: center; }
.vd-stats b { display: block; font-family: var(--vd-serif); font-weight: 500; font-size: clamp(3rem, 8vw, 5.5rem); color: var(--vd-terra); line-height: 1; }
.vd-stats span { font-weight: 700; text-transform: uppercase; letter-spacing: .12em; font-size: .8rem; }
.vd-footer { text-align: center; padding: 30px 16px 110px; opacity: .6; font-size: .85rem; }

@media (max-width: 860px) {
  .vd-nav nav { display: none; }
  .vd-story { grid-template-columns: 1fr; }
  .vd-sticky { position: sticky; top: 70px; height: auto; z-index: 1; padding: 10px 0; background: var(--vd-bg); }
  .vd-orb { width: 140px; }
  .vd-step { min-height: 50vh; }
  .vd-pick-grid, .vd-stats { grid-template-columns: 1fr; }
  .vd-units { gap: 5px; }
}
</style>
