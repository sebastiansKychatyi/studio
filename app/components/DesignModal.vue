<script setup lang="ts">
// Dialog with a clickable design prototype
const { t, projects } = useSite()
const { openId, close } = useDesignModal()
const project = computed(() => projects.value.find((p) => p.id === openId.value && p.prototype))
const dialog = ref<HTMLElement>()

const onKey = (e: KeyboardEvent) => e.key === 'Escape' && close()
watch(project, async (p) => {
  if (!import.meta.client) return
  document.documentElement.style.overflow = p ? 'hidden' : ''
  if (p) {
    await nextTick()
    dialog.value?.focus()
  }
})
onMounted(() => addEventListener('keydown', onKey))
onBeforeUnmount(() => {
  removeEventListener('keydown', onKey)
  document.documentElement.style.overflow = ''
})
</script>

<template>
  <Teleport to="body">
    <Transition name="dm">
      <div v-if="project" class="dm-veil" @click.self="close">
        <div ref="dialog" class="dm" role="dialog" aria-modal="true" :aria-label="project.title" tabindex="-1">
          <header class="dm-head">
            <div>
              <p class="dm-meta">
                {{ t.work.filters[project.category] }} · {{ project.year }} · {{ project.authorPerson.shortName }}
                <span class="dm-badge">{{ t.work.demo }}</span>
              </p>
              <h2>{{ project.title }}</h2>
              <p class="dm-desc">{{ project.desc }}</p>
            </div>
            <button type="button" class="dm-close" :aria-label="t.work.proto.close" @click="close">✕</button>
          </header>
          <div class="dm-stage" :class="`dm-stage--${project.prototype}`">
            <div class="dm-fit" :class="project.prototype === 'nordic' ? 'wide' : 'tall'">
              <ScaledBox :w="project.prototype === 'nordic' ? 900 : 320" :h="project.prototype === 'nordic' ? 560 : 640">
                <ProtoView :kind="project.prototype!" />
              </ScaledBox>
            </div>
          </div>
          <footer class="dm-foot">
            <span class="dm-pulse" /> {{ t.work.proto.hint }}
            <ul class="dm-tags"><li v-for="tag in project.tags" :key="tag">{{ tag }}</li></ul>
          </footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style>
.dm-veil {
  position: fixed; inset: 0; z-index: 200; display: grid; place-items: center; padding: 16px;
  background: rgba(18, 18, 22, .55); -webkit-backdrop-filter: blur(8px); backdrop-filter: blur(8px);
}
.dm {
  width: min(1100px, 100%); max-height: calc(100vh - 32px); overflow: auto; outline: none;
  border-radius: 28px; background: #fff; box-shadow: 0 40px 120px -30px rgba(0, 0, 0, .6); font-family: 'Manrope', system-ui, sans-serif; color: #121216;
}
.dm-head { display: flex; justify-content: space-between; gap: 20px; padding: 24px 28px 16px; }
.dm-meta { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; font-size: .78rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; color: #6B6B78; }
.dm-badge { padding: 3px 10px; border-radius: 999px; background: #FFE9E2; color: #C2410C; letter-spacing: .04em; }
.dm-head h2 { font-family: var(--font-display); font-weight: 600; font-size: clamp(1.5rem, 3vw, 2.2rem); letter-spacing: -.03em; margin: 4px 0; }
.dm-desc { color: #3A3A44; max-width: 640px; }
.dm-close { flex: none; width: 44px; height: 44px; border-radius: 50%; border: 0; background: #EEECE6; font-size: 1.1rem; cursor: pointer; transition: background .25s, transform .3s; }
.dm-close:hover { background: #121216; color: #fff; transform: rotate(90deg); }
.dm-stage { margin: 0 20px; border-radius: 20px; overflow: hidden; display: grid; place-items: center; padding: 24px; min-height: 420px; }
.dm-fit { position: relative; width: 100%; }
.dm-fit.wide { max-width: 900px; aspect-ratio: 900 / 560; }
.dm-fit.tall { width: auto; height: min(640px, calc(100vh - 340px)); aspect-ratio: 320 / 640; }
.dm-stage--nordic { background: linear-gradient(135deg, #E9EDF2, #F7F4EE); }
.dm-stage--byty { background: linear-gradient(135deg, #FEF3C7, #FDE68A); }
.dm-stage--fitflow { background: linear-gradient(135deg, #FFE4DC, #E0E7FF); }
.dm-foot { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; padding: 16px 28px 24px; font-weight: 700; color: #3A3A44; }
.dm-pulse { width: 10px; height: 10px; border-radius: 50%; background: #22C55E; animation: pulse 2s infinite; }
.dm-tags { display: flex; gap: 6px; flex-wrap: wrap; margin-left: auto; }
.dm-tags li { padding: 4px 10px; border-radius: 999px; background: #F6F5F1; border: 1px solid rgba(18, 18, 22, .08); font-size: .8rem; }
.dm-enter-active, .dm-leave-active { transition: opacity .35s; }
.dm-enter-active .dm, .dm-leave-active .dm { transition: transform .45s cubic-bezier(.2, .8, .2, 1); }
.dm-enter-from, .dm-leave-to { opacity: 0; }
.dm-enter-from .dm, .dm-leave-to .dm { transform: translateY(30px) scale(.96); }
@media (max-width: 720px) {
  .dm { border-radius: 22px; }
  .dm-head { padding: 18px 18px 10px; }
  .dm-stage { margin: 0 10px; padding: 12px; min-height: 0; }
  .dm-foot { padding: 14px 18px 18px; }
  .dm-tags { margin-left: 0; }
}
</style>
