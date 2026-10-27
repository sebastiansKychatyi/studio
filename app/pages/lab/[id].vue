<script setup lang="ts">
// Концепт-дизайн: /sk/lab/noir, /uk/lab/pulse … Каждый концепт — отдельный компонент Concept<Name>
import { concepts } from '~~/data/concepts'

const route = useRoute()
const { t, cfg } = useSite()
const { locale } = useI18n()
const localePath = useLocalePath()
const i18nHead = useLocaleHead({ seo: true })

const index = computed(() => concepts.findIndex((c) => c.id === route.params.id))
if (index.value < 0) {
  throw createError({ statusCode: 404, statusMessage: 'Page not found', fatal: true })
}
const concept = computed(() => concepts[index.value]!)
const next = computed(() => concepts[(index.value + 1) % concepts.length]!)
const item = computed(() => t.value.lab.items[concept.value.id])

const title = computed(() => `${concept.value.name} — ${item.value.type} | ${cfg.brand} Lab`)
useSeoMeta({
  title,
  description: () => item.value.desc,
  ogTitle: title,
  ogDescription: () => item.value.desc,
  ogImage: () => `${cfg.domain}/img/concepts/${concept.value.id}.jpg`,
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
      '@type': 'CreativeWork',
      name: `${concept.value.name} — ${item.value.type}`,
      description: item.value.desc,
      inLanguage: locale.value,
      genre: 'Web design concept',
      creator: { '@type': 'Organization', name: cfg.brand, url: `${cfg.domain}/` },
    }),
  }],
}))
</script>

<template>
  <div class="lab-page">
    <ConceptNoir v-if="concept.id === 'noir'" />
    <ConceptPulse v-else-if="concept.id === 'pulse'" />
    <ConceptKinetic v-else-if="concept.id === 'kinetic'" />
    <ConceptVerde v-else-if="concept.id === 'verde'" />

    <!-- Плашка студии: видно, что это концепт, и можно вернуться или перейти к следующему -->
    <div v-if="!route.query.cover" class="concept-bar" role="navigation" aria-label="Duo Studio Lab">
      <NuxtLink class="concept-bar-back" :to="localePath('/') + '#lab'" :title="t.lab.back">
        <span class="logo-mark" aria-hidden="true">D</span>
        <span class="concept-bar-text"><b>{{ cfg.brand }} Lab</b><small>{{ t.lab.badge }}</small></span>
      </NuxtLink>
      <LangSwitch />
      <NuxtLink class="concept-bar-next" :to="localePath(`/lab/${next.id}`)">{{ next.name }} →</NuxtLink>
      <NuxtLink class="btn btn-primary btn-sm concept-bar-cta" :to="localePath('/') + '#contact'">{{ t.lab.cta }}</NuxtLink>
    </div>
    <ClientOnly><GeoLangHint /></ClientOnly>
  </div>
</template>

<style>
.concept-bar {
  position: fixed; z-index: 80; left: 50%; bottom: 16px; transform: translateX(-50%);
  display: flex; align-items: center; gap: 10px; padding: 8px; border-radius: 999px; width: max-content; max-width: calc(100% - 24px);
  background: rgba(255, 255, 255, .9); color: #121216; -webkit-backdrop-filter: blur(16px); backdrop-filter: blur(16px);
  border: 1px solid rgba(18, 18, 22, .1); box-shadow: 0 20px 50px -18px rgba(0, 0, 0, .45);
  font-family: 'Manrope', system-ui, sans-serif; animation: barIn .8s cubic-bezier(.2, .8, .2, 1) .6s both;
}
@keyframes barIn { from { opacity: 0; transform: translate(-50%, 30px); } }
.concept-bar .logo-mark { width: 34px; height: 34px; border-radius: 50%; display: grid; place-items: center; color: #fff; font-weight: 700;
  background: conic-gradient(from 200deg, #5B4BFF, #FF7A59, #19C3A6, #5B4BFF); }
.concept-bar-back { display: flex; align-items: center; gap: 10px; padding-right: 6px; }
.concept-bar-text { display: grid; line-height: 1.15; }
.concept-bar-text b { font-size: .88rem; }
.concept-bar-text small { font-size: .72rem; color: #6B6B78; font-weight: 600; }
.concept-bar-next { padding: 8px 12px; border-radius: 999px; font-weight: 800; font-size: .88rem; }
.concept-bar-next:hover { background: #EEECE6; }
.concept-bar .btn-primary { background: #121216; color: #fff; }
@media (max-width: 720px) {
  .concept-bar-text small, .concept-bar-cta { display: none; }
}
@media print { .concept-bar { display: none; } }
</style>
