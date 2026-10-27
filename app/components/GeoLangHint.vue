<script setup lang="ts">
// Подсказка «Похоже, вы из Украины — перейти на украинский?».
// Без автоматического редиректа: так поисковики индексируют все языковые версии.
const { all } = useSite()
const { locale } = useI18n()
const switchLocalePath = useSwitchLocalePath()
const { choice, remember } = useLangChoice()

const target = ref<string | null>(null)
const hint = computed(() => (target.value ? all[target.value]!.geoHint : null))

onMounted(async () => {
  if (choice.value) return
  try { if (sessionStorage.getItem('geo_hint_closed')) return } catch {}
  const lang = langForCountry(await getVisitorCountry())
  if (lang && lang !== locale.value) target.value = lang
})

function close() {
  target.value = null
  try { sessionStorage.setItem('geo_hint_closed', '1') } catch {}
}
function accept() {
  if (target.value) remember(target.value)
}
</script>

<template>
  <Transition name="toast">
    <div v-if="hint && target" class="geo-hint" role="dialog" :lang="target" aria-live="polite">
      <AppIcon name="pin" />
      <p>{{ hint.text }}</p>
      <NuxtLink class="btn btn-primary btn-sm" :to="switchLocalePath(target as 'sk')" @click="accept">{{ hint.action }}</NuxtLink>
      <button type="button" class="geo-close" :aria-label="hint.close" @click="close">×</button>
    </div>
  </Transition>
</template>

<style scoped>
.geo-hint {
  position: fixed; z-index: 90; left: 50%; bottom: 20px; transform: translateX(-50%);
  display: flex; align-items: center; gap: 12px; flex-wrap: wrap; justify-content: center;
  width: max-content; max-width: calc(100% - 32px); padding: 10px 10px 10px 18px; border-radius: 22px;
  background: rgba(255, 255, 255, .92); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
  border: 1px solid var(--line, rgba(0, 0, 0, .08)); box-shadow: 0 20px 60px -20px rgba(40, 30, 120, .35);
  font-weight: 700; font-size: .95rem; color: #121216;
}
.geo-hint .ico { color: #5B4BFF; }
.geo-close {
  width: 34px; height: 34px; border: 0; border-radius: 50%; background: #EEECE6; cursor: pointer; font-size: 1.2rem; line-height: 1;
}
.toast-enter-active, .toast-leave-active { transition: opacity .5s cubic-bezier(.2, .8, .2, 1), transform .5s cubic-bezier(.2, .8, .2, 1); }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translate(-50%, 24px); }
</style>
