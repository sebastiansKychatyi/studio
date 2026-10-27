// Страницы городов для локального SEO: /sk/bratislava, /cs/praha, /uk/kyiv …
// Порядок = приоритет: Bratislava, Nitra → Praha → Kyiv, Uzhhorod.
// inPerson — можно встретиться лично; projects — какие проекты показать на странице города.

type CityText = {
  name: string
  loc: string // «в городе» в нужном падеже: «v Bratislave», «v Praze», «у Києві»
  metaTitle: string
  metaDescription: string
  h1: [string, string] // [начало, выделенная часть]
  intro: string
  points: [string, string][] // локальные преимущества
  faq: [string, string][]
}

export type City = {
  slug: string
  country: 'SK' | 'CZ' | 'UA'
  geo: { lat: number; lng: number }
  inPerson: boolean
  projects: string[]
  text: { sk: CityText; cs: CityText; uk: CityText }
}

export const cities: City[] = [
  {
    slug: 'bratislava',
    country: 'SK',
    geo: { lat: 48.1486, lng: 17.1077 },
    inPerson: true,
    projects: ['brtc', 'e-drivebook', 'expertsk'],
    text: {
      sk: {
        name: 'Bratislava', loc: 'v Bratislave',
        metaTitle: 'AI automatizácia a tvorba webov v Bratislave | Duo Studio',
        metaDescription: 'AI automatizácia, tvorba webových stránok, aplikácií a mini hier pre firmy v Bratislave. Osobné stretnutie, pevná cena a podpora po spustení.',
        h1: ['AI automatizácia a weby', 'v Bratislave'],
        intro: 'Pomáhame firmám v Bratislave šetriť čas a získavať zákazníkov: automatizujeme procesy pomocou AI, tvoríme rýchle weby, aplikácie a mini hry a integrujeme umelú inteligenciu do vašich systémov.',
        points: [
          ['Osobné stretnutie', 'Za klientmi v Bratislave a okolí prídeme osobne — od Starého Mesta cez Ružinov až po Petržalku.'],
          ['Lokálne SEO pre Bratislavu', 'Web nastavíme tak, aby vás našli zákazníci, ktorí hľadajú vaše služby v Bratislave — v Google aj v AI asistentoch.'],
          ['Skúsenosti z Bratislavy', 'Robili sme pre bratislavské firmy, napríklad web pre Bratislava Technical Company, a na hybridných projektoch priamo v Bratislave.'],
        ],
        faq: [
          ['Robíte weby a AI automatizácie pre firmy v Bratislave?', 'Áno. Pre firmy v Bratislave a okolí robíme AI automatizácie, weby, e-shopy, aplikácie aj mini hry. Prvé stretnutie môže byť osobne v Bratislave alebo online.'],
          ['Koľko stojí web pre firmu v Bratislave?', 'Cenu určujeme podľa rozsahu, nie podľa adresy. Po bezplatnej konzultácii pošleme pevnú cenovú ponuku bez skrytých poplatkov.'],
        ],
      },
      cs: {
        name: 'Bratislava', loc: 'v Bratislavě',
        metaTitle: 'AI automatizace a tvorba webů v Bratislavě | Duo Studio',
        metaDescription: 'AI automatizace, tvorba webových stránek, aplikací a mini her pro firmy v Bratislavě. Osobní schůzka, pevná cena a podpora po spuštění.',
        h1: ['AI automatizace a weby', 'v Bratislavě'],
        intro: 'Pomáháme firmám v Bratislavě šetřit čas a získávat zákazníky: automatizujeme procesy pomocí AI, tvoříme rychlé weby, aplikace a mini hry a integrujeme umělou inteligenci do vašich systémů.',
        points: [
          ['Osobní schůzka', 'Za klienty v Bratislavě a okolí přijedeme osobně — od Starého Města přes Ružinov až po Petržalku.'],
          ['Lokální SEO pro Bratislavu', 'Web nastavíme tak, aby vás našli zákazníci, kteří hledají vaše služby v Bratislavě — v Googlu i v AI asistentech.'],
          ['Zkušenosti z Bratislavy', 'Pracovali jsme pro bratislavské firmy, například web pro Bratislava Technical Company, a na hybridních projektech přímo v Bratislavě.'],
        ],
        faq: [
          ['Děláte weby a AI automatizace pro firmy v Bratislavě?', 'Ano. Pro firmy v Bratislavě a okolí děláme AI automatizace, weby, e-shopy, aplikace i mini hry. První schůzka může být osobně v Bratislavě nebo online.'],
          ['Kolik stojí web pro firmu v Bratislavě?', 'Cenu určujeme podle rozsahu, ne podle adresy. Po bezplatné konzultaci pošleme pevnou cenovou nabídku bez skrytých poplatků.'],
        ],
      },
      uk: {
        name: 'Братислава', loc: 'у Братиславі',
        metaTitle: 'AI-автоматизація та створення сайтів у Братиславі | Duo Studio',
        metaDescription: 'AI-автоматизація, розробка сайтів, застосунків і міні-ігор для бізнесу в Братиславі. Особиста зустріч, фіксована ціна та підтримка після запуску.',
        h1: ['AI-автоматизація та сайти', 'у Братиславі'],
        intro: 'Допомагаємо компаніям у Братиславі економити час і залучати клієнтів: автоматизуємо процеси за допомогою AI, створюємо швидкі сайти, застосунки та міні-ігри й інтегруємо штучний інтелект у ваші системи.',
        points: [
          ['Особиста зустріч', 'До клієнтів у Братиславі та околицях приїдемо особисто — від Старого Міста до Ружинова й Петржалки.'],
          ['Локальне SEO для Братислави', 'Налаштуємо сайт так, щоб вас знаходили клієнти, які шукають ваші послуги в Братиславі — у Google та AI-асистентах.'],
          ['Досвід у Братиславі', 'Працювали для братиславських компаній, зокрема сайт для Bratislava Technical Company, та над гібридними проєктами безпосередньо в Братиславі.'],
        ],
        faq: [
          ['Ви робите сайти та AI-автоматизацію для компаній у Братиславі?', 'Так. Для бізнесу в Братиславі та околицях робимо AI-автоматизацію, сайти, інтернет-магазини, застосунки й міні-ігри. Першу зустріч можна провести особисто в Братиславі або онлайн.'],
          ['Скільки коштує сайт для компанії в Братиславі?', 'Ціна залежить від обсягу, а не від адреси. Після безкоштовної консультації надішлемо фіксовану пропозицію без прихованих платежів.'],
        ],
      },
    },
  },
  {
    slug: 'nitra',
    country: 'SK',
    geo: { lat: 48.3069, lng: 18.0864 },
    inPerson: true,
    projects: ['hodinovy-manzel', 'e-drivebook', 'amstars'],
    text: {
      sk: {
        name: 'Nitra', loc: 'v Nitre',
        metaTitle: 'AI automatizácia a tvorba webov v Nitre | Duo Studio',
        metaDescription: 'Tvorba webových stránok, aplikácií a mini hier, AI automatizácia a integrácia umelej inteligencie pre firmy v Nitre a okolí. Sme z Nitry.',
        h1: ['AI automatizácia a weby', 'v Nitre'],
        intro: 'Sme vývojársky tím s koreňmi v Nitre. Nitrianskym firmám a podnikateľom robíme weby, aplikácie a mini hry, automatizujeme rutinnú prácu pomocou AI a prepájame ich systémy s umelou inteligenciou.',
        points: [
          ['Sme z Nitry', 'Stretneme sa osobne v Nitre a okolí — na Zobore, Klokočine, Chrenovej či priamo u vás vo firme.'],
          ['Lokálne SEO pre Nitru', 'Pomôžeme vám, aby vás zákazníci našli, keď v Google hľadajú vaše služby v Nitre a okolí.'],
          ['Nitrianske projekty', 'Pre nitrianskych podnikateľov sme už robili weby, napríklad landing page Hodinový manžel Nitra, a študujeme na UKF v Nitre.'],
        ],
        faq: [
          ['Robíte weby pre firmy v Nitre?', 'Áno, sme z Nitry. Robíme weby, e-shopy, aplikácie aj AI automatizácie pre firmy v Nitre a v celom Nitrianskom kraji a radi sa stretneme osobne.'],
          ['Pomôžete malému podniku v Nitre s webom a SEO?', 'Áno. Pre živnostníkov a malé firmy pripravíme rýchly web s lokálnym SEO, aby vás našli zákazníci z Nitry a okolia.'],
        ],
      },
      cs: {
        name: 'Nitra', loc: 'v Nitře',
        metaTitle: 'AI automatizace a tvorba webů v Nitře | Duo Studio',
        metaDescription: 'Tvorba webových stránek, aplikací a mini her, AI automatizace a integrace umělé inteligence pro firmy v Nitře a okolí.',
        h1: ['AI automatizace a weby', 'v Nitře'],
        intro: 'Jsme vývojářský tým s kořeny v Nitře. Firmám a podnikatelům v Nitře děláme weby, aplikace a mini hry, automatizujeme rutinní práci pomocí AI a propojujeme jejich systémy s umělou inteligencí.',
        points: [
          ['Jsme z Nitry', 'Sejdeme se osobně v Nitře a okolí — na Zoboru, Klokočině, Chrenové nebo přímo u vás ve firmě.'],
          ['Lokální SEO pro Nitru', 'Pomůžeme vám, aby vás zákazníci našli, když v Googlu hledají vaše služby v Nitře a okolí.'],
          ['Projekty z Nitry', 'Pro podnikatele z Nitry jsme už dělali weby, například landing page Hodinový manžel Nitra, a studujeme na UKF v Nitře.'],
        ],
        faq: [
          ['Děláte weby pro firmy v Nitře?', 'Ano, jsme z Nitry. Děláme weby, e-shopy, aplikace i AI automatizace pro firmy v Nitře a v celém Nitranském kraji a rádi se sejdeme osobně.'],
          ['Pomůžete malému podniku v Nitře s webem a SEO?', 'Ano. Pro živnostníky a malé firmy připravíme rychlý web s lokálním SEO, aby vás našli zákazníci z Nitry a okolí.'],
        ],
      },
      uk: {
        name: 'Нітра', loc: 'у Нітрі',
        metaTitle: 'AI-автоматизація та створення сайтів у Нітрі | Duo Studio',
        metaDescription: 'Розробка сайтів, застосунків і міні-ігор, AI-автоматизація та інтеграція штучного інтелекту для бізнесу в Нітрі та околицях.',
        h1: ['AI-автоматизація та сайти', 'у Нітрі'],
        intro: 'Ми — команда розробників із Нітри. Робимо для компаній і підприємців у Нітрі сайти, застосунки та міні-ігри, автоматизуємо рутину за допомогою AI та поєднуємо їхні системи зі штучним інтелектом.',
        points: [
          ['Ми з Нітри', 'Зустрінемося особисто в Нітрі та околицях — на Зоборі, Клокочині, Хреновій або просто у вашому офісі.'],
          ['Локальне SEO для Нітри', 'Допоможемо, щоб вас знаходили клієнти, які шукають ваші послуги в Нітрі та околицях.'],
          ['Проєкти в Нітрі', 'Ми вже робили сайти для підприємців із Нітри, зокрема лендинг Hodinový manžel Nitra, і навчаємося в UKF у Нітрі.'],
        ],
        faq: [
          ['Ви робите сайти для компаній у Нітрі?', 'Так, ми з Нітри. Робимо сайти, інтернет-магазини, застосунки та AI-автоматизацію для бізнесу в Нітрі й усьому Нітранському краї, охоче зустрінемося особисто.'],
          ['Допоможете малому бізнесу в Нітрі із сайтом і SEO?', 'Так. Для ФОП і малих компаній зробимо швидкий сайт із локальним SEO, щоб вас знаходили клієнти з Нітри та околиць.'],
        ],
      },
    },
  },
  {
    slug: 'praha',
    country: 'CZ',
    geo: { lat: 50.0755, lng: 14.4378 },
    inPerson: false,
    projects: ['e-drivebook', 'expertsk', 'brtc'],
    text: {
      sk: {
        name: 'Praha', loc: 'v Prahe',
        metaTitle: 'AI automatizácia a tvorba webov pre firmy v Prahe | Duo Studio',
        metaDescription: 'AI automatizácia, tvorba webov, aplikácií a mini hier pre firmy v Prahe a v celom Česku. Spolupráca na diaľku, komunikácia v češtine aj slovenčine.',
        h1: ['AI automatizácia a weby', 'pre Prahu'],
        intro: 'Firmám v Prahe a v celom Česku pomáhame na diaľku: automatizujeme procesy pomocou AI, tvoríme weby, aplikácie a mini hry a integrujeme umelú inteligenciu do ich systémov.',
        points: [
          ['Spolupráca na diaľku', 'Konzultácie, návrhy aj odovzdanie prebiehajú online. Pri väčšom projekte sa vieme dohodnúť aj na osobnom stretnutí.'],
          ['SEO pre Google aj Seznam', 'Weby pre český trh optimalizujeme pre Google aj Seznam.cz a pre AI vyhľadávače.'],
          ['Čeština bez prekladateľa', 'Komunikujeme po česky aj po slovensky, texty na web pripravíme v prirodzenej češtine.'],
        ],
        faq: [
          ['Pracujete aj pre firmy v Prahe?', 'Áno. Pre klientov v Prahe a v celom Česku pracujeme na diaľku — od konzultácie po spustenie a ďalšiu podporu.'],
          ['Optimalizujete weby aj pre Seznam?', 'Áno. Pre český trh nastavujeme SEO pre Google aj Seznam.cz, štruktúrované dáta a GEO pre AI asistentov.'],
        ],
      },
      cs: {
        name: 'Praha', loc: 'v Praze',
        metaTitle: 'AI automatizace a tvorba webů v Praze | Duo Studio',
        metaDescription: 'AI automatizace, tvorba webových stránek, aplikací a mini her pro firmy v Praze a po celém Česku. Spolupráce na dálku, komunikace česky.',
        h1: ['AI automatizace a weby', 'pro Prahu'],
        intro: 'Firmám v Praze a po celém Česku pomáháme na dálku: automatizujeme procesy pomocí AI, tvoříme weby, aplikace a mini hry a integrujeme umělou inteligenci do jejich systémů.',
        points: [
          ['Spolupráce na dálku', 'Konzultace, návrhy i předání probíhají online. U většího projektu se domluvíme i na osobní schůzce.'],
          ['SEO pro Google i Seznam', 'Weby pro český trh optimalizujeme pro Google i Seznam.cz a pro AI vyhledávače.'],
          ['Česky, bez překladatele', 'Komunikujeme česky i slovensky, texty na web připravíme v přirozené češtině.'],
        ],
        faq: [
          ['Pracujete pro firmy v Praze?', 'Ano. Pro klienty v Praze a po celém Česku pracujeme na dálku — od konzultace po spuštění a další podporu.'],
          ['Optimalizujete weby i pro Seznam?', 'Ano. Pro český trh nastavujeme SEO pro Google i Seznam.cz, strukturovaná data a GEO pro AI asistenty.'],
        ],
      },
      uk: {
        name: 'Прага', loc: 'у Празі',
        metaTitle: 'AI-автоматизація та створення сайтів для бізнесу в Празі | Duo Studio',
        metaDescription: 'AI-автоматизація, розробка сайтів, застосунків і міні-ігор для компаній у Празі та по всій Чехії. Віддалена співпраця, спілкування українською та чеською.',
        h1: ['AI-автоматизація та сайти', 'для Праги'],
        intro: 'Допомагаємо компаніям у Празі та по всій Чехії віддалено: автоматизуємо процеси за допомогою AI, створюємо сайти, застосунки та міні-ігри й інтегруємо штучний інтелект у їхні системи.',
        points: [
          ['Віддалена співпраця', 'Консультації, макети та здача проєкту проходять онлайн. Для великого проєкту домовимося й про особисту зустріч.'],
          ['SEO для Google і Seznam', 'Сайти для чеського ринку оптимізуємо під Google, Seznam.cz та AI-пошук.'],
          ['Чеська та українська', 'Спілкуємося українською, чеською та словацькою, тексти для сайту готуємо природною чеською.'],
        ],
        faq: [
          ['Ви працюєте з компаніями в Празі?', 'Так. З клієнтами в Празі та по всій Чехії працюємо віддалено — від консультації до запуску й подальшої підтримки.'],
          ['Ви оптимізуєте сайти під Seznam?', 'Так. Для чеського ринку налаштовуємо SEO під Google і Seznam.cz, структуровані дані та GEO для AI-асистентів.'],
        ],
      },
    },
  },
  {
    slug: 'kyiv',
    country: 'UA',
    geo: { lat: 50.4501, lng: 30.5234 },
    inPerson: false,
    projects: ['e-drivebook', 'expertsk', 'amstars'],
    text: {
      sk: {
        name: 'Kyjev', loc: 'v Kyjeve',
        metaTitle: 'AI automatizácia a tvorba webov pre firmy v Kyjeve | Duo Studio',
        metaDescription: 'AI automatizácia, tvorba webov, aplikácií a mini hier pre firmy v Kyjeve a na Ukrajine. Spolupráca na diaľku, komunikácia v ukrajinčine.',
        h1: ['AI automatizácia a weby', 'pre Kyjev'],
        intro: 'Firmám v Kyjeve a na celej Ukrajine pomáhame na diaľku: automatizujeme procesy pomocou AI, tvoríme weby, aplikácie a mini hry a integrujeme umelú inteligenciu do ich systémov.',
        points: [
          ['Po ukrajinsky', 'Komunikujeme po ukrajinsky, rozumieme miestnemu trhu a pripravíme web v ukrajinčine aj pre EÚ.'],
          ['Vstup na trh EÚ', 'Pomôžeme ukrajinským firmám s viacjazyčným webom a SEO pre Slovensko, Česko a ďalšie krajiny EÚ.'],
          ['Spolupráca na diaľku', 'Časový rozdiel je len hodina, konzultácie a odovzdanie prebiehajú online.'],
        ],
        faq: [
          ['Pracujete pre firmy v Kyjeve?', 'Áno. Pre klientov v Kyjeve a na celej Ukrajine pracujeme na diaľku a komunikujeme po ukrajinsky.'],
          ['Pomôžete ukrajinskej firme so vstupom na trh EÚ?', 'Áno. Pripravíme viacjazyčný web (UA, SK, CZ, EN) s SEO pre konkrétne krajiny EÚ a integrujeme AI nástroje do vašich procesov.'],
        ],
      },
      cs: {
        name: 'Kyjev', loc: 'v Kyjevě',
        metaTitle: 'AI automatizace a tvorba webů pro firmy v Kyjevě | Duo Studio',
        metaDescription: 'AI automatizace, tvorba webů, aplikací a mini her pro firmy v Kyjevě a na Ukrajině. Spolupráce na dálku, komunikace ukrajinsky.',
        h1: ['AI automatizace a weby', 'pro Kyjev'],
        intro: 'Firmám v Kyjevě a na celé Ukrajině pomáháme na dálku: automatizujeme procesy pomocí AI, tvoříme weby, aplikace a mini hry a integrujeme umělou inteligenci do jejich systémů.',
        points: [
          ['Ukrajinsky', 'Komunikujeme ukrajinsky, rozumíme místnímu trhu a připravíme web v ukrajinštině i pro EU.'],
          ['Vstup na trh EU', 'Pomůžeme ukrajinským firmám s vícejazyčným webem a SEO pro Slovensko, Česko a další země EU.'],
          ['Spolupráce na dálku', 'Časový rozdíl je jen hodina, konzultace a předání probíhají online.'],
        ],
        faq: [
          ['Pracujete pro firmy v Kyjevě?', 'Ano. Pro klienty v Kyjevě a na celé Ukrajině pracujeme na dálku a komunikujeme ukrajinsky.'],
          ['Pomůžete ukrajinské firmě se vstupem na trh EU?', 'Ano. Připravíme vícejazyčný web (UA, SK, CZ, EN) se SEO pro konkrétní země EU a integrujeme AI nástroje do vašich procesů.'],
        ],
      },
      uk: {
        name: 'Київ', loc: 'у Києві',
        metaTitle: 'AI-автоматизація та створення сайтів у Києві | Duo Studio',
        metaDescription: 'AI-автоматизація, розробка сайтів, застосунків і міні-ігор для бізнесу в Києві та по всій Україні. Віддалена співпраця українською мовою, вихід на ринок ЄС.',
        h1: ['AI-автоматизація та сайти', 'для Києва'],
        intro: 'Допомагаємо компаніям у Києві та по всій Україні віддалено: автоматизуємо процеси за допомогою AI, створюємо сайти, застосунки та міні-ігри й інтегруємо штучний інтелект у ваші системи.',
        points: [
          ['Українською мовою', 'Спілкуємося українською, розуміємо місцевий ринок і зробимо сайт як для України, так і для ЄС.'],
          ['Вихід на ринок ЄС', 'Допоможемо українським компаніям з багатомовним сайтом і SEO для Словаччини, Чехії та інших країн ЄС.'],
          ['Віддалена співпраця', 'Різниця в часі — лише година, консультації та здача проєкту відбуваються онлайн.'],
        ],
        faq: [
          ['Ви працюєте з компаніями в Києві?', 'Так. З клієнтами в Києві та по всій Україні працюємо віддалено й спілкуємося українською.'],
          ['Допоможете українській компанії вийти на ринок ЄС?', 'Так. Зробимо багатомовний сайт (UA, SK, CZ, EN) із SEO під конкретні країни ЄС та інтегруємо AI-інструменти у ваші процеси.'],
        ],
      },
    },
  },
  {
    slug: 'uzhhorod',
    country: 'UA',
    geo: { lat: 48.6208, lng: 22.2879 },
    inPerson: false,
    projects: ['hodinovy-manzel', 'e-drivebook', 'expertsk'],
    text: {
      sk: {
        name: 'Užhorod', loc: 'v Užhorode',
        metaTitle: 'AI automatizácia a tvorba webov pre firmy v Užhorode | Duo Studio',
        metaDescription: 'AI automatizácia, tvorba webov, aplikácií a mini hier pre firmy v Užhorode a na Zakarpatí. Blízko slovenských hraníc, komunikácia po ukrajinsky aj slovensky.',
        h1: ['AI automatizácia a weby', 'pre Užhorod'],
        intro: 'Užhorod leží hneď pri slovenských hraniciach. Firmám v Užhorode a na Zakarpatí robíme weby, aplikácie a mini hry, automatizujeme ich procesy pomocou AI a pomáhame im osloviť zákazníkov na Slovensku aj na Ukrajine.',
        points: [
          ['Blízko Slovenska', 'Užhorod a Zakarpatie sú hneď za hranicou — pomôžeme vám osloviť zákazníkov na Ukrajine aj na Slovensku.'],
          ['Ukrajinčina aj slovenčina', 'Komunikujeme po ukrajinsky aj po slovensky a pripravíme dvojjazyčný web s lokálnym SEO.'],
          ['Cezhraničný biznis', 'Weby a automatizácie pre firmy, ktoré obchodujú medzi Ukrajinou a EÚ — od objednávok po faktúry.'],
        ],
        faq: [
          ['Pracujete pre firmy v Užhorode?', 'Áno. Pre klientov v Užhorode a na Zakarpatí pracujeme na diaľku a komunikujeme po ukrajinsky aj po slovensky.'],
          ['Viete urobiť web pre ukrajinských aj slovenských zákazníkov?', 'Áno. Pripravíme dvojjazyčný web s SEO pre Ukrajinu aj Slovensko, aby vás našli zákazníci na oboch stranách hranice.'],
        ],
      },
      cs: {
        name: 'Užhorod', loc: 'v Užhorodu',
        metaTitle: 'AI automatizace a tvorba webů pro firmy v Užhorodu | Duo Studio',
        metaDescription: 'AI automatizace, tvorba webů, aplikací a mini her pro firmy v Užhorodu a na Zakarpatí. Blízko slovenských hranic, komunikace ukrajinsky i slovensky.',
        h1: ['AI automatizace a weby', 'pro Užhorod'],
        intro: 'Užhorod leží hned u slovenských hranic. Firmám v Užhorodu a na Zakarpatí děláme weby, aplikace a mini hry, automatizujeme jejich procesy pomocí AI a pomáháme jim oslovit zákazníky na Slovensku i na Ukrajině.',
        points: [
          ['Blízko Slovenska', 'Užhorod a Zakarpatí jsou hned za hranicí — pomůžeme vám oslovit zákazníky na Ukrajině i na Slovensku.'],
          ['Ukrajinsky i slovensky', 'Komunikujeme ukrajinsky i slovensky a připravíme dvojjazyčný web s lokálním SEO.'],
          ['Přeshraniční byznys', 'Weby a automatizace pro firmy, které obchodují mezi Ukrajinou a EU — od objednávek po faktury.'],
        ],
        faq: [
          ['Pracujete pro firmy v Užhorodu?', 'Ano. Pro klienty v Užhorodu a na Zakarpatí pracujeme na dálku a komunikujeme ukrajinsky i slovensky.'],
          ['Umíte udělat web pro ukrajinské i slovenské zákazníky?', 'Ano. Připravíme dvojjazyčný web se SEO pro Ukrajinu i Slovensko, aby vás našli zákazníci na obou stranách hranice.'],
        ],
      },
      uk: {
        name: 'Ужгород', loc: 'в Ужгороді',
        metaTitle: 'AI-автоматизація та створення сайтів в Ужгороді | Duo Studio',
        metaDescription: 'AI-автоматизація, розробка сайтів, застосунків і міні-ігор для бізнесу в Ужгороді та на Закарпатті. Поруч зі Словаччиною, спілкування українською та словацькою.',
        h1: ['AI-автоматизація та сайти', 'для Ужгорода'],
        intro: 'Ужгород — просто біля кордону зі Словаччиною. Робимо для компаній з Ужгорода та Закарпаття сайти, застосунки й міні-ігри, автоматизуємо процеси за допомогою AI та допомагаємо залучати клієнтів і в Україні, і в Словаччині.',
        points: [
          ['Поруч зі Словаччиною', 'Ужгород і Закарпаття — одразу за кордоном. Допоможемо знайти клієнтів і в Україні, і в Словаччині.'],
          ['Українська та словацька', 'Спілкуємося українською та словацькою, зробимо двомовний сайт із локальним SEO.'],
          ['Транскордонний бізнес', 'Сайти та автоматизація для компаній, що працюють між Україною та ЄС — від замовлень до рахунків.'],
        ],
        faq: [
          ['Ви працюєте з компаніями в Ужгороді?', 'Так. З клієнтами в Ужгороді та на Закарпатті працюємо віддалено, спілкуємося українською та словацькою.'],
          ['Можете зробити сайт і для українських, і для словацьких клієнтів?', 'Так. Зробимо двомовний сайт із SEO для України та Словаччини, щоб вас знаходили клієнти по обидва боки кордону.'],
        ],
      },
    },
  },
]
