import site from '../../data/site'

// Start URL of the installed app and its shortcuts: /panel?go=… → /<language>/panel…
// Language = the one used last in the panel (cookie set by the panel), else the default.
// The service worker does the same offline (pwa/sw.js).
const GO: Record<string, string> = { quick: '/panel/today?quick=1', task: '/panel?new=task', alarm: '/panel/alarms?new=alarm', expense: '/panel/expenses?new=expense' }

export default defineEventHandler((event) => {
  const saved = getCookie(event, 'panel_lang') ?? ''
  const lang = (site.languages as readonly string[]).includes(saved) ? saved : site.defaultLang
  const target = GO[String(getQuery(event).go ?? '')] ?? '/panel/today'
  // The Android app (android/) marks its start; the page then offers "To system clock"
  const twa = getQuery(event).source === 'twa' ? `${target.includes('?') ? '&' : '?'}source=twa` : ''
  return sendRedirect(event, `/${lang}${target}${twa}`, 302)
})
