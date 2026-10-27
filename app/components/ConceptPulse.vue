<script setup lang="ts">
// Концепт «Pulse» — SaaS / AI-аналитика: стекло, mesh-градиент, «живой» дашборд, AI-чат, переключатель цен
const c = useConceptCopy({
  sk: {
    nav: ['Funkcie', 'AI asistent', 'Cenník'], login: 'Prihlásiť', start: 'Vyskúšať zadarmo',
    badge: 'Nové: AI asistent v1.0', title: ['Vaše dáta.', 'Odpovede za', 'sekundy.'],
    sub: 'Pulse spojí predaj, marketing a sklad do jedného dashboardu — a AI vám povie, čo robiť ďalej.',
    emailPh: 'vas@email.sk', cta: 'Začať zadarmo', note: '14 dní zdarma · bez platobnej karty',
    dash: { revenue: 'Tržby dnes', orders: 'Objednávky', conv: 'Konverzia', live: 'Live', alert: 'AI: Bundle B rastie o 18 % — navýšte rozpočet' },
    logos: 'Dôverujú nám tímy z firiem',
    featTitle: 'Všetko, čo tím potrebuje.',
    feats: [['Živé metriky', 'Dáta sa aktualizujú v reálnom čase, bez obnovovania stránky.'], ['Prepojenia', 'Shopify, Stripe, Google Ads a 40+ ďalších služieb.'], ['Automatické reporty', 'Každý pondelok ráno priamo v e-maile.'], ['Upozornenia', 'Keď sa niečo pokazí, dozviete sa to ako prví.']],
    chatTitle: 'Opýtajte sa svojich dát.', chatSub: 'Ukážka AI asistenta — vyberte otázku:',
    qa: [
      ['Ktorý produkt rastie najrýchlejšie?', 'Bundle B: +18 % za týždeň. Najviac predajov prišlo z kampane na Instagrame — odporúčam navýšiť jej rozpočet o 10 %.'],
      ['Prečo klesla konverzia v utorok?', 'V utorok sa checkout načítaval o 2,1 s dlhšie. Po oprave sa konverzia vrátila na 3,4 %.'],
      ['Priprav report pre šéfa', 'Hotovo ✓ Report za október je v e-maile: tržby +12 %, dva nové segmenty zákazníkov a 3 odporúčania na november.'],
    ],
    chatPh: 'Napíšte otázku…', chatNote: 'Odpovede sú simulované — ide o ukážku dizajnu.',
    priceTitle: 'Jednoduchý cenník.', monthly: 'Mesačne', yearly: 'Ročne', save: '−20 %', per: '/ mes.', choose: 'Vybrať plán', popular: 'Najobľúbenejší',
    plans: [['Start', 19, ['1 projekt', 'Základné metriky', 'E-mailové reporty']], ['Pro', 49, ['5 projektov', 'AI asistent', 'Všetky prepojenia', 'Upozornenia']], ['Team', 129, ['Neobmedzené projekty', 'Roly a prístupy', 'Prioritná podpora']]],
  },
  cs: {
    nav: ['Funkce', 'AI asistent', 'Ceník'], login: 'Přihlásit', start: 'Vyzkoušet zdarma',
    badge: 'Novinka: AI asistent v1.0', title: ['Vaše data.', 'Odpovědi za', 'sekundy.'],
    sub: 'Pulse propojí prodej, marketing a sklad do jednoho dashboardu — a AI vám řekne, co dělat dál.',
    emailPh: 'vas@email.cz', cta: 'Začít zdarma', note: '14 dní zdarma · bez platební karty',
    dash: { revenue: 'Tržby dnes', orders: 'Objednávky', conv: 'Konverze', live: 'Live', alert: 'AI: Bundle B roste o 18 % — navyšte rozpočet' },
    logos: 'Důvěřují nám týmy z firem',
    featTitle: 'Vše, co tým potřebuje.',
    feats: [['Živé metriky', 'Data se aktualizují v reálném čase, bez obnovování stránky.'], ['Propojení', 'Shopify, Stripe, Google Ads a 40+ dalších služeb.'], ['Automatické reporty', 'Každé pondělí ráno přímo v e-mailu.'], ['Upozornění', 'Když se něco pokazí, dozvíte se to jako první.']],
    chatTitle: 'Zeptejte se svých dat.', chatSub: 'Ukázka AI asistenta — vyberte otázku:',
    qa: [
      ['Který produkt roste nejrychleji?', 'Bundle B: +18 % za týden. Nejvíc prodejů přišlo z kampaně na Instagramu — doporučuji navýšit její rozpočet o 10 %.'],
      ['Proč klesla konverze v úterý?', 'V úterý se checkout načítal o 2,1 s déle. Po opravě se konverze vrátila na 3,4 %.'],
      ['Připrav report pro šéfa', 'Hotovo ✓ Report za říjen je v e-mailu: tržby +12 %, dva nové segmenty zákazníků a 3 doporučení na listopad.'],
    ],
    chatPh: 'Napište otázku…', chatNote: 'Odpovědi jsou simulované — jde o ukázku designu.',
    priceTitle: 'Jednoduchý ceník.', monthly: 'Měsíčně', yearly: 'Ročně', save: '−20 %', per: '/ měs.', choose: 'Vybrat plán', popular: 'Nejoblíbenější',
    plans: [['Start', 19, ['1 projekt', 'Základní metriky', 'E-mailové reporty']], ['Pro', 49, ['5 projektů', 'AI asistent', 'Všechna propojení', 'Upozornění']], ['Team', 129, ['Neomezené projekty', 'Role a přístupy', 'Prioritní podpora']]],
  },
  uk: {
    nav: ['Можливості', 'AI-асистент', 'Ціни'], login: 'Увійти', start: 'Спробувати безкоштовно',
    badge: 'Новинка: AI-асистент v1.0', title: ['Ваші дані.', 'Відповіді за', 'секунди.'],
    sub: 'Pulse обʼєднує продажі, маркетинг і склад в одному дашборді — а AI підкаже, що робити далі.',
    emailPh: 'vash@email.com', cta: 'Почати безкоштовно', note: '14 днів безкоштовно · без картки',
    dash: { revenue: 'Виручка сьогодні', orders: 'Замовлення', conv: 'Конверсія', live: 'Live', alert: 'AI: Bundle B росте на 18 % — збільште бюджет' },
    logos: 'Нам довіряють команди з компаній',
    featTitle: 'Усе, що потрібно команді.',
    feats: [['Живі метрики', 'Дані оновлюються в реальному часі без перезавантаження.'], ['Інтеграції', 'Shopify, Stripe, Google Ads і ще 40+ сервісів.'], ['Автозвіти', 'Щопонеділка зранку просто на e-mail.'], ['Сповіщення', 'Якщо щось зламається — ви дізнаєтеся першими.']],
    chatTitle: 'Запитайте свої дані.', chatSub: 'Демо AI-асистента — оберіть запитання:',
    qa: [
      ['Який товар росте найшвидше?', 'Bundle B: +18 % за тиждень. Найбільше продажів дала кампанія в Instagram — раджу збільшити її бюджет на 10 %.'],
      ['Чому впала конверсія у вівторок?', 'У вівторок checkout завантажувався на 2,1 с довше. Після виправлення конверсія повернулася до 3,4 %.'],
      ['Підготуй звіт для шефа', 'Готово ✓ Звіт за жовтень уже на пошті: виручка +12 %, два нові сегменти клієнтів і 3 поради на листопад.'],
    ],
    chatPh: 'Напишіть запитання…', chatNote: 'Відповіді змодельовані — це демо дизайну.',
    priceTitle: 'Прості ціни.', monthly: 'Щомісяця', yearly: 'Щороку', save: '−20 %', per: '/ міс.', choose: 'Обрати план', popular: 'Найпопулярніший',
    plans: [['Start', 19, ['1 проєкт', 'Базові метрики', 'Звіти на e-mail']], ['Pro', 49, ['5 проєктів', 'AI-асистент', 'Усі інтеграції', 'Сповіщення']], ['Team', 129, ['Без обмежень', 'Ролі та доступи', 'Пріоритетна підтримка']]],
  },
})

const { $motion } = useNuxtApp()
const logos = ['Northwind', 'Lumio', 'Kaskada', 'Orbita', 'Fjord', 'Nimbus', 'Vektor']

// --- «Живой» дашборд: график и цифры обновляются
// Округляем до десятых: иначе сервер и браузер дают разные дробные хвосты и ломается гидратация
const points = ref(Array.from({ length: 24 }, (_, i) => Math.round((40 + Math.sin(i / 2.4) * 14 + i * 1.6) * 10) / 10))
const revenue = ref(12480)
const orders = ref(312)
const conv = ref(3.4)
const linePath = computed(() =>
  points.value.map((v, i) => `${i === 0 ? 'M' : 'L'}${((i / 23) * 300).toFixed(1)} ${(110 - v).toFixed(1)}`).join(' ')
)
const areaPath = computed(() => `${linePath.value} L300 120 L0 120 Z`)
let tick: ReturnType<typeof setInterval> | undefined

// --- Цены
const yearly = ref(false)
const price = (base: number) => (yearly.value ? Math.round(base * 0.8) : base)

// --- AI-чат (симуляция)
type Msg = { me: boolean; text: string }
const messages = ref<Msg[]>([])
const typing = ref(false)
const busy = ref(false)
const chatBox = ref<HTMLElement>()
async function ask(i: number) {
  if (busy.value) return
  busy.value = true
  const pair = c.value.qa[i]!
  const q = pair[0]!
  const a = pair[1]!
  messages.value.push({ me: true, text: q })
  typing.value = true
  await new Promise((r) => setTimeout(r, 900))
  typing.value = false
  const msg: Msg = { me: false, text: '' }
  messages.value.push(msg)
  const reply = messages.value[messages.value.length - 1]!
  for (const ch of a) {
    reply.text += ch
    await new Promise((r) => setTimeout(r, $motion.reduce ? 0 : 14))
    chatBox.value?.scrollTo({ top: chatBox.value.scrollHeight })
  }
  busy.value = false
}

onMounted(() => {
  if ($motion.reduce) return
  tick = setInterval(() => {
    const last = points.value[points.value.length - 1]!
    const nextV = Math.max(18, Math.min(98, last + (Math.random() - 0.42) * 12))
    points.value = [...points.value.slice(1), nextV]
    revenue.value += Math.round(Math.random() * 180)
    if (Math.random() > 0.5) orders.value += 1
    conv.value = Math.round((3.2 + Math.random() * 0.5) * 10) / 10
  }, 1400)
})
onBeforeUnmount(() => clearInterval(tick))
const fmt = (n: number) => n.toLocaleString('sk-SK')
</script>

<template>
  <div class="pulse">
    <div class="pl-mesh" aria-hidden="true"><i /><i /><i /><i /></div>

    <header class="pl-nav">
      <span class="pl-logo"><b /> Pulse</span>
      <nav><a href="#pl-feat">{{ c.nav[0] }}</a><a href="#pl-chat">{{ c.nav[1] }}</a><a href="#pl-price">{{ c.nav[2] }}</a></nav>
      <div class="pl-nav-r"><a href="#pl-price" class="pl-link">{{ c.login }}</a><a href="#pl-price" class="pl-btn">{{ c.start }}</a></div>
    </header>

    <section class="pl-hero">
      <div class="pl-copy">
        <p class="pl-badge fade-in"><span>✦</span> {{ c.badge }}</p>
        <h1>
          <span v-for="(line, i) in c.title" :key="i" class="pl-line" :class="{ grad: i === 2 }" :style="{ '--i': i }">{{ line }}</span>
        </h1>
        <p class="pl-sub fade-in" style="--d: 500ms">{{ c.sub }}</p>
        <form class="pl-signup fade-in" style="--d: 650ms" @submit.prevent>
          <input type="email" :placeholder="c.emailPh" :aria-label="c.emailPh">
          <button class="pl-btn" type="submit">{{ c.cta }}</button>
        </form>
        <p class="pl-note fade-in" style="--d: 750ms">{{ c.note }}</p>
      </div>

      <div v-tilt class="pl-dash tilt fade-in" data-tilt="6" style="--d: 300ms" aria-hidden="true">
        <div class="pl-dash-top"><span>{{ c.dash.revenue }}</span><em><i /> {{ c.dash.live }}</em></div>
        <p class="pl-big">€ {{ fmt(revenue) }}</p>
        <svg viewBox="0 0 300 120" preserveAspectRatio="none" class="pl-chart">
          <defs><linearGradient id="plg" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#5B4BFF" stop-opacity=".35" /><stop offset="1" stop-color="#22D3EE" stop-opacity="0" /></linearGradient></defs>
          <path :d="areaPath" fill="url(#plg)" />
          <path :d="linePath" fill="none" stroke="#5B4BFF" stroke-width="2.5" stroke-linejoin="round" />
        </svg>
        <div class="pl-kpis">
          <div><span>{{ c.dash.orders }}</span><b>{{ orders }}</b></div>
          <div><span>{{ c.dash.conv }}</span><b>{{ conv }} %</b></div>
        </div>
        <div class="pl-toast">✦ {{ c.dash.alert }}</div>
      </div>
    </section>

    <div class="pl-logos">
      <p>{{ c.logos }}</p>
      <div class="pl-logos-row"><span v-for="l in logos" :key="l">{{ l }}</span></div>
    </div>

    <section id="pl-feat" class="pl-section">
      <h2 v-reveal>{{ c.featTitle }}</h2>
      <div class="pl-bento">
        <article v-for="(f, i) in c.feats" :key="f[0]" v-reveal v-spot class="pl-card" :class="`pl-card-${i}`" :style="{ '--d': `${i * 90}ms` }">
          <div class="pl-visual" aria-hidden="true">
            <template v-if="i === 0"><span v-for="n in 8" :key="n" class="pl-bar" :style="{ '--h': `${30 + ((n * 37) % 60)}%`, '--n': n }" /></template>
            <template v-else-if="i === 1"><span v-for="n in 6" :key="n" class="pl-node" :style="{ '--n': n }" /><span class="pl-hub">P</span></template>
            <template v-else-if="i === 2"><span class="pl-mail">✉</span><span class="pl-mail-line" /><span class="pl-mail-line s" /></template>
            <template v-else><span class="pl-bell">🔔</span><span class="pl-ping" /></template>
          </div>
          <h3>{{ f[0] }}</h3>
          <p>{{ f[1] }}</p>
        </article>
      </div>
    </section>

    <section id="pl-chat" class="pl-section pl-chat-wrap">
      <div>
        <h2 v-reveal>{{ c.chatTitle }}</h2>
        <p v-reveal class="pl-sub">{{ c.chatSub }}</p>
        <div class="pl-qs">
          <button v-for="(q, i) in c.qa" :key="q[0]" type="button" :disabled="busy" @click="ask(i)">{{ q[0] }} →</button>
        </div>
      </div>
      <div v-reveal class="pl-chat">
        <div class="pl-chat-head"><b /> Pulse AI <small>online</small></div>
        <div ref="chatBox" class="pl-msgs" aria-live="polite">
          <p v-for="(m, i) in messages" :key="i" :class="m.me ? 'me' : 'ai'">{{ m.text }}</p>
          <p v-if="typing" class="ai pl-typing"><i /><i /><i /></p>
        </div>
        <div class="pl-input"><span>{{ c.chatPh }}</span><b>↑</b></div>
        <small class="pl-chat-note">{{ c.chatNote }}</small>
      </div>
    </section>

    <section id="pl-price" class="pl-section">
      <h2 v-reveal>{{ c.priceTitle }}</h2>
      <div class="pl-toggle" role="group">
        <button type="button" :class="{ on: !yearly }" @click="yearly = false">{{ c.monthly }}</button>
        <button type="button" :class="{ on: yearly }" @click="yearly = true">{{ c.yearly }} <em>{{ c.save }}</em></button>
      </div>
      <div class="pl-plans">
        <article v-for="(p, i) in c.plans" :key="p[0] as string" v-reveal class="pl-plan" :class="{ hot: i === 1 }" :style="{ '--d': `${i * 100}ms` }">
          <span v-if="i === 1" class="pl-pop">{{ c.popular }}</span>
          <h3>{{ p[0] }}</h3>
          <p class="pl-price"><Transition name="pl-num" mode="out-in"><b :key="price(p[1] as number)">€{{ price(p[1] as number) }}</b></Transition> {{ c.per }}</p>
          <ul><li v-for="f in (p[2] as string[])" :key="f">✓ {{ f }}</li></ul>
          <a href="#pl-price" class="pl-btn" :class="{ ghost: i !== 1 }">{{ c.choose }}</a>
        </article>
      </div>
    </section>
    <footer class="pl-footer">© Pulse Analytics — {{ c.chatNote }}</footer>
  </div>
</template>

<style>
.pulse { position: relative; min-height: 100vh; background: #F5F7FF; color: #0F1222; font-family: 'Manrope', system-ui, sans-serif; overflow-x: clip; isolation: isolate; }
.pl-mesh { position: absolute; inset: 0 0 auto; height: 1100px; z-index: -1; pointer-events: none; }
.pl-mesh i { position: absolute; border-radius: 50%; filter: blur(90px); opacity: .55; }
.pl-mesh i:nth-child(1) { width: 600px; height: 600px; background: #A5B4FC; top: -200px; left: -100px; animation: float1 18s ease-in-out infinite; }
.pl-mesh i:nth-child(2) { width: 500px; height: 500px; background: #67E8F9; top: 0; right: -120px; animation: float2 22s ease-in-out infinite; }
.pl-mesh i:nth-child(3) { width: 420px; height: 420px; background: #F9A8D4; top: 420px; left: 30%; animation: float3 20s ease-in-out infinite; }
.pl-mesh i:nth-child(4) { width: 300px; height: 300px; background: #C4B5FD; top: 600px; right: 10%; animation: float1 26s ease-in-out infinite reverse; }

.pl-nav { display: flex; align-items: center; justify-content: space-between; gap: 16px; max-width: 1180px; margin: 16px auto 0; padding: 10px 12px 10px 20px; border-radius: 18px; background: rgba(255, 255, 255, .6); border: 1px solid rgba(255, 255, 255, .8); -webkit-backdrop-filter: blur(14px); backdrop-filter: blur(14px); width: calc(100% - 32px); }
.pl-logo { display: flex; align-items: center; gap: 10px; font-family: var(--font-display); font-weight: 600; font-size: 1.2rem; }
.pl-logo b { width: 26px; height: 26px; border-radius: 8px; background: linear-gradient(135deg, #5B4BFF, #22D3EE); box-shadow: 0 6px 16px -6px #5B4BFF; }
.pl-nav nav { display: flex; gap: 26px; font-weight: 600; font-size: .92rem; color: #4B5070; }
.pl-nav nav a:hover { color: #5B4BFF; }
.pl-nav-r { display: flex; align-items: center; gap: 14px; }
.pl-link { font-weight: 700; font-size: .92rem; }
.pl-btn { display: inline-flex; align-items: center; justify-content: center; padding: 12px 20px; border-radius: 12px; border: 0; cursor: pointer; background: linear-gradient(135deg, #5B4BFF, #7C6CFF); color: #fff; font-weight: 700; font-size: .92rem; box-shadow: 0 10px 24px -10px #5B4BFF; transition: transform .3s var(--ease), box-shadow .3s; }
.pl-btn:hover { transform: translateY(-2px); box-shadow: 0 16px 30px -10px #5B4BFF; }
.pl-btn.ghost { background: #fff; color: #0F1222; box-shadow: inset 0 0 0 1px #DDE1F3; }

.pl-hero { display: grid; grid-template-columns: 1.05fr .95fr; gap: 56px; align-items: center; max-width: 1180px; margin: 0 auto; padding: clamp(60px, 9vw, 110px) 16px 60px; }
.pl-badge { display: inline-flex; gap: 8px; align-items: center; padding: 6px 14px; border-radius: 999px; background: rgba(255, 255, 255, .7); border: 1px solid #E0E4F7; font-weight: 700; font-size: .85rem; }
.pl-badge span { color: #5B4BFF; }
.pl-hero h1 { font-family: var(--font-display); font-weight: 600; font-size: clamp(2.4rem, 4.6vw, 4rem); line-height: 1.04; letter-spacing: -.04em; margin: 22px 0; }
.pl-line { display: block; }
.js .pl-line { opacity: 0; transform: translateY(24px); animation: fadeUp .9s var(--ease) forwards; animation-delay: calc(var(--i) * 130ms + 150ms); }
.pl-line.grad { background: linear-gradient(90deg, #5B4BFF, #22D3EE, #EC4899, #5B4BFF); background-size: 300% 100%; -webkit-background-clip: text; background-clip: text; color: transparent; animation: fadeUp .9s var(--ease) forwards, shine 6s linear infinite; animation-delay: .41s, 0s; }
.pl-sub { font-size: 1.12rem; color: #4B5070; max-width: 520px; }
.pl-signup { display: flex; gap: 8px; margin-top: 28px; padding: 6px; border-radius: 16px; background: #fff; border: 1px solid #E0E4F7; max-width: 480px; box-shadow: 0 20px 40px -24px rgba(40, 40, 120, .35); }
.pl-signup input { flex: 1; min-width: 0; border: 0; outline: none; padding: 0 12px; font-size: 1rem; background: none; }
.pl-note { margin-top: 12px; font-size: .85rem; color: #7A7F9A; }

.pl-dash { position: relative; padding: 24px; border-radius: 24px; background: rgba(255, 255, 255, .75); border: 1px solid rgba(255, 255, 255, .9); -webkit-backdrop-filter: blur(18px); backdrop-filter: blur(18px); box-shadow: 0 40px 80px -30px rgba(40, 40, 140, .4); }
.pl-dash-top { display: flex; justify-content: space-between; font-weight: 700; color: #4B5070; font-size: .9rem; }
.pl-dash-top em { display: inline-flex; align-items: center; gap: 6px; font-style: normal; color: #16A34A; }
.pl-dash-top em i { width: 8px; height: 8px; border-radius: 50%; background: #22C55E; animation: pulse 2s infinite; }
.pl-big { font-family: var(--font-display); font-size: 2.4rem; font-weight: 600; letter-spacing: -.03em; margin: 6px 0 10px; font-variant-numeric: tabular-nums; }
.pl-chart { width: 100%; height: 150px; }
.pl-chart path { transition: d 1.2s var(--ease); }
.pl-kpis { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 12px; }
.pl-kpis div { padding: 14px; border-radius: 14px; background: #F3F4FD; }
.pl-kpis span { display: block; font-size: .8rem; color: #7A7F9A; font-weight: 700; }
.pl-kpis b { font-size: 1.4rem; font-variant-numeric: tabular-nums; }
.pl-toast { position: absolute; left: -30px; bottom: -22px; padding: 12px 16px; border-radius: 14px; background: #0F1222; color: #fff; font-weight: 700; font-size: .85rem; box-shadow: 0 20px 40px -16px rgba(0, 0, 0, .5); animation: bob 5s ease-in-out infinite; max-width: 320px; }

.pl-logos { text-align: center; padding: 40px 16px 20px; }
.pl-logos p { font-weight: 700; color: #7A7F9A; font-size: .85rem; letter-spacing: .08em; text-transform: uppercase; }
.pl-logos-row { display: flex; flex-wrap: wrap; justify-content: center; gap: 18px 44px; margin-top: 18px; }
.pl-logos-row span { font-family: var(--font-display); font-size: 1.35rem; font-weight: 600; color: #A3A8C3; transition: color .3s; }
.pl-logos-row span:hover { color: #5B4BFF; }

.pl-section { max-width: 1180px; margin: 0 auto; padding: clamp(70px, 9vw, 120px) 16px 0; }
.pl-section h2 { font-family: var(--font-display); font-weight: 600; font-size: clamp(2rem, 4.4vw, 3.4rem); letter-spacing: -.035em; margin-bottom: 36px; }
.pl-bento { display: grid; grid-template-columns: 1.4fr 1fr 1fr; grid-template-rows: auto auto; gap: 18px; }
.pl-card { --mx: 50%; --my: 50%; position: relative; padding: 26px; border-radius: 24px; background: rgba(255, 255, 255, .8); border: 1px solid #E6E9F8; overflow: hidden; transition: box-shadow .4s, transform .4s var(--ease); }
.pl-card::before { content: ''; position: absolute; inset: 0; background: radial-gradient(360px circle at var(--mx) var(--my), rgba(91, 75, 255, .12), transparent 45%); opacity: 0; transition: opacity .4s; }
.pl-card:hover::before { opacity: 1; }
.pl-card:hover { box-shadow: 0 30px 60px -30px rgba(40, 40, 140, .35); }
.pl-card-0 { grid-row: span 2; }
.pl-card-3 { grid-column: span 2; }
.pl-card h3 { font-size: 1.2rem; margin: 18px 0 6px; position: relative; }
.pl-card p { color: #4B5070; position: relative; }
.pl-visual { position: relative; height: 140px; border-radius: 16px; background: #F3F4FD; display: flex; align-items: flex-end; justify-content: center; gap: 8px; padding: 16px; overflow: hidden; }
.pl-card-0 .pl-visual { height: 260px; }
.pl-bar { width: 22px; height: var(--h); border-radius: 6px 6px 2px 2px; background: linear-gradient(#5B4BFF, #22D3EE); transform-origin: bottom; animation: plBar 2.4s ease-in-out infinite; animation-delay: calc(var(--n) * 120ms); }
@keyframes plBar { 50% { transform: scaleY(.6); } }
.pl-card-1 .pl-visual { align-items: center; }
.pl-hub { position: relative; z-index: 1; width: 48px; height: 48px; border-radius: 14px; display: grid; place-items: center; background: linear-gradient(135deg, #5B4BFF, #22D3EE); color: #fff; font-weight: 800; }
.pl-node { position: absolute; top: 50%; left: 50%; width: 16px; height: 16px; border-radius: 50%; background: #fff; border: 3px solid #5B4BFF; transform: rotate(calc(var(--n) * 60deg)) translateX(56px); animation: plOrbit 12s linear infinite; }
@keyframes plOrbit { to { transform: rotate(calc(var(--n) * 60deg + 360deg)) translateX(56px); } }
.pl-card-2 .pl-visual { flex-direction: column; align-items: flex-start; justify-content: center; }
.pl-mail { font-size: 2rem; animation: bob 4s ease-in-out infinite; }
.pl-mail-line { display: block; width: 70%; height: 8px; border-radius: 4px; background: #DDE1F3; }
.pl-mail-line.s { width: 45%; }
.pl-card-3 .pl-visual { align-items: center; }
.pl-bell { font-size: 2.4rem; animation: wiggle 2s ease-in-out infinite; position: relative; z-index: 1; }
.pl-ping { position: absolute; width: 60px; height: 60px; border-radius: 50%; border: 2px solid #EC4899; animation: plPing 2s ease-out infinite; }
@keyframes plPing { from { transform: scale(.6); opacity: 1; } to { transform: scale(2.4); opacity: 0; } }

.pl-chat-wrap { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; align-items: center; }
.pl-qs { display: grid; gap: 10px; margin-top: 24px; }
.pl-qs button { text-align: left; padding: 14px 18px; border-radius: 14px; border: 1px solid #E0E4F7; background: #fff; font-weight: 700; cursor: pointer; transition: border-color .3s, transform .3s var(--ease), color .3s; }
.pl-qs button:hover:not(:disabled) { border-color: #5B4BFF; color: #5B4BFF; transform: translateX(6px); }
.pl-qs button:disabled { opacity: .5; cursor: wait; }
.pl-chat { border-radius: 24px; background: #fff; border: 1px solid #E6E9F8; box-shadow: 0 40px 80px -40px rgba(40, 40, 140, .4); overflow: hidden; }
.pl-chat-head { display: flex; align-items: center; gap: 10px; padding: 16px 20px; border-bottom: 1px solid #EEF0FA; font-weight: 800; }
.pl-chat-head b { width: 28px; height: 28px; border-radius: 50%; background: linear-gradient(135deg, #5B4BFF, #22D3EE); }
.pl-chat-head small { color: #16A34A; font-weight: 700; }
.pl-msgs { height: 300px; overflow-y: auto; padding: 18px; display: flex; flex-direction: column; gap: 10px; }
.pl-msgs p { max-width: 85%; padding: 12px 16px; border-radius: 18px; font-size: .95rem; animation: fadeUp .4s var(--ease); }
.pl-msgs .me { align-self: flex-end; background: linear-gradient(135deg, #5B4BFF, #7C6CFF); color: #fff; border-bottom-right-radius: 6px; }
.pl-msgs .ai { align-self: flex-start; background: #F3F4FD; border-bottom-left-radius: 6px; }
.pl-typing { display: flex; gap: 4px; }
.pl-typing i { width: 7px; height: 7px; border-radius: 50%; background: #9AA0C3; animation: bob 1s ease-in-out infinite; }
.pl-typing i:nth-child(2) { animation-delay: .15s; }
.pl-typing i:nth-child(3) { animation-delay: .3s; }
.pl-input { display: flex; justify-content: space-between; align-items: center; margin: 0 14px 10px; padding: 12px 14px; border-radius: 14px; background: #F3F4FD; color: #9AA0C3; }
.pl-input b { width: 30px; height: 30px; border-radius: 10px; display: grid; place-items: center; background: #5B4BFF; color: #fff; }
.pl-chat-note { display: block; padding: 0 18px 14px; color: #9AA0C3; }

.pl-toggle { display: inline-flex; padding: 5px; border-radius: 14px; background: #fff; border: 1px solid #E0E4F7; margin-bottom: 30px; }
.pl-toggle button { padding: 10px 18px; border-radius: 10px; border: 0; background: none; font-weight: 700; cursor: pointer; color: #4B5070; transition: background .3s, color .3s; }
.pl-toggle button.on { background: #0F1222; color: #fff; }
.pl-toggle em { font-style: normal; color: #16A34A; margin-left: 4px; }
.pl-toggle button.on em { color: #86EFAC; }
.pl-plans { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; align-items: start; }
.pl-plan { position: relative; padding: 28px; border-radius: 24px; background: rgba(255, 255, 255, .85); border: 1px solid #E6E9F8; display: grid; gap: 14px; }
.pl-plan.hot { background: #0F1222; color: #fff; transform: translateY(-12px); box-shadow: 0 40px 80px -30px rgba(91, 75, 255, .6); }
.js .pl-plan.hot[data-reveal].is-in { transform: translateY(-12px); }
.pl-pop { position: absolute; top: -12px; right: 20px; padding: 4px 12px; border-radius: 999px; background: linear-gradient(90deg, #5B4BFF, #22D3EE); color: #fff; font-size: .75rem; font-weight: 800; }
.pl-plan h3 { font-size: 1.1rem; }
.pl-price { color: #7A7F9A; }
.pl-plan.hot .pl-price { color: #A3A8C3; }
.pl-price b { display: inline-block; font-family: var(--font-display); font-size: 2.6rem; font-weight: 600; color: #0F1222; letter-spacing: -.03em; }
.pl-plan.hot .pl-price b { color: #fff; }
.pl-plan ul { display: grid; gap: 8px; font-weight: 600; }
.pl-num-enter-active, .pl-num-leave-active { transition: opacity .25s, transform .25s; }
.pl-num-enter-from { opacity: 0; transform: translateY(12px); }
.pl-num-leave-to { opacity: 0; transform: translateY(-12px); }
.pl-footer { text-align: center; padding: 60px 16px 110px; color: #7A7F9A; font-size: .85rem; }

@media (max-width: 960px) {
  .pl-hero, .pl-chat-wrap { grid-template-columns: 1fr; }
  .pl-bento, .pl-plans { grid-template-columns: 1fr; }
  .pl-card-0, .pl-card-3 { grid-row: auto; grid-column: auto; }
  .pl-card-0 .pl-visual { height: 160px; }
  .pl-nav nav, .pl-link { display: none; }
  .pl-toast { left: 10px; }
  .pl-plan.hot, .js .pl-plan.hot[data-reveal].is-in { transform: none; }
}
</style>
