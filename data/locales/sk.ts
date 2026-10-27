// Slovenčina. Slová v *hviezdičkách* v nadpise hero sa zvýraznia gradientom.
export default {
  htmlLang: 'sk',
  locale: 'sk_SK',
  label: 'Slovenčina',
  short: 'SK',

  meta: {
    title: 'Duo Studio — tvorba webov, AI automatizácia, SEO a GEO | Nitra',
    description:
      'Dvaja freelanceri z Nitry: tvorba webových stránok a aplikácií, automatizácia procesov pomocou AI a programovania, UI/UX dizajn, SEO a GEO optimalizácia. Slovensko, Česko, Ukrajina.',
    ogTitle: 'Duo Studio — weby a AI automatizácie, ktoré pracujú za vás',
  },

  // Zobrazí sa návštevníkovi zo Slovenska, ak je na inej jazykovej verzii
  geoHint: { text: 'Vyzerá to, že ste zo Slovenska.', action: 'Prepnúť na slovenčinu', close: 'Zavrieť' },

  skip: 'Preskočiť na obsah',
  nav: { about: 'O nás', services: 'Služby', ai: 'AI automatizácia', work: 'Portfólio', lab: 'Lab', process: 'Proces', faq: 'FAQ', contact: 'Kontakt', cta: 'Napíšte nám', menu: 'Menu' },

  hero: {
    badge: 'Prijímame nové projekty',
    title: 'Robíme weby a *automatizácie*, ktoré pracujú za vás.',
    subtitle:
      'Sme dvojica freelancerov z Nitry. Navrhujeme a programujeme rýchle weby a aplikácie, prepájame vaše nástroje s umelou inteligenciou a staráme sa o SEO a GEO, aby vás našli Google aj AI asistenti.',
    ctaPrimary: 'Chcem projekt',
    ctaSecondary: 'Pozrieť portfólio',
    stats: [
      { value: 6, suffix: '+', label: 'projektov v portfóliu' },
      { value: 3, suffix: '', label: 'jazyky: SK · CZ · UA' },
      { value: 24, suffix: 'h', label: 'odpoveď na dopyt' },
    ],
    visual: { url: 'vasfirma.sk', chip1: 'SEO 100/100', chip2: 'LCP 0.8 s', chip3: 'AI odporúča' },
  },

  marquee: ['Webové stránky', 'AI automatizácia', 'Chatboty', 'UI/UX dizajn', 'SEO', 'GEO', 'Integrácie API', 'Python', 'Nuxt'],

  about: {
    eyebrow: 'O nás',
    title: 'Dvaja kamaráti, jedno štúdio.',
    text:
      'Duo Studio je freelance tím dvoch ľudí. Jeden sa stará o kód, backend a automatizácie, druhý o dizajn a používateľský zážitok. Každý z nás má aj vlastnú stránku — pozrite si, kto na vašom projekte bude pracovať.',
    profile: 'Otvoriť profil',
    people: {
      p1: {
        role: 'Python backend & full-stack developer',
        bio: 'FastAPI, Odoo 18, PostgreSQL a Nuxt 3. Postavil skladový systém v Odoo pre e-commerce firmu a vlastný SaaS pre autoškoly e-drivebook. V štúdiu má na starosti backend, integrácie a AI automatizácie.',
      },
      p2: {
        role: 'UI/UX dizajnér',
        bio: 'Navrhuje rozhrania a vizuálnu identitu, ktoré sú pekné aj zrozumiteľné. Od wireframu vo Figme až po hotové animácie. (Doplňte vlastný text.)',
      },
    },
  },

  services: {
    eyebrow: 'Služby',
    title: 'Všetko, čo potrebujete online.',
    text: 'Od prvého návrhu až po automatizované procesy a zákazníkov z vyhľadávania.',
    items: [
      { icon: 'web', title: 'Tvorba webových stránok', text: 'Firemné a prezentačné weby na mieru — rýchle, responzívne, viacjazyčné a pripravené na SEO.' },
      { icon: 'code', title: 'Webové aplikácie', text: 'Aplikácie a interné nástroje na Nuxte a FastAPI — s databázou, prihlásením a API.' },
      { icon: 'spark', title: 'AI automatizácia', text: 'Chatboty, spracovanie dokumentov a automatické workflowy, ktoré šetria hodiny práce.' },
      { icon: 'pen', title: 'UI/UX dizajn', text: 'Návrh vo Figme, prototypy a dizajn systémy, ktoré vedú zákazníka k cieľu.' },
      { icon: 'search', title: 'SEO a GEO', text: 'Technické SEO, štruktúrované dáta a optimalizácia pre ChatGPT, Perplexity a Google AI Overviews.' },
      { icon: 'shield', title: 'Správa a podpora', text: 'Hosting, aktualizácie, zálohy, úpravy obsahu a mesačné reporty.' },
    ],
  },

  ai: {
    eyebrow: 'AI automatizácia',
    title: 'Nechajte rutinu na AI a kód.',
    text: 'Prepojíme vaše nástroje, nasadíme AI asistentov a zautomatizujeme opakujúce sa úlohy — aby ste sa mohli venovať tomu, čo robí váš biznis výnimočným.',
    flow: ['Nový dopyt / e-mail', 'AI ho prečíta a vyhodnotí', 'Zápis do CRM / tabuľky', 'Notifikácia v Telegrame'],
    flowLabel: 'Príklad automatizácie',
    items: [
      { icon: 'bot', title: 'AI chatboty a asistenti', text: 'Chatbot na web alebo do Telegramu, ktorý odpovedá zákazníkom 24/7 na základe vašich dokumentov.' },
      { icon: 'flow', title: 'Automatizácia procesov', text: 'Workflowy v n8n, Make alebo vlastnom Pythone — objednávky, faktúry a reporty bez ručnej práce.' },
      { icon: 'doc', title: 'Spracovanie dokumentov', text: 'AI vyčíta dáta z faktúr, zmlúv či e-mailov a uloží ich presne tam, kam patria.' },
      { icon: 'plug', title: 'Integrácie a API', text: 'Prepojenie webu, e-shopu, CRM, účtovníctva a ďalších systémov cez API.' },
      { icon: 'chart', title: 'Reporty a dashboardy', text: 'Automatické prehľady predaja a návštevnosti, ktoré si už nemusíte skladať ručne.' },
      { icon: 'code', title: 'Nástroje na mieru', text: 'Skripty a malé aplikácie presne pre váš proces — od Pythonu po webové rozhranie.' },
    ],
    benefits: [
      { value: '24/7', label: 'AI odpovedá aj v noci a cez víkend' },
      { value: 'API', label: 'prepojené systémy namiesto copy-paste' },
      { value: '1 klik', label: 'reporty a dokumenty bez ručnej práce' },
    ],
    cta: 'Chcem automatizovať',
  },

  work: {
    eyebrow: 'Portfólio',
    title: 'Vybrané projekty.',
    text: 'Skutočné weby a aplikácie, ktoré sme vytvorili.',
    filters: { all: 'Všetko', web: 'Weby', app: 'Aplikácie', design: 'Dizajn' },
    live: 'Web',
    code: 'GitHub',
    demo: 'Ukážka',
    projects: {
      'e-drivebook': { desc: 'Môj SaaS pre autoškoly: online rezervácie jázd 24/7, rozvrhy inštruktorov, vozidlá, evidencia žiakov a testy na skúšku. V produkcii — denne ho používajú 3 platiace autoškoly.' },
      brtc: { desc: 'Firemný web technickej spoločnosti s katalógom kompresorových riešení pre priemysel.' },
      onyx: { desc: 'Prezentácia nových kancelárskych priestorov v Zlatých Moravciach s mapou a kontaktom.' },
      'hodinovy-manzel': { desc: 'Landing page pre údržbára v Nitre — služby po miestnostiach, cenník, referencie a formulár bez backendu.' },
      amstars: { desc: 'Bakalárska práca: platforma pre amatérsky futbal — tímy, výzvy na zápasy, ELO rating a turnaje.' },
      'travel-planner': { desc: 'REST API na plánovanie ciest po umeleckých dielach, overované cez živé API Art Institute of Chicago.' },
      'nordic-living': { desc: 'Vizuálna identita a UI kit pre značku škandinávskeho nábytku.' },
      'slnecne-byty': { desc: 'UX návrh a prototyp webu pre developerský projekt s výberom bytov.' },
    },
  },

  lab: {
    eyebrow: 'Lab · Koncepty',
    title: 'Na čo sme schopní.',
    text: 'Koncepty webov pre fiktívne značky v úplne odlišných štýloch. Klikajte, skúšajte — všetko je interaktívne.',
    open: 'Otvoriť koncept',
    badge: 'Koncept — fiktívna značka',
    back: 'Späť na Duo Studio',
    next: 'Ďalší koncept',
    cta: 'Chcem podobný web',
    items: {
      noir: { type: 'Reštaurácia · fine dining', desc: 'Tmavý elegantný web s kreslenými animáciami, menu s náhľadom za kurzorom a rezerváciou stola.' },
      pulse: { type: 'SaaS · AI analytika', desc: 'Svetlý startup web so živým dashboardom, AI chatom a prepínačom cien.' },
      kinetic: { type: 'E-shop · streetwear', desc: 'Brutalistický e-shop s funkčným košíkom, výberom veľkosti a odvážnou typografiou.' },
      verde: { type: 'Reality · eko bývanie', desc: 'Prírodný web developerského projektu s parallaxou a interaktívnym výberom bytov.' },
    },
  },

  process: {
    eyebrow: 'Proces',
    title: 'Ako spolu pracujeme.',
    steps: [
      { title: 'Konzultácia', text: 'Zistíme vaše ciele a procesy, ktoré sa dajú zjednodušiť. Pošleme pevnú cenovú ponuku.' },
      { title: 'Návrh', text: 'Pripravíme štruktúru, dizajn vo Figme alebo schému automatizácie.' },
      { title: 'Vývoj', text: 'Naprogramujeme web, aplikáciu či workflow s dôrazom na rýchlosť a spoľahlivosť.' },
      { title: 'Spustenie a rast', text: 'Spustíme, nastavíme analytiku a pomáhame s ďalším rastom.' },
    ],
  },

  faq: {
    eyebrow: 'FAQ',
    title: 'Časté otázky.',
    items: [
      { q: 'Koľko stojí tvorba webovej stránky?', a: 'Cena závisí od rozsahu — počtu stránok, funkcií a jazykov. Po bezplatnej konzultácii vám pošleme pevnú cenovú ponuku bez skrytých poplatkov.' },
      { q: 'Čo všetko viete zautomatizovať pomocou AI?', a: 'Najčastejšie odpovedanie na otázky zákazníkov (chatbot), triedenie e-mailov a dopytov, vyčítanie dát z faktúr a dokumentov, prepájanie systémov cez API a automatické reporty. Na konzultácii spolu nájdeme úlohy, ktoré vám berú najviac času.' },
      { q: 'Ako dlho trvá vytvorenie webu?', a: 'Landing page alebo prezentačný web zvyčajne 2–3 týždne, väčší web alebo aplikácia 4–8 týždňov. Jednoduchú automatizáciu vieme nasadiť aj za pár dní.' },
      { q: 'Čo je GEO optimalizácia?', a: 'GEO (Generative Engine Optimization) je optimalizácia webu pre AI vyhľadávače a asistentov ako ChatGPT, Perplexity či Google AI Overviews. Pomocou štruktúrovaných dát, jasného obsahu a súboru llms.txt zvyšujeme šancu, že AI odporučí práve vás.' },
      { q: 'Pracujete aj pre klientov z Česka a Ukrajiny?', a: 'Áno. Pracujeme na diaľku pre klientov zo Slovenska, Česka aj Ukrajiny a komunikujeme po slovensky, česky aj ukrajinsky.' },
      { q: 'Postaráte sa aj o doménu a hosting?', a: 'Áno, pomôžeme vybrať a nastaviť doménu, hosting, SSL certifikát aj firemné e-maily.' },
    ],
  },

  contact: {
    eyebrow: 'Kontakt',
    title: 'Máte nápad? Poďme ho zrealizovať.',
    text: 'Napíšte nám pár slov o projekte alebo procese, ktorý chcete zautomatizovať. Ozveme sa do 24 hodín.',
    direct: 'Alebo nám napíšte priamo',
    form: {
      name: 'Meno',
      email: 'E-mail',
      type: 'Čo potrebujete?',
      types: ['Webová stránka', 'AI automatizácia', 'Aplikácia', 'Dizajn', 'SEO / GEO', 'Iné'],
      message: 'Správa',
      send: 'Odoslať správu',
      sent: 'Ďakujeme! Ozveme sa čoskoro.',
      error: 'Niečo sa pokazilo. Napíšte nám prosím e-mail.',
      subject: 'Nový dopyt z webu',
    },
  },

  footer: {
    tagline: 'Weby, aplikácie, AI automatizácia, SEO a GEO pre Slovensko, Česko a Ukrajinu.',
    rights: 'Všetky práva vyhradené.',
    top: 'Hore',
  },

  // Osobné stránky (/sk/sebastian, /sk/roman)
  personal: {
    back: 'Späť na štúdio',
    hello: 'Ahoj, som',
    about: 'O mne',
    stack: 'Technológie',
    projects: 'Projekty',
    journey: 'Skúsenosti',
    education: 'Vzdelanie',
    languages: 'Jazyky',
    contact: 'Napíš mi',
    contactText: 'Máš projekt alebo nápad na automatizáciu? Ozvi sa, odpoviem do 24 hodín.',
    available: 'Voľný na nové projekty',
    also: 'Pozri aj profil',
    copy: 'Kopírovať e-mail',
    copied: 'Skopírované ✓',
    sayHi: 'Povedzme si ahoj',
    sticker: 'UI/UX • BRANDING • WEB • DIZAJN • ',
    cv: {
      open: 'Životopis (CV)',
      title: 'Životopis',
      download: 'Stiahnuť PDF',
      fullProfile: 'Celý profil',
      summary: 'Profil',
      skills: 'Zručnosti',
      experience: 'Pracovné skúsenosti',
      education: 'Vzdelanie',
      languages: 'Jazyky',
      projects: 'Vybrané projekty',
      info: 'Informácie',
      contact: 'Kontakt',
      web: 'Web',
      metaTitle: 'Životopis',
    },
    people: {
      p1: {
        metaTitle: 'Bc. Sebastian Kychatyi — Python backend / full-stack developer | Nitra',
        metaDescription: 'Python backend a full-stack developer: FastAPI, Odoo 18, PostgreSQL, Vue.js / Nuxt 3. Skladový systém v Odoo 18, vlastný SaaS pre autoškoly e-drivebook, weby a AI automatizácia.',
        headline: 'Programujem systémy, na ktorých bežia skutočné firmy.',
        intro: 'Python backend a full-stack developer zameraný na firemné systémy — ERP, e-commerce a SaaS. Funkciu dotiahnem od databázovej schémy cez rozhranie až po nasadenie.',
        bio: [
          'Postavil som skladový systém v Odoo 18 pre e-commerce firmu a od nuly vytvoril SaaS pre autoškoly e-drivebook, ktorý je v produkcii a denne ho používajú 3 platiace autoškoly.',
          'Študujem magisterský program Aplikovaná informatika na UKF v Nitre. V Duo Studio mám na starosti backend, integrácie a AI automatizácie.',
        ],
        facts: [
          { k: 'Lokalita', v: 'Nitra, Slovensko' },
          { k: 'Práca', v: 'Hybridne v Bratislave alebo remote' },
          { k: 'Zameranie', v: 'Backend · Full-stack · ERP' },
        ],
        timeline: [
          { year: '04/2025 – dnes', title: 'Full-Stack Developer · e-drivebook (vlastný produkt)', text: 'SaaS pre autoškoly od požiadaviek po nasadenie, denne ho používajú 3 platiace autoškoly. FastAPI, PostgreSQL (SQLAlchemy, Alembic), OAuth2/JWT: evidencia žiakov, automatické plánovanie jázd, priebeh výcviku a údržba vozidiel. Dashboardy v Nuxt 3, Docker Compose, Caddy, CI/CD cez GitHub Actions.' },
          { year: '04/2026 – 10/2026', title: 'Odoo Developer · Adelle Davis s.r.o.', text: 'Bratislava, hybridne. Vlastný skladový systém v Odoo 18 (Python, OWL): skladové pozície, príjem, vychystávanie a balenie so skenovaním čiarových kódov. Zásielky a štítky cez API kuriérov (SPS, Packeta, GLS), konektor WooCommerce ↔ Odoo, zákaznícka podpora v Odoo a FastAPI mikroslužba na výber krabice.' },
          { year: '10/2025 – 07/2026', title: 'Backend Developer · SHARKRISE s.r.o.', text: 'Remote, kontrakt. Mobilná hra Difference Mania (Laravel, MySQL): refaktoring hernej logiky pred spustením a rozšírenie backendu o nový obsah.' },
        ],
        education: [
          { year: '2026 – 2028', title: 'Mgr. — Aplikovaná informatika', text: 'Univerzita Konštantína Filozofa v Nitre (prebieha)' },
          { year: '2023 – 2026', title: 'Bc. — Aplikovaná informatika', text: 'Univerzita Konštantína Filozofa v Nitre · bakalárska práca AmStars' },
        ],
        languages: [
          { k: 'Ukrajinčina', v: 'materinský jazyk' },
          { k: 'Ruština', v: 'C2' },
          { k: 'Slovenčina', v: 'B2' },
          { k: 'Angličtina', v: 'B1' },
        ],
      },
      p2: {
        metaTitle: 'Roman — UI/UX dizajnér | Duo Studio',
        metaDescription: 'Roman, UI/UX dizajnér v Duo Studio: návrh webov a aplikácií, branding a prototypy vo Figme. Portfólio a kontakt.',
        headline: 'Navrhujem rozhrania, ktoré si ľudia zapamätajú.',
        intro: 'UI/UX dizajnér, ktorý verí, že dobrý dizajn je ten, ktorý si nevšimnete — proste funguje. (Doplňte vlastný text.)',
        bio: [
          'Tu bude krátky príbeh o tom, ako som sa dostal k dizajnu a čo ma na ňom baví. (Doplňte vlastný text.)',
          'V Duo Studio mám na starosti vizuál, UX a branding. Spolu so Sebastianom tak klient dostane dizajn aj kód z jedného miesta.',
        ],
        facts: [
          { k: 'Lokalita', v: 'Slovensko' },
          { k: 'Zameranie', v: 'UI/UX · Branding' },
          { k: 'Nástroje', v: 'Figma · Webflow' },
        ],
        education: [] as { year: string; title: string; text: string }[],
        languages: [] as { k: string; v: string }[],
        timeline: [
          { year: '2026', title: 'Váš projekt', text: 'Doplňte projekt, na ktorý ste hrdý.' },
          { year: '2025', title: 'Váš projekt', text: 'Doplňte ďalší projekt alebo skúsenosť.' },
        ],
      },
    },
  },
}
