<script setup lang="ts">
import {
  ACTIVE_STATUSES,
  CURRENT_OWNER_ID,
  STATUS_LABEL,
  TODAY_LABEL,
  type Booking,
  type BookingStatus,
  type Restaurant,
  type RvOption,
} from '~~/data/reservations'
import { buildTrend, countByStatus, revenueCents } from '~/utils/reservations'
import { formatEur } from '~/utils/prototype'

const PAGE = { overview: 'overview', reservations: 'reservations', restaurants: 'restaurants' } as const
const CHART_WIDTH = 600
const CHART_HEIGHT = 150
const CHART_MIN_PEAK = 4
const PERCENT = 100
const RATING_DECIMALS = 1

type Page = (typeof PAGE)[keyof typeof PAGE]

const PAGES: RvOption<Page>[] = [
  { id: PAGE.overview, label: 'Overview' },
  { id: PAGE.reservations, label: 'Reservations' },
  { id: PAGE.restaurants, label: 'My Restaurants' },
]

const props = defineProps<{ restaurants: Restaurant[]; bookings: Booking[] }>()
const emit = defineEmits<{ status: [id: string, status: BookingStatus] }>()

const page = ref<Page>(PAGE.overview)

const mine = computed(() => props.restaurants.filter((r) => r.ownerId === CURRENT_OWNER_ID))
const myBookings = computed(() => props.bookings.filter((b) => mine.value.some((r) => r.id === b.restaurantId)))
const reviewTotal = computed(() => mine.value.reduce((sum, r) => sum + r.reviewCount, 0))
const averageRating = computed(() => {
  const weighted = mine.value.reduce((sum, r) => sum + (r.rating ?? 0) * r.reviewCount, 0)
  return reviewTotal.value ? (weighted / reviewTotal.value).toFixed(RATING_DECIMALS) : '–'
})
const stats = computed(() => [
  { label: 'Total reservations', value: String(myBookings.value.length) },
  { label: 'Revenue', value: formatEur(revenueCents(myBookings.value)) },
  { label: 'Average rating', value: `${averageRating.value} / 5` },
  { label: "Today's reservations", value: String(myBookings.value.filter((b) => b.dateLabel === TODAY_LABEL).length) },
  { label: 'Total reviews', value: String(reviewTotal.value) },
])
const statusRows = computed(() => countByStatus(myBookings.value))
const statusPeak = computed(() => Math.max(1, ...statusRows.value.map((row) => row.count)))
const trend = computed(() => buildTrend(myBookings.value))
const chartPoints = computed(() => {
  const peak = Math.max(CHART_MIN_PEAK, ...trend.value)
  const step = CHART_WIDTH / (trend.value.length - 1)
  return trend.value.map((value, index) => `${(index * step).toFixed(1)},${(CHART_HEIGHT - (value / peak) * CHART_HEIGHT).toFixed(1)}`)
})
const chartArea = computed(() => `0,${CHART_HEIGHT} ${chartPoints.value.join(' ')} ${CHART_WIDTH},${CHART_HEIGHT}`)
const activeCount = (restaurant: Restaurant) => myBookings.value.filter((b) => b.restaurantId === restaurant.id && ACTIVE_STATUSES.includes(b.status)).length
const barWidth = (count: number) => `${(count / statusPeak.value) * PERCENT}%`
</script>

<template>
  <div class="rv-dash">
    <RvSideNav v-model="page" :items="PAGES" heading="Main" />
    <section class="rv-dash-main">
      <template v-if="page === PAGE.overview">
        <h1 class="rv-h1">Dashboard</h1>
        <div class="rv-stats">
          <article v-for="stat in stats" :key="stat.label" class="rv-stat"><span>{{ stat.label }}</span><strong>{{ stat.value }}</strong></article>
        </div>
        <article class="rv-panel">
          <h3>Reservation trends (last 30 days)</h3>
          <svg :viewBox="`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`" class="rv-chart" preserveAspectRatio="none" role="img" aria-label="Reservations per day">
            <polygon :points="chartArea" class="rv-chart-area" />
            <polyline :points="chartPoints.join(' ')" class="rv-chart-line" />
          </svg>
        </article>
        <article class="rv-panel">
          <h3>Reservation status</h3>
          <p v-for="row in statusRows" :key="row.status" class="rv-bar-row">
            <span>{{ STATUS_LABEL[row.status] }}</span>
            <i><b :style="{ width: barWidth(row.count) }" /></i>
            <em>{{ row.count }}</em>
          </p>
        </article>
      </template>

      <template v-else-if="page === PAGE.reservations">
        <h1 class="rv-h1">Reservations</h1>
        <RvReservationsTable :bookings="myBookings" :restaurants="mine" @status="(id, status) => emit('status', id, status)" />
      </template>

      <template v-else>
        <h1 class="rv-h1">My Restaurants</h1>
        <article v-for="restaurant in mine" :key="restaurant.id" class="rv-panel rv-row-card">
          <div>
            <strong>{{ restaurant.name }}</strong>
            <p>{{ restaurant.cuisine }} · {{ restaurant.city }} · {{ restaurant.tableSeats.length }} tables</p>
          </div>
          <span>{{ activeCount(restaurant) }} active bookings</span>
          <i class="rv-chip" :class="restaurant.active ? 'confirmed' : 'cancelled'">{{ restaurant.active ? 'Active' : 'Inactive' }}</i>
        </article>
      </template>
    </section>
  </div>
</template>

<style>
.rv-chart { width: 100%; height: 150px; display: block; }
.rv-chart-area { fill: var(--accent-soft); }
.rv-chart-line { fill: none; stroke: var(--accent); stroke-width: 2.5; vector-effect: non-scaling-stroke; stroke-linejoin: round; }
.rv-bar-row { display: grid; grid-template-columns: 110px 1fr 28px; align-items: center; gap: 12px; margin: 0; padding: 6px 0; font-size: 13px; }
.rv-bar-row i { height: 8px; border-radius: 999px; background: var(--surface2); overflow: hidden; }
.rv-bar-row b { display: block; height: 100%; border-radius: 999px; background: var(--accent); transition: width .4s; }
.rv-bar-row em { font-style: normal; font-weight: 700; text-align: right; }
.rv-row-card { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.rv-row-card p { margin: 2px 0 0; font-size: 13px; color: var(--muted); }
.rv-row-card > span { font-size: 13px; color: var(--muted); }
</style>
