// Общие настройки сайта (не зависят от языка).
// Тексты для каждого языка — в папке data/locales/ (sk.ts, cs.ts, uk.ts).

export type Category = 'web' | 'app' | 'design'

export interface Project {
  id: string
  title: string
  author: 'p1' | 'p2'
  category: Category
  year: number
  url?: string // живой сайт
  repo?: string // GitHub
  image?: string // скриншот в public/img/projects/
  colors: [string, string] // цвета CSS-макета, если нет скриншота
  layout: 1 | 2 | 3 | 4 // 4 = «код/API»-макет
  tags: string[]
  placeholder?: boolean // заглушка — показывается с пометкой «Ukážka»
  prototype?: 'nordic' | 'byty' | 'fitflow' // кликабельный прототип в окне (app/components/Proto*.vue)
}

const site = {
  // TODO: замените на реальный домен (без слеша в конце) — нужен для canonical, hreflang и sitemap
  domain: 'https://duostudio.sk',
  brand: 'Duo Studio',
  email: 'kichatyisebastian@gmail.com', // контакты студии (главная страница, форма, schema.org)
  phone: '+421 951 508 228',
  telegram: '', // например 'https://t.me/username'

  // Где вы находитесь — Geo meta-теги и schema.org
  location: {
    city: 'Nitra',
    region: 'SK-NI',
    country: 'SK',
    lat: 48.3069,
    lng: 18.0864,
  },
  // Страны, для которых вы работаете (ISO) — schema.org areaServed
  areaServed: ['SK', 'CZ', 'UA'],
  // Города для локального SEO — в порядке приоритета (schema.org areaServed, llms.txt, тексты)
  cities: [
    { name: 'Bratislava', country: 'SK' },
    { name: 'Nitra', country: 'SK' },
    { name: 'Prague', country: 'CZ' },
    { name: 'Kyiv', country: 'UA' },
    { name: 'Uzhhorod', country: 'UA' },
  ],

  // Определение языка по стране посетителя (по IP): страна -> язык сайта
  geoLanguages: { SK: 'sk', CZ: 'cs', UA: 'uk' } as Record<string, string>,

  // Форма отправляется на серверный /api/contact → Telegram и e-mail (Web3Forms). Ключи — в .env (см. .env.example).
  // Если сервер не настроен (чисто статический хостинг), форма сама откроет почтовую программу.
  contactApi: '/api/contact',

  // Аналитика без cookies — заполните одну (пусто = выключено)
  analytics: {
    umami: { src: '', websiteId: '' }, // например src: 'https://cloud.umami.is/script.js'
    plausible: { domain: '', src: 'https://plausible.io/js/script.js' }, // domain: 'duostudio.sk'
  },
  // Подтверждение владения сайтом: Google Search Console («HTML-тег» → content) и Bing Webmaster Tools
  verification: { google: '', bing: '' },

  defaultLang: 'sk' as const,
  languages: ['sk', 'cs', 'uk'] as const,

  // Команда. slug — адрес личной страницы (/sk/sebastian). theme — дизайн личной страницы: 'dev' | 'creative'.
  // Тексты (роль, биография, личная страница) — в data/locales/<lang>.ts -> about.people и personal.people
  people: [
    {
      id: 'p1' as const,
      slug: 'sebastian',
      theme: 'dev' as const,
      name: 'Sebastian Kychatyi',
      degree: 'Bc.', // титул в резюме
      shortName: 'Sebastian',
      initials: 'SK',
      photo: '', // например '/img/sebastian.jpg' (файл положить в public/img/)
      // Контакты из резюме — видны на личной странице и в CV. Пусто — используется общий email студии
      email: 'kichatyisebastian@gmail.com',
      phone: '+421 951 508 228',
      colors: ['#5B4BFF', '#9F8CFF'] as [string, string],
      // Короткий список (карточка на главной, чипы)
      skills: ['Python', 'FastAPI', 'Odoo 18', 'PostgreSQL', 'Vue.js / Nuxt 3', 'TypeScript', 'Docker', 'AI automation'],
      // Полный стек по группам (личная страница и резюме)
      skillGroups: [
        { k: 'Backend', v: ['Python', 'FastAPI', 'Odoo 18 (ERP, ORM, OWL)', 'SQLAlchemy', 'Alembic', 'REST API', 'API integrations', 'OAuth2 / JWT', 'Laravel (PHP)'] },
        { k: 'Frontend', v: ['Vue.js', 'Nuxt 3', 'TypeScript', 'JavaScript', 'Pinia', 'HTML / CSS'] },
        { k: 'Data & DevOps', v: ['PostgreSQL', 'MySQL', 'Docker / Compose', 'Linux (Ubuntu)', 'Caddy', 'GitHub Actions (CI/CD)', 'Git', 'pytest'] },
      ],
      terminal: ['whoami', 'Bc. Sebastian Kychatyi', 'role', 'Python Backend / Full-Stack', 'stack', 'FastAPI · Odoo 18 · PostgreSQL · Nuxt 3', 'status', 'open to work ✓'],
      links: {
        github: 'https://github.com/sebastiansKychatyi',
        linkedin: 'https://www.linkedin.com/in/sebastian-kychatyi-16aa7a272/',
        instagram: '',
      },
    },
    {
      id: 'p2' as const,
      slug: 'roman',
      theme: 'creative' as const,
      name: 'Roman', // TODO: фамилия Романа
      degree: '',
      shortName: 'Roman',
      initials: 'R',
      photo: '',
      email: '',
      phone: '',
      colors: ['#FF7A59', '#FFB199'] as [string, string],
      skills: ['Figma', 'UI/UX', 'Branding', 'Webflow', 'WordPress', 'Illustrator'],
      skillGroups: [] as { k: string; v: string[] }[],
      terminal: [] as string[],
      links: { github: '', linkedin: '', instagram: '' },
    },
  ],

  // Портфолио. Описание каждого проекта на каждом языке — data/locales/<lang>.ts -> work.projects[id]
  projects: [
    {
      id: 'e-drivebook', title: 'e-Drivebook', author: 'p1', category: 'app', year: 2025,
      url: 'https://e-drivebook.com', image: '/img/projects/e-drivebook.jpg',
      colors: ['#2563EB', '#BFDBFE'], layout: 1,
      tags: ['FastAPI', 'PostgreSQL', 'OAuth2 / JWT', 'Nuxt 3', 'Pinia', 'Docker', 'GitHub Actions'],
    },
    {
      id: 'expertsk', title: 'Expert SK', author: 'p1', category: 'app', year: 2026,
      url: 'https://expertsk.k2drive.com/', image: '/img/projects/expertsk.jpg',
      colors: ['#1D4ED8', '#BFDBFE'], layout: 1,
      tags: ['Nuxt', 'Tailwind CSS', 'i18n SK · EN · RU', 'Marketplace'],
    },
    {
      id: 'brtc', title: 'Bratislava Technical Company', author: 'p1', category: 'web', year: 2026,
      url: 'https://brtc.tech', repo: 'https://github.com/sebastiansKychatyi/brtc',
      image: '/img/projects/brtc.jpg', colors: ['#111827', '#3B82F6'], layout: 1,
      tags: ['HTML', 'CSS', 'JavaScript', 'B2B'],
    },
    {
      id: 'onyx', title: 'ONYX Business Residence', author: 'p1', category: 'web', year: 2026,
      url: 'https://onyx-br.com', repo: 'https://github.com/sebastiansKychatyi/moravce',
      image: '/img/projects/onyx.jpg', colors: ['#18181B', '#F59E0B'], layout: 3,
      tags: ['HTML', 'CSS', 'Google Maps'],
    },
    {
      id: 'hodinovy-manzel', title: 'Hodinový manžel Nitra', author: 'p1', category: 'web', year: 2026,
      url: 'https://hodinovy-manzel.k2drive.com/', repo: 'https://github.com/sebastiansKychatyi/Landing',
      image: '/img/projects/hodinovy-manzel.jpg', colors: ['#1E3A5F', '#2563EB'], layout: 1,
      tags: ['Landing page', 'Local SEO', 'Web3Forms'],
    },
    {
      id: 'amstars', title: 'AmStars', author: 'p1', category: 'app', year: 2026,
      repo: 'https://github.com/sebastiansKychatyi/ukf-bp-amstar',
      colors: ['#16A34A', '#BBF7D0'], layout: 4,
      tags: ['FastAPI', 'Nuxt 3', 'PostgreSQL', 'Redis', 'Docker'],
    },
    {
      id: 'travel-planner', title: 'Travel Planner API', author: 'p1', category: 'app', year: 2026,
      repo: 'https://github.com/sebastiansKychatyi/travel-planner-api',
      colors: ['#0EA5E9', '#BAE6FD'], layout: 4,
      tags: ['FastAPI', 'SQLAlchemy', 'Pydantic', 'httpx'],
    },
    // Дизайн-концепты Романа с кликабельными прототипами (окно по клику). TODO: замените на реальные работы
    {
      id: 'nordic-living', title: 'Nordic Living', author: 'p2', category: 'design', year: 2026,
      colors: ['#64748B', '#E2E8F0'], layout: 2, tags: ['Figma', 'UI Kit', 'E-shop'], placeholder: true, prototype: 'nordic',
    },
    {
      id: 'slnecne-byty', title: 'Slnečné Byty', author: 'p2', category: 'design', year: 2026,
      colors: ['#EAB308', '#FEF3C7'], layout: 3, tags: ['Mobile app', 'UX', 'Prototyp'], placeholder: true, prototype: 'byty',
    },
    {
      id: 'fitflow', title: 'FitFlow', author: 'p2', category: 'design', year: 2026,
      colors: ['#FF5A36', '#FFD3C7'], layout: 3, tags: ['Mobile app', 'Dark mode', 'Motion'], placeholder: true, prototype: 'fitflow',
    },
  ] as Project[],
}

export default site
