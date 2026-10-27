<script setup lang="ts">
// Fits fixed-size content (w × h) into its parent via transform: scale
const props = defineProps<{ w: number; h: number }>()
const box = ref<HTMLElement>()
const scale = ref(0.4)
let ro: ResizeObserver | undefined

onMounted(() => {
  ro = new ResizeObserver(([entry]) => {
    const { width, height } = entry!.contentRect
    scale.value = Math.min(width / props.w, height / props.h, 1) // never upscale
  })
  ro.observe(box.value!)
})
onBeforeUnmount(() => ro?.disconnect())
</script>

<template>
  <div ref="box" class="scaled-box">
    <div class="scaled-inner" :style="{ width: `${w}px`, height: `${h}px`, transform: `translate(-50%, -50%) scale(${scale})` }">
      <slot />
    </div>
  </div>
</template>

<style>
.scaled-box { position: absolute; inset: 0; overflow: hidden; }
.scaled-inner { position: absolute; top: 50%; left: 50%; transform-origin: center; }
</style>
