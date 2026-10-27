<script setup lang="ts">
const { t, cfg } = useSite()
const localePath = useLocalePath()
const route = useRoute()
// На главной — якоря (#about), на остальных страницах — ссылки на разделы главной (/sk#about)
const anchor = (id: string) => (route.path === localePath('/') ? `#${id}` : `${localePath('/')}#${id}`)

const navItems = ['about', 'ai', 'work', 'lab', 'faq'] as const
const open = ref(false)
const scrolled = ref(false)
const progress = ref(0)
const active = ref('')

let sectionIO: IntersectionObserver | undefined
let raf = 0

function onScroll() {
  cancelAnimationFrame(raf)
  raf = requestAnimationFrame(() => {
    const max = document.documentElement.scrollHeight - innerHeight
    scrolled.value = scrollY > 20
    progress.value = max > 0 ? scrollY / max : 0
  })
}
const onKey = (e: KeyboardEvent) => e.key === 'Escape' && (open.value = false)

onMounted(() => {
  addEventListener('scroll', onScroll, { passive: true })
  addEventListener('keydown', onKey)
  onScroll()
  sectionIO = new IntersectionObserver(
    (entries) => entries.forEach((e) => e.isIntersecting && (active.value = e.target.id)),
    { rootMargin: '-45% 0px -50% 0px' }
  )
  document.querySelectorAll('main section[id]').forEach((s) => sectionIO!.observe(s))
})
onBeforeUnmount(() => {
  removeEventListener('scroll', onScroll)
  removeEventListener('keydown', onKey)
  sectionIO?.disconnect()
})
</script>

<template>
  <div class="progress" aria-hidden="true" :style="{ '--p': progress }" />
  <header class="site-header" :class="{ 'is-scrolled': scrolled }">
    <div class="container nav-wrap">
      <NuxtLink class="logo" :to="localePath('/')" :aria-label="cfg.brand">
        <span class="logo-mark" aria-hidden="true">D</span>
        <span class="logo-text">{{ cfg.brand }}</span>
      </NuxtLink>

      <nav class="nav-links" aria-label="Main">
        <a v-for="k in navItems" :key="k" :href="anchor(k)" :class="{ active: active === k }">{{ t.nav[k] }}</a>
      </nav>

      <div class="nav-right">
        <LangSwitch />
        <a v-magnetic class="btn btn-primary btn-sm hide-sm" :href="anchor('contact')">{{ t.nav.cta }}</a>
        <button
          class="menu-toggle"
          :aria-expanded="open"
          aria-controls="mobile-menu"
          :aria-label="t.nav.menu"
          @click="open = !open"
        >
          <span /><span />
        </button>
      </div>
    </div>

    <div v-show="open" id="mobile-menu" class="mobile-menu">
      <nav class="container" aria-label="Mobile">
        <a v-for="k in navItems" :key="k" :href="anchor(k)" @click="open = false">{{ t.nav[k] }}</a>
        <a :href="anchor('contact')" @click="open = false">{{ t.nav.contact }}</a>
      </nav>
    </div>
  </header>
</template>
