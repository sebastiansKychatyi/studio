<script setup lang="ts">
import {
  ADMIN_SELF_ID,
  RV_ROLES,
  STATUS_LABEL,
  TODAY_LABEL,
  type Booking,
  type BookingStatus,
  type Restaurant,
  type RvOption,
  type RvRoleId,
  type RvUser,
} from '~~/data/reservations'
import { countByStatus } from '~/utils/reservations'

const PAGE = { dashboard: 'dashboard', users: 'users', restaurants: 'restaurants', reservations: 'reservations' } as const
const ALL_ROLES = 'all'
const PERCENT = 100

type Page = (typeof PAGE)[keyof typeof PAGE]

const PAGES: RvOption<Page>[] = [
  { id: PAGE.dashboard, label: 'Dashboard' },
  { id: PAGE.users, label: 'Users' },
  { id: PAGE.restaurants, label: 'Restaurants' },
  { id: PAGE.reservations, label: 'Reservations' },
]

const props = defineProps<{ users: RvUser[]; restaurants: Restaurant[]; bookings: Booking[] }>()
const emit = defineEmits<{
  role: [id: string, role: RvRoleId]
  lock: [id: string]
  toggleRestaurant: [id: string]
  status: [id: string, status: BookingStatus]
}>()

const page = ref<Page>(PAGE.dashboard)
const search = ref('')
const roleFilter = ref<string>(ALL_ROLES)

const reviewTotal = computed(() => props.restaurants.reduce((sum, r) => sum + r.reviewCount, 0))
const activeRestaurants = computed(() => props.restaurants.filter((r) => r.active).length)
const stats = computed(() => [
  { label: 'Total users', value: String(props.users.length) },
  { label: 'Restaurants', value: `${activeRestaurants.value} / ${props.restaurants.length} active` },
  { label: 'Total reservations', value: String(props.bookings.length) },
  { label: "Today's reservations", value: String(props.bookings.filter((b) => b.dateLabel === TODAY_LABEL).length) },
  { label: 'Total reviews', value: String(reviewTotal.value) },
])
const roleRows = computed(() => RV_ROLES.map((role) => ({ label: role.label, count: props.users.filter((u) => u.role === role.id).length })))
const statusRows = computed(() => countByStatus(props.bookings))
const statusPeak = computed(() => Math.max(1, ...statusRows.value.map((row) => row.count)))
const shownUsers = computed(() => {
  const needle = search.value.trim().toLowerCase()
  return props.users.filter((u) => (roleFilter.value === ALL_ROLES || u.role === roleFilter.value) && `${u.name} ${u.email}`.toLowerCase().includes(needle))
})
const barWidth = (count: number) => `${(count / statusPeak.value) * PERCENT}%`
const onRoleChange = (user: RvUser, event: Event) => emit('role', user.id, (event.target as HTMLSelectElement).value as RvRoleId)
</script>

<template>
  <div class="rv-dash">
    <RvSideNav v-model="page" :items="PAGES" heading="Management" />
    <section class="rv-dash-main">
      <template v-if="page === PAGE.dashboard">
        <h1 class="rv-h1">Admin Panel</h1>
        <div class="rv-stats">
          <article v-for="stat in stats" :key="stat.label" class="rv-stat"><span>{{ stat.label }}</span><strong>{{ stat.value }}</strong></article>
        </div>
        <div class="rv-two-panels">
          <article class="rv-panel">
            <h3>Users by role</h3>
            <p v-for="row in roleRows" :key="row.label" class="rv-kv"><span>{{ row.label }}</span><b>{{ row.count }}</b></p>
          </article>
          <article class="rv-panel">
            <h3>Reservation status</h3>
            <p v-for="row in statusRows" :key="row.status" class="rv-bar-row">
              <span>{{ STATUS_LABEL[row.status] }}</span>
              <i><b :style="{ width: barWidth(row.count) }" /></i>
              <em>{{ row.count }}</em>
            </p>
          </article>
        </div>
      </template>

      <template v-else-if="page === PAGE.users">
        <h1 class="rv-h1">Users</h1>
        <div class="rv-toolbar">
          <input v-model="search" type="search" placeholder="Search by name or email..." aria-label="Search users">
          <select v-model="roleFilter" aria-label="Filter by role">
            <option :value="ALL_ROLES">All roles</option>
            <option v-for="role in RV_ROLES" :key="role.id" :value="role.id">{{ role.label }}</option>
          </select>
        </div>
        <article v-for="user in shownUsers" :key="user.id" class="rv-panel rv-row-card" :class="{ locked: user.locked }">
          <div>
            <strong>{{ user.name }}</strong>
            <p>{{ user.email }}</p>
          </div>
          <i class="rv-chip" :class="user.locked ? 'cancelled' : 'confirmed'">{{ user.locked ? 'Locked' : 'Active' }}</i>
          <em v-if="user.id === ADMIN_SELF_ID" class="rv-you">You</em>
          <div v-else class="rv-user-actions">
            <select :value="user.role" :aria-label="`Role of ${user.name}`" @change="onRoleChange(user, $event)">
              <option v-for="role in RV_ROLES" :key="role.id" :value="role.id">{{ role.label }}</option>
            </select>
            <button type="button" class="rv-ghost danger" @click="emit('lock', user.id)">{{ user.locked ? 'Unlock' : 'Lock' }}</button>
          </div>
        </article>
      </template>

      <template v-else-if="page === PAGE.restaurants">
        <h1 class="rv-h1">Restaurants</h1>
        <article v-for="restaurant in restaurants" :key="restaurant.id" class="rv-panel rv-row-card" :class="{ locked: !restaurant.active }">
          <div>
            <strong>{{ restaurant.name }}</strong>
            <p>{{ restaurant.cuisine }} · {{ restaurant.city }} · owner {{ restaurant.ownerName }}</p>
          </div>
          <i class="rv-chip" :class="restaurant.active ? 'confirmed' : 'cancelled'">{{ restaurant.active ? 'Active' : 'Inactive' }}</i>
          <button type="button" class="rv-ghost danger" @click="emit('toggleRestaurant', restaurant.id)">{{ restaurant.active ? 'Deactivate' : 'Activate' }}</button>
        </article>
      </template>

      <template v-else>
        <h1 class="rv-h1">Reservations</h1>
        <RvReservationsTable :bookings="bookings" :restaurants="restaurants" @status="(id, status) => emit('status', id, status)" />
      </template>
    </section>
  </div>
</template>

<style>
.rv-toolbar { display: flex; gap: 10px; }
.rv-toolbar input, .rv-toolbar select, .rv-user-actions select { padding: 10px 14px; font: inherit; font-size: 14px; color: var(--text); background: var(--surface); border: 1px solid var(--line); border-radius: 10px; }
.rv-toolbar input { flex: 1; min-width: 0; }
.rv-user-actions { display: flex; gap: 8px; align-items: center; }
.rv-user-actions select { padding: 7px 10px; background: var(--surface2); }
.rv-you { font-style: normal; font-size: 13px; color: var(--muted); }
.rv-row-card.locked { opacity: .6; }
.rv-two-panels { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.rv-kv { display: flex; justify-content: space-between; margin: 0; padding: 7px 0; font-size: 14px; }
@container rv (max-width: 700px) {
  .rv-two-panels { grid-template-columns: 1fr; }
  .rv-row-card { flex-wrap: wrap; }
}
</style>
