<script setup lang="ts">
const { t } = useSite()
</script>

<template>
  <section id="process" class="section section-alt">
    <div class="container">
      <div class="section-head center">
        <p v-reveal class="eyebrow">{{ t.process.eyebrow }}</p>
        <h2 v-reveal style="--d: 80ms">{{ t.process.title }}</h2>
      </div>
      <ol v-reveal class="steps">
        <li v-for="(s, i) in t.process.steps" :key="s.title" class="step" :style="{ '--d': `${i * 150}ms` }">
          <span class="step-num">0{{ i + 1 }}</span>
          <h3>{{ s.title }}</h3>
          <p>{{ s.text }}</p>
        </li>
      </ol>
    </div>
  </section>
</template>
