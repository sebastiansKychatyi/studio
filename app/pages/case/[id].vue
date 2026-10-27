<script setup lang="ts">
// Кейс проекта: /sk/case/e-drivebook, /uk/case/expertsk …
import { cases } from '~~/data/cases'

const route = useRoute()
const { t, cfg, projects } = useSite()
const { locale } = useI18n()
const localePath = useLocalePath()
const i18nHead = useLocaleHead({ seo: true })

const index = computed(() => cases.findIndex((c) => c.id === route.params.id))
if (index.value < 0) {
  throw createError({ statusCode: 404, statusMessage: 'Page not found', fatal: true })
}
const study = computed(() => cases[index.value]!)
const next = computed(() => cases[(index.value + 1) % cases.length]!)
const c = computed(() => study.value.text[locale.value as 'sk' | 'cs' | 'uk'])
const project = computed(() => projects.value.find((p) => p.id === study.value.id)!)
const nextProject = computed(() => projects.value.find((p) => p.id === next.value.id)!)
const url = computed(() => `${cfg.domain}/${locale.value}/case/${study.value.id}`)

useSeoMeta({
  title: () => c.value.metaTitle,
  description: () => c.value.metaDescription,
  ogTitle: () => c.value.metaTitle,
  ogDescription: () => c.value.metaDescription,
  ogImage: () => `${cfg.domain}${project.value.image}`,
  ogType: 'article',
  twitterCard: 'summary_large_image',
})
useHead(() => ({
  htmlAttrs: { lang: locale.value },
  link: [...(i18nHead.value.link || [])],
  meta: [...(i18nHead.value.meta || [])],
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@graph': [
        {
          '@type': 'Article',
          '@id': `${url.value}#article`,
          headline: c.value.metaTitle,
          description: c.value.metaDescription,
          image: `${cfg.domain}${project.value.image}`,
          inLanguage: locale.value,
          author: { '@type': 'Person', name: project.value.authorPerson.name, url: `${cfg.domain}/${locale.value}/${project.value.authorPerson.slug}` },
          publisher: { '@type': 'Organization', name: cfg.brand, url: `${cfg.domain}/` },
          about: { '@type': 'SoftwareApplication', name: project.value.title, url: project.value.url, applicationCategory: 'BusinessApplication' },
        },
        {
          '@type': 'BreadcrumbList',
          itemListElement: [
            { '@type': 'ListItem', position: 1, name: cfg.brand, item: `${cfg.domain}/${locale.value}` },
            { '@type': 'ListItem', position: 2, name: t.value.work.eyebrow, item: `${cfg.domain}/${locale.value}#work` },
            { '@type': 'ListItem', position: 3, name: project.value.title, item: url.value },
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
    <main id="main" class="cs">
      <section class="cs-hero">
        <div class="hero-bg" aria-hidden="true"><div class="grid-bg" /><div class="blob blob-1" /><div class="blob blob-3" /></div>
        <div class="container">
          <nav class="crumbs fade-in" aria-label="Breadcrumb">
            <NuxtLink :to="localePath('/')">{{ cfg.brand }}</NuxtLink> <span>/</span>
            <NuxtLink :to="`${localePath('/')}#work`">{{ t.work.eyebrow }}</NuxtLink> <span>/</span>
            <span>{{ project.title }}</span>
          </nav>
          <p class="eyebrow fade-in" style="--d: 80ms">{{ t.caseStudy.label }}</p>
          <h1 class="cs-title fade-in" style="--d: 150ms">{{ project.title }}</h1>
          <p class="lead fade-in" style="--d: 250ms">{{ c.lead }}</p>
          <dl class="cs-meta fade-in" style="--d: 350ms">
            <div><dt>{{ t.caseStudy.client }}</dt><dd>{{ c.client }}</dd></div>
            <div><dt>{{ t.caseStudy.role }}</dt><dd>{{ c.role }}</dd></div>
            <div><dt>{{ t.caseStudy.year }}</dt><dd>{{ project.year }}</dd></div>
          </dl>
          <div class="hero-cta fade-in" style="--d: 450ms">
            <a v-if="project.url" v-magnetic class="btn btn-primary" :href="project.url" target="_blank" rel="noopener">{{ t.caseStudy.visit }} <AppIcon name="arrow" /></a>
            <a v-magnetic class="btn btn-ghost" href="#contact">{{ t.caseStudy.cta }}</a>
          </div>
        </div>
      </section>

      <div class="container">
        <div v-reveal v-tilt class="cs-shot tilt" data-tilt="4">
          <div class="browser-bar"><i /><i /><i /><span>{{ project.url?.replace(/^https?:\/\//, '').replace(/\/$/, '') }}</span></div>
          <img :src="project.image" :alt="project.title" width="1200" height="750">
        </div>
      </div>

      <section class="cs-results">
        <div class="container">
          <p v-reveal class="eyebrow">{{ t.caseStudy.results }}</p>
          <dl class="cs-stats">
            <div v-for="(r, i) in c.results" :key="r[1]" v-reveal :style="{ '--d': `${i * 100}ms` }"><dt>{{ r[0] }}</dt><dd>{{ r[1] }}</dd></div>
          </dl>
        </div>
      </section>

      <section class="section">
        <div class="container cs-split">
          <article v-reveal>
            <p class="eyebrow">{{ t.caseStudy.challenge }}</p>
            <p class="cs-text">{{ c.challenge }}</p>
          </article>
          <article v-reveal style="--d: 120ms">
            <p class="eyebrow">{{ t.caseStudy.solution }}</p>
            <p class="cs-text">{{ c.solution }}</p>
          </article>
        </div>
      </section>

      <section class="section section-alt">
        <div class="container">
          <div class="section-head">
            <p v-reveal class="eyebrow">{{ t.caseStudy.features }}</p>
            <h2 v-reveal style="--d: 80ms">{{ project.title }}</h2>
          </div>
          <div class="services">
            <article v-for="(f, i) in c.features" :key="f[0]" v-reveal v-spot class="service" :style="{ '--d': `${(i % 3) * 100}ms` }">
              <span class="service-num">0{{ i + 1 }}</span>
              <h3>{{ f[0] }}</h3>
              <p>{{ f[1] }}</p>
            </article>
          </div>
          <p v-reveal class="eyebrow cs-stack-label">{{ t.caseStudy.stack }}</p>
          <ul v-reveal class="chips cs-stack"><li v-for="s in study.stack" :key="s">{{ s }}</li></ul>
        </div>
      </section>

      <section class="section">
        <div class="container">
          <NuxtLink v-reveal class="cs-next" :to="localePath(`/case/${next.id}`)">
            <span class="eyebrow">{{ t.caseStudy.next }}</span>
            <strong>{{ nextProject.title }} →</strong>
            <img :src="nextProject.image" :alt="nextProject.title" loading="lazy" width="1200" height="750">
          </NuxtLink>
        </div>
      </section>

      <ContactSection />
    </main>
    <SiteFooter />
    <ClientOnly><GeoLangHint /></ClientOnly>
  </div>
</template>

<style>
.cs-hero { position: relative; padding: 150px 0 50px; overflow: hidden; isolation: isolate; }
.cs-title { font-family: var(--font-display); font-weight: 600; font-size: clamp(2.6rem, 7vw, 5.6rem); line-height: 1; letter-spacing: -.04em; margin: 10px 0 20px; }
.cs-meta { display: flex; flex-wrap: wrap; gap: 16px 48px; margin-top: 30px; padding-top: 24px; border-top: 1px solid var(--line); }
.cs-meta dt { font-size: .78rem; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); }
.cs-meta dd { font-weight: 700; margin-top: 4px; }
.cs-shot { border-radius: 22px; overflow: hidden; background: #fff; border: 1px solid var(--line); box-shadow: var(--shadow-lg); }
.js .cs-shot[data-reveal].is-in { transform: rotateX(var(--rx)) rotateY(var(--ry)); }
.cs-shot .browser-bar span { margin-left: 12px; }
.cs-shot img { width: 100%; display: block; }
.cs-results { margin-top: 80px; padding: 60px 0; background: var(--ink); color: #fff; }
.cs-results .eyebrow { color: var(--accent-3); }
.cs-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 28px; }
.cs-stats dt { font-family: var(--font-display); font-weight: 600; font-size: clamp(2.6rem, 6vw, 4rem); letter-spacing: -.03em; line-height: 1; background: linear-gradient(90deg, #fff, #C7C2FF); -webkit-background-clip: text; background-clip: text; color: transparent; }
.cs-stats dd { color: rgba(255, 255, 255, .7); margin-top: 8px; }
.cs-split { display: grid; grid-template-columns: 1fr 1fr; gap: 48px; }
.cs-text { font-size: 1.15rem; color: var(--ink-2); }
.cs-stack-label { margin-top: 48px; }
.cs-next { position: relative; display: grid; gap: 10px; padding: clamp(24px, 4vw, 44px); border-radius: var(--radius); background: var(--surface); border: 1px solid var(--line); overflow: hidden; transition: box-shadow .4s; }
.cs-next:hover { box-shadow: var(--shadow-lg); }
.cs-next strong { position: relative; z-index: 1; font-family: var(--font-display); font-weight: 600; font-size: clamp(1.8rem, 4vw, 3rem); letter-spacing: -.03em; transition: color .3s; }
.cs-next:hover strong { color: var(--accent); }
.cs-next img { position: absolute; right: -40px; top: 50%; width: 46%; translate: 0 -50%; border-radius: 14px; box-shadow: var(--shadow-lg); transform: rotate(-4deg); transition: transform .6s var(--ease); }
.cs-next:hover img { transform: rotate(0) scale(1.03); }
@media (max-width: 860px) {
  .cs-split { grid-template-columns: 1fr; }
  .cs-next img { position: static; width: 100%; translate: none; transform: none; margin-top: 10px; }
}
</style>
