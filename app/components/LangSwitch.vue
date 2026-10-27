<script setup lang="ts">
// Language dropdown.
// `up` opens the menu upwards (footer, bottom bars).
defineProps<{ up?: boolean }>()

const { cfg, all } = useSite()
const { locale } = useI18n()
const route = useRoute()
const localePath = useLocalePath()
const { remember } = useLangChoice()

const open = ref(false)
const root = ref<HTMLElement>()

// Same page in another language (no #hash to keep SSR and client in sync)
const rest = computed(() => route.path.replace(/^\/[a-z]{2}(?=\/|$)/, '') || '/')
const target = (l: (typeof cfg.languages)[number]) => localePath(rest.value, l)

function choose(l: string) {
  remember(l)
  open.value = false
}
const onDoc = (e: MouseEvent) => {
  if (open.value && root.value && !root.value.contains(e.target as Node)) open.value = false
}
const onKey = (e: KeyboardEvent) => e.key === 'Escape' && (open.value = false)
onMounted(() => {
  document.addEventListener('click', onDoc)
  addEventListener('keydown', onKey)
})
onBeforeUnmount(() => {
  document.removeEventListener('click', onDoc)
  removeEventListener('keydown', onKey)
})
watch(() => route.fullPath, () => (open.value = false))
</script>

<template>
  <div ref="root" class="lang-dd" :class="{ open, up }">
    <button
      type="button"
      class="lang-dd-btn"
      :aria-expanded="open"
      aria-haspopup="true"
      :aria-label="`Language: ${all[locale]!.label}`"
      @click="open = !open"
    >
      <AppIcon name="globe" />
      <span>{{ all[locale]!.short }}</span>
      <svg class="lang-dd-chev" viewBox="0 0 12 12" aria-hidden="true"><path d="M3 4.5 6 7.5 9 4.5" /></svg>
    </button>
    <!-- Links stay in the DOM for crawlers; menu is only hidden -->
    <ul class="lang-dd-menu" role="menu" :aria-hidden="!open">
      <li v-for="l in cfg.languages" :key="l" role="none">
        <NuxtLink
          role="menuitem"
          :to="target(l)"
          :hreflang="l"
          :lang="l"
          :tabindex="open ? 0 : -1"
          :class="{ active: l === locale }"
          :aria-current="l === locale ? 'true' : undefined"
          @click="choose(l)"
        >
          <b>{{ all[l]!.short }}</b>
          <span>{{ all[l]!.label }}</span>
          <i v-if="l === locale" aria-hidden="true">✓</i>
        </NuxtLink>
      </li>
    </ul>
  </div>
</template>

<style>
.lang-dd { position: relative; font-family: 'Manrope', system-ui, sans-serif; }
.lang-dd-btn {
  display: inline-flex; align-items: center; gap: 6px; height: 38px; padding: 0 10px 0 11px; border: 0; border-radius: 999px;
  background: var(--bg-2, #EEECE6); color: var(--ink, #121216); font-family: inherit; font-size: .78rem; font-weight: 800; line-height: 1; letter-spacing: .04em; cursor: pointer;
  transition: background .25s, box-shadow .25s;
}
.lang-dd-btn:hover, .lang-dd.open .lang-dd-btn { background: #fff; box-shadow: 0 0 0 1px rgba(18, 18, 22, .12); }
.lang-dd-btn .ico { width: 15px; height: 15px; opacity: .75; }
.lang-dd-chev { width: 12px; height: 12px; fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; transition: transform .3s cubic-bezier(.2, .8, .2, 1); }
.lang-dd.open .lang-dd-chev { transform: rotate(180deg); }
.lang-dd-menu {
  position: absolute; right: 0; top: calc(100% + 8px); z-index: 120; min-width: 190px; padding: 6px; margin: 0; list-style: none;
  border-radius: 16px; background: #fff; border: 1px solid rgba(18, 18, 22, .1); box-shadow: 0 18px 40px -16px rgba(18, 18, 22, .35);
  opacity: 0; visibility: hidden; transform: translateY(-6px) scale(.98); transform-origin: top right;
  transition: opacity .2s, transform .25s cubic-bezier(.2, .8, .2, 1), visibility .2s;
}
.lang-dd.up .lang-dd-menu { top: auto; bottom: calc(100% + 8px); transform: translateY(6px) scale(.98); transform-origin: bottom right; }
.lang-dd.open .lang-dd-menu { opacity: 1; visibility: visible; transform: none; }
.lang-dd-menu a {
  display: grid; grid-template-columns: 30px 1fr auto; align-items: center; gap: 6px; padding: 9px 10px; border-radius: 10px;
  color: #3A3A44; font-size: .9rem; font-weight: 600; text-decoration: none; transition: background .2s, color .2s;
}
.lang-dd-menu a:hover, .lang-dd-menu a:focus-visible { background: #F6F5F1; color: #121216; outline: none; }
.lang-dd-menu a.active { color: #121216; }
.lang-dd-menu b { font-size: .72rem; letter-spacing: .06em; color: #6B6B78; }
.lang-dd-menu i { font-style: normal; color: #5B4BFF; font-weight: 800; }
</style>
