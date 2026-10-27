import type { PersonView } from './useSite'

// SEO + GEO: meta-теги, hreflang, Open Graph, Geo-теги и schema.org (JSON-LD).
// Без аргумента — общая страница студии; с person — личная страница; cv: true — страница-резюме человека.
export function useSiteSeo(person?: Ref<PersonView | undefined>, opts: { cv?: boolean } = {}) {
  const { t, cfg, all, people, projects } = useSite()
  const { locale } = useI18n()
  const i18nHead = useLocaleHead({ seo: true })

  const home = computed(() => `${cfg.domain}/${locale.value}`)
  const url = computed(() =>
    person?.value ? `${home.value}/${person.value.slug}${opts.cv ? '/cv' : ''}` : home.value
  )
  const title = computed(() => {
    const p = person?.value
    if (!p) return t.value.meta.title
    return opts.cv ? `${t.value.personal.cv.metaTitle} — ${p.name}, ${p.role}` : p.page.metaTitle
  })
  const description = computed(() => person?.value?.page.metaDescription ?? t.value.meta.description)
  const ogTitle = computed(() => (person?.value ? title.value : t.value.meta.ogTitle))
  // У каждого человека своя картинка-превью для соцсетей: public/og-<slug>.png
  const ogImage = computed(() => `${cfg.domain}/${person?.value ? `og-${person.value.slug}` : 'og-image'}.png`)
  const countryNames: Record<string, string> = { SK: 'Slovakia', CZ: 'Czech Republic', UA: 'Ukraine' }

  useSeoMeta({
    title,
    description,
    // Резюме дублирует личную страницу — не индексируем, чтобы не конкурировать с ней в поиске
    robots: opts.cv ? 'noindex, follow' : undefined,
    author: () => person?.value?.name ?? people.value.map((p) => p.name).join(', '),
    ogType: () => (person?.value ? 'profile' : 'website'),
    ogSiteName: cfg.brand,
    ogTitle,
    ogDescription: description,
    ogImage,
    ogImageWidth: 1200,
    ogImageHeight: 630,
    twitterCard: 'summary_large_image',
    twitterTitle: ogTitle,
    twitterDescription: description,
    twitterImage: ogImage,
  })

  const personLd = (p: PersonView) => ({
    '@type': 'Person',
    '@id': `${cfg.domain}/#${p.id}`,
    name: p.name,
    url: `${home.value}/${p.slug}`,
    jobTitle: p.role,
    description: p.bio,
    knowsAbout: p.skillGroups.length ? p.skillGroups.flatMap((g) => g.v) : p.skills,
    ...(p.degree ? { honorificPrefix: p.degree } : {}),
    ...(p.page.education.length
      ? { alumniOf: { '@type': 'CollegeOrUniversity', name: 'Constantine the Philosopher University in Nitra' } }
      : {}),
    knowsLanguage: cfg.languages,
    homeLocation: { '@type': 'Place', name: p.page.facts[0]?.v },
    worksFor: { '@id': `${cfg.domain}/#org` },
    sameAs: Object.values(p.links).filter((l) => l && l !== '#'),
  })

  const workLd = (list: typeof projects.value) => ({
    '@type': 'ItemList',
    '@id': `${url.value}#portfolio`,
    name: t.value.work.title,
    itemListElement: list.map((p, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      item: {
        '@type': p.category === 'app' ? 'SoftwareSourceCode' : 'CreativeWork',
        name: p.title,
        description: p.desc,
        dateCreated: String(p.year),
        url: p.url || p.repo,
        ...(p.repo ? { codeRepository: p.repo } : {}),
        keywords: p.tags.join(', '),
        creator: { '@id': `${cfg.domain}/#${p.author}` },
      },
    })),
  })

  const org = computed(() => ({
    '@type': 'ProfessionalService',
    '@id': `${cfg.domain}/#org`,
    name: cfg.brand,
    url: `${cfg.domain}/`,
    logo: `${cfg.domain}/favicon.svg`,
    image: `${cfg.domain}/og-image.png`,
    description: t.value.meta.description,
    email: cfg.email,
    telephone: cfg.phone,
    priceRange: '€€',
    address: { '@type': 'PostalAddress', addressLocality: cfg.location.city, addressCountry: cfg.location.country },
    geo: { '@type': 'GeoCoordinates', latitude: cfg.location.lat, longitude: cfg.location.lng },
    // Сначала города по приоритету (Bratislava, Nitra, Prague, Kyiv, Uzhhorod), затем страны целиком
    areaServed: [
      ...cfg.cities.map((ct) => ({
        '@type': 'City',
        name: ct.name,
        containedInPlace: { '@type': 'Country', name: countryNames[ct.country] || ct.country },
      })),
      ...cfg.areaServed.map((c) => ({ '@type': 'Country', name: countryNames[c] || c })),
    ],
    knowsLanguage: cfg.languages,
    founder: people.value.map((p) => ({ '@id': `${cfg.domain}/#${p.id}` })),
    hasOfferCatalog: {
      '@type': 'OfferCatalog',
      name: t.value.services.title,
      itemListElement: [...t.value.services.items, ...t.value.ai.items].map((s) => ({
        '@type': 'Offer',
        itemOffered: { '@type': 'Service', name: s.title, description: s.text },
      })),
    },
  }))

  const schema = computed(() => {
    const p = person?.value
    const graph: object[] = [
      {
        '@type': 'WebSite',
        '@id': `${cfg.domain}/#website`,
        url: `${cfg.domain}/`,
        name: cfg.brand,
        inLanguage: cfg.languages,
        publisher: { '@id': `${cfg.domain}/#org` },
      },
      org.value,
    ]
    if (p) {
      graph.push(
        {
          '@type': 'ProfilePage',
          '@id': `${url.value}#webpage`,
          url: url.value,
          name: title.value,
          description: description.value,
          inLanguage: locale.value,
          isPartOf: { '@id': `${cfg.domain}/#website` },
          mainEntity: { '@id': `${cfg.domain}/#${p.id}` },
        },
        personLd(p),
        workLd(projects.value.filter((x) => x.author === p.id && !x.placeholder))
      )
    } else {
      graph.push(
        ...people.value.map(personLd),
        {
          '@type': 'WebPage',
          '@id': `${url.value}#webpage`,
          url: url.value,
          name: title.value,
          description: description.value,
          inLanguage: locale.value,
          isPartOf: { '@id': `${cfg.domain}/#website` },
          about: { '@id': `${cfg.domain}/#org` },
        },
        {
          '@type': 'FAQPage',
          '@id': `${url.value}#faq`,
          inLanguage: locale.value,
          mainEntity: t.value.faq.items.map((f) => ({
            '@type': 'Question',
            name: f.q,
            acceptedAnswer: { '@type': 'Answer', text: f.a },
          })),
        },
        workLd(projects.value.filter((x) => !x.placeholder))
      )
    }
    return { '@context': 'https://schema.org', '@graph': graph }
  })

  useHead(() => ({
    htmlAttrs: { lang: all[locale.value]?.htmlLang ?? locale.value },
    link: [...(i18nHead.value.link || [])],
    meta: [
      ...(i18nHead.value.meta || []),
      { name: 'geo.region', content: cfg.location.region },
      { name: 'geo.placename', content: cfg.cities.slice(0, 2).map((c) => c.name).join(', ') },
      { name: 'geo.position', content: `${cfg.location.lat};${cfg.location.lng}` },
      { name: 'ICBM', content: `${cfg.location.lat}, ${cfg.location.lng}` },
    ],
    script: [{ type: 'application/ld+json', innerHTML: JSON.stringify(schema.value) }],
  }))
}
