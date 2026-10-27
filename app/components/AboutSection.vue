<script setup lang="ts">
const { t, people } = useSite()
const localePath = useLocalePath()
const socialLinks = (links: Record<string, string>) => Object.entries(links).filter(([, href]) => href)
</script>

<template>
  <section id="about" class="section">
    <div class="container">
      <div class="section-head split">
        <div>
          <p v-reveal class="eyebrow">{{ t.about.eyebrow }}</p>
          <h2 v-reveal style="--d: 80ms">{{ t.about.title }}</h2>
        </div>
        <p v-reveal class="section-text" style="--d: 160ms">{{ t.about.text }}</p>
      </div>

      <div class="team">
        <article
          v-for="(p, i) in people"
          :key="p.id"
          v-reveal
          v-tilt
          class="person tilt"
          :class="`person--${p.theme}`"
          :style="{ '--d': `${i * 120}ms`, '--c1': p.colors[0], '--c2': p.colors[1] }"
        >
          <div class="person-top">
            <div class="avatar">
              <img v-if="p.photo" :src="p.photo" :alt="p.name" width="96" height="96" loading="lazy">
              <span v-else>{{ p.initials }}</span>
            </div>
            <div class="person-links">
              <a
                v-for="[k, href] in socialLinks(p.links)"
                :key="k"
                :href="href"
                :aria-label="`${p.name} ${k}`"
                target="_blank"
                rel="noopener"
              ><AppIcon :name="k" /></a>
            </div>
          </div>
          <h3>{{ p.name }}</h3>
          <p class="role">{{ p.role }}</p>
          <p class="bio">{{ p.bio }}</p>
          <ul class="chips">
            <li v-for="s in p.skills.slice(0, 6)" :key="s">{{ s }}</li>
          </ul>
          <NuxtLink class="person-cta" :to="localePath(`/${p.slug}`)">
            {{ t.about.profile }} <AppIcon name="arrow" />
          </NuxtLink>
        </article>
      </div>
    </div>
  </section>
</template>
