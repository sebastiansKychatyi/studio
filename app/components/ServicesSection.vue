<script setup lang="ts">
const { t } = useSite()
</script>

<template>
  <section id="services" class="section section-alt">
    <div class="container">
      <div class="section-head center">
        <p v-reveal class="eyebrow">{{ t.services.eyebrow }}</p>
        <h2 v-reveal style="--d: 80ms">{{ t.services.title }}</h2>
        <p v-reveal class="section-text" style="--d: 160ms">{{ t.services.text }}</p>
      </div>
      <div class="services">
        <article
          v-for="(s, i) in t.services.items"
          :key="s.icon"
          v-reveal
          v-spot
          class="service"
          :style="{ '--d': `${(i % 3) * 100}ms` }"
        >
          <div class="service-ico"><AppIcon :name="s.icon" /></div>
          <h3>{{ s.title }}</h3>
          <p>{{ s.text }}</p>
          <span class="service-num">0{{ i + 1 }}</span>
        </article>
      </div>
    </div>
  </section>
</template>
