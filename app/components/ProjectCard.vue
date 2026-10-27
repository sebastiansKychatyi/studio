<script setup lang="ts">
import type { ProjectView } from '~/composables/useSite'

const props = defineProps<{ project: ProjectView; showAuthor?: boolean }>()
const { t } = useSite()
const localePath = useLocalePath()
// Основная ссылка карточки: живой сайт, иначе GitHub
const href = computed(() => props.project.url || props.project.repo || '')
</script>

<template>
  <div class="project-link" :style="{ '--c1': project.colors[0], '--c2': project.colors[1] }">
    <a v-if="href" class="project-cover" :href="href" target="_blank" rel="noopener" :aria-label="project.title">
      <ProjectMock :image="project.image" :title="project.title" :layout="project.layout" :tags="project.tags" />
      <span class="project-arrow" aria-hidden="true"><AppIcon name="arrow" /></span>
    </a>
    <div v-else class="project-cover">
      <ProjectMock :image="project.image" :title="project.title" :layout="project.layout" :tags="project.tags" />
    </div>
    <span v-if="project.placeholder" class="project-badge">{{ t.work.demo }}</span>

    <div class="project-info">
      <p class="project-meta">
        {{ t.work.filters[project.category] }} · {{ project.year }}
        <NuxtLink
          v-if="showAuthor"
          class="project-author"
          :to="localePath(`/${project.authorPerson.slug}`)"
          :style="{ '--c1': project.authorPerson.colors[0] }"
        >
          <span>{{ project.authorPerson.initials }}</span>{{ project.authorPerson.shortName }}
        </NuxtLink>
      </p>
      <h3>{{ project.title }}</h3>
      <p>{{ project.desc }}</p>
      <ul class="chips">
        <li v-for="tag in project.tags" :key="tag">{{ tag }}</li>
      </ul>
      <div v-if="project.url || project.repo" class="project-actions">
        <a v-if="project.url" :href="project.url" target="_blank" rel="noopener">{{ t.work.live }} ↗</a>
        <a v-if="project.repo" :href="project.repo" target="_blank" rel="noopener"><AppIcon name="github" /> {{ t.work.code }}</a>
      </div>
    </div>
  </div>
</template>
