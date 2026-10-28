<script setup lang="ts">
import type { Lang } from '~~/data/site'
import { cities } from '~~/data/cities'

const { t, cfg } = useSite()
const { locale } = useI18n()
const localePath = useLocalePath()
const year = new Date().getFullYear()
const lang = computed(() => locale.value as Lang)
</script>

<template>
  <footer class="site-footer">
    <div class="container">
      <p class="footer-big" aria-hidden="true">{{ cfg.brand }}</p>
      <div class="footer-row">
        <p>{{ t.footer.tagline }}</p>
        <LangSwitch up />
      </div>
      <!-- City pages: internal links for local SEO -->
      <nav class="footer-row footer-cities" :aria-label="t.city.footerTitle">
        <span>{{ t.city.footerTitle }}:</span>
        <NuxtLink v-for="c in cities" :key="c.slug" :to="localePath(`/${c.slug}`)">{{ c.text[lang].name }}</NuxtLink>
      </nav>
      <div class="footer-row small">
        <p>© {{ year }} {{ cfg.brand }} · {{ cfg.cities.slice(0, 2).map((c) => c.name).join(' · ') }}. {{ t.footer.rights }}</p>
        <div class="footer-links">
          <NuxtLink :to="localePath('/privacy')">{{ t.footer.privacy }}</NuxtLink>
          <NuxtLink :to="localePath('/login')" rel="nofollow">{{ t.panel.login }}</NuxtLink>
          <a href="#top" class="to-top">{{ t.footer.top }} ↑</a>
        </div>
      </div>
    </div>
  </footer>
</template>
