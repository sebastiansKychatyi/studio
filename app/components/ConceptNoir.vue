<script setup lang="ts">
// "Noir" concept: fine dining restaurant, dark and gold
useHead({
  link: [{ rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&display=swap' }],
})

const c = useConceptCopy({
  sk: {
    nav: ['Menu', 'Príbeh', 'Rezervácia'], book: 'Rezervovať stôl',
    kicker: 'Sezónna degustačná kuchyňa · Bratislava', sub: 'Osem chodov. Jeden večer. Chute, ktoré si zapamätáte.', scroll: 'Posuňte nižšie',
    menuTitle: 'Menu', tabs: ['Degustačné', 'À la carte'],
    menus: [
      [['Ustrica & yuzu', 'uhorka, kôpor, morská pena'], ['Pečená cvikla', 'kozí syr, lieskovce, malina'], ['Pstruh z Tatier', 'maslová omáčka, kaviár, pór'], ['Kačacie prsia', 'čerešne, celer, demi-glace'], ['Syr & med', 'liptovská bryndza, agátový med'], ['Čokoláda 70 %', 'slaný karamel, kakaové bôby']],
      [['Tatarák z hovädzieho', 'žĺtok, kapary, kváskový chlieb'], ['Risotto s hríbmi', 'parmezán, tymián, hľuzovka'], ['Jahňacie karé', 'baklažán, jogurt, mäta'], ['Sezónny sorbet', 'rakytník, bazový kvet']],
    ],
    prices: ['89 € / osoba', ['18 €', '24 €', '34 €', '9 €']],
    storyKicker: 'Príbeh', quote: 'Varíme z toho, čo práve dozrelo — nie z toho, čo je práve v móde.', author: 'Šéfkuchár, Noir',
    stats: [['8', 'chodov degustácie'], ['24', 'miest pri stoloch'], ['100 %', 'sezónne suroviny']],
    resTitle: 'Rezervácia', date: 'Dátum', guests: 'Počet hostí', time: 'Čas', send: 'Potvrdiť rezerváciu',
    done: 'Ďakujeme! Toto je len ukážka — rezervácia sa nikam neodoslala.',
  },
  cs: {
    nav: ['Menu', 'Příběh', 'Rezervace'], book: 'Rezervovat stůl',
    kicker: 'Sezónní degustační kuchyně · Praha', sub: 'Osm chodů. Jeden večer. Chutě, které si zapamatujete.', scroll: 'Posuňte níže',
    menuTitle: 'Menu', tabs: ['Degustační', 'À la carte'],
    menus: [
      [['Ústřice & yuzu', 'okurka, kopr, mořská pěna'], ['Pečená řepa', 'kozí sýr, lískové ořechy, malina'], ['Pstruh z Šumavy', 'máslová omáčka, kaviár, pórek'], ['Kachní prsa', 'třešně, celer, demi-glace'], ['Sýr & med', 'tvarůžky, akátový med'], ['Čokoláda 70 %', 'slaný karamel, kakaové boby']],
      [['Tatarák z hovězího', 'žloutek, kapary, kváskový chléb'], ['Rizoto s hříbky', 'parmazán, tymián, lanýž'], ['Jehněčí kotletky', 'lilek, jogurt, máta'], ['Sezónní sorbet', 'rakytník, bezový květ']],
    ],
    prices: ['2 290 Kč / osoba', ['450 Kč', '590 Kč', '850 Kč', '220 Kč']],
    storyKicker: 'Příběh', quote: 'Vaříme z toho, co právě dozrálo — ne z toho, co je zrovna v módě.', author: 'Šéfkuchař, Noir',
    stats: [['8', 'chodů degustace'], ['24', 'míst u stolů'], ['100 %', 'sezónní suroviny']],
    resTitle: 'Rezervace', date: 'Datum', guests: 'Počet hostů', time: 'Čas', send: 'Potvrdit rezervaci',
    done: 'Děkujeme! Toto je jen ukázka — rezervace se nikam neodeslala.',
  },
  uk: {
    nav: ['Меню', 'Історія', 'Бронювання'], book: 'Забронювати стіл',
    kicker: 'Сезонна дегустаційна кухня · Київ', sub: 'Вісім страв. Один вечір. Смаки, які запамʼятаєте.', scroll: 'Гортайте нижче',
    menuTitle: 'Меню', tabs: ['Дегустаційне', 'À la carte'],
    menus: [
      [['Устриця & юдзу', 'огірок, кріп, морська піна'], ['Печений буряк', 'козячий сир, фундук, малина'], ['Карпатська форель', 'вершкове масло, ікра, порей'], ['Качина грудка', 'вишня, селера, демі-гласс'], ['Сир & мед', 'бринза, акацієвий мед'], ['Шоколад 70 %', 'солона карамель, какао-боби']],
      [['Тартар з яловичини', 'жовток, каперси, хліб на заквасці'], ['Різото з білими грибами', 'пармезан, чебрець, трюфель'], ['Ягняча корейка', 'баклажан, йогурт, мʼята'], ['Сезонний сорбет', 'обліпиха, бузина']],
    ],
    prices: ['3 900 ₴ / особа', ['790 ₴', '1 050 ₴', '1 490 ₴', '390 ₴']],
    storyKicker: 'Історія', quote: 'Ми готуємо з того, що щойно дозріло, — а не з того, що зараз у моді.', author: 'Шеф-кухар, Noir',
    stats: [['8', 'страв дегустації'], ['24', 'місця за столами'], ['100 %', 'сезонні продукти']],
    resTitle: 'Бронювання', date: 'Дата', guests: 'Кількість гостей', time: 'Час', send: 'Підтвердити бронювання',
    done: 'Дякуємо! Це лише демо — бронювання нікуди не надіслано.',
  },
  en: {
    "nav": [
      "Menu",
      "Story",
      "Reservations"
    ],
    "book": "Book a table",
    "kicker": "Seasonal tasting cuisine · Bratislava",
    "sub": "Eight courses. One evening. Flavours you will remember.",
    "scroll": "Scroll down",
    "menuTitle": "Menu",
    "tabs": [
      "Tasting",
      "À la carte"
    ],
    "menus": [
      [
        [
          "Oyster & yuzu",
          "cucumber, dill, sea foam"
        ],
        [
          "Roasted beetroot",
          "goat cheese, hazelnuts, raspberry"
        ],
        [
          "Tatra trout",
          "beurre blanc, caviar, leek"
        ],
        [
          "Duck breast",
          "cherries, celeriac, demi-glace"
        ],
        [
          "Cheese & honey",
          "sheep cheese, acacia honey"
        ],
        [
          "Chocolate 70 %",
          "salted caramel, cocoa nibs"
        ]
      ],
      [
        [
          "Beef tartare",
          "egg yolk, capers, sourdough"
        ],
        [
          "Porcini risotto",
          "parmesan, thyme, truffle"
        ],
        [
          "Rack of lamb",
          "aubergine, yoghurt, mint"
        ],
        [
          "Seasonal sorbet",
          "sea buckthorn, elderflower"
        ]
      ]
    ],
    "prices": [
      "€89 / person",
      [
        "€18",
        "€24",
        "€34",
        "€9"
      ]
    ],
    "storyKicker": "Story",
    "quote": "We cook with what has just ripened — not with what happens to be in fashion.",
    "author": "Head chef, Noir",
    "stats": [
      [
        "8",
        "tasting courses"
      ],
      [
        "24",
        "seats"
      ],
      [
        "100 %",
        "seasonal ingredients"
      ]
    ],
    "resTitle": "Reservations",
    "date": "Date",
    "guests": "Guests",
    "time": "Time",
    "send": "Confirm reservation",
    "done": "Thank you! This is just a demo — the reservation was not sent anywhere."
  },
})

const plateColors = ['#E9D8B4', '#9B2C3A', '#D9825B', '#6E3B2A', '#E7C46A', '#3B2418']
const tab = ref(0)
const courses = computed(() => c.value.menus[tab.value]!)
const priceOf = (i: number) => (tab.value === 0 ? (i === 0 ? c.value.prices[0] : '') : (c.value.prices[1] as string[])[i])

// Plate preview following the cursor over the menu
const hover = reactive({ i: -1, x: 0, y: 0 })
function move(e: PointerEvent, i: number) {
  hover.i = i
  hover.x = e.clientX
  hover.y = e.clientY
}

// Deterministic gold dust (SSR-safe)
const dust = Array.from({ length: 22 }, (_, i) => ({
  left: `${(i * 37) % 100}%`,
  delay: `${(i * 0.7) % 8}s`,
  dur: `${8 + ((i * 3) % 7)}s`,
  size: `${2 + (i % 3)}px`,
}))

// Reservation (demo)
const res = reactive({ date: '', guests: 2, time: '19:30', sent: false })
const times = ['18:00', '19:30', '21:00']
</script>

<template>
  <div class="noir">
    <header class="nr-nav">
      <span class="nr-logo">NOIR</span>
      <nav><a href="#nr-menu">{{ c.nav[0] }}</a><a href="#nr-story">{{ c.nav[1] }}</a><a href="#nr-res">{{ c.nav[2] }}</a></nav>
      <a class="nr-btn" href="#nr-res">{{ c.book }}</a>
    </header>

    <section class="nr-hero">
      <div class="nr-dust" aria-hidden="true">
        <i v-for="(d, i) in dust" :key="i" :style="{ left: d.left, animationDelay: d.delay, animationDuration: d.dur, width: d.size, height: d.size }" />
      </div>
      <svg class="nr-plate" viewBox="0 0 400 400" aria-hidden="true">
        <circle cx="200" cy="200" r="150" />
        <circle cx="200" cy="200" r="112" />
        <path d="M40 120 V280 M28 120 V170 Q28 185 40 190 Q52 185 52 170 V120" />
        <path d="M362 120 Q378 170 362 210 V280" />
        <path d="M160 200 Q200 150 240 200 Q200 240 160 200Z" />
      </svg>
      <p class="nr-kicker">{{ c.kicker }}</p>
      <h1 class="nr-title"><span v-for="(ch, i) in 'Noir'.split('')" :key="i" :style="{ '--i': i }">{{ ch }}</span></h1>
      <p class="nr-sub">{{ c.sub }}</p>
      <a href="#nr-menu" class="nr-scroll">{{ c.scroll }} <i /></a>
    </section>

    <section id="nr-menu" class="nr-section">
      <div class="nr-menu-head">
        <h2 v-reveal>{{ c.menuTitle }}</h2>
        <div class="nr-tabs" role="tablist">
          <button v-for="(tb, i) in c.tabs" :key="tb" role="tab" :aria-selected="tab === i" :class="{ on: tab === i }" @click="tab = i">{{ tb }}</button>
        </div>
      </div>
      <Transition name="nr-fade" mode="out-in">
        <ol :key="tab" class="nr-courses" @pointerleave="hover.i = -1">
          <li v-for="(co, i) in courses" :key="co[0]" :style="{ '--i': i }" @pointermove="move($event, i)">
            <span class="nr-num">{{ String(i + 1).padStart(2, '0') }}</span>
            <div><h3>{{ co[0] }}</h3><p>{{ co[1] }}</p></div>
            <span class="nr-dots" />
            <span class="nr-price">{{ priceOf(i) }}</span>
          </li>
        </ol>
      </Transition>
      <div class="nr-preview" :class="{ on: hover.i > -1 }" :style="{ transform: `translate(${hover.x}px, ${hover.y}px)`, '--plate': plateColors[(hover.i + tab * 2) % plateColors.length] }" aria-hidden="true" />
    </section>

    <section id="nr-story" class="nr-section nr-story">
      <p v-reveal class="nr-kicker">{{ c.storyKicker }}</p>
      <blockquote v-reveal style="--d: 100ms">“{{ c.quote }}”</blockquote>
      <p v-reveal class="nr-author" style="--d: 200ms">— {{ c.author }}</p>
      <dl class="nr-stats">
        <div v-for="(s, i) in c.stats" :key="s[1]" v-reveal :style="{ '--d': `${i * 120}ms` }"><dt>{{ s[0] }}</dt><dd>{{ s[1] }}</dd></div>
      </dl>
    </section>

    <section id="nr-res" class="nr-section nr-res">
      <h2 v-reveal>{{ c.resTitle }}</h2>
      <form v-reveal class="nr-form" @submit.prevent="res.sent = true">
        <label><span>{{ c.date }}</span><input v-model="res.date" type="date" required></label>
        <div class="nr-field">
          <span>{{ c.guests }}</span>
          <div class="nr-stepper">
            <button type="button" aria-label="−" @click="res.guests = Math.max(1, res.guests - 1)">−</button>
            <output>{{ res.guests }}</output>
            <button type="button" aria-label="+" @click="res.guests = Math.min(10, res.guests + 1)">+</button>
          </div>
        </div>
        <div class="nr-field">
          <span>{{ c.time }}</span>
          <div class="nr-times">
            <button v-for="tm in times" :key="tm" type="button" :class="{ on: res.time === tm }" @click="res.time = tm">{{ tm }}</button>
          </div>
        </div>
        <button class="nr-btn nr-submit" type="submit">{{ c.send }}</button>
        <Transition name="nr-fade"><p v-if="res.sent" class="nr-done" role="status">✦ {{ c.done }}</p></Transition>
      </form>
    </section>
    <footer class="nr-footer">NOIR · {{ c.kicker }}</footer>
  </div>
</template>

<style>
.noir {
  --gold: #C9A45C; --cream: #F3EBDD; --serif: 'Cormorant Garamond', Georgia, serif;
  background: #0E0D0B; color: var(--cream); min-height: 100vh; font-family: 'Manrope', system-ui, sans-serif; overflow-x: clip;
}
.nr-nav { position: sticky; top: 0; z-index: 20; display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 18px clamp(16px, 4vw, 48px); background: linear-gradient(#0E0D0B, rgba(14, 13, 11, 0)); }
.nr-logo { font-family: var(--serif); font-size: 1.6rem; letter-spacing: .5em; color: var(--gold); }
.nr-nav nav { display: flex; gap: 28px; font-size: .85rem; letter-spacing: .14em; text-transform: uppercase; }
.nr-nav nav a { opacity: .75; transition: opacity .3s, color .3s; }
.nr-nav nav a:hover { opacity: 1; color: var(--gold); }
.nr-btn { display: inline-block; padding: 12px 22px; border: 1px solid var(--gold); color: var(--gold); font-size: .8rem; letter-spacing: .16em; text-transform: uppercase; background: none; cursor: pointer; transition: background .4s, color .4s; }
.nr-btn:hover { background: var(--gold); color: #0E0D0B; }

.nr-hero { position: relative; min-height: 92vh; display: grid; place-content: center; justify-items: center; text-align: center; padding: 40px 16px 80px; overflow: hidden; }
.nr-plate { position: absolute; width: min(620px, 92vw); top: 50%; left: 50%; translate: -50% -52%; fill: none; stroke: var(--gold); stroke-width: 1.2; opacity: .55; }
.nr-plate * { stroke-dasharray: 1200; stroke-dashoffset: 1200; animation: nrDraw 3.2s cubic-bezier(.6, 0, .2, 1) forwards; }
.nr-plate *:nth-child(2) { animation-delay: .4s; }
.nr-plate *:nth-child(3), .nr-plate *:nth-child(4) { animation-delay: 1.1s; }
.nr-plate *:nth-child(5) { animation-delay: 1.6s; fill: rgba(201, 164, 92, .08); }
@keyframes nrDraw { to { stroke-dashoffset: 0; } }
.nr-dust { position: absolute; inset: 0; pointer-events: none; }
.nr-dust i { position: absolute; bottom: -10px; border-radius: 50%; background: var(--gold); opacity: 0; animation: nrRise linear infinite; box-shadow: 0 0 8px var(--gold); }
@keyframes nrRise { 0% { opacity: 0; transform: translateY(0); } 15% { opacity: .8; } 100% { opacity: 0; transform: translateY(-95vh); } }
.nr-kicker { position: relative; font-size: .78rem; letter-spacing: .3em; text-transform: uppercase; color: var(--gold); }
.nr-title { position: relative; font-family: var(--serif); font-weight: 500; font-size: clamp(6rem, 22vw, 17rem); line-height: .9; letter-spacing: .04em; margin: 10px 0; }
.nr-title span { display: inline-block; background: linear-gradient(180deg, #F7E7C4, var(--gold) 60%, #7A5D2A); -webkit-background-clip: text; background-clip: text; color: transparent; }
.js .nr-title span { opacity: 0; filter: blur(12px); transform: translateY(30px); animation: nrIn 1.4s cubic-bezier(.2, .8, .2, 1) forwards; animation-delay: calc(var(--i) * 160ms + 500ms); }
@keyframes nrIn { to { opacity: 1; filter: none; transform: none; } }
.nr-sub { position: relative; font-family: var(--serif); font-style: italic; font-size: clamp(1.3rem, 2.4vw, 1.9rem); max-width: 560px; opacity: .9; }
.nr-scroll { position: absolute; bottom: 28px; left: 50%; translate: -50% 0; display: grid; justify-items: center; gap: 10px; font-size: .72rem; letter-spacing: .25em; text-transform: uppercase; opacity: .7; }
.nr-scroll i { width: 1px; height: 46px; background: linear-gradient(var(--gold), transparent); animation: nrLine 2s ease-in-out infinite; transform-origin: top; }
@keyframes nrLine { 0% { transform: scaleY(0); } 50% { transform: scaleY(1); } 100% { transform: scaleY(1); opacity: 0; } }

.nr-section { padding: clamp(70px, 10vw, 130px) clamp(16px, 6vw, 96px); max-width: 1100px; margin: 0 auto; position: relative; }
.nr-section h2 { font-family: var(--serif); font-weight: 500; font-size: clamp(3rem, 8vw, 6rem); line-height: 1; color: var(--gold); }
.nr-menu-head { display: flex; justify-content: space-between; align-items: flex-end; gap: 20px; flex-wrap: wrap; margin-bottom: 40px; }
.nr-tabs { display: flex; border: 1px solid rgba(201, 164, 92, .4); }
.nr-tabs button { padding: 10px 20px; background: none; border: 0; color: var(--cream); cursor: pointer; letter-spacing: .12em; text-transform: uppercase; font-size: .78rem; transition: background .4s, color .4s; }
.nr-tabs button.on { background: var(--gold); color: #0E0D0B; }
.nr-courses li { display: grid; grid-template-columns: 50px auto 1fr auto; gap: 18px; align-items: baseline; padding: 22px 0; border-bottom: 1px solid rgba(243, 235, 221, .12); cursor: default; animation: nrRow .7s cubic-bezier(.2, .8, .2, 1) both; animation-delay: calc(var(--i) * 70ms); }
@keyframes nrRow { from { opacity: 0; transform: translateY(16px); } }
.nr-courses h3 { font-family: var(--serif); font-weight: 500; font-size: clamp(1.5rem, 3vw, 2.2rem); transition: color .3s, letter-spacing .4s; }
.nr-courses li:hover h3 { color: var(--gold); letter-spacing: .02em; }
.nr-courses p { font-size: .9rem; opacity: .6; font-style: italic; }
.nr-num { font-family: var(--serif); color: var(--gold); font-size: 1.1rem; }
.nr-dots { border-bottom: 1px dotted rgba(201, 164, 92, .5); transform: translateY(-6px); }
.nr-price { font-family: var(--serif); font-size: 1.3rem; color: var(--gold); white-space: nowrap; }
.nr-preview {
  position: fixed; top: -90px; left: 40px; z-index: 30; width: 180px; height: 180px; border-radius: 50%; pointer-events: none; opacity: 0; scale: .4;
  background: radial-gradient(circle at 40% 40%, var(--plate) 0 28%, color-mix(in srgb, var(--plate) 60%, #000) 29% 36%, #F5EFE4 37% 64%, #D9CDB8 65% 68%, transparent 69%);
  box-shadow: 0 0 0 1px var(--gold), 0 30px 60px -10px #000; transition: opacity .3s, scale .4s cubic-bezier(.2, .8, .2, 1), transform .15s linear, background .4s;
}
.nr-preview.on { opacity: 1; scale: 1; }
.nr-fade-enter-active, .nr-fade-leave-active { transition: opacity .35s, transform .35s; }
.nr-fade-enter-from, .nr-fade-leave-to { opacity: 0; transform: translateY(10px); }

.nr-story { text-align: center; }
.nr-story blockquote { font-family: var(--serif); font-style: italic; font-size: clamp(1.8rem, 4.5vw, 3.4rem); line-height: 1.2; margin: 20px auto; max-width: 900px; }
.nr-author { color: var(--gold); letter-spacing: .1em; }
.nr-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 60px; border-top: 1px solid rgba(201, 164, 92, .3); padding-top: 40px; }
.nr-stats dt { font-family: var(--serif); font-size: clamp(2.6rem, 6vw, 4.4rem); color: var(--gold); line-height: 1; }
.nr-stats dd { font-size: .8rem; letter-spacing: .14em; text-transform: uppercase; opacity: .7; margin-top: 8px; }

.nr-form { display: grid; gap: 22px; margin-top: 40px; max-width: 560px; }
.nr-form label, .nr-field { display: grid; gap: 10px; }
.nr-form span { font-size: .75rem; letter-spacing: .2em; text-transform: uppercase; color: var(--gold); }
.nr-form input { background: transparent; border: 0; border-bottom: 1px solid rgba(243, 235, 221, .3); color: var(--cream); padding: 10px 0; font-size: 1.1rem; color-scheme: dark; outline: none; }
.nr-form input:focus { border-color: var(--gold); }
.nr-stepper { display: flex; align-items: center; gap: 20px; }
.nr-stepper button { width: 44px; height: 44px; border-radius: 50%; border: 1px solid var(--gold); background: none; color: var(--gold); font-size: 1.3rem; cursor: pointer; transition: background .3s, color .3s; }
.nr-stepper button:hover { background: var(--gold); color: #0E0D0B; }
.nr-stepper output { font-family: var(--serif); font-size: 2rem; min-width: 30px; text-align: center; }
.nr-times { display: flex; gap: 10px; flex-wrap: wrap; }
.nr-times button { padding: 10px 18px; border: 1px solid rgba(243, 235, 221, .3); background: none; color: var(--cream); cursor: pointer; transition: all .3s; }
.nr-times button.on { border-color: var(--gold); background: rgba(201, 164, 92, .15); color: var(--gold); }
.nr-submit { justify-self: start; margin-top: 8px; }
.nr-done { font-family: var(--serif); font-style: italic; font-size: 1.3rem; color: var(--gold); }
.nr-footer { text-align: center; padding: 40px 16px 110px; font-size: .75rem; letter-spacing: .25em; text-transform: uppercase; opacity: .5; }
@media (max-width: 720px) {
  .nr-nav nav { display: none; }
  .nr-courses li { grid-template-columns: 34px 1fr auto; }
  .nr-dots { display: none; }
  .nr-stats { grid-template-columns: 1fr; }
}
@media (hover: none) { .nr-preview { display: none; } }
</style>
