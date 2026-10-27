<script setup lang="ts">
// Прототип «Slnečné Byty» — мобильное приложение (320×640): список → квартира → бронирование просмотра → готово
const props = defineProps<{ preview?: boolean }>()

const c = useConceptCopy({
  sk: { hello: 'Dobrý deň 👋', find: 'Nájdite svoj nový domov', filters: ['Všetky', '2-izb.', '3-izb.'], rooms: 'izb.', floor: 'posch.', plan: 'Pôdorys', book: 'Rezervovať obhliadku', day: 'Vyberte deň', time: 'Vyberte čas', confirm: 'Potvrdiť termín', doneTitle: 'Obhliadka je rezervovaná!', doneText: 'Pošleme vám SMS so všetkými detailmi.', done: 'Hotovo', home: 'Domov', favs: 'Obľúbené', profile: 'Profil', days: ['Po', 'Ut', 'St', 'Št', 'Pi'], noFav: 'Ťuknite na ♡ pri byte, ktorý sa vám páči.', sunny: 'slnečný' },
  cs: { hello: 'Dobrý den 👋', find: 'Najděte svůj nový domov', filters: ['Všechny', '2+kk', '3+kk'], rooms: 'pok.', floor: 'patro', plan: 'Půdorys', book: 'Rezervovat prohlídku', day: 'Vyberte den', time: 'Vyberte čas', confirm: 'Potvrdit termín', doneTitle: 'Prohlídka je rezervována!', doneText: 'Pošleme vám SMS se všemi detaily.', done: 'Hotovo', home: 'Domů', favs: 'Oblíbené', profile: 'Profil', days: ['Po', 'Út', 'St', 'Čt', 'Pá'], noFav: 'Ťukněte na ♡ u bytu, který se vám líbí.', sunny: 'slunný' },
  uk: { hello: 'Добрий день 👋', find: 'Знайдіть свій новий дім', filters: ['Усі', '2-кімн.', '3-кімн.'], rooms: 'кімн.', floor: 'пов.', plan: 'Планування', book: 'Забронювати перегляд', day: 'Оберіть день', time: 'Оберіть час', confirm: 'Підтвердити', doneTitle: 'Перегляд заброньовано!', doneText: 'Ми надішлемо SMS з усіма деталями.', done: 'Готово', home: 'Головна', favs: 'Обране', profile: 'Профіль', days: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт'], noFav: 'Натисніть ♡ біля квартири, яка сподобалась.', sunny: 'сонячна' },
})

const flats = [
  { id: 'A2.1', rooms: 2, area: 58, floor: 2, price: 189000, g: ['#FDE68A', '#F59E0B'] },
  { id: 'A3.4', rooms: 3, area: 79, floor: 3, price: 245000, g: ['#BFDBFE', '#60A5FA'] },
  { id: 'B1.2', rooms: 2, area: 61, floor: 1, price: 179000, g: ['#BBF7D0', '#34D399'] },
  { id: 'B4.1', rooms: 3, area: 86, floor: 4, price: 268000, g: ['#FBCFE8', '#F472B6'] },
]
const photos = [['#FEF3C7', '#FCD34D'], ['#E0F2FE', '#7DD3FC'], ['#F5F5F4', '#D6D3D1']]

const screen = ref<'list' | 'detail' | 'book' | 'done'>('list')
const tab = ref<'home' | 'favs'>('home')
const filter = ref(0)
const favs = ref<string[]>(['B1.2'])
const flat = ref(flats[0]!)
const photo = ref(0)
const day = ref(1)
const time = ref('16:00')
const times = ['10:00', '13:30', '16:00', '18:00']

const list = computed(() =>
  (tab.value === 'favs' ? flats.filter((f) => favs.value.includes(f.id)) : flats).filter((f) => filter.value === 0 || f.rooms === filter.value + 1)
)
const toggleFav = (id: string) => (favs.value = favs.value.includes(id) ? favs.value.filter((x) => x !== id) : [...favs.value, id])
const open = (f: (typeof flats)[number]) => { flat.value = f; photo.value = 0; screen.value = 'detail' }
const fmt = (n: number) => `${n.toLocaleString('sk-SK')} €`
</script>

<template>
  <div class="pb-phone" :class="{ 'is-preview': props.preview }" :inert="props.preview || undefined">
    <div class="pb-notch" />
    <div class="pb-status"><b>9:41</b><span>●●● ▮</span></div>

    <Transition name="pb-push" mode="out-in">
      <!-- Список -->
      <div v-if="screen === 'list'" key="list" class="pb-screen">
        <p class="pb-hello">{{ c.hello }}</p>
        <h3>{{ tab === 'favs' ? c.favs : c.find }}</h3>
        <div class="pb-chips">
          <button v-for="(f, i) in c.filters" :key="f" type="button" :class="{ on: filter === i }" @click="filter = i">{{ f }}</button>
        </div>
        <TransitionGroup name="pb-list" tag="div" class="pb-list">
          <article v-for="f in list" :key="f.id" class="pb-flat" @click="open(f)">
            <div class="pb-thumb" :style="{ background: `linear-gradient(135deg, ${f.g[0]}, ${f.g[1]})` }">
              <svg viewBox="0 0 60 40" aria-hidden="true"><path d="M8 38V16L30 4l22 12v22Z M24 38V26h12v12" fill="#fff" fill-opacity=".85" /></svg>
            </div>
            <div class="pb-info">
              <b>{{ f.id }} · {{ f.rooms }} {{ c.rooms }}</b>
              <span>{{ f.area }} m² · {{ f.floor }}. {{ c.floor }}</span>
              <em>{{ fmt(f.price) }}</em>
            </div>
            <button type="button" class="pb-heart" :class="{ on: favs.includes(f.id) }" :aria-label="c.favs" @click.stop="toggleFav(f.id)">{{ favs.includes(f.id) ? '♥' : '♡' }}</button>
          </article>
        </TransitionGroup>
        <p v-if="!list.length" class="pb-empty">{{ c.noFav }}</p>
      </div>

      <!-- Детали квартиры -->
      <div v-else-if="screen === 'detail'" key="detail" class="pb-screen pb-detail">
        <div class="pb-gallery" :style="{ background: `linear-gradient(160deg, ${photos[photo]![0]}, ${photos[photo]![1]})` }">
          <button type="button" class="pb-round pb-back" @click="screen = 'list'">←</button>
          <button type="button" class="pb-round pb-fav" :class="{ on: favs.includes(flat.id) }" @click="toggleFav(flat.id)">{{ favs.includes(flat.id) ? '♥' : '♡' }}</button>
          <svg viewBox="0 0 200 120" aria-hidden="true"><rect x="20" y="30" width="80" height="60" rx="4" fill="#fff" fill-opacity=".7" /><rect x="110" y="20" width="70" height="80" rx="4" fill="#fff" fill-opacity=".5" /><circle cx="160" cy="18" r="10" fill="#FCD34D" /></svg>
          <div class="pb-dots"><button v-for="(p, i) in photos" :key="i" type="button" :class="{ on: photo === i }" :aria-label="`${i + 1}`" @click="photo = i" /></div>
        </div>
        <div class="pb-body">
          <div class="pb-row"><h3>{{ flat.id }}</h3><em>{{ fmt(flat.price) }}</em></div>
          <div class="pb-specs"><span>🛏 {{ flat.rooms }} {{ c.rooms }}</span><span>📐 {{ flat.area }} m²</span><span>☀ {{ c.sunny }}</span></div>
          <p class="pb-label">{{ c.plan }}</p>
          <svg class="pb-plan" viewBox="0 0 200 90" aria-hidden="true"><rect x="2" y="2" width="196" height="86" rx="4" /><path d="M110 2V60M110 60H198" /><path v-if="flat.rooms === 3" d="M60 88V50H2" /></svg>
          <button type="button" class="pb-cta" @click="screen = 'book'">{{ c.book }}</button>
        </div>
      </div>

      <!-- Бронирование -->
      <div v-else-if="screen === 'book'" key="book" class="pb-screen">
        <button type="button" class="pb-round pb-back static" @click="screen = 'detail'">←</button>
        <h3>{{ c.book }}</h3>
        <p class="pb-label">{{ c.day }}</p>
        <div class="pb-days">
          <button v-for="(d, i) in c.days" :key="d" type="button" :class="{ on: day === i }" @click="day = i"><small>{{ d }}</small><b>{{ 3 + i }}</b></button>
        </div>
        <p class="pb-label">{{ c.time }}</p>
        <div class="pb-times"><button v-for="tm in times" :key="tm" type="button" :class="{ on: time === tm }" @click="time = tm">{{ tm }}</button></div>
        <button type="button" class="pb-cta" @click="screen = 'done'">{{ c.confirm }}</button>
      </div>

      <!-- Готово -->
      <div v-else key="done" class="pb-screen pb-done">
        <div class="pb-check"><svg viewBox="0 0 52 52"><circle cx="26" cy="26" r="24" /><path d="M15 27l7 7 15-16" /></svg></div>
        <h3>{{ c.doneTitle }}</h3>
        <p>{{ flat.id }} · {{ c.days[day] }} {{ 3 + day }}. · {{ time }}</p>
        <p class="pb-muted">{{ c.doneText }}</p>
        <button type="button" class="pb-cta" @click="screen = 'list'; tab = 'home'">{{ c.done }}</button>
      </div>
    </Transition>

    <nav class="pb-tabbar">
      <button type="button" :class="{ on: tab === 'home' && screen === 'list' }" @click="tab = 'home'; screen = 'list'">⌂<small>{{ c.home }}</small></button>
      <button type="button" :class="{ on: tab === 'favs' && screen === 'list' }" @click="tab = 'favs'; screen = 'list'">♡<small>{{ c.favs }} {{ favs.length }}</small></button>
      <button type="button">◯<small>{{ c.profile }}</small></button>
    </nav>
  </div>
</template>

<style>
.pb-phone { position: relative; width: 320px; height: 640px; border-radius: 44px; background: #FFFBF2; border: 10px solid #1C1917; box-shadow: 0 40px 80px -30px rgba(0, 0, 0, .5); overflow: hidden; font-family: 'Manrope', system-ui, sans-serif; color: #1C1917; text-align: left; display: flex; flex-direction: column; }
.pb-phone button { font: inherit; color: inherit; cursor: pointer; border: 0; }
.pb-notch { position: absolute; top: 8px; left: 50%; translate: -50% 0; width: 90px; height: 24px; border-radius: 20px; background: #1C1917; z-index: 5; }
.pb-status { display: flex; justify-content: space-between; padding: 12px 22px 4px; font-size: 12px; }
.pb-screen { flex: 1; padding: 10px 18px; overflow-y: auto; scrollbar-width: none; position: relative; }
.pb-hello { font-size: 13px; color: #78716C; }
.pb-screen h3 { font-size: 22px; line-height: 1.15; font-weight: 800; letter-spacing: -.02em; margin: 2px 0 12px; }
.pb-chips { display: flex; gap: 6px; margin-bottom: 12px; }
.pb-chips button { padding: 7px 12px; border-radius: 999px; background: #F5EEDC; font-size: 12px; font-weight: 700; transition: background .2s, color .2s; }
.pb-chips button.on { background: #1C1917; color: #FDE68A; }
.pb-list { display: grid; gap: 10px; }
.pb-flat { display: grid; grid-template-columns: 64px 1fr auto; gap: 10px; align-items: center; padding: 8px; border-radius: 18px; background: #fff; box-shadow: 0 6px 18px -12px rgba(0, 0, 0, .3); cursor: pointer; transition: transform .2s; }
.pb-flat:hover { transform: scale(1.02); }
.pb-thumb { height: 64px; border-radius: 14px; display: grid; place-items: center; }
.pb-thumb svg { width: 40px; }
.pb-info { display: grid; font-size: 12px; }
.pb-info b { font-size: 14px; }
.pb-info span { color: #78716C; }
.pb-info em { font-style: normal; font-weight: 800; color: #B45309; }
.pb-heart { width: 34px; height: 34px; border-radius: 50%; background: #F5EEDC !important; font-size: 16px; transition: transform .25s cubic-bezier(.34, 1.56, .64, 1); }
.pb-heart.on, .pb-fav.on { color: #E11D48 !important; transform: scale(1.15); }
.pb-empty { font-size: 13px; color: #78716C; text-align: center; margin-top: 30px; }
.pb-list-enter-active, .pb-list-leave-active { transition: all .3s; }
.pb-list-enter-from, .pb-list-leave-to { opacity: 0; transform: translateX(20px); }
.pb-detail { padding: 0; }
.pb-gallery { position: relative; height: 200px; display: grid; place-items: center; transition: background .4s; }
.pb-gallery svg { width: 70%; }
.pb-round { position: absolute; top: 12px; width: 36px; height: 36px; border-radius: 50%; background: #fff !important; font-size: 16px; box-shadow: 0 4px 12px -6px rgba(0, 0, 0, .4); }
.pb-back { left: 14px; }
.pb-back.static { position: static; margin-bottom: 10px; }
.pb-fav { right: 14px; }
.pb-dots { position: absolute; bottom: 10px; display: flex; gap: 6px; }
.pb-dots button { width: 8px; height: 8px; border-radius: 4px; background: rgba(255, 255, 255, .6) !important; transition: width .3s; padding: 0; }
.pb-dots button.on { width: 22px; background: #fff !important; }
.pb-body { padding: 14px 18px; }
.pb-row { display: flex; justify-content: space-between; align-items: baseline; }
.pb-row h3 { margin: 0; }
.pb-row em { font-style: normal; font-weight: 800; color: #B45309; }
.pb-specs { display: flex; gap: 6px; flex-wrap: wrap; margin: 8px 0 12px; }
.pb-specs span { font-size: 11px; padding: 5px 9px; border-radius: 999px; background: #F5EEDC; font-weight: 700; }
.pb-label { font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: .1em; color: #A8A29E; margin: 10px 0 8px; }
.pb-plan { width: 100%; fill: #fff; stroke: #1C1917; stroke-width: 2.5; }
.pb-cta { width: 100%; margin-top: 14px; padding: 14px; border-radius: 16px; background: #1C1917 !important; color: #FDE68A !important; font-weight: 800; font-size: 14px; transition: transform .2s; }
.pb-cta:active { transform: scale(.97); }
.pb-days { display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; }
.pb-days button { display: grid; padding: 8px 0; border-radius: 14px; background: #fff; box-shadow: inset 0 0 0 1px #EDE5D3; transition: all .2s; }
.pb-days small { font-size: 11px; color: #78716C; }
.pb-days b { font-size: 17px; }
.pb-days button.on { background: #FDE68A; box-shadow: inset 0 0 0 2px #1C1917; }
.pb-times { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.pb-times button { padding: 10px; border-radius: 12px; background: #fff; box-shadow: inset 0 0 0 1px #EDE5D3; font-weight: 700; }
.pb-times button.on { background: #1C1917; color: #FDE68A; }
.pb-done { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
.pb-done p { font-weight: 700; }
.pb-muted { color: #78716C; font-weight: 500 !important; font-size: 13px; margin-top: 6px; }
.pb-check svg { width: 90px; fill: none; stroke: #16A34A; stroke-width: 3; stroke-linecap: round; stroke-linejoin: round; }
.pb-check circle { stroke-dasharray: 160; stroke-dashoffset: 160; animation: nrDraw .7s ease forwards; }
.pb-check path { stroke-dasharray: 40; stroke-dashoffset: 40; animation: nrDraw .4s .6s ease forwards; }
.pb-tabbar { display: grid; grid-template-columns: repeat(3, 1fr); padding: 8px 10px 16px; background: #fff; border-top: 1px solid #F0E8D6; }
.pb-tabbar button { display: grid; justify-items: center; background: none; font-size: 18px; color: #A8A29E !important; }
.pb-tabbar small { font-size: 10px; font-weight: 700; }
.pb-tabbar button.on { color: #1C1917 !important; }
.pb-push-enter-active, .pb-push-leave-active { transition: opacity .25s, transform .3s cubic-bezier(.2, .8, .2, 1); }
.pb-push-enter-from { opacity: 0; transform: translateX(30px); }
.pb-push-leave-to { opacity: 0; transform: translateX(-30px); }
.pb-phone.is-preview { pointer-events: none; }
</style>
