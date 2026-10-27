<script setup lang="ts">
const { cfg, all } = useSite()
const { locale } = useI18n()
const route = useRoute()
const localePath = useLocalePath()
const { remember } = useLangChoice()
// Переключение на ту же страницу в другом языке (без #якоря — иначе SSR и клиент дают разные ссылки)
const target = (l: (typeof cfg.languages)[number]) => localePath(route.params.slug ? `/${route.params.slug}` : '/', l)
</script>

<template>
  <div class="lang-switch" role="navigation" aria-label="Language">
    <NuxtLink
      v-for="l in cfg.languages"
      :key="l"
      :to="target(l)"
      :hreflang="l"
      :lang="l"
      :title="all[l]!.label"
      :class="{ active: l === locale }"
      :aria-current="l === locale ? 'true' : undefined"
      @click="remember(l)"
    >
      {{ all[l]!.short }}
    </NuxtLink>
  </div>
</template>
