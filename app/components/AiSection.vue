<script setup lang="ts">
const { t } = useSite()
const flowIcons = ['mail', 'spark', 'doc', 'send']
</script>

<template>
  <section id="ai" class="section ai">
    <div class="ai-bg" aria-hidden="true">
      <div class="ai-orb ai-orb-1" />
      <div class="ai-orb ai-orb-2" />
    </div>
    <div class="container">
      <div class="section-head center">
        <p v-reveal class="eyebrow">{{ t.ai.eyebrow }}</p>
        <h2 v-reveal style="--d: 80ms">{{ t.ai.title }}</h2>
        <p v-reveal class="section-text" style="--d: 160ms">{{ t.ai.text }}</p>
      </div>

      <!-- Анимированная схема автоматизации: данные «бегут» по цепочке -->
      <div v-reveal class="flow" style="--d: 200ms">
        <p class="flow-label">{{ t.ai.flowLabel }}</p>
        <ol class="flow-steps">
          <li v-for="(step, i) in t.ai.flow" :key="step" class="flow-node" :style="{ '--i': i }">
            <span class="flow-ico" :class="{ 'is-ai': i === 1 }"><AppIcon :name="flowIcons[i]!" /></span>
            <span class="flow-text">{{ step }}</span>
            <span v-if="i < t.ai.flow.length - 1" class="flow-link" aria-hidden="true"><i /></span>
          </li>
        </ol>
      </div>

      <div class="ai-grid">
        <article
          v-for="(item, i) in t.ai.items"
          :key="item.title"
          v-reveal
          v-spot
          class="service ai-card"
          :style="{ '--d': `${(i % 3) * 100}ms` }"
        >
          <div class="service-ico"><AppIcon :name="item.icon" /></div>
          <h3>{{ item.title }}</h3>
          <p>{{ item.text }}</p>
        </article>
      </div>

      <div v-reveal class="ai-benefits">
        <div v-for="b in t.ai.benefits" :key="b.value" class="ai-benefit">
          <strong>{{ b.value }}</strong>
          <span>{{ b.label }}</span>
        </div>
        <a v-magnetic class="btn btn-primary" href="#contact">{{ t.ai.cta }} <AppIcon name="arrow" /></a>
      </div>
    </div>
  </section>
</template>
