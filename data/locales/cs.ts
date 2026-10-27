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
      { value: 7, suffix: '+', label: 'projektů v portfoliu' },
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
        role: 'Web developer & AI automatizace',
        bio: 'Programuje firemní weby, backend v Pythonu (FastAPI) a aplikace v Nuxtu. Propojuje systémy s AI, aby rutinní práce běžela sama.',
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
    projects: {
      fscommerce: { desc: 'Vícestránkový web pro dodavatele kompresorových stanic — katalog produktů, servis, cenová nabídka a dotazník.' },
      brtc: { desc: 'Firemní web technické společnosti s katalogem kompresorových řešení pro průmysl.' },
      azs: { desc: 'Maďarská verze průmyslového webu — produkty, služby, servis a poptávkový formulář.' },
      onyx: { desc: 'Prezentace nových kancelářských prostor ve Zlatých Moravcích s mapou a kontaktem.' },
      'hodinovy-manzel': { desc: 'Landing page pro údržbáře v Nitře — služby po místnostech, ceník, reference a formulář bez backendu.' },
      amstars: { desc: 'Bakalářská práce: platforma pro amatérský fotbal — týmy, výzvy k zápasům, ELO rating a turnaje.' },
      'travel-planner': { desc: 'REST API pro plánování cest po uměleckých dílech, ověřované přes živé API Art Institute of Chicago.' },
      'nordic-living': { desc: 'Vizuální identita a UI kit pro značku skandinávského nábytku.' },
      'slnecne-byty': { desc: 'UX návrh a prototyp webu pro developerský projekt s výběrem bytů.' },
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
      { q: 'Pracujete i pro klienty z Česka?', a: 'Ano. Pracujeme na dálku pro klienty z Česka, Slovenska, Ukrajiny i Maďarska a komunikujeme česky, slovensky i ukrajinsky.' },
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
    journey: 'Co jsem dělal',
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
      experience: 'Zkušenosti a projekty',
      projects: 'Vybrané projekty',
      info: 'Informace',
      contact: 'Kontakt',
      web: 'Web',
      metaTitle: 'Životopis',
    },
    people: {
      p1: {
        metaTitle: 'Sebastian Kychatyi — web developer a AI automatizace',
        metaDescription: 'Sebastian Kychatyi, web developer: firemní weby, backend v Pythonu (FastAPI), aplikace v Nuxtu a automatizace procesů pomocí AI. Portfolio a kontakt.',
        headline: 'Programuji weby a automatizace, které šetří čas.',
        intro: 'Web developer z Nitry. Dělám firemní weby, backend v Pythonu a propojuji systémy s AI, aby pracovaly za vás.',
        bio: [
          'Studuji na Fakultě přírodních věd a informatiky UKF v Nitře. Moje bakalářská práce AmStars je platforma pro amatérský fotbal postavená na FastAPI, PostgreSQL a Nuxtu.',
          'Pro firmy jsem vytvořil weby jako F.S. Commerce, Bratislava Technical Company či AZS Engineering — rychlé, vícestránkové a připravené na SEO. Teď se věnuji hlavně automatizaci procesů pomocí AI. (Upravte text podle sebe.)',
        ],
        facts: [
          { k: 'Lokalita', v: 'Nitra, Slovensko' },
          { k: 'Studium', v: 'FPVaI UKF Nitra' },
          { k: 'Zaměření', v: 'Frontend · Backend · AI' },
        ],
        timeline: [
          { year: '2026', title: 'AmStars — bakalářská práce', text: 'Platforma pro amatérské fotbalové týmy: výzvy, ELO rating, turnaje. FastAPI, PostgreSQL, Redis, Nuxt 3, Docker.' },
          { year: '2026', title: 'Weby pro průmyslové firmy', text: 'F.S. Commerce, Bratislava Technical Company a maďarská AZS Engineering — produktové katalogy, poptávkové formuláře, více jazyků.' },
          { year: '2026', title: 'Travel Planner API', text: 'Asynchronní REST API ve FastAPI s validací přes externí API.' },
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
        timeline: [
          { year: '2026', title: 'Váš projekt', text: 'Doplňte projekt, na který jste hrdý.' },
          { year: '2025', title: 'Váš projekt', text: 'Doplňte další projekt nebo zkušenost.' },
        ],
      },
    },
  },
}

export default cs
