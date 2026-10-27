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
}

const site = {
  // TODO: замените на реальный домен (без слеша в конце) — нужен для canonical, hreflang и sitemap
  domain: 'https://duostudio.sk',
  brand: 'Duo Studio',
  email: 'hello@duostudio.sk', // TODO
  phone: '+421 900 000 000', // TODO
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

  // Определение языка по стране посетителя (по IP): страна -> язык сайта
  geoLanguages: { SK: 'sk', CZ: 'cs', UA: 'uk' } as Record<string, string>,

  // Если есть Formspree / другой бэкенд для формы — вставьте URL. Пусто — откроется почта (mailto).
  formEndpoint: '',

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
      shortName: 'Sebastian',
      initials: 'SK',
      photo: '', // например '/img/sebastian.jpg' (файл положить в public/img/)
      email: '', // личный e-mail для страницы; пусто — используется общий email выше
      colors: ['#5B4BFF', '#9F8CFF'] as [string, string],
      skills: ['HTML/CSS', 'JavaScript', 'Vue / Nuxt', 'Python', 'FastAPI', 'PostgreSQL', 'Docker', 'SEO', 'AI automation', 'n8n'],
      terminal: ['whoami', 'Sebastian Kychatyi', 'location', 'Nitra, Slovakia', 'stack', 'Nuxt · Python · FastAPI · AI', 'status', 'open to work ✓'],
      links: { github: 'https://github.com/sebastiansKychatyi', linkedin: '', instagram: '' },
    },
    {
      id: 'p2' as const,
      slug: 'roman',
      theme: 'creative' as const,
      name: 'Roman', // TODO: фамилия Романа
      shortName: 'Roman',
      initials: 'R',
      photo: '',
      email: '',
      colors: ['#FF7A59', '#FFB199'] as [string, string],
      skills: ['Figma', 'UI/UX', 'Branding', 'Webflow', 'WordPress', 'Illustrator'],
      terminal: [] as string[],
      links: { github: '', linkedin: '', instagram: '' },
    },
  ],

  // Портфолио. Описание каждого проекта на каждом языке — data/locales/<lang>.ts -> work.projects[id]
  projects: [
    {
      id: 'fscommerce', title: 'F.S. Commerce', author: 'p1', category: 'web', year: 2026,
      url: 'https://fscommerce.tech', repo: 'https://github.com/sebastiansKychatyi/fscommerse',
      image: '/img/projects/fscommerce.jpg', colors: ['#1E4E9A', '#7FC241'], layout: 1,
      tags: ['HTML', 'CSS', 'JavaScript', 'SEO'],
    },
    {
      id: 'brtc', title: 'Bratislava Technical Company', author: 'p1', category: 'web', year: 2026,
      url: 'https://brtc.tech', repo: 'https://github.com/sebastiansKychatyi/brtc',
      image: '/img/projects/brtc.jpg', colors: ['#111827', '#3B82F6'], layout: 1,
      tags: ['HTML', 'CSS', 'JavaScript', 'B2B'],
    },
    {
      id: 'azs', title: 'AZS Engineering', author: 'p1', category: 'web', year: 2026,
      url: 'https://azs-engineering.com', repo: 'https://github.com/sebastiansKychatyi/azs',
      image: '/img/projects/azs.jpg', colors: ['#1F2937', '#D4A35A'], layout: 1,
      tags: ['HTML', 'CSS', 'JavaScript', 'HU'],
    },
    {
      id: 'onyx', title: 'ONYX Business Residence', author: 'p1', category: 'web', year: 2026,
      url: 'https://onyx-br.com', repo: 'https://github.com/sebastiansKychatyi/moravce',
      image: '/img/projects/onyx.jpg', colors: ['#18181B', '#F59E0B'], layout: 3,
      tags: ['HTML', 'CSS', 'Google Maps'],
    },
    {
      id: 'hodinovy-manzel', title: 'Hodinový manžel Nitra', author: 'p1', category: 'web', year: 2026,
      repo: 'https://github.com/sebastiansKychatyi/Landing',
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
    // TODO: проекты друга — замените заглушки на реальные
    {
      id: 'nordic-living', title: 'Nordic Living', author: 'p2', category: 'design', year: 2026,
      colors: ['#64748B', '#E2E8F0'], layout: 2, tags: ['Figma', 'UI Kit', 'Branding'], placeholder: true,
    },
    {
      id: 'slnecne-byty', title: 'Slnečné Byty', author: 'p2', category: 'design', year: 2026,
      colors: ['#EAB308', '#FEF3C7'], layout: 3, tags: ['UI/UX', 'Prototyp', 'Webflow'], placeholder: true,
    },
  ] as Project[],
}

export default site
