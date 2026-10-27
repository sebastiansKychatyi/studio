<script setup lang="ts">
const { t } = useSite()
</script>

<template>
  <div class="marquee" aria-hidden="true">
    <div class="marquee-track">
      <template v-for="n in 2" :key="n">
        <template v-for="m in t.marquee" :key="`${n}-${m}`">
          <span>{{ m }}</span><i>✦</i>
        </template>
      </template>
    </div>
  </div>
</template>
