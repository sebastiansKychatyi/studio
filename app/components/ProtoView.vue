<script setup lang="ts">
// Renders a prototype; `preview` = non-interactive copy for card covers
defineProps<{ kind: 'nordic' | 'byty' | 'fitflow'; preview?: boolean }>()
</script>

<template>
  <ProtoNordic v-if="kind === 'nordic'" :preview="preview" />
  <ProtoByty v-else-if="kind === 'byty'" :preview="preview" />
  <ProtoFitflow v-else :preview="preview" />
</template>
