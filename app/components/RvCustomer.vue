<script setup lang="ts">
import {
  ACTIVE_STATUSES,
  BOOKING_STATUS,
  CARD_SLOT_COUNT,
  DEFAULT_PARTY_SIZE,
  DEFAULT_TIME,
  DEPOSIT_CENTS,
  GUEST_NAME,
  PARTY_SIZES,
  PHONE_PATTERN,
  QUICK_SLOTS,
  REQUESTS_MAX_LENGTH,
  SLOT_TIMES,
  STATUS_LABEL,
  TODAY_LABEL,
  type Booking,
  type BookingStatus,
  type Restaurant,
  type RvOption,
} from '~~/data/reservations'
import { describeTable, freeTableIndexes, starFlags } from '~/utils/reservations'
import { formatEur, newId } from '~/utils/prototype'

const SECTION = { search: 'search', mine: 'mine' } as const
const VIEW = { home: 'home', restaurant: 'restaurant', booking: 'booking', done: 'done' } as const
const TAB = { overview: 'overview', menu: 'menu', reviews: 'reviews' } as const
const EXCEPTIONAL_RATING = 4.5
const AWESOME_RATING = 4
const CURRENCY_SIGN = '€'
const BOOKING_ID_PREFIX = 'RSV-'

type Section = (typeof SECTION)[keyof typeof SECTION]
type View = (typeof VIEW)[keyof typeof VIEW]
type Tab = (typeof TAB)[keyof typeof TAB]

const TAB_OPTIONS: RvOption<Tab>[] = [
  { id: TAB.overview, label: 'Overview' },
  { id: TAB.menu, label: 'Menu' },
  { id: TAB.reviews, label: 'Reviews' },
]

const props = defineProps<{ restaurants: Restaurant[]; bookings: Booking[] }>()
const emit = defineEmits<{ add: [booking: Booking]; status: [id: string, status: BookingStatus] }>()

const section = ref<Section>(SECTION.search)
const view = ref<View>(VIEW.home)
const tab = ref<Tab>(TAB.overview)
const query = ref('')
const searchTime = ref(DEFAULT_TIME)
const searchParty = ref(DEFAULT_PARTY_SIZE)
const selectedId = ref('')
const party = ref(DEFAULT_PARTY_SIZE)
const time = ref(DEFAULT_TIME)
const phone = ref('')
const requests = ref('')
const lastBookingId = ref('')

const cardSlots = QUICK_SLOTS.slice(0, CARD_SLOT_COUNT)
const selected = computed(() => props.restaurants.find((r) => r.id === selectedId.value))
const visible = computed(() => {
  const needle = query.value.trim().toLowerCase()
  return props.restaurants.filter((r) => r.active && `${r.name} ${r.cuisine} ${r.city}`.toLowerCase().includes(needle))
})
const freeTables = computed(() => (selected.value ? freeTableIndexes(selected.value, props.bookings, TODAY_LABEL, time.value, party.value) : []))
const phoneValid = computed(() => PHONE_PATTERN.test(phone.value))
const canComplete = computed(() => phoneValid.value && freeTables.value.length > 0)
const myBookings = computed(() => props.bookings.filter((b) => b.guest === GUEST_NAME))
const lastBooking = computed(() => props.bookings.find((b) => b.id === lastBookingId.value))
const confirming = computed(() => lastBooking.value?.status === BOOKING_STATUS.pending)
const availabilityText = computed(() => {
  const count = freeTables.value.length
  if (!count) return 'No table fits this party at this time'
  return `${count} ${count === 1 ? 'table' : 'tables'} available`
})

const plural = (count: number, one: string, many: string) => (count === 1 ? one : many)
const partyLabel = (size: number) => `${size} ${plural(size, 'person', 'people')}`
const priceSigns = (restaurant: Restaurant) => CURRENCY_SIGN.repeat(restaurant.priceLevel)
const photoStyle = (restaurant: Restaurant) => ({ background: `linear-gradient(135deg, ${restaurant.colors[0]}, ${restaurant.colors[1]})` })
const restaurantOf = (booking: Booking) => props.restaurants.find((r) => r.id === booking.restaurantId)!
const bookedToday = (restaurant: Restaurant) =>
  props.bookings.filter((b) => b.restaurantId === restaurant.id && b.dateLabel === TODAY_LABEL && ACTIVE_STATUSES.includes(b.status)).length
const slotAvailable = (restaurant: Restaurant, slot: string) =>
  freeTableIndexes(restaurant, props.bookings, TODAY_LABEL, slot, searchParty.value).length > 0

function ratingLabel(rating: number | null): string {
  if (rating === null) return 'No ratings yet'
  if (rating >= EXCEPTIONAL_RATING) return 'Exceptional'
  return rating >= AWESOME_RATING ? 'Awesome' : 'Very good'
}

function openRestaurant(restaurant: Restaurant, slot?: string) {
  selectedId.value = restaurant.id
  party.value = searchParty.value
  time.value = slot ?? searchTime.value
  tab.value = TAB.overview
  view.value = VIEW.restaurant
}

function submitBooking() {
  const restaurant = selected.value
  const tableIndex = freeTables.value[0]
  if (!restaurant || tableIndex === undefined || !canComplete.value) return
  const booking: Booking = {
    id: `${BOOKING_ID_PREFIX}${newId().toUpperCase()}`,
    restaurantId: restaurant.id,
    guest: GUEST_NAME,
    dateLabel: TODAY_LABEL,
    time: time.value,
    party: party.value,
    tableIndex,
    status: BOOKING_STATUS.pending,
  }
  lastBookingId.value = booking.id
  emit('add', booking)
  view.value = VIEW.done
}

function backToSearch() {
  phone.value = ''
  requests.value = ''
  section.value = SECTION.search
  view.value = VIEW.home
}
</script>

<template>
  <div class="rv-customer">
    <div class="rv-tabs rv-tabs-top" role="tablist">
      <button type="button" :class="{ on: section === SECTION.search }" @click="section = SECTION.search">Search</button>
      <button type="button" :class="{ on: section === SECTION.mine }" @click="section = SECTION.mine">My reservations ({{ myBookings.length }})</button>
    </div>

    <template v-if="section === SECTION.search">
      <template v-if="view === VIEW.home">
        <div class="rv-searchbar">
          <span class="rv-pill">{{ TODAY_LABEL }}</span>
          <select v-model="searchTime" class="rv-pill" aria-label="Time">
            <option v-for="slot in SLOT_TIMES" :key="slot" :value="slot">{{ slot }}</option>
          </select>
          <select v-model.number="searchParty" class="rv-pill" aria-label="Party size">
            <option v-for="size in PARTY_SIZES" :key="size" :value="size">{{ partyLabel(size) }}</option>
          </select>
          <input v-model="query" class="rv-search-input" type="search" placeholder="Location, Restaurant, or Cuisine" aria-label="Search restaurants">
        </div>

        <h2 class="rv-h2">Top Rated Restaurants</h2>
        <div class="rv-cards">
          <article v-for="restaurant in visible" :key="restaurant.id" class="rv-rcard">
            <button type="button" class="rv-photo" :style="photoStyle(restaurant)" @click="openRestaurant(restaurant)">
              <span>{{ restaurant.name }}</span>
            </button>
            <div class="rv-rcard-body">
              <p class="rv-stars">
                <i v-for="(filled, index) in starFlags(restaurant.rating)" :key="index" :class="{ on: filled }">★</i>
                <b>{{ restaurant.reviewCount }} {{ plural(restaurant.reviewCount, 'review', 'reviews') }}</b>
              </p>
              <p class="rv-sub">{{ restaurant.cuisine }} · {{ priceSigns(restaurant) }} · {{ restaurant.city }}</p>
              <p class="rv-booked">Booked {{ bookedToday(restaurant) }} {{ plural(bookedToday(restaurant), 'time', 'times') }} today</p>
              <div class="rv-slots">
                <button v-for="slot in cardSlots" :key="slot" type="button" :disabled="!slotAvailable(restaurant, slot)" @click="openRestaurant(restaurant, slot)">{{ slot }}</button>
              </div>
            </div>
          </article>
        </div>
        <p v-if="!visible.length" class="rv-empty-note">No restaurants match your search.</p>
      </template>

      <template v-else-if="view === VIEW.restaurant && selected">
        <button type="button" class="rv-back" @click="view = VIEW.home">← All restaurants</button>
        <div class="rv-hero" :style="photoStyle(selected)"><span>{{ selected.name }}</span></div>
        <div class="rv-detail">
          <div class="rv-detail-main">
            <div class="rv-tabs" role="tablist">
              <button v-for="option in TAB_OPTIONS" :key="option.id" type="button" :class="{ on: option.id === tab }" @click="tab = option.id">{{ option.label }}</button>
            </div>
            <h1 class="rv-h1">{{ selected.name }}</h1>
            <p class="rv-stars">
              <i v-for="(filled, index) in starFlags(selected.rating)" :key="index" :class="{ on: filled }">★</i>
              <b>{{ ratingLabel(selected.rating) }}</b> ({{ selected.reviewCount }} {{ plural(selected.reviewCount, 'review', 'reviews') }})
            </p>
            <p class="rv-sub">{{ priceSigns(selected) }} · {{ selected.cuisine }} · {{ selected.city }} — {{ selected.address }}</p>

            <template v-if="tab === TAB.overview">
              <div class="rv-tags"><span v-for="tag in selected.tags" :key="tag">{{ tag }}</span></div>
              <p class="rv-about">{{ selected.about }}</p>
              <p class="rv-sub">{{ selected.tableSeats.length }} tables · seats {{ Math.min(...selected.tableSeats) }}–{{ Math.max(...selected.tableSeats) }}</p>
            </template>
            <template v-else-if="tab === TAB.menu">
              <section v-for="menuSection in selected.menu" :key="menuSection.title" class="rv-menu">
                <h3>{{ menuSection.title }}</h3>
                <p v-for="item in menuSection.items" :key="item.name"><span>{{ item.name }}</span><b>{{ formatEur(item.priceCents) }}</b></p>
              </section>
            </template>
            <template v-else>
              <article v-for="review in selected.reviews" :key="review.author + review.text" class="rv-review">
                <p class="rv-stars"><i v-for="(filled, index) in starFlags(review.rating)" :key="index" :class="{ on: filled }">★</i> <b>{{ review.author }}</b></p>
                <p>{{ review.text }}</p>
              </article>
              <p v-if="!selected.reviews.length" class="rv-sub">No reviews yet. Be the first after your visit.</p>
            </template>
          </div>

          <aside class="rv-book">
            <header><b>Make a reservation</b><span>A {{ formatEur(DEPOSIT_CENTS) }} deposit confirms your table</span></header>
            <div class="rv-book-body">
              <label>Party size
                <select v-model.number="party"><option v-for="size in PARTY_SIZES" :key="size" :value="size">{{ partyLabel(size) }}</option></select>
              </label>
              <div class="rv-two">
                <label>Date<span class="rv-pill">{{ TODAY_LABEL.slice(5, 11) }}</span></label>
                <label>Time
                  <select v-model="time"><option v-for="slot in SLOT_TIMES" :key="slot" :value="slot">{{ slot }}</option></select>
                </label>
              </div>
              <p class="rv-avail" :class="{ none: !freeTables.length }">{{ availabilityText }}</p>
              <p class="rv-cap">Quick-select a time</p>
              <div class="rv-slots rv-slots-wrap">
                <button v-for="slot in QUICK_SLOTS" :key="slot" type="button" :class="{ on: slot === time }" @click="time = slot">{{ slot }}</button>
              </div>
              <button type="button" class="rv-primary" :disabled="!freeTables.length" @click="view = VIEW.booking">Book a Table · {{ time }}</button>
            </div>
          </aside>
        </div>
      </template>

      <template v-else-if="view === VIEW.booking && selected">
        <button type="button" class="rv-back" @click="view = VIEW.restaurant">← Back to {{ selected.name }}</button>
        <h1 class="rv-h1">{{ selected.name }}</h1>
        <div class="rv-detail">
          <form class="rv-form" @submit.prevent="submitBooking">
            <fieldset>
              <legend>Your details</legend>
              <label>Name<input :value="GUEST_NAME" readonly></label>
              <label>Phone number *
                <input v-model="phone" type="tel" placeholder="+421 900 000 000" :class="{ invalid: phone.length > 0 && !phoneValid }">
                <small>We'll only use this to contact you about your reservation</small>
              </label>
            </fieldset>
            <fieldset>
              <legend>Reservation details</legend>
              <div class="rv-three">
                <label>Party size<select v-model.number="party"><option v-for="size in PARTY_SIZES" :key="size" :value="size">{{ partyLabel(size) }}</option></select></label>
                <label>Date<span class="rv-pill">{{ TODAY_LABEL.slice(5, 11) }}</span></label>
                <label>Time<select v-model="time"><option v-for="slot in SLOT_TIMES" :key="slot" :value="slot">{{ slot }}</option></select></label>
              </div>
              <label>Special requests (optional)
                <textarea v-model="requests" :maxlength="REQUESTS_MAX_LENGTH" rows="3" placeholder="Allergies, anniversary, high chair needed..." />
                <small class="rv-counter">{{ requests.length }}/{{ REQUESTS_MAX_LENGTH }}</small>
              </label>
            </fieldset>
            <button type="submit" class="rv-primary" :disabled="!canComplete">Complete reservation</button>
            <p class="rv-note">A deposit of {{ formatEur(DEPOSIT_CENTS) }} is required to confirm your reservation</p>
          </form>
          <aside class="rv-summary">
            <h3>Booking summary</h3>
            <dl>
              <dt>Date</dt><dd>{{ TODAY_LABEL }}</dd>
              <dt>Time</dt><dd>{{ time }}</dd>
              <dt>Party</dt><dd>{{ partyLabel(party) }}</dd>
              <dt>Location</dt><dd>{{ selected.name }}<small>{{ selected.address }}</small></dd>
              <dt>Table</dt><dd>{{ freeTables.length ? `${describeTable(selected, freeTables[0]!)} · best fit` : 'None free' }}</dd>
            </dl>
          </aside>
        </div>
      </template>

      <template v-else-if="view === VIEW.done && lastBooking">
        <div class="rv-done">
          <span class="rv-done-mark" :class="{ wait: confirming }">{{ confirming ? '…' : '✓' }}</span>
          <h1 class="rv-h1">{{ confirming ? 'Confirming your deposit…' : 'Reservation confirmed' }}</h1>
          <p class="rv-sub">{{ confirming ? 'Waiting for the signed payment webhook.' : 'Your table is booked. See you soon!' }}</p>
          <dl class="rv-facts">
            <dt>Restaurant</dt><dd>{{ restaurantOf(lastBooking).name }}</dd>
            <dt>When</dt><dd>{{ lastBooking.dateLabel }} · {{ lastBooking.time }}</dd>
            <dt>Party</dt><dd>{{ partyLabel(lastBooking.party) }}</dd>
            <dt>Table</dt><dd>{{ describeTable(restaurantOf(lastBooking), lastBooking.tableIndex) }}</dd>
            <dt>Reference</dt><dd>{{ lastBooking.id }}</dd>
            <dt>Status</dt><dd><i class="rv-chip" :class="lastBooking.status">{{ STATUS_LABEL[lastBooking.status] }}</i></dd>
          </dl>
          <div class="rv-done-actions">
            <button type="button" class="rv-primary" @click="backToSearch">Back to restaurants</button>
            <button type="button" class="rv-ghost" @click="section = SECTION.mine">My reservations</button>
          </div>
        </div>
      </template>
    </template>

    <template v-else>
      <h2 class="rv-h2">My reservations</h2>
      <div class="rv-mine">
        <article v-for="booking in myBookings" :key="booking.id" class="rv-mine-card">
          <div>
            <strong>{{ restaurantOf(booking).name }}</strong>
            <p class="rv-sub">{{ booking.dateLabel }} · {{ booking.time }} · {{ partyLabel(booking.party) }} · {{ describeTable(restaurantOf(booking), booking.tableIndex) }}</p>
          </div>
          <i class="rv-chip" :class="booking.status">{{ STATUS_LABEL[booking.status] }}</i>
          <button v-if="ACTIVE_STATUSES.includes(booking.status)" type="button" class="rv-ghost danger" :disabled="booking.status === BOOKING_STATUS.pending" @click="emit('status', booking.id, BOOKING_STATUS.cancelled)">Cancel</button>
        </article>
      </div>
    </template>
  </div>
</template>

<style>
.rv-customer { display: flex; flex-direction: column; gap: 16px; }
.rv-tabs { display: flex; gap: 22px; border-bottom: 1px solid var(--line); }
.rv-tabs button { padding: 10px 2px; border: 0; border-bottom: 2px solid transparent; margin-bottom: -1px; background: none; color: var(--muted); font: inherit; font-size: 14px; font-weight: 600; cursor: pointer; }
.rv-tabs button.on { color: var(--accent-text); border-bottom-color: var(--accent); }
.rv-searchbar { display: flex; gap: 10px; flex-wrap: wrap; padding: 14px; border-radius: 14px; background: var(--surface); border: 1px solid var(--line); }
.rv-pill, .rv-customer select, .rv-customer input, .rv-customer textarea { font: inherit; font-size: 14px; color: var(--text); background: var(--surface2); border: 1px solid var(--line); border-radius: 10px; }
.rv-pill { display: inline-flex; align-items: center; padding: 10px 14px; font-weight: 600; }
.rv-customer select { padding: 10px 12px; font-weight: 600; cursor: pointer; }
.rv-search-input { flex: 1; min-width: 180px; padding: 10px 14px; }
.rv-customer input:focus, .rv-customer select:focus, .rv-customer textarea:focus { outline: 2px solid var(--accent); outline-offset: -1px; }
.rv-h1 { margin: 6px 0 0; font-size: 26px; font-weight: 700; }
.rv-h2 { margin: 6px 0 0; font-size: 20px; font-weight: 700; }
.rv-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.rv-rcard { display: flex; flex-direction: column; border-radius: 14px; overflow: hidden; background: var(--surface); border: 1px solid var(--line); }
.rv-photo, .rv-hero { position: relative; display: flex; align-items: flex-end; width: 100%; height: 150px; padding: 12px; border: 0; color: #fff; font: inherit; font-size: 15px; font-weight: 700; text-align: left; cursor: pointer; }
.rv-photo::before, .rv-hero::before { content: ''; position: absolute; inset: 0; background: radial-gradient(circle at 80% 15%, rgba(255, 255, 255, .22), transparent 55%), linear-gradient(to top, rgba(0, 0, 0, .55), transparent 60%); }
.rv-photo span, .rv-hero span { position: relative; text-shadow: 0 1px 6px rgba(0, 0, 0, .5); }
.rv-hero { height: 150px; border-radius: 14px; cursor: default; font-size: 22px; }
.rv-rcard-body { display: flex; flex-direction: column; gap: 6px; padding: 12px; }
.rv-rcard-body p, .rv-customer p { margin: 0; }
.rv-stars { display: flex; align-items: center; gap: 2px; font-size: 13px; }
.rv-stars i { font-style: normal; color: var(--line); }
.rv-stars i.on { color: var(--accent); }
.rv-stars b { margin-left: 6px; font-weight: 600; }
.rv-sub { font-size: 13px; color: var(--muted); }
.rv-booked { font-size: 13px; font-weight: 600; }
.rv-slots { display: flex; gap: 6px; margin-top: 4px; }
.rv-slots-wrap { flex-wrap: wrap; }
.rv-slots button { flex: 1; padding: 8px 6px; border: 0; border-radius: 6px; background: var(--accent); color: #fff; font: inherit; font-size: 13px; font-weight: 700; cursor: pointer; transition: filter .2s; }
.rv-slots button:hover:not(:disabled) { filter: brightness(1.12); }
.rv-slots button:disabled { background: var(--surface2); color: var(--muted); cursor: not-allowed; }
.rv-slots button.on { box-shadow: 0 0 0 2px var(--bg), 0 0 0 4px var(--accent); }
.rv-empty-note { color: var(--muted); font-size: 14px; }
.rv-back { align-self: flex-start; padding: 0; border: 0; background: none; color: var(--accent-text); font: inherit; font-size: 14px; font-weight: 600; cursor: pointer; }
.rv-detail { display: grid; grid-template-columns: 1fr 340px; gap: 24px; align-items: start; }
.rv-detail-main { display: flex; flex-direction: column; gap: 10px; min-width: 0; }
.rv-tags { display: flex; gap: 8px; flex-wrap: wrap; }
.rv-tags span { padding: 7px 14px; border-radius: 999px; border: 1px solid var(--line); background: var(--surface); font-size: 13px; }
.rv-about { font-size: 15px; line-height: 1.55; }
.rv-menu { padding: 14px 16px; border-radius: 12px; background: var(--surface); border: 1px solid var(--line); }
.rv-menu h3 { margin: 0 0 8px; font-size: 12px; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }
.rv-menu p { display: flex; justify-content: space-between; padding: 6px 0; font-size: 14px; }
.rv-review { padding: 14px 16px; border-radius: 12px; background: var(--surface); border: 1px solid var(--line); display: flex; flex-direction: column; gap: 6px; font-size: 14px; }
.rv-book { border-radius: 14px; overflow: hidden; background: var(--surface); border: 1px solid var(--line); position: sticky; top: 0; }
.rv-book header { display: flex; flex-direction: column; gap: 2px; padding: 14px 18px; background: var(--accent); color: #fff; }
.rv-book header span { font-size: 12px; opacity: .8; }
.rv-book-body { display: flex; flex-direction: column; gap: 12px; padding: 16px 18px 18px; }
.rv-customer label { display: flex; flex-direction: column; gap: 6px; font-size: 11px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); }
.rv-customer label select, .rv-customer label input, .rv-customer label textarea, .rv-customer label .rv-pill { text-transform: none; letter-spacing: normal; }
.rv-two { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.rv-three { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.rv-avail { padding: 9px 12px; border-radius: 8px; background: rgba(34, 197, 94, .12); border: 1px solid rgba(34, 197, 94, .3); color: var(--ok); font-size: 13px; font-weight: 600; }
.rv-avail.none { background: rgba(239, 68, 68, .1); border-color: rgba(239, 68, 68, .3); color: var(--bad); }
.rv-cap { font-size: 11px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); }
.rv-primary { width: 100%; padding: 13px; border: 0; border-radius: 10px; background: var(--accent); color: #fff; font: inherit; font-size: 15px; font-weight: 700; cursor: pointer; transition: filter .2s, opacity .2s; }
.rv-primary:hover:not(:disabled) { filter: brightness(1.12); }
.rv-primary:disabled { opacity: .45; cursor: not-allowed; }
.rv-ghost { padding: 11px 20px; border: 1px solid var(--line); border-radius: 10px; background: none; color: var(--text); font: inherit; font-size: 14px; font-weight: 600; cursor: pointer; }
.rv-ghost.danger { color: var(--bad); padding: 7px 14px; }
.rv-ghost:disabled { opacity: .4; cursor: not-allowed; }
.rv-form { display: flex; flex-direction: column; gap: 14px; }
.rv-form fieldset { display: flex; flex-direction: column; gap: 14px; margin: 0; padding: 18px; border-radius: 14px; background: var(--surface); border: 1px solid var(--line); }
.rv-form legend { padding: 0 6px; font-size: 15px; font-weight: 700; }
.rv-form input.invalid { border-color: var(--bad); }
.rv-form small { font-size: 12px; font-weight: 400; letter-spacing: normal; text-transform: none; color: var(--muted); }
.rv-counter { text-align: right; }
.rv-customer textarea { resize: none; padding: 10px 12px; }
.rv-note { text-align: center; font-size: 12px; color: var(--muted); }
.rv-summary { padding: 18px; border-radius: 14px; background: var(--surface); border: 1px solid var(--line); }
.rv-summary h3 { margin: 0 0 12px; font-size: 15px; }
.rv-summary dl, .rv-facts { display: grid; grid-template-columns: auto 1fr; gap: 10px 16px; margin: 0; font-size: 13px; }
.rv-summary dt, .rv-facts dt { color: var(--muted); }
.rv-summary dd, .rv-facts dd { margin: 0; font-weight: 600; text-align: right; }
.rv-summary small { display: block; font-weight: 400; color: var(--muted); }
.rv-done { display: flex; flex-direction: column; align-items: center; gap: 12px; max-width: 460px; margin: 16px auto 0; text-align: center; }
.rv-done-mark { display: grid; place-items: center; width: 64px; height: 64px; border-radius: 50%; background: rgba(34, 197, 94, .16); color: var(--ok); font-size: 30px; font-weight: 700; }
.rv-done-mark.wait { background: rgba(245, 158, 11, .16); color: var(--warn); }
.rv-facts { width: 100%; padding: 18px; border-radius: 14px; background: var(--surface); border: 1px solid var(--line); text-align: left; }
.rv-done-actions { display: flex; gap: 10px; width: 100%; }
.rv-mine { display: flex; flex-direction: column; gap: 10px; }
.rv-mine-card { display: flex; align-items: center; gap: 14px; justify-content: space-between; padding: 14px 18px; border-radius: 12px; background: var(--surface); border: 1px solid var(--line); }
.rv-mine-card > div { flex: 1; }
@container rv (max-width: 700px) {
  .rv-cards { grid-template-columns: 1fr; }
  .rv-detail { grid-template-columns: 1fr; }
  .rv-book { position: static; }
  .rv-hero { height: 120px; }
  .rv-three { grid-template-columns: 1fr; }
  .rv-search-input { flex-basis: 100%; }
  .rv-done-actions, .rv-mine-card { flex-direction: column; align-items: stretch; }
  .rv-tabs { gap: 16px; }
}
</style>
