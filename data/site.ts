// Language-independent site config.
// Per-language texts live in data/locales/.
import type { PrototypeKind } from './prototypes'

export type Lang = 'sk' | 'cs' | 'uk' | 'en'
export type Category = 'web' | 'app'

export interface Project {
  id: string
  title: string
  author: 'p1' | 'p2'
  category: Category
  year: number
  url?: string // live site
  repo?: string // GitHub
  image?: string // screenshot in public/img/projects/
  colors: [string, string] // mock colors when there is no screenshot
  layout: 1 | 2 | 3 | 4 // 4 = code/API mock
  tags: string[]
  placeholder?: boolean // placeholder, shown with a "demo" badge
  prototype?: PrototypeKind
}

const site = {
  // Main domain (no trailing slash); change with `npm run set-domain`
  domain: 'https://studio.k2drive.com',
  brand: 'Duo Studio',
  email: 'kichatyisebastian@gmail.com', // studio contact (site, form, schema.org)
  phone: '+421 951 508 228',
  telegram: '', // e.g. 'https://t.me/username'

  // Location for geo meta tags and schema.org
  location: {
    city: 'Nitra',
    region: 'SK-NI',
    country: 'SK',
    lat: 48.3069,
    lng: 18.0864,
  },
  // Served countries (ISO) for schema.org areaServed
  areaServed: ['SK', 'CZ', 'UA'],
  // Local SEO cities by priority
  cities: [
    { name: 'Bratislava', country: 'SK' },
    { name: 'Nitra', country: 'SK' },
    { name: 'Prague', country: 'CZ' },
    { name: 'Kyiv', country: 'UA' },
    { name: 'Uzhhorod', country: 'UA' },
  ],

  // Visitor country (IP) → site language
  geoLanguages: { SK: 'sk', CZ: 'cs', UA: 'uk' } as Record<string, string>,
  // Language for all other countries
  fallbackLang: 'en' as const,

  // Contact form endpoint → Telegram + e-mail (keys in .env).
  // Falls back to mailto on static hosting.
  contactApi: '/api/contact',

  // Cookie-less analytics; empty = disabled
  analytics: {
    umami: { src: '', websiteId: '' }, // e.g. src: 'https://cloud.umami.is/script.js'
    plausible: { domain: '', src: 'https://plausible.io/js/script.js' }, // domain: 'studio.k2drive.com'
  },
  // Search Console / Bing verification tokens
  verification: { google: '', bing: '' },

  defaultLang: 'sk' as const,
  languages: ['sk', 'cs', 'uk', 'en'] as const,

  // Team. slug = personal page URL; theme = 'dev' | 'creative'.
  // Texts: locales -> about.people, personal.people
  people: [
    {
      id: 'p1' as const,
      slug: 'sebastian',
      theme: 'dev' as const,
      name: 'Sebastian Kychatyi',
      degree: 'Bc.', // academic title on the résumé
      shortName: 'Sebastian',
      initials: 'SK',
      photo: '', // e.g. '/img/sebastian.jpg' (in public/img/)
      // Personal contact; empty = studio e-mail
      email: 'kichatyisebastian@gmail.com',
      phone: '+421 951 508 228',
      colors: ['#5B4BFF', '#9F8CFF'] as [string, string],
      // Short list (cards, chips)
      skills: ['Python', 'FastAPI', 'Odoo 18', 'PostgreSQL', 'Vue.js / Nuxt 3', 'TypeScript', 'Docker', 'AI automation'],
      // Full stack by group (profile, résumé)
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
        telegram: '',
      },
    },
    {
      id: 'p2' as const,
      slug: 'roman',
      theme: 'dev' as const,
      name: 'Roman Zotsenko',
      degree: 'Bc.',
      shortName: 'Roman',
      initials: 'RZ',
      photo: '',
      email: 'roman.zotsenko.dev@gmail.com',
      phone: '',
      colors: ['#2F5BEA', '#7AA2FF'] as [string, string],
      skills: ['Next.js', 'React', 'FastAPI', 'Python', 'TypeScript', 'PostgreSQL', 'Laravel', 'Docker'],
      skillGroups: [
        { k: 'Frontend', v: ['Next.js 16', 'React 19', 'TypeScript', 'Tailwind CSS', 'Vue 3 / Inertia', 'Material UI'] },
        { k: 'Backend', v: ['Python', 'FastAPI', 'SQLAlchemy', 'Alembic', 'Laravel 12/13', 'Express', 'REST API', 'WebSockets', 'Queues & background jobs', 'Payment integrations', 'OAuth'] },
        { k: 'Data & DevOps', v: ['PostgreSQL', 'MySQL', 'Redis', 'Docker', 'Nginx', 'GitHub Actions (CI/CD)', 'AWS S3', 'Linux', 'Git', 'pytest', 'Pest / PHPUnit'] },
      ],
      terminal: ['whoami', 'Bc. Roman Zotsenko', 'role', 'Full-Stack Engineer', 'stack', 'Next.js · React · FastAPI · Python', 'status', 'open to work ✓'],
      links: {
        github: 'https://github.com/wwtanji',
        linkedin: 'https://www.linkedin.com/in/roman-zotsenko',
        instagram: '',
        telegram: 'https://t.me/r_zotsenko',
      },
    },
  ],

  // Portfolio; descriptions in locales -> work.projects[id]
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
    {
      id: 'classifieds', title: 'Classifieds Platform', author: 'p2', category: 'app', year: 2025,
      colors: ['#2F5BEA', '#BFD0FF'], layout: 1, prototype: 'classifieds',
      tags: ['Next.js 16', 'React 19', 'Laravel', 'PostgreSQL', 'Redis', 'Docker'],
    },
    {
      id: 'restaurant-reservation', title: 'Restaurant Reservation System', author: 'p2', category: 'app', year: 2026,
      repo: 'https://github.com/wwtanji/bp-restaurant-reservation-system',
      colors: ['#0F766E', '#99F6E4'], layout: 4,
      tags: ['FastAPI', 'SQLAlchemy', 'MySQL', 'React 19', 'TypeScript', 'Stripe', 'pytest'],
    },
    {
      id: 'billing', title: 'Subscription Billing', author: 'p2', category: 'app', year: 2026,
      colors: ['#7C3AED', '#DDD6FE'], layout: 1, prototype: 'billing',
      tags: ['Laravel', 'Filament', 'PostgreSQL', 'Redis', 'Crypto payments'],
    },
    {
      id: 'team-crm', title: 'Team CRM', author: 'p2', category: 'app', year: 2025,
      colors: ['#0EA5E9', '#BAE6FD'], layout: 1, prototype: 'crm',
      tags: ['Electron', 'Express', 'MySQL', 'JWT'],
    },
    {
      id: 'leads-workspace', title: 'Leads Workspace', author: 'p2', category: 'app', year: 2026,
      colors: ['#F97316', '#FED7AA'], layout: 1, prototype: 'leads',
      tags: ['Lead enrichment', 'Scoring', 'UI prototype'],
    },
    {
      id: 'orbit-portfolio', title: 'Orbit Portfolio', author: 'p2', category: 'web', year: 2026,
      url: 'https://portfolio-azure-alpha-83.vercel.app', repo: 'https://github.com/wwtanji/portfolio',
      image: '/img/projects/orbit-portfolio.jpg', colors: ['#020617', '#38BDF8'], layout: 1,
      tags: ['JavaScript', 'WebGL', 'GSAP', 'Vite'],
    },
    {
      id: 'calibre-watches', title: 'Calibre Watches', author: 'p2', category: 'web', year: 2026,
      url: 'https://calibre-watches-three.vercel.app', repo: 'https://github.com/wwtanji/calibre-watches',
      image: '/img/projects/calibre-watches.jpg', colors: ['#0A0A0A', '#C9A15A'], layout: 1,
      tags: ['JavaScript', 'SVG', 'GSAP', 'Vite'],
    },
    {
      id: 'clay-gtm', title: 'GTM Platform Homepage', author: 'p2', category: 'web', year: 2025,
      url: 'https://clay-ruddy-eight.vercel.app/', repo: 'https://github.com/wwtanji/clay-project',
      image: '/img/projects/clay-gtm.jpg', colors: ['#111111', '#F3F3F0'], layout: 1,
      tags: ['Vue 3', 'Tailwind CSS', 'UI concept'],
    },
  ] as Project[],
}

export default site
