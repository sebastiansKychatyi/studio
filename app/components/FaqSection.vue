<script setup lang="ts">
const { t } = useSite()
</script>

<template>
  <section id="faq" class="section">
    <div class="container faq-grid">
      <div class="section-head">
        <p v-reveal class="eyebrow">{{ t.faq.eyebrow }}</p>
        <h2 v-reveal style="--d: 80ms">{{ t.faq.title }}</h2>
      </div>
      <div class="faq">
        <details v-for="(f, i) in t.faq.items" :key="f.q" v-reveal :style="{ '--d': `${i * 60}ms` }" :open="i === 0">
          <summary>
            <h3>{{ f.q }}</h3>
            <span class="plus" aria-hidden="true" />
          </summary>
          <div class="answer"><p>{{ f.a }}</p></div>
        </details>
      </div>
    </div>
  </section>
</template>
