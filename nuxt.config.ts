import site from './data/site'
import { concepts } from './data/concepts'
import { cities } from './data/cities'
import { cases } from './data/cases'

// Verification meta tags and cookie-less analytics (configured in data/site.ts)
const verificationMeta: { name: string; content: string }[] = []
if (site.verification.google) verificationMeta.push({ name: 'google-site-verification', content: site.verification.google })
if (site.verification.bing) verificationMeta.push({ name: 'msvalidate.01', content: site.verification.bing })
const analyticsScripts: Record<string, string | boolean>[] = []
if (site.analytics.umami.src && site.analytics.umami.websiteId)
  analyticsScripts.push({ src: site.analytics.umami.src, defer: true, 'data-website-id': site.analytics.umami.websiteId })
if (site.analytics.plausible.domain)
  analyticsScripts.push({ src: site.analytics.plausible.src, defer: true, 'data-domain': site.analytics.plausible.domain })

export default defineNuxtConfig({
  compatibilityDate: '2026-10-01',
  devtools: { enabled: true },
  modules: ['@nuxtjs/i18n'],
  css: ['~/assets/css/main.css'],

  app: {
    head: {
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'theme-color', content: '#F6F5F1' },
        { name: 'robots', content: 'index, follow, max-image-preview:large, max-snippet:-1' },
        ...verificationMeta,
      ],
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
        { rel: 'apple-touch-icon', href: '/apple-touch-icon.png' },
        { rel: 'manifest', href: '/site.webmanifest' },
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Unbounded:wght@500;600;700&family=Orbitron:wght@400;500;600;700&family=Roboto:wght@400;500;600;700&display=swap',
        },
      ],
      // Hide reveal elements only when JS is on
      script: [{ innerHTML: "document.documentElement.classList.add('js')", tagPosition: 'head' }, ...analyticsScripts],
    },
  },

  // Server-only form secrets (from .env)
  runtimeConfig: {
    telegramBotToken: '',
    telegramChatId: '',
    web3formsKey: '',
    // FastAPI backend of the team panel (backend/)
    teamApiUrl: 'http://127.0.0.1:8000',
  },

  // Private team panel: client-only, never indexed
  routeRules: Object.fromEntries(
    site.languages.flatMap((l) => [
      [`/${l}/panel`, { ssr: false, headers: { 'x-robots-tag': 'noindex, nofollow' } }],
      [`/${l}/panel/**`, { ssr: false, headers: { 'x-robots-tag': 'noindex, nofollow' } }],
      [`/${l}/login`, { headers: { 'x-robots-tag': 'noindex, nofollow' } }],
    ])
  ),

  i18n: {
    baseUrl: site.domain,
    strategy: 'prefix',
    defaultLocale: site.defaultLang,
    locales: [
      { code: 'sk', language: 'sk-SK', name: 'Slovenčina' },
      { code: 'cs', language: 'cs-CZ', name: 'Čeština' },
      { code: 'uk', language: 'uk-UA', name: 'Українська' },
      { code: 'en', language: 'en', name: 'English' },
    ],
    // Language detection is custom (country based), see useGeoLang.ts
    detectBrowserLanguage: false,
  },

  nitro: {
    prerender: {
      crawlLinks: true,
      routes: [
        ...site.languages.flatMap((l) => [
          `/${l}`,
          ...site.people.flatMap((p) => [`/${l}/${p.slug}`, `/${l}/${p.slug}/cv`]),
          ...concepts.map((c) => `/${l}/lab/${c.id}`),
          ...cities.map((c) => `/${l}/${c.slug}`),
          ...cases.map((c) => `/${l}/case/${c.id}`),
          `/${l}/privacy`,
        ]),
        '/sitemap.xml',
        '/robots.txt',
        '/llms.txt',
        '/site.webmanifest',
      ],
    },
  },
})
