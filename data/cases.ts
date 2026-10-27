// Case studies: /sk/case/<id>
// id matches a project in data/site.ts (link, screenshot, tags).
// Verifiable facts only.

type CaseText = {
  metaTitle: string
  metaDescription: string
  lead: string
  client: string
  role: string
  challenge: string
  solution: string
  features: [string, string][]
  results: [string, string][] // [value, label]
}

export type CaseStudy = {
  id: string
  stack: string[]
  text: { sk: CaseText; cs: CaseText; uk: CaseText; en: CaseText }
}

const base: (Omit<CaseStudy, 'text'> & { text: Omit<CaseStudy['text'], 'en'> })[] = [
  {
    id: 'e-drivebook',
    stack: ['Python', 'FastAPI', 'PostgreSQL', 'SQLAlchemy', 'Alembic', 'OAuth2 / JWT', 'Nuxt 3', 'Vue.js', 'Pinia', 'Docker Compose', 'Caddy', 'GitHub Actions', 'pytest'],
    text: {
      sk: {
        metaTitle: 'e-Drivebook — prípadová štúdia: SaaS pre autoškoly | Duo Studio',
        metaDescription: 'Ako sme od nuly postavili e-Drivebook — softvér pre autoškoly s online rezerváciami jázd 24/7, rozvrhmi inštruktorov a evidenciou žiakov. FastAPI, PostgreSQL, Nuxt 3.',
        lead: 'Vlastný SaaS pre autoškoly — od prvých požiadaviek až po produkciu, ktorú denne používajú platiace autoškoly.',
        client: 'Autoškoly na Slovensku', role: 'Návrh, backend, frontend, nasadenie',
        challenge: 'Autoškoly plánovali jazdy cez telefón, papierové zošity a tabuľky. Žiaci nevedeli, kedy je voľný termín, inštruktori strácali čas dohadovaním a evidencia jázd a vozidiel bola roztrúsená na viacerých miestach.',
        solution: 'Navrhli sme a od nuly naprogramovali webovú aplikáciu, ktorá rieši rezervácie, rozvrhy, žiakov, inštruktorov aj autá na jednom mieste. Žiaci si rezervujú jazdy online 24/7 z počítača aj mobilu, autoškola má prehľad v administrácii.',
        features: [
          ['Online rezervácie 24/7', 'Žiaci si sami vyberú voľný termín jazdy — bez telefonovania.'],
          ['Rozvrhy inštruktorov', 'Automatické plánovanie jázd podľa dostupnosti inštruktorov a vozidiel.'],
          ['Evidencia žiakov a výcviku', 'Záznamy o jazdách, ich dĺžke a postupe každého žiaka.'],
          ['Vozový park', 'Prehľad áut a ich údržby na jednom mieste.'],
          ['Testy na skúšku', 'Príprava žiakov na teoretickú časť skúšky priamo v aplikácii.'],
          ['Bezpečné prihlásenie', 'OAuth2 / JWT, oddelené prístupy pre administrátora, inštruktorov a žiakov.'],
        ],
        results: [['3', 'platiace autoškoly používajú systém denne'], ['24/7', 'online rezervácie jázd pre žiakov'], ['1', 'vývojár od databázy po nasadenie'], ['CI/CD', 'automatické testy a nasadzovanie cez GitHub Actions']],
      },
      cs: {
        metaTitle: 'e-Drivebook — případová studie: SaaS pro autoškoly | Duo Studio',
        metaDescription: 'Jak jsme od nuly postavili e-Drivebook — software pro autoškoly s online rezervacemi jízd 24/7, rozvrhy instruktorů a evidencí žáků. FastAPI, PostgreSQL, Nuxt 3.',
        lead: 'Vlastní SaaS pro autoškoly — od prvních požadavků až po produkci, kterou denně používají platící autoškoly.',
        client: 'Autoškoly na Slovensku', role: 'Návrh, backend, frontend, nasazení',
        challenge: 'Autoškoly plánovaly jízdy přes telefon, papírové sešity a tabulky. Žáci nevěděli, kdy je volný termín, instruktoři ztráceli čas domlouváním a evidence jízd a vozidel byla roztroušená na více místech.',
        solution: 'Navrhli jsme a od nuly naprogramovali webovou aplikaci, která řeší rezervace, rozvrhy, žáky, instruktory i auta na jednom místě. Žáci si rezervují jízdy online 24/7 z počítače i mobilu, autoškola má přehled v administraci.',
        features: [
          ['Online rezervace 24/7', 'Žáci si sami vyberou volný termín jízdy — bez telefonování.'],
          ['Rozvrhy instruktorů', 'Automatické plánování jízd podle dostupnosti instruktorů a vozidel.'],
          ['Evidence žáků a výcviku', 'Záznamy o jízdách, jejich délce a postupu každého žáka.'],
          ['Vozový park', 'Přehled aut a jejich údržby na jednom místě.'],
          ['Testy na zkoušku', 'Příprava žáků na teoretickou část zkoušky přímo v aplikaci.'],
          ['Bezpečné přihlášení', 'OAuth2 / JWT, oddělené přístupy pro administrátora, instruktory a žáky.'],
        ],
        results: [['3', 'platící autoškoly používají systém denně'], ['24/7', 'online rezervace jízd pro žáky'], ['1', 'vývojář od databáze po nasazení'], ['CI/CD', 'automatické testy a nasazování přes GitHub Actions']],
      },
      uk: {
        metaTitle: 'e-Drivebook — кейс: SaaS для автошкіл | Duo Studio',
        metaDescription: 'Як ми з нуля створили e-Drivebook — програму для автошкіл з онлайн-бронюванням занять 24/7, розкладом інструкторів і обліком учнів. FastAPI, PostgreSQL, Nuxt 3.',
        lead: 'Власний SaaS для автошкіл — від перших вимог до продакшену, яким щодня користуються платні автошколи.',
        client: 'Автошколи в Словаччині', role: 'Проєктування, бекенд, фронтенд, деплой',
        challenge: 'Автошколи планували заняття телефоном, у паперових журналах і таблицях. Учні не знали, коли є вільний час, інструктори витрачали час на узгодження, а облік занять і автомобілів був розкиданий по різних місцях.',
        solution: 'Ми спроєктували й з нуля розробили вебзастосунок, що об’єднує бронювання, розклад, учнів, інструкторів і автомобілі в одному місці. Учні бронюють заняття онлайн 24/7 з комп’ютера й телефона, а автошкола бачить усе в адмінпанелі.',
        features: [
          ['Онлайн-бронювання 24/7', 'Учні самі обирають вільний час заняття — без дзвінків.'],
          ['Розклад інструкторів', 'Автоматичне планування занять за доступністю інструкторів і автомобілів.'],
          ['Облік учнів і навчання', 'Записи про заняття, їхню тривалість і прогрес кожного учня.'],
          ['Автопарк', 'Огляд автомобілів та їх обслуговування в одному місці.'],
          ['Тести до іспиту', 'Підготовка учнів до теоретичної частини іспиту просто в застосунку.'],
          ['Безпечний вхід', 'OAuth2 / JWT, окремі доступи для адміністратора, інструкторів і учнів.'],
        ],
        results: [['3', 'платні автошколи користуються системою щодня'], ['24/7', 'онлайн-бронювання занять для учнів'], ['1', 'розробник від бази даних до деплою'], ['CI/CD', 'автотести та деплой через GitHub Actions']],
      },
    },
  },
  {
    id: 'expertsk',
    stack: ['Nuxt', 'Vue.js', 'Tailwind CSS', 'i18n (SK · EN · RU)', 'SSR', 'hreflang'],
    text: {
      sk: {
        metaTitle: 'Expert SK — prípadová štúdia: katalóg overených majstrov | Duo Studio',
        metaDescription: 'Expert SK — trojjazyčná platforma na vyhľadanie overených majstrov na Slovensku: služby, mestá, hodnotenia a registrácia pre profesionálov. Nuxt, Tailwind CSS.',
        lead: 'Platforma, kde zákazníci na Slovensku nájdu overeného elektrikára, inštalatéra či upratovaciu službu vo svojom meste.',
        client: 'Platforma služieb, Slovensko', role: 'Návrh, vývoj, SEO, viacjazyčnosť',
        challenge: 'Nájsť spoľahlivého majstra je zdĺhavé: ponuky sú roztrúsené po inzerátoch a sociálnych sieťach, chýbajú hodnotenia a ceny a cudzinci na Slovensku narážajú aj na jazykovú bariéru.',
        solution: 'Vytvorili sme katalóg služieb s vyhľadávaním podľa typu práce a mesta, profilmi majstrov s hodnoteniami a cenami a priamym kontaktom. Platforma je v slovenčine, angličtine aj ruštine a majstri sa môžu sami zaregistrovať.',
        features: [
          ['Vyhľadávanie', 'Podľa služby a mesta — od hodinového manžela po automechanika.'],
          ['10+ kategórií', 'Elektrikár, inštalatér, maliar, obkladač, montáž nábytku, upratovanie, sťahovanie a ďalšie.'],
          ['Hodnotenia a ceny', 'Zákazník porovná majstrov podľa skúseností iných a cien.'],
          ['Registrácia profesionálov', 'Majstri si sami vytvoria profil a ponúkajú služby.'],
          ['Tri jazyky', 'Slovenčina, angličtina a ruština s hreflang pre vyhľadávače.'],
          ['Rýchly a SEO-ready', 'Nuxt so server-side renderingom a štruktúrou pripravenou pre Google.'],
        ],
        results: [['10+', 'kategórií služieb'], ['3', 'jazyky: SK · EN · RU'], ['SSR', 'rýchle načítanie a SEO vďaka Nuxtu']],
      },
      cs: {
        metaTitle: 'Expert SK — případová studie: katalog ověřených řemeslníků | Duo Studio',
        metaDescription: 'Expert SK — trojjazyčná platforma pro vyhledání ověřených řemeslníků na Slovensku: služby, města, hodnocení a registrace pro profesionály. Nuxt, Tailwind CSS.',
        lead: 'Platforma, kde zákazníci na Slovensku najdou ověřeného elektrikáře, instalatéra či úklidovou službu ve svém městě.',
        client: 'Platforma služeb, Slovensko', role: 'Návrh, vývoj, SEO, vícejazyčnost',
        challenge: 'Najít spolehlivého řemeslníka je zdlouhavé: nabídky jsou roztroušené po inzerátech a sociálních sítích, chybí hodnocení a ceny a cizinci na Slovensku narážejí i na jazykovou bariéru.',
        solution: 'Vytvořili jsme katalog služeb s vyhledáváním podle typu práce a města, profily řemeslníků s hodnocením a cenami a přímým kontaktem. Platforma je ve slovenštině, angličtině i ruštině a řemeslníci se mohou sami zaregistrovat.',
        features: [
          ['Vyhledávání', 'Podle služby a města — od hodinového manžela po automechanika.'],
          ['10+ kategorií', 'Elektrikář, instalatér, malíř, obkladač, montáž nábytku, úklid, stěhování a další.'],
          ['Hodnocení a ceny', 'Zákazník porovná řemeslníky podle zkušeností ostatních a cen.'],
          ['Registrace profesionálů', 'Řemeslníci si sami vytvoří profil a nabízejí služby.'],
          ['Tři jazyky', 'Slovenština, angličtina a ruština s hreflang pro vyhledávače.'],
          ['Rychlý a SEO-ready', 'Nuxt se server-side renderingem a strukturou připravenou pro Google.'],
        ],
        results: [['10+', 'kategorií služeb'], ['3', 'jazyky: SK · EN · RU'], ['SSR', 'rychlé načítání a SEO díky Nuxtu']],
      },
      uk: {
        metaTitle: 'Expert SK — кейс: каталог перевірених майстрів | Duo Studio',
        metaDescription: 'Expert SK — тримовна платформа для пошуку перевірених майстрів у Словаччині: послуги, міста, відгуки та реєстрація для професіоналів. Nuxt, Tailwind CSS.',
        lead: 'Платформа, де клієнти в Словаччині знаходять перевіреного електрика, сантехніка чи клінінгову службу у своєму місті.',
        client: 'Платформа послуг, Словаччина', role: 'Проєктування, розробка, SEO, багатомовність',
        challenge: 'Знайти надійного майстра довго: пропозиції розкидані по оголошеннях і соцмережах, бракує відгуків і цін, а іноземці в Словаччині ще й стикаються з мовним бар’єром.',
        solution: 'Ми створили каталог послуг із пошуком за видом робіт і містом, профілі майстрів з відгуками й цінами та прямим контактом. Платформа працює словацькою, англійською та російською, а майстри можуть зареєструватися самостійно.',
        features: [
          ['Пошук', 'За послугою та містом — від майстра на годину до автомеханіка.'],
          ['10+ категорій', 'Електрик, сантехнік, маляр, плиточник, збирання меблів, прибирання, переїзди та інше.'],
          ['Відгуки та ціни', 'Клієнт порівнює майстрів за досвідом інших людей і цінами.'],
          ['Реєстрація професіоналів', 'Майстри самі створюють профіль і пропонують послуги.'],
          ['Три мови', 'Словацька, англійська та російська з hreflang для пошукових систем.'],
          ['Швидкий і готовий до SEO', 'Nuxt із серверним рендерингом і структурою, підготовленою для Google.'],
        ],
        results: [['10+', 'категорій послуг'], ['3', 'мови: SK · EN · RU'], ['SSR', 'швидке завантаження та SEO завдяки Nuxt']],
      },
    },
  },
]

// English texts (international visitors)
const en: Record<string, CaseText> = {
  'e-drivebook': {
    metaTitle: 'e-Drivebook case study: SaaS for driving schools | Duo Studio',
    metaDescription: 'How we built e-Drivebook from scratch — driving school software with 24/7 online lesson booking, instructor schedules and student records. FastAPI, PostgreSQL, Nuxt 3.',
    lead: 'Our own SaaS for driving schools — from the first requirements to production used every day by paying driving schools.',
    client: 'Driving schools in Slovakia', role: 'Design, backend, frontend, deployment',
    challenge: 'Driving schools planned lessons over the phone, in paper notebooks and spreadsheets. Students did not know when a slot was free, instructors lost time arranging lessons and records of lessons and vehicles were scattered across many places.',
    solution: 'We designed and built a web application from scratch that brings bookings, schedules, students, instructors and cars into one place. Students book lessons online 24/7 from a computer or phone, and the driving school sees everything in the admin panel.',
    features: [
      ['24/7 online booking', 'Students pick a free lesson slot themselves — no phone calls.'],
      ['Instructor schedules', 'Automatic lesson planning based on instructor and vehicle availability.'],
      ['Student & training records', 'Records of lessons, their duration and each student’s progress.'],
      ['Vehicle fleet', 'An overview of cars and their maintenance in one place.'],
      ['Exam tests', 'Students prepare for the theory exam right in the app.'],
      ['Secure login', 'OAuth2 / JWT with separate access for administrators, instructors and students.'],
    ],
    results: [['3', 'paying driving schools use the system daily'], ['24/7', 'online lesson booking for students'], ['1', 'developer from database to deployment'], ['CI/CD', 'automated tests and deployments with GitHub Actions']],
  },
  expertsk: {
    metaTitle: 'Expert SK case study: directory of verified tradespeople | Duo Studio',
    metaDescription: 'Expert SK — a trilingual platform for finding verified tradespeople in Slovakia: services, cities, reviews and sign-up for professionals. Nuxt, Tailwind CSS.',
    lead: 'A platform where customers in Slovakia find a verified electrician, plumber or cleaning service in their city.',
    client: 'Services platform, Slovakia', role: 'Design, development, SEO, localization',
    challenge: 'Finding a reliable tradesperson takes time: offers are scattered across classifieds and social media, reviews and prices are missing, and foreigners in Slovakia also face a language barrier.',
    solution: 'We built a services directory with search by type of work and city, tradesperson profiles with reviews and prices, and direct contact. The platform is available in Slovak, English and Russian, and professionals can sign up on their own.',
    features: [
      ['Search', 'By service and city — from handyman to car mechanic.'],
      ['10+ categories', 'Electrician, plumber, painter, tiler, furniture assembly, cleaning, moving and more.'],
      ['Reviews & prices', 'Customers compare tradespeople by other people’s experience and price.'],
      ['Sign-up for professionals', 'Tradespeople create their own profile and offer their services.'],
      ['Three languages', 'Slovak, English and Russian with hreflang for search engines.'],
      ['Fast and SEO-ready', 'Nuxt with server-side rendering and a structure built for Google.'],
    ],
    results: [['10+', 'service categories'], ['3', 'languages: SK · EN · RU'], ['SSR', 'fast loading and SEO thanks to Nuxt']],
  },
}

export const cases: CaseStudy[] = base.map((c) => ({ ...c, text: { ...c.text, en: en[c.id]! } }))
