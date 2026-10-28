<script setup lang="ts">
import {
  BOOKING_STATUS,
  STATUS_LABEL,
  type Booking,
  type BookingStatus,
  type Restaurant,
} from '~~/data/reservations'
import { describeTable } from '~/utils/reservations'

const ALL_FILTER = 'all'
const FILTERS: string[] = [ALL_FILTER, ...Object.values(BOOKING_STATUS)]
const RESOLUTIONS: { status: BookingStatus; label: string }[] = [
  { status: BOOKING_STATUS.completed, label: 'Complete' },
  { status: BOOKING_STATUS.noShow, label: 'No show' },
  { status: BOOKING_STATUS.cancelled, label: 'Cancel' },
]

const props = defineProps<{ bookings: Booking[]; restaurants: Restaurant[] }>()
const emit = defineEmits<{ status: [id: string, status: BookingStatus] }>()

const filter = ref(ALL_FILTER)
const filterLabel = (value: string) => (value === ALL_FILTER ? 'All' : STATUS_LABEL[value as BookingStatus])
const rows = computed(() => props.bookings.filter((b) => filter.value === ALL_FILTER || b.status === filter.value))
const restaurantOf = (booking: Booking) => props.restaurants.find((r) => r.id === booking.restaurantId)!
</script>

<template>
  <div class="rv-table">
    <div class="rv-filters" role="group" aria-label="Reservation status">
      <button v-for="value in FILTERS" :key="value" type="button" :class="{ on: value === filter }" @click="filter = value">{{ filterLabel(value) }}</button>
    </div>

    <div class="rv-grid rv-grid-head">
      <span>Guest</span><span>Restaurant</span><span>Date</span><span>Time</span><span>Party</span><span>Table</span><span>Status</span><span class="rv-actions-col">Actions</span>
    </div>
    <div v-for="booking in rows" :key="booking.id" class="rv-grid rv-grid-row">
      <strong>{{ booking.guest }}</strong>
      <span>{{ restaurantOf(booking).name }}</span>
      <span>{{ booking.dateLabel }}</span>
      <span>{{ booking.time }}</span>
      <span>{{ booking.party }}</span>
      <span>{{ describeTable(restaurantOf(booking), booking.tableIndex) }}</span>
      <span><i class="rv-chip" :class="booking.status">{{ STATUS_LABEL[booking.status] }}</i></span>
      <span class="rv-actions-col">
        <template v-if="booking.status === BOOKING_STATUS.confirmed">
          <button v-for="resolution in RESOLUTIONS" :key="resolution.status" type="button" :class="resolution.status" @click="emit('status', booking.id, resolution.status)">
            {{ resolution.label }}
          </button>
        </template>
      </span>
    </div>
    <p v-if="!rows.length" class="rv-empty">No reservations in this status.</p>
  </div>
</template>

<style>
.rv-filters { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 14px; }
.rv-filters button { padding: 7px 14px; border: 1px solid var(--line); border-radius: 8px; background: var(--surface); color: var(--muted); font: inherit; font-size: 13px; font-weight: 600; cursor: pointer; }
.rv-filters button.on { background: var(--accent); border-color: var(--accent); color: #fff; }
.rv-grid { display: grid; grid-template-columns: 1.3fr 1.2fr 1.7fr .8fr .5fr 1fr .9fr 1.7fr; gap: 10px; align-items: center; padding: 13px 16px; font-size: 13px; }
.rv-grid-head { background: var(--surface); border: 1px solid var(--line); border-radius: 12px 12px 0 0; font-size: 12px; font-weight: 700; color: var(--muted); }
.rv-grid-row { background: var(--surface); border: 1px solid var(--line); border-top: 0; }
.rv-grid-row:last-of-type { border-radius: 0 0 12px 12px; }
.rv-actions-col { display: flex; gap: 8px; justify-content: flex-end; }
.rv-actions-col button { padding: 5px 10px; border: 0; border-radius: 6px; font: inherit; font-size: 12px; font-weight: 700; cursor: pointer; background: none; }
.rv-actions-col .completed { background: #2563EB; color: #fff; }
.rv-actions-col .no_show { color: var(--warn); }
.rv-actions-col .cancelled { color: var(--bad); }
.rv-chip { font-style: normal; display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 11px; font-weight: 700; background: var(--surface2); color: var(--muted); }
.rv-chip.pending { background: rgba(245, 158, 11, .16); color: var(--warn); }
.rv-chip.confirmed, .rv-chip.completed { background: rgba(34, 197, 94, .16); color: var(--ok); }
.rv-chip.no_show, .rv-chip.cancelled { background: rgba(239, 68, 68, .14); color: var(--bad); }
.rv-empty { margin: 0; padding: 28px; text-align: center; color: var(--muted); font-size: 14px; background: var(--surface); border: 1px solid var(--line); border-top: 0; border-radius: 0 0 12px 12px; }
@container rv (max-width: 700px) {
  .rv-grid-head { display: none; }
  .rv-grid-row { grid-template-columns: 1fr 1fr; border-top: 1px solid var(--line); border-radius: 12px; margin-bottom: 10px; }
  .rv-actions-col { grid-column: 1 / -1; justify-content: flex-start; }
}
</style>
