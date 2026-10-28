<script setup lang="ts">
import {
  BOOKING_STATUS,
  BRAND_NAME,
  DEVICE,
  PAYMENT_CONFIRM_DELAY_MS,
  RESTAURANTS,
  ROLE,
  ROLE_AVATAR,
  ROLE_NAV_LABEL,
  RV_DEVICES,
  RV_ROLES,
  RV_THEMES,
  SEED_BOOKINGS,
  SEED_USERS,
  THEME,
  type Booking,
  type BookingStatus,
  type RvDeviceId,
  type RvRoleId,
  type RvThemeId,
} from '~~/data/reservations'

defineProps<{ preview?: boolean }>()

const themeId = ref<RvThemeId>(THEME.dark)
const deviceId = ref<RvDeviceId>(DEVICE.desktop)
const roleId = ref<RvRoleId>(ROLE.customer)
const bookings = ref(SEED_BOOKINGS.map((b) => ({ ...b })))
const users = ref(SEED_USERS.map((u) => ({ ...u })))
const restaurants = ref(RESTAURANTS.map((r) => ({ ...r })))
const settleTimers = new Set<ReturnType<typeof setTimeout>>()

const themeIcon = computed(() => (themeId.value === THEME.dark ? '☀' : '☾'))
const navLabels = computed(() => (roleId.value === ROLE.customer ? [ROLE_NAV_LABEL[ROLE.customer]] : [ROLE_NAV_LABEL[ROLE.customer], ROLE_NAV_LABEL[roleId.value]]))

function setBookingStatus(id: string, status: BookingStatus) {
  const booking = bookings.value.find((b) => b.id === id)
  if (booking) booking.status = status
}

function addBooking(booking: Booking) {
  bookings.value.unshift(booking)
  const timer = setTimeout(() => {
    settleTimers.delete(timer)
    setBookingStatus(booking.id, BOOKING_STATUS.confirmed)
  }, PAYMENT_CONFIRM_DELAY_MS)
  settleTimers.add(timer)
}

function setUserRole(id: string, role: RvRoleId) {
  const user = users.value.find((u) => u.id === id)
  if (user) user.role = role
}

function toggleUserLock(id: string) {
  const user = users.value.find((u) => u.id === id)
  if (user) user.locked = !user.locked
}

function toggleRestaurant(id: string) {
  const restaurant = restaurants.value.find((r) => r.id === id)
  if (restaurant) restaurant.active = !restaurant.active
}

function toggleTheme() {
  themeId.value = themeId.value === THEME.dark ? THEME.light : THEME.dark
}

onBeforeUnmount(() => settleTimers.forEach(clearTimeout))
</script>

<template>
  <div class="rv" :class="[`rv--${themeId}`, `rv--${deviceId}`, { 'is-preview': preview }]" :inert="preview || undefined">
    <div class="rv-bar">
      <strong>{{ BRAND_NAME }} prototype</strong>
      <RvSegmented v-model="roleId" :options="RV_ROLES" label="Role" />
      <RvSegmented v-model="themeId" :options="RV_THEMES" label="Theme" />
      <RvSegmented v-model="deviceId" :options="RV_DEVICES" label="Device" />
    </div>

    <div class="rv-stage">
      <div class="rv-frame">
        <header class="rv-head">
          <b class="rv-brand">{{ BRAND_NAME }}</b>
          <nav><span v-for="(label, index) in navLabels" :key="label" :class="{ on: index === navLabels.length - 1 }">{{ label }}</span></nav>
          <button type="button" class="rv-theme" :aria-label="`Switch to ${themeId === THEME.dark ? 'light' : 'dark'} theme`" @click="toggleTheme">{{ themeIcon }}</button>
          <span class="rv-avatar">{{ ROLE_AVATAR[roleId] }}</span>
        </header>
        <main class="rv-main">
          <RvCustomer v-if="roleId === ROLE.customer" :restaurants="restaurants" :bookings="bookings" @add="addBooking" @status="setBookingStatus" />
          <RvOwner v-else-if="roleId === ROLE.owner" :restaurants="restaurants" :bookings="bookings" @status="setBookingStatus" />
          <RvAdmin
            v-else
            :users="users"
            :restaurants="restaurants"
            :bookings="bookings"
            @role="setUserRole"
            @lock="toggleUserLock"
            @toggle-restaurant="toggleRestaurant"
            @status="setBookingStatus"
          />
        </main>
      </div>
    </div>
  </div>
</template>

<style>
.rv { width: 1200px; height: 760px; display: flex; flex-direction: column; border-radius: 16px; overflow: hidden; background: #101015; color: #fff; font-family: 'Roboto', system-ui, sans-serif; text-align: left; box-shadow: 0 30px 70px -30px rgba(0, 0, 0, .55); }
.rv--dark { --bg: #0A0A0B; --head: #0E0E10; --surface: #141417; --surface2: #1C1C21; --line: rgba(255, 255, 255, .09); --text: #ECECF1; --muted: #9A9AA6; --accent: #4F46E5; --accent-text: #8B86F5; --accent-soft: rgba(79, 70, 229, .16); --ok: #22C55E; --warn: #F59E0B; --bad: #F87171; }
.rv--light { --bg: #F1F4F9; --head: #FFFFFF; --surface: #FFFFFF; --surface2: #F3F5F9; --line: #E3E8F0; --text: #1B2536; --muted: #6B7690; --accent: #4F46E5; --accent-text: #4338CA; --accent-soft: rgba(79, 70, 229, .1); --ok: #15803D; --warn: #B45309; --bad: #DC2626; }
.rv button { font: inherit; }
.rv h1, .rv h2, .rv h3 { font-family: inherit; letter-spacing: normal; }
.rv.is-preview { pointer-events: none; }
.rv-bar { flex: none; display: flex; align-items: center; gap: 14px; padding: 10px 16px; border-bottom: 1px solid rgba(255, 255, 255, .08); }
.rv-bar strong { margin-right: auto; font-size: 13px; letter-spacing: .02em; color: #D6D6DE; }
.rv-stage { flex: 1; min-height: 0; display: grid; place-items: center; padding: 12px; background: radial-gradient(circle at 50% 0%, #1D1D26, #101015 70%); }
.rv-frame { container: rv / inline-size; display: flex; flex-direction: column; width: 100%; height: 100%; overflow: hidden; border-radius: 12px; background: var(--bg); color: var(--text); transition: background .3s, color .3s; }
.rv--mobile .rv-frame { width: 390px; border-radius: 34px; border: 7px solid #2B2B35; box-shadow: 0 20px 50px -20px #000; }
.rv-head { flex: none; display: flex; align-items: center; gap: 22px; padding: 0 24px; height: 58px; background: var(--head); border-bottom: 1px solid var(--line); }
.rv-brand { font-size: 19px; font-weight: 800; color: var(--accent-text); }
.rv-head nav { display: flex; gap: 18px; margin-right: auto; font-size: 14px; font-weight: 500; }
.rv-head nav span { color: var(--text); }
.rv-head nav span.on { color: var(--accent-text); }
.rv-theme { width: 36px; height: 36px; border: 0; border-radius: 10px; background: none; color: var(--muted); font-size: 17px; cursor: pointer; }
.rv-theme:hover { background: var(--surface2); }
.rv-avatar { display: grid; place-items: center; width: 36px; height: 36px; border-radius: 50%; background: var(--accent); color: #fff; font-size: 12px; font-weight: 700; }
.rv-main { flex: 1; min-height: 0; overflow-y: auto; padding: 20px 24px 28px; scrollbar-width: thin; scrollbar-color: var(--line) transparent; }
.rv-dash { display: flex; gap: 22px; align-items: flex-start; }
.rv-dash-main { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 16px; }
.rv-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; }
.rv-stat { display: flex; flex-direction: column; gap: 10px; padding: 16px; border-radius: 12px; background: var(--surface); border: 1px solid var(--line); }
.rv-stat span { font-size: 13px; color: var(--muted); }
.rv-stat strong { font-size: 26px; font-weight: 700; }
.rv-panel { padding: 18px; border-radius: 12px; background: var(--surface); border: 1px solid var(--line); }
.rv-panel h3 { margin: 0 0 10px; font-size: 14px; }
.rv-dash .rv-h1 { margin: 0; }
.rv-row-card strong { font-size: 15px; }
@container rv (max-width: 700px) {
  .rv-head { padding: 0 16px; gap: 12px; }
  .rv-head nav { display: none; }
  .rv-brand { margin-right: auto; }
  .rv-main { padding: 14px 14px 24px; }
  .rv-dash { flex-direction: column; gap: 10px; }
  .rv-dash-main { width: 100%; }
}
</style>
