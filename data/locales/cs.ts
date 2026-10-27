// Czech. *Words* in the hero title get the gradient.
import type sk from './sk'

const cs: typeof sk = {
  htmlLang: 'cs',
  locale: 'cs_CZ',
  label: 'Čeština',
  short: 'CZ',

  meta: {
    title: 'Duo Studio — AI automatizace, tvorba webů a aplikací | Praha, Bratislava',
    description:
      'AI automatizace, tvorba webových stránek, aplikací a mini her a integrace umělé inteligence pro firmy v Praze a po celém Česku. Tým z Bratislavy a Nitry, pracujeme i pro Kyjev a Užhorod.',
    ogTitle: 'Duo Studio — AI automatizace, weby a aplikace | Praha · Bratislava',
  },

  geoHint: { text: 'Vypadá to, že jste z Česka.', action: 'Přepnout do češtiny', close: 'Zavřít' },

  skip: 'Přeskočit na obsah',
  nav: { about: 'O nás', services: 'Služby', ai: 'AI automatizace', work: 'Portfolio', lab: 'Lab', process: 'Proces', faq: 'FAQ', contact: 'Kontakt', cta: 'Napište nám', menu: 'Menu' },

  hero: {
    badge: 'Přijímáme nové projekty',
    title: 'Automatizujeme byznys pomocí *AI* a kódu.',
    subtitle:
      'Vývojářský tým z Bratislavy a Nitry, pracujeme i pro klienty v Praze. Děláme AI automatizace, weby, aplikace a mini hry na míru, integrujeme umělou inteligenci do vašich systémů a zrychlujeme procesy automatizací kódu.',
    ctaPrimary: 'Chci projekt',
    ctaSecondary: 'Prohlédnout portfolio',
    stats: [
      { value: 7, suffix: '+', label: 'projektů v portfoliu' },
      { value: 4, suffix: '', label: 'jazyky: CZ · SK · UA · EN' },
      { value: 24, suffix: 'h', label: 'odpověď na poptávku' },
    ],
    visual: { url: 'vasefirma.cz', chip1: 'SEO 100/100', chip2: 'LCP 0.8 s', chip3: 'AI doporučuje' },
  },

  marquee: ['AI automatizace', 'Tvorba webů', 'Aplikace', 'Mini hry', 'Integrace AI', 'Chatboti', 'Automatizace kódu', 'Praha', 'Bratislava', 'Nitra', 'Kyjev'],

  about: {
    eyebrow: 'O nás',
    title: 'AI, kód a design v jednom týmu.',
    text:
      'Duo Studio je vývojářský tým z Bratislavy a Nitry. Zaměřujeme se na AI automatizaci, tvorbu webů, webových a mobilních aplikací a mini her, integraci umělé inteligence do firemních systémů a optimalizaci procesů pomocí automatizace kódu. Pracujeme pro klienty v Praze a po celém Česku, na Slovensku i na Ukrajině.',
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
    title: 'Co pro vás děláme.',
    text: 'AI, weby, aplikace a hry — od nápadu po spuštění a další rozvoj.',
    items: [
      { icon: 'spark', title: 'AI automatizace', text: 'Automatizujeme opakující se úkoly: zpracování poptávek, dokumentů, objednávek a reportů — procesy běží samy 24/7.' },
      { icon: 'web', title: 'Tvorba webových stránek', text: 'Rychlé firemní weby a e-shopy s SEO a GEO optimalizací, aby vás našli Google i AI asistenti v Praze i po celém Česku.' },
      { icon: 'code', title: 'Webové a mobilní aplikace', text: 'SaaS, interní systémy a ERP řešení na FastAPI, Odoo a Nuxtu — s databází, přihlášením a API.' },
      { icon: 'game', title: 'Mini hry', text: 'Webové a mobilní mini hry, hry pro Telegram a gamifikace pro marketingové kampaně a věrnostní programy.' },
      { icon: 'flow', title: 'Optimalizace automatizací kódu', text: 'CI/CD, automatické testy, refaktoring a skripty, které zrychlí vývoj a sníží chyby i náklady.' },
      { icon: 'bot', title: 'Integrace AI', text: 'Napojíme ChatGPT, Claude a další modely na váš web, CRM či e-shop — chatboti, asistenti a chytré vyhledávání.' },
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
      expertsk: { desc: 'Katalog ověřených řemeslníků na Slovensku: elektrikáři, instalatéři, úklid a další služby — vyhledávání podle města, hodnocení, ceny a registrace pro profesionály.' },
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

  city: {
    eyebrow: 'Působíme',
    services: 'Co pro vás uděláme',
    why: 'Proč právě my',
    projects: 'Vybrané projekty',
    faq: 'Časté dotazy',
    cta: 'Napište nám',
    inPerson: 'Osobní schůzka',
    remote: 'Spolupráce na dálku',
    other: 'Působíme i v dalších městech',
    footerTitle: 'Působíme',
  },
  caseStudy: {
    label: 'Případová studie',
    back: 'Zpět na portfolio',
    client: 'Klient',
    role: 'Naše role',
    year: 'Rok',
    challenge: 'Výzva',
    solution: 'Řešení',
    features: 'Co jsme vytvořili',
    results: 'Výsledky',
    stack: 'Technologie',
    visit: 'Otevřít web',
    next: 'Další studie',
    ctaTitle: 'Chcete podobný projekt?',
    ctaText: 'Napište nám pár slov o vašem nápadu — ozveme se do 24 hodin.',
    cta: 'Napište nám',
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
      { q: 'Kolik stojí tvorba webu nebo aplikace?', a: 'Cena závisí na rozsahu — počtu stránek, funkcí a integrací. Po bezplatné konzultaci vám pošleme pevnou cenovou nabídku bez skrytých poplatků.' },
      { q: 'Co všechno umíte zautomatizovat pomocí AI?', a: 'Nejčastěji odpovídání na dotazy zákazníků (chatbot), třídění e-mailů a poptávek, vyčítání dat z faktur a dokumentů, propojování systémů přes API a automatické reporty. Na konzultaci společně najdeme úkoly, které vám berou nejvíc času.' },
      { q: 'Pracujete i pro klienty v Praze?', a: 'Ano. Tým sídlí v Bratislavě a Nitře a pro klienty v Praze a po celém Česku pracujeme na dálku — komunikujeme česky, slovensky i ukrajinsky. Působíme také v Kyjevě a Užhorodu.' },
      { q: 'Děláte i mini hry?', a: 'Ano. Vytváříme webové a mobilní mini hry, hry pro Telegram a herní prvky do marketingových kampaní — například soutěže, kola štěstí či věrnostní výzvy.' },
      { q: 'Co je optimalizace automatizací kódu?', a: 'Nastavíme CI/CD, automatické testy a nasazování, zrefaktorujeme pomalé části a napíšeme skripty na rutinní úkoly. Vývoj je rychlejší a v produkci je méně chyb.' },
      { q: 'Jak dlouho trvá vytvoření webu?', a: 'Landing page nebo prezentační web obvykle 2–3 týdny, větší web nebo aplikace 4–8 týdnů. Jednoduchou automatizaci umíme nasadit i za pár dní.' },
      { q: 'Co je GEO optimalizace?', a: 'GEO (Generative Engine Optimization) je optimalizace webu pro AI vyhledávače a asistenty jako ChatGPT, Perplexity či Google AI Overviews. Pomocí strukturovaných dat, jasného obsahu a souboru llms.txt zvyšujeme šanci, že AI doporučí právě vás.' },
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
      types: ['AI automatizace', 'Webové stránky', 'Aplikace', 'Mini hra', 'Integrace AI', 'Jiné'],
      message: 'Zpráva',
      send: 'Odeslat zprávu',
      sent: 'Děkujeme! Brzy se ozveme.',
      error: 'Něco se pokazilo. Napište nám prosím e-mail.',
      subject: 'Nová poptávka z webu',
      consent: 'Souhlasím se zpracováním osobních údajů podle',
      consentLink: 'zásad ochrany osobních údajů',
      sending: 'Odesílám…',
    },
  },

  footer: {
    tagline: 'AI automatizace, weby, aplikace a mini hry · Praha · Bratislava · Nitra · Kyjev · Užhorod',
    rights: 'Všechna práva vyhrazena.',
    privacy: 'Ochrana osobních údajů',
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
