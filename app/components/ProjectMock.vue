<script setup lang="ts">
// Если у проекта нет скриншота — рисуем абстрактный макет в цветах проекта
defineProps<{ image?: string; title: string; layout: number; tags?: string[] }>()
</script>

<template>
  <div class="mock">
    <img v-if="image" :src="image" :alt="title" loading="lazy" decoding="async" width="1200" height="750">
    <div v-else-if="layout === 4" class="mock-window mock-code">
      <div class="mock-bar"><i /><i /><i /><span>{{ title.toLowerCase().replace(/\s+/g, '-') }}</span></div>
      <pre><code><b>$</b> docker compose up
<span v-for="tag in (tags || []).slice(0, 3)" :key="tag"><em>✔</em> {{ tag }}
</span><b>GET</b>  /api/v1/{{ title.split(' ')[0]!.toLowerCase() }}  <em>200 OK</em>
<i>#</i> {{ (tags || []).slice(3).join(' · ') || 'ready' }}</code></pre>
    </div>
    <div v-else class="mock-window">
      <div class="mock-bar"><i /><i /><i /></div>
      <div v-if="layout === 2" class="m-l2">
        <i class="m-line w40 strong" />
        <div class="m-cards"><span /><span /><span /></div>
      </div>
      <div v-else-if="layout === 3" class="m-l3">
        <i class="m-line w50 strong c" /><i class="m-line w70 c" />
        <div class="m-cols"><span /><span /></div>
      </div>
      <div v-else class="m-l1">
        <div><i class="m-line w60 strong" /><i class="m-line w80" /><i class="m-line w50" /><i class="m-btn" /></div>
        <div class="m-img" />
      </div>
    </div>
  </div>
</template>
