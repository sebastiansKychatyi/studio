import site from './data/site'

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
      ],
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
        { rel: 'apple-touch-icon', href: '/apple-touch-icon.png' },
        { rel: 'manifest', href: '/site.webmanifest' },
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Unbounded:wght@500;600;700&display=swap',
        },
      ],
      // Скрываем элементы для анимации появления только если JS включён
      script: [{ innerHTML: "document.documentElement.classList.add('js')", tagPosition: 'head' }],
    },
  },

  i18n: {
    baseUrl: site.domain,
    strategy: 'prefix',
    defaultLocale: site.defaultLang,
    locales: [
      { code: 'sk', language: 'sk-SK', name: 'Slovenčina' },
      { code: 'cs', language: 'cs-CZ', name: 'Čeština' },
      { code: 'uk', language: 'uk-UA', name: 'Українська' },
    ],
    // Язык определяем сами: по стране посетителя (public/index.html + GeoLangHint), см. app/composables/useGeoLang.ts
    detectBrowserLanguage: false,
  },

  nitro: {
    prerender: {
      crawlLinks: true,
      routes: [
        ...site.languages.flatMap((l) => [`/${l}`, ...site.people.map((p) => `/${l}/${p.slug}`)]),
        '/sitemap.xml',
        '/robots.txt',
        '/llms.txt',
        '/site.webmanifest',
      ],
    },
  },
})
