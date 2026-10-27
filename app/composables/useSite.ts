import site from '~~/data/site'
import sk from '~~/data/locales/sk'
import cs from '~~/data/locales/cs'
import uk from '~~/data/locales/uk'

export type SiteContent = typeof sk
type ProjectId = keyof SiteContent['work']['projects']

const all: Record<string, SiteContent> = { sk, cs, uk }

// Тексты текущего языка + общие настройки
export function useSite() {
  const { locale } = useI18n()
  const t = computed(() => all[locale.value] ?? all[site.defaultLang]!)
  const people = computed(() =>
    site.people.map((p) => ({ ...p, ...t.value.about.people[p.id], page: t.value.personal.people[p.id] }))
  )
  const projects = computed(() =>
    site.projects.map((p) => ({
      ...p,
      ...t.value.work.projects[p.id as ProjectId],
      authorPerson: site.people.find((x) => x.id === p.author)!,
    }))
  )
  return { t, cfg: site, all, people, projects }
}

export type PersonView = ReturnType<typeof useSite>['people']['value'][number]
export type ProjectView = ReturnType<typeof useSite>['projects']['value'][number]
