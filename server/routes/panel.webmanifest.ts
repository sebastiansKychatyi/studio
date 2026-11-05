import site from '../../data/site'
import sk from '../../data/locales/sk'
import cs from '../../data/locales/cs'
import uk from '../../data/locales/uk'
import en from '../../data/locales/en'

// Installable team panel (PWA), linked from panel pages only; the public site keeps /site.webmanifest.
// One app for all languages: start_url /panel opens the language used last (server/routes/panel.ts).
const all: Record<string, typeof sk> = { sk, cs, uk, en }

export default defineEventHandler((event) => {
  const asked = String(getQuery(event).lang ?? '')
  const lang = (site.languages as readonly string[]).includes(asked) ? asked : site.defaultLang
  const a = all[lang]!.panel.app
  const png = (src: string, size: number, purpose = 'any') => ({ src, sizes: `${size}x${size}`, type: 'image/png', purpose })
  setHeader(event, 'Content-Type', 'application/manifest+json')
  return {
    id: '/panel',
    name: a.name,
    short_name: site.brand,
    description: a.description,
    lang,
    start_url: '/panel?source=pwa',
    scope: '/',
    display: 'standalone',
    display_override: ['standalone', 'minimal-ui'],
    orientation: 'portrait',
    background_color: '#F6F5F1',
    theme_color: '#F6F5F1',
    categories: ['productivity', 'utilities'],
    icons: [
      png('/pwa/icon-192.png', 192),
      png('/pwa/icon-512.png', 512),
      png('/pwa/maskable-512.png', 512, 'maskable'),
      { src: '/favicon.svg', sizes: 'any', type: 'image/svg+xml' },
    ],
    shortcuts: [
      { name: a.quick, url: '/panel?go=quick', icons: [png('/pwa/shortcut-task.png', 96)] },
      { name: a.newTask, url: '/panel?go=task', icons: [png('/pwa/shortcut-task.png', 96)] },
      { name: a.newAlarm, url: '/panel?go=alarm', icons: [png('/pwa/shortcut-alarm.png', 96)] },
      { name: a.newExpense, url: '/panel?go=expense', icons: [png('/pwa/shortcut-expense.png', 96)] },
    ],
    // Richer install dialog on Android (regenerate: node scripts/pwa-assets.mjs --screens …)
    screenshots: [
      { src: '/pwa/screen-tasks.png', sizes: '1080x1920', type: 'image/png', form_factor: 'narrow', label: a.screenTasks },
      { src: '/pwa/screen-calendar.png', sizes: '1080x1920', type: 'image/png', form_factor: 'narrow', label: a.screenCalendar },
      { src: '/pwa/screen-wide.png', sizes: '1920x1080', type: 'image/png', form_factor: 'wide', label: a.screenTasks },
    ],
  }
})
