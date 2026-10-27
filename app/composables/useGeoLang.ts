import site from '~~/data/site'

const CHOICE_COOKIE = 'lang' // язык, который посетитель выбрал сам
const CACHE_KEY = 'geo_country'

// Страна посетителя по IP (api.country.is — бесплатный, без ключа). Кэшируется на сессию.
export async function getVisitorCountry(): Promise<string | null> {
  if (import.meta.server) return null
  try {
    const cached = sessionStorage.getItem(CACHE_KEY)
    if (cached) return cached || null
  } catch {}
  try {
    const ctrl = new AbortController()
    const timer = setTimeout(() => ctrl.abort(), 2500)
    const res = await fetch('https://api.country.is/', { signal: ctrl.signal })
    clearTimeout(timer)
    const { country } = (await res.json()) as { country?: string }
    try { sessionStorage.setItem(CACHE_KEY, country || '') } catch {}
    return country || null
  } catch {
    return null
  }
}

export function langForCountry(country: string | null) {
  return (country && site.geoLanguages[country.toUpperCase()]) || null
}

export function useLangChoice() {
  const choice = useCookie<string | null>(CHOICE_COOKIE, { maxAge: 60 * 60 * 24 * 365, sameSite: 'lax', path: '/' })
  return {
    choice,
    remember: (lang: string) => { choice.value = lang },
  }
}
