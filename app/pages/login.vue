<script setup lang="ts">
// Team sign-in. No sign-up: accounts are created in the database (see backend/).
const { t, cfg } = useSite()
const { locale } = useI18n()
const localePath = useLocalePath()
const { user, refresh, login } = useTeam()

const p = computed(() => t.value.panel)
const form = reactive({ username: '', password: '' })
const busy = ref(false)
const error = ref('')
const shake = ref(0)

useSeoMeta({ title: () => `${p.value.loginTitle} | ${cfg.brand}`, description: () => p.value.loginText, robots: 'noindex, nofollow' })
useHead(() => ({ htmlAttrs: { lang: locale.value } }))

// Already signed in → straight to the panel
onMounted(async () => {
  if (user.value ?? (await refresh())) navigateTo(localePath('/panel'))
})

async function submit() {
  if (busy.value) return
  busy.value = true
  error.value = ''
  try {
    await login(form.username.trim(), form.password)
    await navigateTo(localePath('/panel'))
  } catch (e) {
    const s = httpStatus(e)
    error.value = s === 401 || s === 422 ? p.value.errorAuth : s === 429 ? p.value.errorLimit : p.value.errorServer
    form.password = ''
    shake.value++
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <main class="login">
    <div class="hero-bg" aria-hidden="true">
      <div class="grid-bg" />
      <div class="blob blob-1" />
      <div class="blob blob-2" />
      <div class="blob blob-3" />
    </div>

    <div class="login-top">
      <NuxtLink class="logo" :to="localePath('/')">
        <span class="logo-mark" aria-hidden="true">D</span>
        <span class="logo-text">{{ cfg.brand }}</span>
      </NuxtLink>
      <LangSwitch />
    </div>

    <form :key="shake" class="login-card" :class="{ shake: shake > 0 }" @submit.prevent="submit">
      <span class="login-icon" aria-hidden="true"><AppIcon name="user" /></span>
      <h1>{{ p.loginTitle }}</h1>
      <p class="login-text">{{ p.loginText }}</p>

      <label class="tp-field">
        <span>{{ p.username }}</span>
        <input v-model="form.username" name="username" autocomplete="username" autocapitalize="none" spellcheck="false" required maxlength="64">
      </label>
      <label class="tp-field">
        <span>{{ p.password }}</span>
        <input v-model="form.password" name="password" type="password" autocomplete="current-password" required maxlength="200">
      </label>

      <Transition name="login-err">
        <p v-if="error" class="login-error" role="alert">{{ error }}</p>
      </Transition>

      <button class="btn btn-primary btn-block" :disabled="busy">
        <span v-if="busy" class="spinner" aria-hidden="true" />
        {{ busy ? p.wait : p.submit }}
      </button>
      <NuxtLink class="login-back" :to="localePath('/')"><AppIcon name="back" /> {{ p.back }}</NuxtLink>
    </form>
  </main>
</template>

<style>
.login { position: relative; min-height: 100svh; display: grid; place-items: center; padding: 96px 16px 48px; overflow: hidden; isolation: isolate; }
.login-top { position: absolute; top: 20px; left: 0; right: 0; display: flex; justify-content: space-between; align-items: center; width: min(1200px, 100% - 32px); margin-inline: auto; }
.login-card {
  width: min(420px, 100%); padding: 36px 32px 28px; border-radius: var(--radius);
  background: rgba(255, 255, 255, .82); border: 1px solid var(--line);
  -webkit-backdrop-filter: blur(18px); backdrop-filter: blur(18px); box-shadow: var(--shadow-lg);
  animation: loginIn .8s var(--ease) both;
}
.login-card.shake { animation: loginShake .45s var(--ease); }
@keyframes loginIn { from { opacity: 0; transform: translateY(24px) scale(.98); } }
@keyframes loginShake { 20%, 60% { transform: translateX(-8px); } 40%, 80% { transform: translateX(8px); } }
.login-icon {
  display: grid; place-items: center; width: 52px; height: 52px; border-radius: 16px; color: #fff; margin-bottom: 18px;
  background: conic-gradient(from 200deg, var(--accent), var(--accent-2), var(--accent-3), var(--accent));
  animation: loginSpin 10s linear infinite;
}
.login-icon .ico { width: 24px; height: 24px; }
@keyframes loginSpin { 50% { filter: hue-rotate(40deg); } }
.login h1 { font-family: var(--font-display); font-weight: 600; font-size: 1.7rem; letter-spacing: -.03em; line-height: 1.15; }
.login-text { color: var(--muted); font-size: .95rem; margin: 8px 0 22px; }
.login-error { padding: 10px 14px; margin-bottom: 14px; border-radius: 12px; background: #FFF0EC; color: #B4381B; font-size: .9rem; font-weight: 600; }
.login-err-enter-active { transition: opacity .3s, transform .3s var(--ease); }
.login-err-enter-from { opacity: 0; transform: translateY(-6px); }
.login .btn { margin-top: 6px; }
.login .btn:disabled { opacity: .7; cursor: progress; }
.login-back { display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 18px; color: var(--muted); font-size: .9rem; font-weight: 600; transition: color .2s; }
.login-back:hover { color: var(--ink); }
</style>
