<script setup lang="ts">
// Team panel shell: sidebar menu, user, light/dark theme, alarm ringer. Client-only (routeRules).
import type { SyncNotice } from '~/composables/useTeam'

definePageMeta({ middleware: 'team' })

const { t, cfg } = useSite()
const { locale } = useI18n()
const localePath = useLocalePath()
const route = useRoute()
const { user, mentions, online, pending, synced, notices, logout, loadUsers, loadAlarms, loadMentions, loadEvents, startSync, flush } = useTeam()
const { ready, loadPrefs, pref } = usePrefs()

const p = computed(() => t.value.panel)
const nav = computed(() => [
  { to: localePath('/panel'), icon: 'tasks', label: p.value.nav.tasks },
  { to: localePath('/panel/calendar'), icon: 'calendar', label: p.value.nav.calendar },
  { to: localePath('/panel/alarms'), icon: 'alarm', label: p.value.nav.alarms },
  { to: localePath('/panel/expenses'), icon: 'wallet', label: p.value.nav.expenses },
  { to: localePath('/panel/income'), icon: 'income', label: p.value.nav.income },
  { to: localePath('/panel/settings'), icon: 'gear', label: p.value.nav.settings },
])
const current = computed(() => nav.value.find((n) => n.to === route.path)?.label ?? '')
// Phone tab bar: expenses + income share one "Finance" tab (switch inside the page)
const money = computed(() => [localePath('/panel/expenses'), localePath('/panel/income')])
const tabs = computed(() => [
  ...nav.value.slice(0, 3).map((n) => ({ ...n, active: route.path === n.to })),
  { to: money.value[0]!, icon: 'wallet', label: p.value.nav.finance, active: money.value.includes(route.path) },
])
const inTabs = (to: string) => tabs.value.some((n) => n.to === to) || money.value.includes(to)

useSeoMeta({ title: () => `${current.value} | ${cfg.brand}`, robots: 'noindex, nofollow' })
// Edge to edge on notched phones (safe areas are padded below)
useHead({ meta: [{ name: 'viewport', content: 'width=device-width, initial-scale=1, viewport-fit=cover' }] })

// Installed app: own manifest, worker, install button, update prompt
const { canInstall, standalone, ios, updateReady, register, install, update } = usePwa()
useHead(() => ({ link: [{ rel: 'manifest', href: `/panel.webmanifest?lang=${locale.value}`, key: 'manifest' }] }))
const iosHint = ref(false)
const showInstall = computed(() => !standalone.value && (canInstall.value || ios.value))
const installApp = () => (canInstall.value ? install() : (iosHint.value = !iosHint.value))
// The installed app opens /panel → this language (server/routes/panel.ts)
watch(locale, (l) => (document.cookie = `panel_lang=${l}; path=/; max-age=31536000; samesite=lax`), { immediate: import.meta.client })
onMounted(register)
// Theme (account setting): light | dark | system
const theme = pref<'light' | 'dark' | 'system'>('theme', 'system')
const systemDark = ref(false)
onMounted(() => {
  const mq = matchMedia('(prefers-color-scheme: dark)')
  systemDark.value = mq.matches
  mq.addEventListener('change', (e) => (systemDark.value = e.matches))
})
const dark = computed(() => (theme.value === 'system' ? systemDark.value : theme.value === 'dark'))
const toggleTheme = () => (theme.value = dark.value ? 'light' : 'dark')

useHead(() => ({
  htmlAttrs: { lang: locale.value, class: dark.value ? 'tp-dark' : '' },
  meta: [{ name: 'theme-color', content: dark.value ? '#0E0E13' : '#F6F5F1' }],
}))

// Badge with open mentions; refreshed every minute
let poll: ReturnType<typeof setInterval> | undefined
onMounted(() => {
  loadPrefs().catch(() => {})
  loadUsers().catch(() => {})
  loadAlarms().catch(() => {})
  loadMentions().catch(() => {})
  loadEvents().catch(() => {})
  // Mentions badge + events for reminders (changes from other devices)
  poll = setInterval(() => {
    loadMentions().catch(() => {})
    loadEvents().catch(() => {})
  }, 60000)
})
onBeforeUnmount(() => clearInterval(poll))

// Push notifications are timed and worded on the server: it needs this device's time zone and language
const tz = pref<string>('tz', '')
const pushLang = pref<string>('lang', '')
watch(ready, (ok) => {
  if (!ok) return
  const zone = Intl.DateTimeFormat().resolvedOptions().timeZone
  if (zone && tz.value !== zone) tz.value = zone
  if (pushLang.value !== locale.value) pushLang.value = locale.value
}, { immediate: true })
watch(locale, (l) => ready.value && (pushLang.value = l))
// Tap on a notification while the app is open: switch screens (pwa/sw.js)
onMounted(() => navigator.serviceWorker?.addEventListener('message', (e) => e.data?.type === 'open' && navigateTo(e.data.url)))

// Offline: status chip, sync of waiting changes, honest messages about conflicts
onMounted(startSync)
const justSynced = ref(false)
let syncedTimer: ReturnType<typeof setTimeout> | undefined
watch(synced, () => {
  loadAlarms().catch(() => {})
  loadEvents().catch(() => {})
  loadMentions().catch(() => {})
  justSynced.value = true
  clearTimeout(syncedTimer)
  syncedTimer = setTimeout(() => (justSynced.value = false), 4000)
})
const syncState = computed(() => (!online.value ? 'offline' : pending.value ? 'pending' : justSynced.value ? 'synced' : ''))
const syncText = computed(() =>
  syncState.value === 'offline' ? (pending.value ? `${p.value.sync.offline} · ${pending.value}` : p.value.sync.offline)
  : syncState.value === 'pending' ? `${p.value.sync.pending}: ${pending.value}` : p.value.sync.synced)
const noticeText = (n: SyncNotice) => `«${n.label || '…'}» — ${p.value.sync[n.kind]}`
watch(() => notices.value.length, (len, was) => {
  if (len > was) setTimeout(() => notices.value.shift(), 7000)
})

const outError = ref(false)
async function out() {
  // Pending offline changes would be lost
  if (pending.value && !confirm(`${p.value.sync.pending}: ${pending.value}. ${p.value.sync.logoutLoses}`)) return
  try {
    await logout()
    await navigateTo(localePath('/login'))
  } catch {
    outError.value = true
    setTimeout(() => (outError.value = false), 3500)
  }
}

const initial = (name = '') => name.trim().charAt(0).toUpperCase() || '?'

// Phone: bottom tab bar with the main sections; "More" opens the sidebar as a sheet
const sheet = ref(false)
const moreActive = computed(() => !inTabs(route.path))
watch(() => route.path, () => (sheet.value = false))
</script>

<template>
  <div class="tp" :class="{ dark }">
    <!-- Phone top bar -->
    <header class="tp-top">
      <NuxtLink class="logo" :to="localePath('/')" :aria-label="cfg.brand"><span class="logo-mark" aria-hidden="true">D</span></NuxtLink>
      <b class="tp-top-title">{{ current }}</b>
      <button v-if="syncState" type="button" class="tp-sync" :class="syncState" :title="p.sync.hint" @click="flush()"><i />{{ syncText }}</button>
      <span v-if="user" class="tp-avatar sm" :data-c="user.id % 3" :title="user.name || user.username">{{ initial(user.name || user.username) }}</span>
    </header>

    <aside class="tp-side" :class="{ open: sheet }">
      <NuxtLink class="logo" :to="localePath('/')">
        <span class="logo-mark" aria-hidden="true">D</span>
        <span class="logo-text">{{ cfg.brand }}</span>
      </NuxtLink>

      <nav class="tp-nav" :aria-label="p.menu">
        <NuxtLink v-for="n in nav" :key="n.to" :to="n.to" :class="{ active: route.path === n.to, 'in-tabs': inTabs(n.to) }">
          <AppIcon :name="n.icon" /><span>{{ n.label }}</span>
          <b v-if="n.icon === 'tasks' && mentions.length" class="tp-badge" :title="p.kanban.forMe">{{ mentions.length }}</b>
        </NuxtLink>
      </nav>

      <div class="tp-side-foot">
        <button v-if="syncState" type="button" class="tp-sync tp-sync-side" :class="syncState" :title="p.sync.hint" @click="flush()"><i />{{ syncText }}</button>
        <button v-if="showInstall" type="button" class="tp-install" :aria-expanded="ios && !canInstall ? iosHint : undefined" @click="installApp">
          <AppIcon name="download" />{{ p.app.install }}
        </button>
        <p v-if="iosHint" class="tp-ios-hint">{{ p.app.iosHint }}</p>
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
      <NuxtPage v-if="ready" />
      <div v-else class="kb-loading"><span class="spinner" /></div>
    </main>

    <!-- Phone tab bar -->
    <nav class="tp-tabbar" :aria-label="p.menu">
      <NuxtLink v-for="n in tabs" :key="n.to" :to="n.to" class="tp-tab" :class="{ active: n.active }">
        <AppIcon :name="n.icon" /><span>{{ n.label }}</span>
        <b v-if="n.icon === 'tasks' && mentions.length" class="tp-badge">{{ mentions.length }}</b>
      </NuxtLink>
      <button type="button" class="tp-tab" :class="{ active: sheet || moreActive }" :aria-expanded="sheet" @click="sheet = !sheet">
        <AppIcon :name="sheet ? 'close' : 'more'" /><span>{{ p.more }}</span>
      </button>
    </nav>
    <Transition name="toast-fade"><div v-if="sheet" class="tp-scrim" @click="sheet = false" /></Transition>

    <!-- Sync messages: offline change overwritten / not applied -->
    <TransitionGroup tag="div" name="toast-fade" class="tp-notices" role="status">
      <p v-for="n in notices" :key="n.id" class="tp-notice" :class="n.kind" @click="notices.splice(notices.indexOf(n), 1)">{{ noticeText(n) }}</p>
      <p v-if="outError" key="out" class="tp-notice rejected">{{ p.sync.logoutOffline }}</p>
    </TransitionGroup>

    <!-- New deploy: the waiting worker takes over after the click -->
    <Transition name="toast">
      <div v-if="updateReady" class="tp-update" role="status">
        <AppIcon name="spark" /><span>{{ p.app.updateText }}</span>
        <button type="button" class="btn btn-primary btn-sm" @click="update">{{ p.app.update }}</button>
      </div>
    </Transition>

    <TeamAlarmRinger />
  </div>
</template>

<style>
/* ===== Team panel shell ===== */
.tp { min-height: 100vh; min-height: 100dvh; display: grid; grid-template-columns: 250px minmax(0, 1fr); background: var(--bg); }
.tp-side {
  position: sticky; top: 0; height: 100vh; height: 100dvh; display: flex; flex-direction: column; gap: 28px; padding: 22px 16px;
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

/* Offline / sync status */
.tp-sync {
  display: inline-flex; align-items: center; gap: 7px; min-height: 32px; padding: 0 12px; border-radius: 999px; cursor: pointer; white-space: nowrap;
  border: 1px solid var(--line-2); background: var(--surface); color: var(--ink-2); font-weight: 800; font-size: .78rem;
}
.tp-sync i { width: 8px; height: 8px; border-radius: 50%; background: #19C3A6; }
.tp-sync.offline i { background: #9CA3AF; }
.tp-sync.pending i { background: #F59E0B; animation: tpPulse 1.6s ease-in-out infinite; }
@keyframes tpPulse { 50% { box-shadow: 0 0 0 4px rgba(245, 158, 11, .25); } }
.tp-sync.offline { color: var(--muted); }
.tp-sync-side { justify-content: center; min-height: 40px; }
.tp-notices { position: fixed; left: 50%; bottom: 24px; z-index: 305; transform: translateX(-50%); display: grid; gap: 8px; width: min(440px, calc(100vw - 24px)); }
.tp-notice {
  padding: 12px 16px; border-radius: 16px; background: var(--surface); border: 1px solid var(--line-2); border-left: 4px solid #F59E0B;
  box-shadow: var(--shadow-lg); font-weight: 700; font-size: .88rem; cursor: pointer;
}
.tp-notice.discarded, .tp-notice.rejected { border-left-color: #E5484D; }

/* Installed app */
.tp-install {
  display: flex; align-items: center; justify-content: center; gap: 8px; min-height: 44px; padding: 10px 14px; border-radius: 14px; cursor: pointer;
  border: 1px dashed var(--accent); background: rgba(91, 75, 255, .06); color: var(--accent); font-weight: 800; font-size: .9rem;
}
.tp-install .ico { width: 17px; height: 17px; }
.tp-install:hover { background: rgba(91, 75, 255, .12); }
.tp-ios-hint { margin-top: -6px; padding: 10px 12px; border-radius: 12px; background: var(--bg-2); color: var(--ink-2); font-size: .82rem; font-weight: 600; line-height: 1.45; }
.tp-update {
  position: fixed; left: 50%; top: calc(14px + env(safe-area-inset-top)); z-index: 310; transform: translateX(-50%);
  display: flex; align-items: center; gap: 10px; width: max-content; max-width: calc(100vw - 24px); padding: 8px 8px 8px 16px;
  border-radius: 999px; background: var(--surface); border: 1px solid var(--line-2); box-shadow: var(--shadow-lg); font-weight: 700; font-size: .9rem;
}
.tp-update > .ico { width: 18px; height: 18px; color: var(--accent); }
.tp-update .btn { min-height: 40px; }

/* Phone-only parts */
.tp-top, .tp-tabbar, .tp-scrim { display: none; }

@media (max-width: 860px) {
  .tp { grid-template-columns: minmax(0, 1fr); }
  .tp-top {
    position: sticky; top: 0; z-index: 40; display: flex; align-items: center; gap: 12px;
    padding: calc(10px + env(safe-area-inset-top)) 16px 10px; border-bottom: 1px solid var(--line);
    background: color-mix(in srgb, var(--bg) 82%, transparent); -webkit-backdrop-filter: blur(14px); backdrop-filter: blur(14px);
  }
  .tp-top .logo-mark { width: 32px; height: 32px; }
  .tp-top-title { flex: 1; min-width: 0; font-family: var(--font-display); font-weight: 600; font-size: 1.05rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

  /* Sidebar becomes a sheet above the tab bar */
  .tp-side {
    position: fixed; left: 10px; right: 10px; top: auto; bottom: calc(76px + env(safe-area-inset-bottom)); z-index: 60;
    height: auto; gap: 14px; padding: 14px; border: 1px solid var(--line); border-radius: 24px;
    background: var(--surface); box-shadow: var(--shadow-lg);
    opacity: 0; visibility: hidden; transform: translateY(16px) scale(.98); transform-origin: bottom center;
    transition: opacity .25s, transform .35s var(--ease), visibility .25s;
  }
  .tp-side.open { opacity: 1; visibility: visible; transform: none; }
  .tp-side .logo { display: none; }
  .tp-nav { grid-template-columns: 1fr 1fr; }
  .tp-nav a { padding: 12px; }
  .tp-nav a.in-tabs { display: none; }
  .tp-side-actions .tp-icon-btn { width: 44px; height: 44px; }
  .tp-side-foot { margin-top: 0; }
  .tp.dark .tp-side { background: var(--surface); }

  .tp-tabbar {
    position: fixed; left: 0; right: 0; bottom: 0; z-index: 70; display: flex; gap: 2px;
    padding: 6px 6px calc(6px + env(safe-area-inset-bottom)); border-top: 1px solid var(--line);
    background: color-mix(in srgb, var(--surface) 90%, transparent); -webkit-backdrop-filter: blur(16px); backdrop-filter: blur(16px);
  }
  .tp-tab {
    position: relative; flex: 1; min-width: 0; display: grid; justify-items: center; gap: 3px; padding: 7px 2px 5px; border: 0; border-radius: 14px;
    background: none; cursor: pointer; color: var(--muted); font-family: inherit; font-size: .66rem; font-weight: 700; line-height: 1.1;
    transition: color .2s, background .2s; -webkit-tap-highlight-color: transparent;
  }
  .tp-tab span { max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .tp-tab .ico { width: 22px; height: 22px; transition: transform .3s var(--ease); }
  .tp-tab.active { color: var(--accent); background: rgba(91, 75, 255, .09); }
  .tp-tab.active .ico { transform: translateY(-1px) scale(1.06); }
  .tp-tab .tp-badge { position: absolute; top: 2px; left: calc(50% + 6px); margin: 0; min-width: 17px; height: 17px; font-size: .62rem; padding: 0 4px; }
  .tp-scrim { display: block; position: fixed; inset: 0; z-index: 55; background: rgba(18, 18, 22, .32); }

  .tp-main { padding: 18px max(16px, env(safe-area-inset-right)) calc(96px + env(safe-area-inset-bottom)) max(16px, env(safe-area-inset-left)); }
  .tp-head { margin-bottom: 18px; }
  .tp-toast { bottom: calc(88px + env(safe-area-inset-bottom)); max-width: calc(100vw - 32px); text-align: center; }
  .tp-notices { bottom: calc(88px + env(safe-area-inset-bottom)); }
  .tp-sync-side { display: none; }
  /* iOS zooms into fields with text under 16px */
  .tp-input { font-size: 16px; }
  .tp .kb-title-input { font-size: 1.1rem; }
}
/* Touch: at least 44 px hit areas without changing the look */
@media (pointer: coarse) {
  .tp-icon-btn.sm, .al-switch { position: relative; }
  .tp-icon-btn.sm::after, .al-switch::after { content: ''; position: absolute; inset: -7px; }
}
.toast-fade-enter-active, .toast-fade-leave-active { transition: opacity .25s; }
.toast-fade-enter-from, .toast-fade-leave-to { opacity: 0; }

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
