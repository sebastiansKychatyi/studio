// Čeština. Slova v *hvězdičkách* v nadpisu hero se zvýrazní gradientem.
import type sk from './sk'

const cs: typeof sk = {
  htmlLang: 'cs',
  locale: 'cs_CZ',
  label: 'Čeština',
  short: 'CZ',

  meta: {
    title: 'Duo Studio — tvorba webů, AI automatizace, SEO a GEO',
    description:
      'Dva freelanceři: tvorba webových stránek a aplikací, automatizace procesů pomocí AI a programování, UI/UX design, SEO a GEO optimalizace. Pracujeme pro klienty z Česka, Slovenska a Ukrajiny.',
    ogTitle: 'Duo Studio — weby a AI automatizace, které pracují za vás',
  },

  geoHint: { text: 'Vypadá to, že jste z Česka.', action: 'Přepnout do češtiny', close: 'Zavřít' },

  skip: 'Přeskočit na obsah',
  nav: { about: 'O nás', services: 'Služby', ai: 'AI automatizace', work: 'Portfolio', lab: 'Lab', process: 'Proces', faq: 'FAQ', contact: 'Kontakt', cta: 'Napište nám', menu: 'Menu' },

  hero: {
    badge: 'Přijímáme nové projekty',
    title: 'Tvoříme weby a *automatizace*, které pracují za vás.',
    subtitle:
      'Jsme dvojice freelancerů. Navrhujeme a programujeme rychlé weby a aplikace, propojujeme vaše nástroje s umělou inteligencí a staráme se o SEO a GEO, aby vás našli Google i AI asistenti.',
    ctaPrimary: 'Chci projekt',
    ctaSecondary: 'Prohlédnout portfolio',
    stats: [
      { value: 6, suffix: '+', label: 'projektů v portfoliu' },
      { value: 3, suffix: '', label: 'jazyky: CZ · SK · UA' },
      { value: 24, suffix: 'h', label: 'odpověď na poptávku' },
    ],
    visual: { url: 'vasefirma.cz', chip1: 'SEO 100/100', chip2: 'LCP 0.8 s', chip3: 'AI doporučuje' },
  },

  marquee: ['Webové stránky', 'AI automatizace', 'Chatboti', 'UI/UX design', 'SEO', 'GEO', 'Integrace API', 'Python', 'Nuxt'],

  about: {
    eyebrow: 'O nás',
    title: 'Dva kamarádi, jedno studio.',
    text:
      'Duo Studio je freelance tým dvou lidí. Jeden se stará o kód, backend a automatizace, druhý o design a uživatelský zážitek. Každý z nás má i vlastní stránku — podívejte se, kdo bude na vašem projektu pracovat.',
    profile: 'Otevřít profil',
    people: {
      p1: {
        role: 'Python backend & full-stack developer',
        bio: 'FastAPI, Odoo 18, PostgreSQL a Nuxt 3. Postavil skladový systém v Odoo pro e-commerce firmu a vlastní SaaS pro autoškoly e-drivebook. Ve studiu má na starosti backend, integrace a AI automatizace.',
      },
      p2: {
        role: 'UI/UX designér',
        bio: 'Navrhuje rozhraní a vizuální identitu, která jsou hezká i srozumitelná. Od wireframu ve Figmě až po hotové animace. (Doplňte vlastní text.)',
      },
    },
  },

  services: {
    eyebrow: 'Služby',
    title: 'Vše, co online potřebujete.',
    text: 'Od prvního návrhu až po automatizované procesy a zákazníky z vyhledávání.',
    items: [
      { icon: 'web', title: 'Tvorba webových stránek', text: 'Firemní a prezentační weby na míru — rychlé, responzivní, vícejazyčné a připravené na SEO.' },
      { icon: 'code', title: 'Webové aplikace', text: 'Aplikace a interní nástroje na Nuxtu a FastAPI — s databází, přihlášením a API.' },
      { icon: 'spark', title: 'AI automatizace', text: 'Chatboti, zpracování dokumentů a automatické workflowy, které šetří hodiny práce.' },
      { icon: 'pen', title: 'UI/UX design', text: 'Návrh ve Figmě, prototypy a design systémy, které vedou zákazníka k cíli.' },
      { icon: 'search', title: 'SEO a GEO', text: 'Technické SEO, strukturovaná data a optimalizace pro ChatGPT, Perplexity a Google AI Overviews.' },
      { icon: 'shield', title: 'Správa a podpora', text: 'Hosting, aktualizace, zálohy, úpravy obsahu a měsíční reporty.' },
    ],
  },

  ai: {
    eyebrow: 'AI automatizace',
    title: 'Nechte rutinu na AI a kódu.',
    text: 'Propojíme vaše nástroje, nasadíme AI asistenty a zautomatizujeme opakující se úkoly — abyste se mohli věnovat tomu, co dělá váš byznys výjimečným.',
    flow: ['Nová poptávka / e-mail', 'AI ji přečte a vyhodnotí', 'Zápis do CRM / tabulky', 'Notifikace v Telegramu'],
    flowLabel: 'Příklad automatizace',
    items: [
      { icon: 'bot', title: 'AI chatboti a asistenti', text: 'Chatbot na web nebo do Telegramu, který odpovídá zákazníkům 24/7 na základě vašich dokumentů.' },
      { icon: 'flow', title: 'Automatizace procesů', text: 'Workflowy v n8n, Make nebo vlastním Pythonu — objednávky, faktury a reporty bez ruční práce.' },
      { icon: 'doc', title: 'Zpracování dokumentů', text: 'AI vyčte data z faktur, smluv či e-mailů a uloží je přesně tam, kam patří.' },
      { icon: 'plug', title: 'Integrace a API', text: 'Propojení webu, e-shopu, CRM, účetnictví a dalších systémů přes API.' },
      { icon: 'chart', title: 'Reporty a dashboardy', text: 'Automatické přehledy prodeje a návštěvnosti, které už nemusíte skládat ručně.' },
      { icon: 'code', title: 'Nástroje na míru', text: 'Skripty a malé aplikace přesně pro váš proces — od Pythonu po webové rozhraní.' },
    ],
    benefits: [
      { value: '24/7', label: 'AI odpovídá i v noci a o víkendu' },
      { value: 'API', label: 'propojené systémy místo copy-paste' },
      { value: '1 klik', label: 'reporty a dokumenty bez ruční práce' },
    ],
    cta: 'Chci automatizovat',
  },

  work: {
    eyebrow: 'Portfolio',
    title: 'Vybrané projekty.',
    text: 'Skutečné weby a aplikace, které jsme vytvořili.',
    filters: { all: 'Vše', web: 'Weby', app: 'Aplikace', design: 'Design' },
    live: 'Web',
    code: 'GitHub',
    demo: 'Ukázka',
    proto: { open: 'Otevřít prototyp', hint: 'Klikací prototyp — zkuste klikat', close: 'Zavřít' },
    projects: {
      'e-drivebook': { desc: 'Můj SaaS pro autoškoly: online rezervace jízd 24/7, rozvrhy instruktorů, vozidla, evidence žáků a testy na zkoušku. V produkci — denně ho používají 3 platící autoškoly.' },
      brtc: { desc: 'Firemní web technické společnosti s katalogem kompresorových řešení pro průmysl.' },
      onyx: { desc: 'Prezentace nových kancelářských prostor ve Zlatých Moravcích s mapou a kontaktem.' },
      'hodinovy-manzel': { desc: 'Landing page pro údržbáře v Nitře — služby po místnostech, ceník, reference a formulář bez backendu.' },
      amstars: { desc: 'Bakalářská práce: platforma pro amatérský fotbal — týmy, výzvy k zápasům, ELO rating a turnaje.' },
      'travel-planner': { desc: 'REST API pro plánování cest po uměleckých dílech, ověřované přes živé API Art Institute of Chicago.' },
      'nordic-living': { desc: 'Koncept e-shopu se skandinávským nábytkem: katalog, detail produktu s výběrem barvy, košík a UI kit.' },
      'slnecne-byty': { desc: 'Mobilní aplikace developerského projektu: výběr bytu, galerie, půdorys a rezervace prohlídky.' },
      fitflow: { desc: 'Fitness aplikace s kroužky aktivity, tréninkovým časovačem a tmavým režimem.' },
    },
  },

  lab: {
    eyebrow: 'Lab · Koncepty',
    title: 'Co všechno umíme.',
    text: 'Koncepty webů pro fiktivní značky ve zcela odlišných stylech. Klikejte, zkoušejte — vše je interaktivní.',
    open: 'Otevřít koncept',
    badge: 'Koncept — fiktivní značka',
    back: 'Zpět na Duo Studio',
    next: 'Další koncept',
    cta: 'Chci podobný web',
    items: {
      noir: { type: 'Restaurace · fine dining', desc: 'Tmavý elegantní web s kreslenými animacemi, menu s náhledem u kurzoru a rezervací stolu.' },
      pulse: { type: 'SaaS · AI analytika', desc: 'Světlý startup web s živým dashboardem, AI chatem a přepínačem cen.' },
      kinetic: { type: 'E-shop · streetwear', desc: 'Brutalistický e-shop s funkčním košíkem, výběrem velikosti a odvážnou typografií.' },
      verde: { type: 'Reality · eko bydlení', desc: 'Přírodní web developerského projektu s parallaxou a interaktivním výběrem bytů.' },
    },
  },

  process: {
    eyebrow: 'Proces',
    title: 'Jak spolu pracujeme.',
    steps: [
      { title: 'Konzultace', text: 'Zjistíme vaše cíle a procesy, které lze zjednodušit. Pošleme pevnou cenovou nabídku.' },
      { title: 'Návrh', text: 'Připravíme strukturu, design ve Figmě nebo schéma automatizace.' },
      { title: 'Vývoj', text: 'Naprogramujeme web, aplikaci či workflow s důrazem na rychlost a spolehlivost.' },
      { title: 'Spuštění a růst', text: 'Spustíme, nastavíme analytiku a pomáháme s dalším růstem.' },
    ],
  },

  faq: {
    eyebrow: 'FAQ',
    title: 'Časté dotazy.',
    items: [
      { q: 'Kolik stojí tvorba webových stránek?', a: 'Cena závisí na rozsahu — počtu stránek, funkcí a jazyků. Po bezplatné konzultaci vám pošleme pevnou cenovou nabídku bez skrytých poplatků.' },
      { q: 'Co všechno umíte zautomatizovat pomocí AI?', a: 'Nejčastěji odpovídání na dotazy zákazníků (chatbot), třídění e-mailů a poptávek, vyčítání dat z faktur a dokumentů, propojování systémů přes API a automatické reporty. Na konzultaci společně najdeme úkoly, které vám berou nejvíc času.' },
      { q: 'Jak dlouho trvá vytvoření webu?', a: 'Landing page nebo prezentační web obvykle 2–3 týdny, větší web nebo aplikace 4–8 týdnů. Jednoduchou automatizaci umíme nasadit i za pár dní.' },
      { q: 'Co je GEO optimalizace?', a: 'GEO (Generative Engine Optimization) je optimalizace webu pro AI vyhledávače a asistenty jako ChatGPT, Perplexity či Google AI Overviews. Pomocí strukturovaných dat, jasného obsahu a souboru llms.txt zvyšujeme šanci, že AI doporučí právě vás.' },
      { q: 'Pracujete i pro klienty z Česka?', a: 'Ano. Pracujeme na dálku pro klienty z Česka, Slovenska i Ukrajiny a komunikujeme česky, slovensky i ukrajinsky.' },
      { q: 'Postaráte se i o doménu a hosting?', a: 'Ano, pomůžeme vybrat a nastavit doménu, hosting, SSL certifikát i firemní e-maily.' },
    ],
  },

  contact: {
    eyebrow: 'Kontakt',
    title: 'Máte nápad? Pojďme ho zrealizovat.',
    text: 'Napište nám pár slov o projektu nebo procesu, který chcete zautomatizovat. Ozveme se do 24 hodin.',
    direct: 'Nebo nám napište přímo',
    form: {
      name: 'Jméno',
      email: 'E-mail',
      type: 'Co potřebujete?',
      types: ['Webové stránky', 'AI automatizace', 'Aplikace', 'Design', 'SEO / GEO', 'Jiné'],
      message: 'Zpráva',
      send: 'Odeslat zprávu',
      sent: 'Děkujeme! Brzy se ozveme.',
      error: 'Něco se pokazilo. Napište nám prosím e-mail.',
      subject: 'Nová poptávka z webu',
    },
  },

  footer: {
    tagline: 'Weby, aplikace, AI automatizace, SEO a GEO pro Česko, Slovensko a Ukrajinu.',
    rights: 'Všechna práva vyhrazena.',
    top: 'Nahoru',
  },

  personal: {
    back: 'Zpět na studio',
    hello: 'Ahoj, jsem',
    about: 'O mně',
    stack: 'Technologie',
    projects: 'Projekty',
    journey: 'Zkušenosti',
    education: 'Vzdělání',
    languages: 'Jazyky',
    contact: 'Napiš mi',
    contactText: 'Máš projekt nebo nápad na automatizaci? Ozvi se, odpovím do 24 hodin.',
    available: 'Volný pro nové projekty',
    also: 'Podívej se i na profil',
    copy: 'Kopírovat e-mail',
    copied: 'Zkopírováno ✓',
    sayHi: 'Pojďme si říct ahoj',
    sticker: 'UI/UX • BRANDING • WEB • DESIGN • ',
    cv: {
      open: 'Životopis (CV)',
      title: 'Životopis',
      download: 'Stáhnout PDF',
      fullProfile: 'Celý profil',
      summary: 'Profil',
      skills: 'Dovednosti',
      experience: 'Pracovní zkušenosti',
      education: 'Vzdělání',
      languages: 'Jazyky',
      projects: 'Vybrané projekty',
      info: 'Informace',
      contact: 'Kontakt',
      web: 'Web',
      metaTitle: 'Životopis',
    },
    people: {
      p1: {
        metaTitle: 'Bc. Sebastian Kychatyi — Python backend / full-stack developer',
        metaDescription: 'Python backend a full-stack developer: FastAPI, Odoo 18, PostgreSQL, Vue.js / Nuxt 3. Skladový systém v Odoo 18, vlastní SaaS pro autoškoly e-drivebook, weby a AI automatizace.',
        headline: 'Programuji systémy, na kterých běží skutečné firmy.',
        intro: 'Python backend a full-stack developer zaměřený na firemní systémy — ERP, e-commerce a SaaS. Funkci dotáhnu od databázového schématu přes rozhraní až po nasazení.',
        bio: [
          'Postavil jsem skladový systém v Odoo 18 pro e-commerce firmu a od nuly vytvořil SaaS pro autoškoly e-drivebook, který je v produkci a denně ho používají 3 platící autoškoly.',
          'Studuji magisterský program Aplikovaná informatika na UKF v Nitře. V Duo Studio mám na starosti backend, integrace a AI automatizace.',
        ],
        facts: [
          { k: 'Lokalita', v: 'Nitra, Slovensko' },
          { k: 'Práce', v: 'Hybridně v Bratislavě nebo remote' },
          { k: 'Zaměření', v: 'Backend · Full-stack · ERP' },
        ],
        timeline: [
          { year: '04/2025 – dosud', title: 'Full-Stack Developer · e-drivebook (vlastní produkt)', text: 'SaaS pro autoškoly od požadavků po nasazení, denně ho používají 3 platící autoškoly. FastAPI, PostgreSQL (SQLAlchemy, Alembic), OAuth2/JWT: evidence žáků, automatické plánování jízd, průběh výcviku a údržba vozidel. Dashboardy v Nuxt 3, Docker Compose, Caddy, CI/CD přes GitHub Actions.' },
          { year: '04/2026 – 10/2026', title: 'Odoo Developer · Adelle Davis s.r.o.', text: 'Bratislava, hybridně. Vlastní skladový systém v Odoo 18 (Python, OWL): skladové pozice, příjem, vychystávání a balení se skenováním čárových kódů. Zásilky a štítky přes API kurýrů (SPS, Packeta, GLS), konektor WooCommerce ↔ Odoo, zákaznická podpora v Odoo a FastAPI mikroslužba pro výběr krabice.' },
          { year: '10/2025 – 07/2026', title: 'Backend Developer · SHARKRISE s.r.o.', text: 'Remote, kontrakt. Mobilní hra Difference Mania (Laravel, MySQL): refaktoring herní logiky před spuštěním a rozšíření backendu o nový obsah.' },
        ],
        education: [
          { year: '2026 – 2028', title: 'Mgr. — Aplikovaná informatika', text: 'Univerzita Konštantína Filozofa v Nitře (probíhá)' },
          { year: '2023 – 2026', title: 'Bc. — Aplikovaná informatika', text: 'Univerzita Konštantína Filozofa v Nitře · bakalářská práce AmStars' },
        ],
        languages: [
          { k: 'Ukrajinština', v: 'rodný jazyk' },
          { k: 'Ruština', v: 'C2' },
          { k: 'Slovenština', v: 'B2' },
          { k: 'Angličtina', v: 'B1' },
        ],
      },
      p2: {
        metaTitle: 'Roman — UI/UX designér | Duo Studio',
        metaDescription: 'Roman, UI/UX designér v Duo Studio: návrh webů a aplikací, branding a prototypy ve Figmě. Portfolio a kontakt.',
        headline: 'Navrhuji rozhraní, která si lidé zapamatují.',
        intro: 'UI/UX designér, který věří, že dobrý design je ten, kterého si nevšimnete — prostě funguje. (Doplňte vlastní text.)',
        bio: [
          'Tady bude krátký příběh o tom, jak jsem se dostal k designu a co mě na něm baví. (Doplňte vlastní text.)',
          'V Duo Studio mám na starosti vizuál, UX a branding. Spolu se Sebastianem tak klient dostane design i kód z jednoho místa.',
        ],
        facts: [
          { k: 'Lokalita', v: 'Slovensko' },
          { k: 'Zaměření', v: 'UI/UX · Branding' },
          { k: 'Nástroje', v: 'Figma · Webflow' },
        ],
        education: [] as { year: string; title: string; text: string }[],
        languages: [] as { k: string; v: string }[],
        timeline: [
          { year: '2026', title: 'Váš projekt', text: 'Doplňte projekt, na který jste hrdý.' },
          { year: '2025', title: 'Váš projekt', text: 'Doplňte další projekt nebo zkušenost.' },
        ],
      },
    },
  },
}

export default cs
