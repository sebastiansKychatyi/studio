<script setup lang="ts">
const { t, projects } = useSite()

type Filter = keyof typeof t.value.work.filters
const filter = ref<Filter>('all')
// Collapsed: a short pick (2 per author); a filter click or "show all" opens the full list
const expanded = ref(false)
const PICK = 2
const filtered = computed(() => projects.value.filter((p) => filter.value === 'all' || p.category === filter.value))
const picked = computed(() => {
  const count: Record<string, number> = {}
  return projects.value.filter((p) => (count[p.author] = (count[p.author] ?? 0) + 1) <= PICK)
})
const visible = computed(() => (expanded.value ? filtered.value : picked.value))
const filterKeys = computed(() => Object.keys(t.value.work.filters) as Filter[])

function choose(k: Filter) {
  filter.value = k
  expanded.value = true
}
function collapse() {
  expanded.value = false
  filter.value = 'all'
  document.getElementById('work')?.scrollIntoView({ behavior: 'smooth' })
}
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
            :class="{ active: expanded && filter === k }"
            :aria-pressed="expanded && filter === k"
            @click="choose(k)"
          >
            {{ t.work.filters[k] }}
          </button>
        </div>
      </div>

      <Transition name="grid" mode="out-in">
        <div :key="`${filter}-${expanded}`" class="projects">
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

      <div class="work-more">
        <button v-if="!expanded" type="button" class="btn btn-ghost" @click="choose('all')">
          {{ t.work.showAll }} <span class="work-count">{{ projects.length }}</span>
        </button>
        <button v-else-if="filtered.length > picked.length" type="button" class="btn btn-ghost" @click="collapse">
          {{ t.work.collapse }}
        </button>
      </div>
    </div>
  </section>
</template>

<style>
.work-more { display: flex; justify-content: center; margin-top: 34px; }
.work-more .btn { gap: 10px; }
.work-count { display: inline-grid; place-items: center; min-width: 26px; height: 26px; padding: 0 8px; border-radius: 999px; background: var(--ink); color: #fff; font-size: .8rem; font-weight: 800; }
</style>
