<script setup lang="ts">
// Team panel shell: sidebar menu, user, alarm ringer. Client-only (routeRules).
definePageMeta({ middleware: 'team' })

const { t, cfg } = useSite()
const { locale } = useI18n()
const localePath = useLocalePath()
const route = useRoute()
const { user, mentions, logout, loadUsers, loadAlarms, loadMentions } = useTeam()

const p = computed(() => t.value.panel)
const nav = computed(() => [
  { to: localePath('/panel'), icon: 'tasks', label: p.value.nav.tasks },
  { to: localePath('/panel/alarms'), icon: 'alarm', label: p.value.nav.alarms },
  { to: localePath('/panel/expenses'), icon: 'wallet', label: p.value.nav.expenses },
  { to: localePath('/panel/income'), icon: 'income', label: p.value.nav.income },
])
const current = computed(() => nav.value.find((n) => n.to === route.path)?.label ?? '')

useSeoMeta({ title: () => `${current.value} | ${cfg.brand}`, robots: 'noindex, nofollow' })
useHead(() => ({ htmlAttrs: { lang: locale.value } }))

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
  <div class="tp">
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
.tp-side-actions { display: flex; justify-content: space-between; align-items: center; }
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
</style>
