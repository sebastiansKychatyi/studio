<script setup lang="ts">
// Team panel shell: sidebar menu, user, light/dark theme, alarm ringer. Client-only (routeRules).
definePageMeta({ middleware: 'team' })

const { t, cfg } = useSite()
const { locale } = useI18n()
const localePath = useLocalePath()
const route = useRoute()
const { user, mentions, logout, loadUsers, loadAlarms, loadMentions } = useTeam()

const p = computed(() => t.value.panel)
const nav = computed(() => [
  { to: localePath('/panel'), icon: 'tasks', label: p.value.nav.tasks },
  { to: localePath('/panel/calendar'), icon: 'calendar', label: p.value.nav.calendar },
  { to: localePath('/panel/alarms'), icon: 'alarm', label: p.value.nav.alarms },
  { to: localePath('/panel/expenses'), icon: 'wallet', label: p.value.nav.expenses },
  { to: localePath('/panel/income'), icon: 'income', label: p.value.nav.income },
])
const current = computed(() => nav.value.find((n) => n.to === route.path)?.label ?? '')

useSeoMeta({ title: () => `${current.value} | ${cfg.brand}`, robots: 'noindex, nofollow' })
// Theme: saved choice, else the system setting
const THEME = 'team-theme'
const dark = ref(false)
onMounted(() => {
  let saved: string | null = null
  try { saved = localStorage.getItem(THEME) } catch { /* private mode */ }
  dark.value = saved ? saved === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches
})
function toggleTheme() {
  dark.value = !dark.value
  try { localStorage.setItem(THEME, dark.value ? 'dark' : 'light') } catch { /* private mode */ }
}

useHead(() => ({ htmlAttrs: { lang: locale.value, class: dark.value ? 'tp-dark' : '' } }))

// Badge with open mentions; refreshed every minute
let poll: ReturnType<typeof setInterval> | undefined
onMounted(() => {
  loadUsers().catch(() => {})
  loadAlarms().catch(() => {})
  loadMentions().catch(() => {})
  poll = setInterval(() => document.visibilityState === 'visible' && loadMentions().catch(() => {}), 60000)
})
onBeforeUnmount(() => clearInterval(poll))

async function out() {
  await logout()
  await navigateTo(localePath('/login'))
}

const initial = (name = '') => name.trim().charAt(0).toUpperCase() || '?'
</script>

<template>
  <div class="tp" :class="{ dark }">
    <aside class="tp-side">
      <NuxtLink class="logo" :to="localePath('/')">
        <span class="logo-mark" aria-hidden="true">D</span>
        <span class="logo-text">{{ cfg.brand }}</span>
      </NuxtLink>

      <nav class="tp-nav" :aria-label="p.menu">
        <NuxtLink v-for="n in nav" :key="n.to" :to="n.to" :class="{ active: route.path === n.to }">
          <AppIcon :name="n.icon" /><span>{{ n.label }}</span>
          <b v-if="n.icon === 'tasks' && mentions.length" class="tp-badge" :title="p.kanban.forMe">{{ mentions.length }}</b>
        </NuxtLink>
      </nav>

      <div class="tp-side-foot">
        <div v-if="user" class="tp-me">
          <span class="tp-avatar" :data-c="user.id % 3">{{ initial(user.name || user.username) }}</span>
          <span class="tp-me-name"><b>{{ user.name || user.username }}</b><small>@{{ user.username }}</small></span>
        </div>
        <div class="tp-side-actions">
          <LangSwitch up />
          <button
            type="button"
            class="tp-icon-btn tp-theme"
            :title="dark ? p.themeLight : p.themeDark"
            :aria-label="dark ? p.themeLight : p.themeDark"
            :aria-pressed="dark"
            @click="toggleTheme"
          >
            <Transition name="tp-spin" mode="out-in"><AppIcon :key="String(dark)" :name="dark ? 'sun' : 'moon'" /></Transition>
          </button>
          <button type="button" class="tp-icon-btn" :title="p.logout" :aria-label="p.logout" @click="out"><AppIcon name="logout" /></button>
        </div>
      </div>
    </aside>

    <main class="tp-main">
      <NuxtPage />
    </main>

    <TeamAlarmRinger />
  </div>
</template>

<style>
/* ===== Team panel shell ===== */
.tp { min-height: 100svh; display: grid; grid-template-columns: 250px minmax(0, 1fr); background: var(--bg); }
.tp-side {
  position: sticky; top: 0; height: 100svh; display: flex; flex-direction: column; gap: 28px; padding: 22px 16px;
  background: rgba(255, 255, 255, .7); border-right: 1px solid var(--line);
}
.tp-side .logo { padding: 4px 8px; }
.tp-nav { display: grid; gap: 4px; }
.tp-nav a {
  position: relative; display: flex; align-items: center; gap: 12px; padding: 11px 14px; border-radius: 14px;
  color: var(--ink-2); font-weight: 700; font-size: .95rem; transition: background .25s, color .25s;
}
.tp-nav a:hover { background: var(--bg-2); color: var(--ink); }
.tp-nav a.active { background: var(--ink); color: #fff; box-shadow: 0 10px 24px -12px rgba(18, 18, 22, .6); }
.tp-nav a.active .ico { color: #B9B1FF; }
.tp-badge {
  margin-left: auto; min-width: 20px; height: 20px; padding: 0 6px; border-radius: 999px; display: grid; place-items: center;
  background: var(--accent); color: #fff; font-size: .72rem; font-weight: 800; animation: tpUp .4s var(--ease) both;
}
.tp-side-foot { margin-top: auto; display: grid; gap: 14px; }
.tp-me { display: flex; align-items: center; gap: 10px; padding: 10px; border-radius: 16px; background: var(--surface); border: 1px solid var(--line); }
.tp-me-name { display: grid; line-height: 1.25; min-width: 0; }
.tp-me-name b { font-size: .92rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.tp-me-name small { color: var(--muted); font-size: .78rem; }
.tp-side-actions { display: flex; align-items: center; gap: 6px; }
.tp-side-actions .lang-dd { margin-right: auto; }
.tp-spin-enter-active, .tp-spin-leave-active { transition: opacity .2s, transform .3s var(--ease); }
.tp-spin-enter-from { opacity: 0; transform: rotate(-90deg) scale(.6); }
.tp-spin-leave-to { opacity: 0; transform: rotate(90deg) scale(.6); }
/* Sidebar sits at the left edge: open the language menu to the right */
.tp-side-actions .lang-dd-menu { right: auto; left: 0; transform-origin: bottom left; }

.tp-avatar {
  flex: none; display: grid; place-items: center; width: 34px; height: 34px; border-radius: 50%;
  color: #fff; font-weight: 800; font-size: .85rem; background: var(--accent);
}
.tp-avatar[data-c="1"] { background: var(--accent-2); }
.tp-avatar[data-c="2"] { background: var(--accent-3); }
.tp-avatar.sm { width: 24px; height: 24px; font-size: .68rem; }

.tp-icon-btn {
  display: inline-grid; place-items: center; width: 38px; height: 38px; border-radius: 50%; border: 0; cursor: pointer;
  background: var(--bg-2); color: var(--ink-2); transition: background .2s, color .2s, transform .3s var(--ease);
}
.tp-icon-btn:hover { background: var(--ink); color: #fff; }
.tp-icon-btn.danger:hover, .tp-icon-btn.confirm { background: #E5484D; color: #fff; }
.tp-icon-btn.sm { width: 30px; height: 30px; }
.tp-icon-btn .ico { width: 17px; height: 17px; }

.tp-main { min-width: 0; padding: 32px clamp(16px, 3vw, 40px) 48px; }
.tp-head { display: flex; flex-wrap: wrap; align-items: flex-end; justify-content: space-between; gap: 16px; margin-bottom: 24px; animation: tpUp .7s var(--ease) both; }
.tp-head h1 { font-family: var(--font-display); font-weight: 600; font-size: clamp(1.6rem, 3vw, 2.2rem); letter-spacing: -.03em; line-height: 1.1; }
.tp-head p { color: var(--muted); margin-top: 6px; }
.tp-toast {
  position: fixed; left: 50%; bottom: 24px; z-index: 300; transform: translateX(-50%);
  padding: 12px 20px; border-radius: 999px; background: var(--ink); color: #fff; font-weight: 700; font-size: .9rem; box-shadow: var(--shadow-lg);
}
.toast-enter-active, .toast-leave-active { transition: opacity .3s, transform .3s var(--ease); }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translate(-50%, 12px); }

.tp-input {
  padding: 10px 14px; border-radius: 12px; border: 1px solid var(--line-2); background: #fff; font-size: .95rem; font-weight: 600; min-width: 0;
  transition: border-color .2s, box-shadow .2s;
}
.tp-input:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 4px rgba(91, 75, 255, .14); }

@media (max-width: 860px) {
  .tp { grid-template-columns: 1fr; }
  .tp-side {
    position: sticky; z-index: 40; height: auto; flex-direction: row; align-items: center; gap: 10px; padding: 10px 16px;
    border-right: 0; border-bottom: 1px solid var(--line); -webkit-backdrop-filter: blur(14px); backdrop-filter: blur(14px);
  }
  .tp-side .logo-text, .tp-nav span, .tp-me-name { display: none; }
  .tp-nav { display: flex; gap: 4px; }
  .tp-nav a { padding: 10px 12px; }
  .tp-side-foot { margin: 0 0 0 auto; display: flex; align-items: center; gap: 8px; }
  .tp-me { padding: 0; border: 0; background: none; }
  .tp-side-actions { gap: 8px; }
  /* Top bar: open downwards, aligned right */
  .tp-side-actions .lang-dd.up .lang-dd-menu { top: calc(100% + 8px); bottom: auto; left: auto; right: 0; transform-origin: top right; }
  .tp-main { padding-top: 22px; }
}

/* ===== Dark theme (panel only) ===== */
html.tp-dark { background: #0E0E13; color-scheme: dark; }
.tp { transition: background .35s, color .35s; }
.tp.dark {
  --bg: #0E0E13;
  --bg-2: #1C1C25;
  --surface: #16161E;
  --field: #1E1E28;
  --solid: #2C2B3B;
  --ink: #EDEDF2;
  --ink-2: #C4C4CF;
  --muted: #8A8A9A;
  --line: rgba(255, 255, 255, .07);
  --line-2: rgba(255, 255, 255, .13);
  --shadow: 0 1px 2px rgba(0, 0, 0, .3), 0 12px 40px -12px rgba(0, 0, 0, .55);
  --shadow-lg: 0 2px 4px rgba(0, 0, 0, .3), 0 30px 80px -20px rgba(0, 0, 0, .7);
  color: var(--ink); color-scheme: dark;
}
.tp.dark .tp-side { background: rgba(22, 22, 30, .85); }
/* Solid dark elements stay dark (ink is light here) */
.tp.dark .tp-nav a.active, .tp.dark .tp-toast, .tp.dark .kb-tab.active, .tp.dark .kb-lock.on, .tp.dark .ex-seg button.on,
.tp.dark .ex-stat-main, .tp.dark .rc-pay, .tp.dark .tp-icon-btn:hover, .tp.dark .kb-col-actions .tp-icon-btn:hover:not(:disabled) {
  background: var(--solid); border-color: var(--solid); color: #fff;
}
.tp.dark .tp-nav a.active { box-shadow: inset 0 0 0 1px rgba(139, 127, 255, .35); }
.tp.dark .ex-stat-main { border-color: rgba(255, 255, 255, .08); }
.tp.dark .btn-primary { background: var(--accent); color: #fff; box-shadow: 0 10px 30px -10px rgba(91, 75, 255, .6); }
.tp.dark .btn-primary:hover { background: #7466FF; }
.tp.dark .rc-pay:hover, .tp.dark .tp-icon-btn.danger:hover, .tp.dark .tp-icon-btn.confirm { color: #fff; }
.tp.dark .rc-pay:hover { background: var(--accent); }
.tp.dark .tp-icon-btn.danger:hover, .tp.dark .tp-icon-btn.confirm { background: #E5484D; }
/* Fields, chips, menus: white → field */
.tp.dark .tp-input, .tp.dark .tp-field input, .tp.dark .tp-field textarea, .tp.dark .tp-field select,
.tp.dark .al-day, .tp.dark .tm-chip, .tp.dark .tm-vis button, .tp.dark .ex-cat, .tp.dark .lang-dd-menu, .tp.dark .rc-ask .ex-amount input {
  background: var(--field); color: var(--ink); border-color: var(--line-2);
}
.tp.dark .ex-cat.on { background: var(--c); border-color: var(--c); color: #fff; }
.tp.dark .al-day.on { background: var(--accent); border-color: var(--accent); color: #fff; }
.tp.dark .ev-days .al-day.on { background: var(--c); border-color: var(--c); }
.tp.dark .tm-vis button.on { background: rgba(91, 75, 255, .18); }
.tp.dark .lang-dd-btn:hover, .tp.dark .lang-dd.open .lang-dd-btn { background: var(--field); box-shadow: 0 0 0 1px var(--line-2); }
.tp.dark .lang-dd-menu { border-color: var(--line-2); box-shadow: 0 18px 40px -16px rgba(0, 0, 0, .7); }
.tp.dark .lang-dd-menu a { color: var(--ink-2); }
.tp.dark .lang-dd-menu a:hover, .tp.dark .lang-dd-menu a:focus-visible { background: var(--bg-2); color: var(--ink); }
.tp.dark .lang-dd-menu a.active { color: var(--ink); }
.tp.dark .lang-dd-menu b { color: var(--muted); }
.tp.dark .lang-dd-menu i { color: #B9B1FF; }
.tp.dark .tm-overlay { background: rgba(0, 0, 0, .55); }
/* Light tints → dark tints */
.tp.dark .kb-col.over { background: rgba(91, 75, 255, .14); }
.tp.dark .kb-at { background: rgba(139, 127, 255, .18); color: #B9B1FF; }
.tp.dark .kb-at.me { background: var(--accent); color: #fff; }
.tp.dark .kb-empty-icon { background: rgba(91, 75, 255, .18); }
.tp.dark .kb-due.soon, .tp.dark .cal-due-chip { background: rgba(245, 158, 11, .16); color: #FBBF5A; }
.tp.dark .kb-due.today { background: rgba(249, 115, 22, .18); color: #FDA668; }
.tp.dark .cal-due-chip.late { background: #E5484D; color: #fff; }
.tp.dark .cal-due-chip.done { background: var(--bg-2); color: var(--muted); }
.tp.dark .rc-item.late { background: rgba(229, 72, 77, .1); }
.tp.dark .ex-col:hover .ex-col-bar { background: rgba(139, 127, 255, .35); }
.tp.dark .ex-dot { background: color-mix(in srgb, var(--c) 20%, var(--surface)); }
.tp.dark .cal-ev { background: color-mix(in srgb, var(--c) 24%, var(--surface)); }
.tp.dark .cal-ev small { color: color-mix(in srgb, var(--c) 65%, #fff); }
.tp.dark .cal-pill { background: color-mix(in srgb, var(--c) 18%, var(--surface)); }
.tp.dark .cal-pill:hover { background: color-mix(in srgb, var(--c) 30%, var(--surface)); }
.tp.dark .cal-col { background-image: linear-gradient(var(--line) 1px, transparent 1px), linear-gradient(rgba(255, 255, 255, .025) 1px, transparent 1px); }
.tp.dark .cal-col.today { background-color: rgba(91, 75, 255, .07); }
.tp.dark .ex-catform-colors button { border-color: var(--surface); }
.tp.dark .al-switch i { background: #EDEDF2; }
.tp.dark .ex-row-amount.ex-plus, .tp.dark .ex-stat-value.pos, .tp.dark .rc-done small { color: #3FD9BC; }
.tp.dark .kb-ghost { background: rgba(91, 75, 255, .1); }
</style>
