<script setup lang="ts">
const { t, cfg } = useSite()
const year = new Date().getFullYear()
</script>

<template>
  <footer class="site-footer">
    <div class="container">
      <p class="footer-big" aria-hidden="true">{{ cfg.brand }}</p>
      <div class="footer-row">
        <p>{{ t.footer.tagline }}</p>
        <LangSwitch />
      </div>
      <div class="footer-row small">
        <p>© {{ year }} {{ cfg.brand }} · {{ cfg.cities.slice(0, 2).map((c) => c.name).join(' · ') }}. {{ t.footer.rights }}</p>
        <a href="#top" class="to-top">{{ t.footer.top }} ↑</a>
      </div>
    </div>
  </footer>
</template>
