// English. Words in *asterisks* in the hero title are highlighted with a gradient.
import type sk from './sk'

const en: typeof sk = {
  htmlLang: 'en',
  locale: 'en_US',
  label: 'English',
  short: 'EN',

  meta: {
    title: 'Duo Studio — AI automation, web & app development | Bratislava, Slovakia',
    description:
      'AI automation, website, app and mini game development and AI integration for businesses. A development team from Bratislava and Nitra, Slovakia, working with clients across Europe — Prague, Kyiv, Uzhhorod and beyond.',
    ogTitle: 'Duo Studio — AI automation, websites and apps | Bratislava · Nitra',
  },

  geoHint: { text: 'Prefer to read in English?', action: 'Switch to English', close: 'Close' },

  skip: 'Skip to content',
  nav: { about: 'About', services: 'Services', ai: 'AI automation', work: 'Portfolio', lab: 'Lab', process: 'Process', faq: 'FAQ', contact: 'Contact', cta: 'Get in touch', menu: 'Menu' },

  hero: {
    badge: 'Taking on new projects',
    title: 'We automate business with *AI* and code.',
    subtitle:
      'A development team from Bratislava and Nitra, Slovakia. We build AI automations, websites, apps and mini games, integrate artificial intelligence into your systems and speed up processes through code automation.',
    ctaPrimary: 'Start a project',
    ctaSecondary: 'See our work',
    stats: [
      { value: 7, suffix: '+', label: 'projects in the portfolio' },
      { value: 4, suffix: '', label: 'languages: EN · SK · CZ · UA' },
      { value: 24, suffix: 'h', label: 'response time' },
    ],
    visual: { url: 'yourcompany.com', chip1: 'SEO 100/100', chip2: 'LCP 0.8 s', chip3: 'AI recommends' },
  },

  marquee: ['AI automation', 'Web development', 'Apps', 'Mini games', 'AI integration', 'Chatbots', 'Code automation', 'Bratislava', 'Nitra', 'Prague', 'Kyiv'],

  about: {
    eyebrow: 'About us',
    title: 'AI, code and design in one team.',
    text:
      'Duo Studio is a development team from Bratislava and Nitra, Slovakia. We focus on AI automation, websites, web and mobile apps and mini games, integrating artificial intelligence into business systems and optimizing processes through code automation. We work with clients in Slovakia, Czechia, Ukraine and across Europe.',
    profile: 'Open profile',
    people: {
      p1: {
        role: 'Python backend & full-stack developer',
        bio: 'FastAPI, Odoo 18, PostgreSQL and Nuxt 3. Built a warehouse management system in Odoo for an e-commerce company and his own SaaS for driving schools, e-drivebook. At the studio he handles backend, integrations and AI automation.',
      },
      p2: {
        role: 'UI/UX designer',
        bio: 'Designs interfaces and visual identities that look great and are easy to use — from Figma wireframes to finished animations. (Add your own text.)',
      },
    },
  },

  services: {
    eyebrow: 'Services',
    title: 'What we do for you.',
    text: 'AI, websites, apps and games — from the first idea to launch and beyond.',
    items: [
      { icon: 'spark', title: 'AI automation', text: 'We automate repetitive work: handling enquiries, documents, orders and reports — your processes run on their own, 24/7.' },
      { icon: 'web', title: 'Website development', text: 'Fast business websites and e-shops with SEO and GEO optimization, so Google and AI assistants recommend you.' },
      { icon: 'code', title: 'Web & mobile apps', text: 'SaaS, internal tools and ERP solutions built on FastAPI, Odoo and Nuxt — with a database, login and API.' },
      { icon: 'game', title: 'Mini games', text: 'Web and mobile mini games, Telegram games and gamification for marketing campaigns and loyalty programs.' },
      { icon: 'flow', title: 'Optimization through code automation', text: 'CI/CD, automated tests, refactoring and scripts that speed up development and cut bugs and costs.' },
      { icon: 'bot', title: 'AI integration', text: 'We connect ChatGPT, Claude and other models to your website, CRM or e-shop — chatbots, assistants and smart search.' },
    ],
  },

  ai: {
    eyebrow: 'AI automation',
    title: 'Leave the routine to AI and code.',
    text: 'We connect your tools, deploy AI assistants and automate repetitive tasks — so you can focus on what makes your business stand out.',
    flow: ['New enquiry / e-mail', 'AI reads and evaluates it', 'Saved to CRM / spreadsheet', 'Telegram notification'],
    flowLabel: 'Example automation',
    items: [
      { icon: 'bot', title: 'AI chatbots & assistants', text: 'A chatbot for your website or Telegram that answers customers 24/7 based on your own documents.' },
      { icon: 'flow', title: 'Process automation', text: 'Workflows in n8n, Make or custom Python — orders, invoices and reports without manual work.' },
      { icon: 'doc', title: 'Document processing', text: 'AI extracts data from invoices, contracts and e-mails and stores it exactly where it belongs.' },
      { icon: 'plug', title: 'Integrations & API', text: 'Connecting your website, e-shop, CRM, accounting and other systems through APIs.' },
      { icon: 'chart', title: 'Reports & dashboards', text: 'Automatic sales and traffic overviews you no longer have to put together by hand.' },
      { icon: 'code', title: 'Custom tools', text: 'Scripts and small apps tailored to your process — from Python to a web interface.' },
    ],
    benefits: [
      { value: '24/7', label: 'AI answers at night and on weekends' },
      { value: 'API', label: 'connected systems instead of copy-paste' },
      { value: '1 click', label: 'reports and documents without manual work' },
    ],
    cta: 'Automate my work',
  },

  work: {
    eyebrow: 'Portfolio',
    title: 'Selected projects.',
    text: 'Real websites and apps we have built.',
    filters: { all: 'All', web: 'Websites', app: 'Apps', design: 'Design' },
    live: 'Website',
    code: 'GitHub',
    demo: 'Concept',
    proto: { open: 'Open prototype', hint: 'Clickable prototype — try clicking around', close: 'Close' },
    projects: {
      'e-drivebook': { desc: 'My SaaS for driving schools: 24/7 online lesson booking, instructor schedules, vehicles, student records and exam tests. In production — used daily by 3 paying driving schools.' },
      expertsk: { desc: 'A directory of verified tradespeople in Slovakia: electricians, plumbers, cleaning and more — search by city, reviews, prices and sign-up for professionals.' },
      brtc: { desc: 'Corporate website of a technical company with a catalogue of compressor solutions for industry.' },
      onyx: { desc: 'Presentation of new office space in Zlaté Moravce with a map and contact details.' },
      'hodinovy-manzel': { desc: 'Landing page for a handyman in Nitra — services room by room, pricing, references and a form without a backend.' },
      amstars: { desc: 'Bachelor thesis: a platform for amateur football — teams, match challenges, ELO ratings and tournaments.' },
      'travel-planner': { desc: 'REST API for planning trips around artworks, validated against the live Art Institute of Chicago API.' },
      'nordic-living': { desc: 'Scandinavian furniture e-shop concept: catalogue, product page with colour selection, cart and UI kit.' },
      'slnecne-byty': { desc: 'Mobile app for a residential development: apartment selection, gallery, floor plan and viewing booking.' },
      fitflow: { desc: 'Fitness app with activity rings, a workout timer and dark mode.' },
    },
  },

  lab: {
    eyebrow: 'Lab · Concepts',
    title: 'What we are capable of.',
    text: 'Website concepts for fictional brands in completely different styles. Click around — everything is interactive.',
    open: 'Open concept',
    badge: 'Concept — fictional brand',
    back: 'Back to Duo Studio',
    next: 'Next concept',
    cta: 'I want a site like this',
    items: {
      noir: { type: 'Restaurant · fine dining', desc: 'A dark, elegant site with drawn animations, a menu with cursor preview and table booking.' },
      pulse: { type: 'SaaS · AI analytics', desc: 'A light startup site with a live dashboard, AI chat and a pricing toggle.' },
      kinetic: { type: 'E-shop · streetwear', desc: 'A brutalist e-shop with a working cart, size selection and bold typography.' },
      verde: { type: 'Real estate · eco living', desc: 'A natural-toned site for a residential development with parallax and an interactive apartment picker.' },
    },
  },

  city: {
    eyebrow: 'Where we work',
    services: 'What we will do for you',
    why: 'Why us',
    projects: 'Selected projects',
    faq: 'Frequently asked questions',
    cta: 'Get in touch',
    inPerson: 'In-person meeting',
    remote: 'Remote collaboration',
    other: 'We also work in other cities',
    footerTitle: 'Where we work',
  },
  caseStudy: {
    label: 'Case study',
    back: 'Back to portfolio',
    client: 'Client',
    role: 'Our role',
    year: 'Year',
    challenge: 'Challenge',
    solution: 'Solution',
    features: 'What we built',
    results: 'Results',
    stack: 'Technologies',
    visit: 'Visit website',
    next: 'Next case study',
    ctaTitle: 'Want a similar project?',
    ctaText: 'Tell us a few words about your idea — we will get back to you within 24 hours.',
    cta: 'Get in touch',
  },

  process: {
    eyebrow: 'Process',
    title: 'How we work together.',
    steps: [
      { title: 'Consultation', text: 'We learn your goals and the processes that can be simplified, then send a fixed-price quote.' },
      { title: 'Design', text: 'We prepare the structure, a Figma design or an automation diagram.' },
      { title: 'Development', text: 'We build the website, app or workflow with a focus on speed and reliability.' },
      { title: 'Launch & growth', text: 'We launch, set up analytics and help you keep growing.' },
    ],
  },

  faq: {
    eyebrow: 'FAQ',
    title: 'Frequently asked questions.',
    items: [
      { q: 'How much does a website or app cost?', a: 'It depends on the scope — the number of pages, features and integrations. After a free consultation we send a fixed-price quote with no hidden fees.' },
      { q: 'What can you automate with AI?', a: 'Most often: answering customer questions (chatbots), sorting e-mails and enquiries, extracting data from invoices and documents, connecting systems via APIs and automatic reports. In the consultation we find the tasks that take up most of your time.' },
      { q: 'Where are you based?', a: 'We are based in Bratislava and Nitra, Slovakia, where we can also meet in person. We work remotely with clients in Prague, Kyiv, Uzhhorod and across Europe.' },
      { q: 'Do you also make mini games?', a: 'Yes. We create web and mobile mini games, Telegram games and game elements for marketing campaigns — contests, prize wheels or loyalty challenges.' },
      { q: 'What is optimization through code automation?', a: 'We set up CI/CD, automated tests and deployments, refactor slow parts and write scripts for routine tasks. Development gets faster and there are fewer bugs in production.' },
      { q: 'How long does it take to build a website?', a: 'A landing page or company website usually takes 2–3 weeks, a larger website or app 4–8 weeks. A simple automation can be live within a few days.' },
      { q: 'What is GEO optimization?', a: 'GEO (Generative Engine Optimization) means optimizing a website for AI search and assistants such as ChatGPT, Perplexity or Google AI Overviews. With structured data, clear content and an llms.txt file we increase the chance that AI recommends you.' },
      { q: 'Can you take care of the domain and hosting?', a: 'Yes, we help you choose and set up the domain, hosting, SSL certificate and business e-mail.' },
    ],
  },

  contact: {
    eyebrow: 'Contact',
    title: 'Have an idea? Let’s make it happen.',
    text: 'Tell us a few words about your project or the process you want to automate. We will reply within 24 hours.',
    direct: 'Or contact us directly',
    form: {
      name: 'Name',
      email: 'E-mail',
      type: 'What do you need?',
      types: ['AI automation', 'Website', 'App', 'Mini game', 'AI integration', 'Other'],
      message: 'Message',
      send: 'Send message',
      sent: 'Thank you! We will be in touch soon.',
      error: 'Something went wrong. Please send us an e-mail.',
      subject: 'New enquiry from the website',
      consent: 'I agree to the processing of my personal data according to the',
      consentLink: 'privacy policy',
      sending: 'Sending…',
    },
  },

  footer: {
    tagline: 'AI automation, websites, apps and mini games · Bratislava · Nitra · Prague · Kyiv · Uzhhorod',
    rights: 'All rights reserved.',
    privacy: 'Privacy policy',
    top: 'Top',
  },

  personal: {
    back: 'Back to the studio',
    hello: 'Hi, I am',
    about: 'About me',
    stack: 'Technologies',
    projects: 'Projects',
    journey: 'Experience',
    education: 'Education',
    languages: 'Languages',
    contact: 'Write to me',
    contactText: 'Have a project or an automation idea? Get in touch — I will reply within 24 hours.',
    available: 'Available for new projects',
    also: 'See also the profile of',
    copy: 'Copy e-mail',
    copied: 'Copied ✓',
    sayHi: 'Let’s say hello',
    sticker: 'UI/UX • BRANDING • WEB • DESIGN • ',
    cv: {
      open: 'Résumé (CV)',
      title: 'Résumé',
      download: 'Download PDF',
      fullProfile: 'Full profile',
      summary: 'Summary',
      skills: 'Skills',
      experience: 'Work experience',
      education: 'Education',
      languages: 'Languages',
      projects: 'Selected projects',
      info: 'Information',
      contact: 'Contact',
      web: 'Website',
      metaTitle: 'Résumé',
    },
    people: {
      p1: {
        metaTitle: 'Bc. Sebastian Kychatyi — Python backend / full-stack developer | Slovakia',
        metaDescription: 'Python backend and full-stack developer: FastAPI, Odoo 18, PostgreSQL, Vue.js / Nuxt 3. Warehouse management system in Odoo 18, own SaaS for driving schools e-drivebook, websites and AI automation.',
        headline: 'I build systems that real businesses run on.',
        intro: 'Python backend and full-stack developer focused on business systems — ERP, e-commerce and SaaS. I own features end to end, from the database schema to the UI and deployment.',
        bio: [
          'I built a warehouse management system in Odoo 18 for an e-commerce company and created e-drivebook, a SaaS for driving schools, from scratch — it is in production and used daily by 3 paying driving schools.',
          'I am a Master’s student in Applied Informatics at Constantine the Philosopher University in Nitra. At Duo Studio I handle backend, integrations and AI automation.',
        ],
        facts: [
          { k: 'Location', v: 'Nitra, Slovakia' },
          { k: 'Work', v: 'Hybrid in Bratislava or remote' },
          { k: 'Focus', v: 'Backend · Full-stack · ERP' },
        ],
        timeline: [
          { year: '04/2025 – present', title: 'Full-Stack Developer · e-drivebook (own product)', text: 'SaaS for driving schools from requirements to deployment, used daily by 3 paying driving schools. FastAPI, PostgreSQL (SQLAlchemy, Alembic), OAuth2/JWT: student records, automated lesson scheduling, lesson tracking and fleet maintenance. Nuxt 3 dashboards, Docker Compose, Caddy, CI/CD with GitHub Actions.' },
          { year: '04/2026 – 10/2026', title: 'Odoo Developer · Adelle Davis s.r.o.', text: 'Bratislava, hybrid. Custom warehouse management system in Odoo 18 (Python, OWL): bin locations, receiving, picking and packing with barcode scanning. Courier shipments and labels via carrier APIs (SPS, Packeta, GLS), WooCommerce ↔ Odoo connector, customer support inside Odoo and a FastAPI microservice for automatic box selection.' },
          { year: '10/2025 – 07/2026', title: 'Backend Developer · SHARKRISE s.r.o.', text: 'Remote, contract. Difference Mania mobile game (Laravel, MySQL): refactored core game logic before launch and extended the backend with new content.' },
        ],
        education: [
          { year: '2026 – 2028', title: 'Master’s degree — Applied Informatics', text: 'Constantine the Philosopher University in Nitra (in progress)' },
          { year: '2023 – 2026', title: 'Bachelor’s degree (Bc.) — Applied Informatics', text: 'Constantine the Philosopher University in Nitra · thesis: AmStars' },
        ],
        languages: [
          { k: 'Ukrainian', v: 'native' },
          { k: 'Russian', v: 'C2' },
          { k: 'Slovak', v: 'B2' },
          { k: 'English', v: 'B1' },
        ],
      },
      p2: {
        metaTitle: 'Roman — UI/UX designer | Duo Studio',
        metaDescription: 'Roman, UI/UX designer at Duo Studio: website and app design, branding and Figma prototypes. Portfolio and contact.',
        headline: 'I design interfaces people remember.',
        intro: 'A UI/UX designer who believes good design is the kind you don’t notice — it simply works. (Add your own text.)',
        bio: [
          'A short story about how I got into design and what I love about it will go here. (Add your own text.)',
          'At Duo Studio I take care of visuals, UX and branding. Together with Sebastian, clients get design and code from one place.',
        ],
        facts: [
          { k: 'Location', v: 'Slovakia' },
          { k: 'Focus', v: 'UI/UX · Branding' },
          { k: 'Tools', v: 'Figma · Webflow' },
        ],
        education: [] as { year: string; title: string; text: string }[],
        languages: [] as { k: string; v: string }[],
        timeline: [
          { year: '2026', title: 'Your project', text: 'Add a project you are proud of.' },
          { year: '2025', title: 'Your project', text: 'Add another project or experience.' },
        ],
      },
    },
  },
}

export default en
