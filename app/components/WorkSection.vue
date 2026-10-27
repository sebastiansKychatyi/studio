<script setup lang="ts">
const { t, projects } = useSite()

type Filter = keyof typeof t.value.work.filters
const filter = ref<Filter>('all')
const visible = computed(() => projects.value.filter((p) => filter.value === 'all' || p.category === filter.value))
const filterKeys = computed(() => Object.keys(t.value.work.filters) as Filter[])
</script>

<template>
  <section id="work" class="section">
    <div class="container">
      <div class="section-head split">
        <div>
          <p v-reveal class="eyebrow">{{ t.work.eyebrow }}</p>
          <h2 v-reveal style="--d: 80ms">{{ t.work.title }}</h2>
        </div>
        <div v-reveal class="filters" role="group" style="--d: 160ms">
          <button
            v-for="k in filterKeys"
            :key="k"
            type="button"
            :class="{ active: filter === k }"
            :aria-pressed="filter === k"
            @click="filter = k"
          >
            {{ t.work.filters[k] }}
          </button>
        </div>
      </div>

      <Transition name="grid" mode="out-in">
        <div :key="filter" class="projects">
          <article
            v-for="(p, i) in visible"
            :key="p.id"
            v-reveal
            class="project"
            :style="{ '--d': `${(i % 2) * 120}ms` }"
          >
            <ProjectCard :project="p" show-author />
          </article>
        </div>
      </Transition>
    </div>
  </section>
</template>
