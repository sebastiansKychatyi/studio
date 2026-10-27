<script setup lang="ts">
// GDPR privacy policy page
import type { Lang } from '~~/data/site'
import { privacy } from '~~/data/privacy'

const { t, cfg } = useSite()
const { locale } = useI18n()
const localePath = useLocalePath()
const i18nHead = useLocaleHead({ seo: true })

const p = computed(() => privacy[locale.value as Lang])
const controller = cfg.people[0]!
const fill = (s: string) =>
  s.replace('{name}', controller.name).replace(/\{email\}/g, cfg.email).replace('{phone}', cfg.phone).replace('{city}', cfg.location.city)

useSeoMeta({ title: () => `${p.value.title} | ${cfg.brand}`, description: () => p.value.intro, robots: 'noindex, follow' })
useHead(() => ({ htmlAttrs: { lang: locale.value }, link: [...(i18nHead.value.link || [])] }))
</script>

<template>
  <div>
    <SiteHeader />
    <main class="legal">
      <div class="container legal-inner">
        <nav class="crumbs" aria-label="Breadcrumb">
          <NuxtLink :to="localePath('/')">{{ cfg.brand }}</NuxtLink> <span>/</span> <span>{{ p.title }}</span>
        </nav>
        <h1>{{ p.title }}</h1>
        <p class="legal-updated">{{ p.updated }}</p>
        <p class="legal-intro">{{ p.intro }}</p>
        <section v-for="(s, i) in p.sections" :key="s[0]">
          <h2><span>{{ String(i + 1).padStart(2, '0') }}</span> {{ s[0] }}</h2>
          <ul v-if="s[1].length > 1"><li v-for="para in s[1]" :key="para">{{ fill(para) }}</li></ul>
          <p v-else>{{ fill(s[1][0]!) }}</p>
        </section>
        <NuxtLink class="btn btn-ghost" :to="localePath('/')">← {{ cfg.brand }}</NuxtLink>
      </div>
    </main>
    <SiteFooter />
  </div>
</template>

<style>
.legal { padding: 140px 0 80px; }
.legal-inner { max-width: 820px; }
.legal h1 { font-family: var(--font-display); font-weight: 600; font-size: clamp(2rem, 5vw, 3.4rem); letter-spacing: -.03em; margin-top: 14px; }
.legal-updated { color: var(--muted); font-weight: 700; margin: 6px 0 20px; }
.legal-intro { font-size: 1.1rem; color: var(--ink-2); margin-bottom: 30px; }
.legal section { padding: 22px 0; border-top: 1px solid var(--line); }
.legal h2 { display: flex; gap: 12px; align-items: baseline; font-size: 1.25rem; font-weight: 800; margin-bottom: 10px; }
.legal h2 span { font: 600 .85rem/1 ui-monospace, monospace; color: var(--accent); }
.legal ul { display: grid; gap: 8px; padding-left: 0; }
.legal li { position: relative; padding-left: 20px; color: var(--ink-2); }
.legal li::before { content: ''; position: absolute; left: 4px; top: .65em; width: 6px; height: 6px; border-radius: 50%; background: var(--accent); }
.legal p { color: var(--ink-2); }
.legal .btn { margin-top: 30px; }
</style>
