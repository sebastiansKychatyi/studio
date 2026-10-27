<script setup lang="ts">
// City landing page for local SEO: /sk/bratislava, /cs/praha, /uk/kyiv…
import type { Lang } from '~~/data/site'
import { cities, type City } from '~~/data/cities'

const props = defineProps<{ city: City }>()
const { t, cfg, projects } = useSite()
const { locale } = useI18n()
const localePath = useLocalePath()
const i18nHead = useLocaleHead({ seo: true })

const lang = computed(() => locale.value as Lang)
const c = computed(() => props.city.text[lang.value])
const cityProjects = computed(() => props.city.projects.map((id) => projects.value.find((p) => p.id === id)).filter((p) => !!p))
const others = computed(() => cities.filter((x) => x.slug !== props.city.slug))
const url = computed(() => `${cfg.domain}/${locale.value}/${props.city.slug}`)
const countryNames: Record<string, string> = { SK: 'Slovakia', CZ: 'Czech Republic', UA: 'Ukraine' }

useSeoMeta({
  title: () => c.value.metaTitle,
  description: () => c.value.metaDescription,
  ogTitle: () => c.value.metaTitle,
  ogDescription: () => c.value.metaDescription,
  ogImage: `${cfg.domain}/og-image.png`,
  twitterCard: 'summary_large_image',
})

useHead(() => ({
  htmlAttrs: { lang: locale.value },
  link: [...(i18nHead.value.link || [])],
  meta: [
    ...(i18nHead.value.meta || []),
    { name: 'geo.placename', content: props.city.text.sk.name },
    { name: 'geo.position', content: `${props.city.geo.lat};${props.city.geo.lng}` },
    { name: 'ICBM', content: `${props.city.geo.lat}, ${props.city.geo.lng}` },
  ],
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@graph': [
        {
          '@type': 'Service',
          '@id': `${url.value}#service`,
          name: c.value.metaTitle,
          description: c.value.metaDescription,
          serviceType: t.value.services.items.map((s) => s.title),
          provider: { '@type': 'ProfessionalService', '@id': `${cfg.domain}/#org`, name: cfg.brand, url: `${cfg.domain}/`, email: cfg.email, telephone: cfg.phone },
          areaServed: {
            '@type': 'City',
            name: c.value.name,
            geo: { '@type': 'GeoCoordinates', latitude: props.city.geo.lat, longitude: props.city.geo.lng },
            containedInPlace: { '@type': 'Country', name: countryNames[props.city.country] },
          },
          inLanguage: locale.value,
        },
        {
          '@type': 'FAQPage',
          '@id': `${url.value}#faq`,
          mainEntity: c.value.faq.map(([q, a]) => ({ '@type': 'Question', name: q, acceptedAnswer: { '@type': 'Answer', text: a } })),
        },
        {
          '@type': 'BreadcrumbList',
          itemListElement: [
            { '@type': 'ListItem', position: 1, name: cfg.brand, item: `${cfg.domain}/${locale.value}` },
            { '@type': 'ListItem', position: 2, name: c.value.name, item: url.value },
          ],
        },
      ],
    }),
  }],
}))
</script>

<template>
  <div>
    <a class="skip-link" href="#main">{{ t.skip }}</a>
    <SiteHeader />
    <main id="main">
      <section class="city-hero">
        <div class="hero-bg" aria-hidden="true"><div class="grid-bg" /><div class="blob blob-1" /><div class="blob blob-2" /></div>
        <div class="container city-hero-grid">
          <div>
            <nav class="crumbs fade-in" aria-label="Breadcrumb">
              <NuxtLink :to="localePath('/')">{{ cfg.brand }}</NuxtLink> <span>/</span> <span>{{ c.name }}</span>
            </nav>
            <p class="badge fade-in" style="--d: 80ms"><span class="dot" />{{ city.inPerson ? t.city.inPerson : t.city.remote }} · {{ c.name }}</p>
            <h1 class="city-title fade-in" style="--d: 150ms">{{ c.h1[0] }} <span class="grad">{{ c.h1[1] }}</span></h1>
            <p class="lead fade-in" style="--d: 300ms">{{ c.intro }}</p>
            <div class="hero-cta fade-in" style="--d: 450ms">
              <a v-magnetic class="btn btn-primary" href="#contact">{{ t.city.cta }} <AppIcon name="arrow" /></a>
              <a v-magnetic class="btn btn-ghost" href="#city-work">{{ t.city.projects }}</a>
            </div>
          </div>
          <div class="city-map fade-in" style="--d: 300ms" aria-hidden="true">
            <svg viewBox="0 0 300 300">
              <circle cx="150" cy="150" r="130" class="ring r3" />
              <circle cx="150" cy="150" r="90" class="ring r2" />
              <circle cx="150" cy="150" r="50" class="ring r1" />
              <path d="M30 190 Q90 120 150 150 T280 110" class="road" />
              <path d="M60 60 Q120 110 150 150 T230 260" class="road" />
            </svg>
            <div class="city-pin"><AppIcon name="pin" /></div>
            <p class="city-coords">{{ city.geo.lat.toFixed(4) }}° N · {{ city.geo.lng.toFixed(4) }}° E</p>
            <p class="city-name">{{ c.name }}</p>
          </div>
        </div>
      </section>

      <section class="section section-alt">
        <div class="container">
          <div class="section-head center">
            <p v-reveal class="eyebrow">{{ t.city.why }}</p>
            <h2 v-reveal style="--d: 80ms">{{ c.h1[0] }} {{ c.h1[1] }}</h2>
          </div>
          <div class="city-points">
            <article v-for="(pt, i) in c.points" :key="pt[0]" v-reveal v-spot class="service" :style="{ '--d': `${i * 100}ms` }">
              <span class="service-num">0{{ i + 1 }}</span>
              <h3>{{ pt[0] }}</h3>
              <p>{{ pt[1] }}</p>
            </article>
          </div>
        </div>
      </section>

      <ServicesSection />

      <section id="city-work" class="section">
        <div class="container">
          <div class="section-head">
            <p v-reveal class="eyebrow">{{ t.work.eyebrow }}</p>
            <h2 v-reveal style="--d: 80ms">{{ t.city.projects }}</h2>
          </div>
          <div class="projects city-projects">
            <article v-for="(p, i) in cityProjects" :key="p!.id" v-reveal class="project" :style="{ '--d': `${(i % 3) * 100}ms` }">
              <ProjectCard :project="p!" show-author />
            </article>
          </div>
        </div>
      </section>

      <section class="section section-alt">
        <div class="container faq-grid">
          <div class="section-head">
            <p v-reveal class="eyebrow">FAQ</p>
            <h2 v-reveal style="--d: 80ms">{{ t.city.faq }}</h2>
          </div>
          <div class="faq">
            <details v-for="(f, i) in c.faq" :key="f[0]" v-reveal :style="{ '--d': `${i * 60}ms` }" :open="i === 0">
              <summary><h3>{{ f[0] }}</h3><span class="plus" aria-hidden="true" /></summary>
              <div class="answer"><p>{{ f[1] }}</p></div>
            </details>
          </div>
        </div>
      </section>

      <section class="section city-others">
        <div class="container">
          <p v-reveal class="eyebrow">{{ t.city.other }}</p>
          <div class="city-links">
            <NuxtLink v-for="o in others" :key="o.slug" v-reveal :to="localePath(`/${o.slug}`)" class="city-link">
              <AppIcon name="pin" /> {{ o.text[lang].name }} <span>→</span>
            </NuxtLink>
          </div>
        </div>
      </section>

      <ContactSection />
    </main>
    <SiteFooter />
    <ClientOnly><GeoLangHint /></ClientOnly>
    <DesignModal />
  </div>
</template>

<style>
.city-hero { position: relative; padding: 150px 0 80px; overflow: hidden; isolation: isolate; }
.city-hero-grid { display: grid; grid-template-columns: 1.2fr .8fr; gap: 48px; align-items: center; }
.crumbs { display: flex; gap: 8px; font-size: .88rem; color: var(--muted); margin-bottom: 18px; }
.crumbs a { font-weight: 700; color: var(--ink-2); }
.crumbs a:hover { color: var(--accent); }
.city-title { font-family: var(--font-display); font-weight: 600; font-size: clamp(2.2rem, 5vw, 4.2rem); line-height: 1.06; letter-spacing: -.035em; margin: 22px 0; text-wrap: balance; }
.city-map { position: relative; aspect-ratio: 1; max-width: 420px; width: 100%; margin-inline: auto; border-radius: 50%; background: radial-gradient(circle, #fff 0 40%, transparent 70%); }
.city-map svg { width: 100%; height: 100%; }
.city-map .ring { fill: none; stroke: var(--accent); stroke-opacity: .25; stroke-width: 1.5; transform-origin: 150px 150px; animation: cityRing 4s ease-out infinite; }
.city-map .r2 { animation-delay: 1.2s; }
.city-map .r3 { animation-delay: 2.4s; }
@keyframes cityRing { 0% { transform: scale(.6); stroke-opacity: .5; } 100% { transform: scale(1.1); stroke-opacity: 0; } }
.city-map .road { fill: none; stroke: var(--line-2); stroke-width: 6; stroke-linecap: round; }
.city-pin { position: absolute; top: 50%; left: 50%; translate: -50% -100%; font-size: 3.2rem; color: var(--accent-2); filter: drop-shadow(0 10px 12px rgba(255, 122, 89, .4)); animation: bob 3s ease-in-out infinite; }
.city-coords { position: absolute; left: 50%; bottom: 18%; translate: -50% 0; font: 600 .78rem/1 ui-monospace, monospace; color: var(--muted); white-space: nowrap; }
.city-name { position: absolute; left: 50%; top: 4%; translate: -50% 0; padding: 8px 16px; border-radius: 999px; background: var(--ink); color: #fff; font-weight: 800; white-space: nowrap; box-shadow: var(--shadow); }
.city-points { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.city-projects { grid-template-columns: repeat(3, 1fr); }
.city-links { display: flex; flex-wrap: wrap; gap: 10px; }
.city-link { display: inline-flex; align-items: center; gap: 8px; padding: 14px 20px; border-radius: 999px; background: var(--surface); border: 1px solid var(--line); font-weight: 700; transition: background .25s, color .25s, transform .3s var(--ease); }
.city-link:hover { background: var(--ink); color: #fff; transform: translateY(-3px); }
.city-link span { transition: transform .3s var(--ease); }
.city-link:hover span { transform: translateX(4px); }
@media (max-width: 1080px) {
  .city-hero-grid { grid-template-columns: 1fr; }
  .city-map { max-width: 300px; }
  .city-points, .city-projects { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 720px) {
  .city-hero { padding-top: 120px; }
  .city-points, .city-projects { grid-template-columns: 1fr; }
}
</style>
