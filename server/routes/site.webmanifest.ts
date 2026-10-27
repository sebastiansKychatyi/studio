import site from '../../data/site'

export default defineEventHandler((event) => {
  setHeader(event, 'Content-Type', 'application/manifest+json')
  return {
    name: site.brand,
    short_name: site.brand,
    start_url: `/${site.defaultLang}`,
    display: 'standalone',
    background_color: '#F6F5F1',
    theme_color: '#F6F5F1',
    icons: [
      { src: '/favicon.svg', sizes: 'any', type: 'image/svg+xml' },
      { src: '/apple-touch-icon.png', sizes: '180x180', type: 'image/png' },
    ],
  }
})
