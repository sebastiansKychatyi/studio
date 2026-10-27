<script setup lang="ts">
// Выбирает нужный прототип. preview — уменьшенная неинтерактивная копия для обложки карточки
defineProps<{ kind: 'nordic' | 'byty' | 'fitflow'; preview?: boolean }>()
</script>

<template>
  <ProtoNordic v-if="kind === 'nordic'" :preview="preview" />
  <ProtoByty v-else-if="kind === 'byty'" :preview="preview" />
  <ProtoFitflow v-else :preview="preview" />
</template>
