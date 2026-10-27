<script setup lang="ts">
import { concepts } from '~~/data/concepts'

const { t } = useSite()
const localePath = useLocalePath()
</script>

<template>
  <section id="lab" class="section section-alt lab">
    <div class="container">
      <div class="section-head split">
        <div>
          <p v-reveal class="eyebrow">{{ t.lab.eyebrow }}</p>
          <h2 v-reveal style="--d: 80ms">{{ t.lab.title }}</h2>
        </div>
        <p v-reveal class="section-text" style="--d: 160ms">{{ t.lab.text }}</p>
      </div>

      <div class="lab-grid">
        <NuxtLink
          v-for="(c, i) in concepts"
          :key="c.id"
          v-reveal
          v-tilt
          class="lab-card tilt"
          :class="`lab-card--${c.id}`"
          :to="localePath(`/lab/${c.id}`)"
          :style="{ '--d': `${(i % 2) * 120}ms`, '--c1': c.colors[0], '--c2': c.colors[1] }"
        >
          <div class="lab-cover">
            <img :src="`/img/concepts/${c.id}.jpg`" :alt="c.name" loading="lazy" width="1200" height="750">
            <span class="lab-name">{{ c.name }}</span>
          </div>
          <div class="lab-info">
            <p class="project-meta">{{ t.lab.items[c.id].type }}</p>
            <p>{{ t.lab.items[c.id].desc }}</p>
            <span class="lab-open">{{ t.lab.open }} <AppIcon name="arrow" /></span>
          </div>
        </NuxtLink>
      </div>
    </div>
  </section>
</template>

<style>
.lab-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 28px; perspective: 1400px; }
.lab-card { display: block; border-radius: var(--radius); background: var(--bg); border: 1px solid var(--line); overflow: hidden; transition: box-shadow .5s, transform .5s var(--ease); }
.lab-card:hover { box-shadow: var(--shadow-lg); }
.js .lab-card[data-reveal].is-in { transform: rotateX(var(--rx)) rotateY(var(--ry)); }
.lab-cover { position: relative; aspect-ratio: 16 / 10; overflow: hidden; background: linear-gradient(135deg, var(--c1), var(--c2)); }
.lab-cover img { width: 100%; height: 100%; object-fit: cover; object-position: top; transition: transform 1s var(--ease); }
.lab-card:hover .lab-cover img { transform: scale(1.06); }
.lab-name {
  position: absolute; left: 18px; bottom: 18px; padding: 8px 16px; border-radius: 999px; background: rgba(255, 255, 255, .92);
  font-family: var(--font-display); font-weight: 600; font-size: 1.1rem; box-shadow: var(--shadow);
}
.lab-info { padding: 22px 24px 26px; }
.lab-info > p:not(.project-meta) { color: var(--ink-2); }
.lab-open { display: inline-flex; align-items: center; gap: 8px; margin-top: 16px; font-weight: 800; transition: gap .3s var(--ease), color .3s; }
.lab-card:hover .lab-open { gap: 14px; color: var(--accent); }
@media (max-width: 720px) { .lab-grid { grid-template-columns: 1fr; } }
</style>
