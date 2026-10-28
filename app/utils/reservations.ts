import {
  ACTIVE_STATUSES,
  BOOKING_STATUS,
  DEPOSIT_CENTS,
  DINING_DURATION_MINUTES,
  REVENUE_STATUSES,
  TODAY_LABEL,
  TREND_DAYS,
  TREND_SPIKE_INDEX,
  type Booking,
  type BookingStatus,
  type Restaurant,
} from '~~/data/reservations'

const MINUTES_PER_HOUR = 60
const HOURS_PER_HALF_DAY = 12
const MERIDIEM_PM = 'PM'
const STAR_COUNT = 5

/**
 * Converts a 12-hour clock label such as "7:00 PM" to minutes since midnight.
 * @param {string} label
 * @returns {number}
 */
export function toMinutes(label: string): number {
  const [clock = '', meridiem = ''] = label.split(' ')
  const [hours = 0, minutes = 0] = clock.split(':').map(Number)
  const morningMinutes = (hours % HOURS_PER_HALF_DAY) * MINUTES_PER_HOUR + minutes
  return meridiem === MERIDIEM_PM ? morningMinutes + HOURS_PER_HALF_DAY * MINUTES_PER_HOUR : morningMinutes
}

/**
 * Lists table indexes that are free for the requested slot and fit the party, smallest table first.
 * A table is taken when an active booking on the same day starts within the dining duration of the slot.
 * @param {Restaurant} restaurant
 * @param {Booking[]} bookings
 * @param {string} dateLabel
 * @param {string} time
 * @param {number} party
 * @returns {number[]}
 */
export function freeTableIndexes(restaurant: Restaurant, bookings: Booking[], dateLabel: string, time: string, party: number): number[] {
  const requestedStart = toMinutes(time)
  const takenTables = new Set(
    bookings
      .filter(
        (b) =>
          b.restaurantId === restaurant.id &&
          b.dateLabel === dateLabel &&
          ACTIVE_STATUSES.includes(b.status) &&
          Math.abs(toMinutes(b.time) - requestedStart) < DINING_DURATION_MINUTES,
      )
      .map((b) => b.tableIndex),
  )
  return restaurant.tableSeats
    .map((seats, index) => ({ seats, index }))
    .filter((table) => !takenTables.has(table.index) && table.seats >= party)
    .sort((a, b) => a.seats - b.seats || a.index - b.index)
    .map((table) => table.index)
}

/**
 * Describes a table for display, for example "T3 · seats 4".
 * @param {Restaurant} restaurant
 * @param {number} tableIndex
 * @returns {string}
 */
export function describeTable(restaurant: Restaurant, tableIndex: number): string {
  return `T${tableIndex + 1} · seats ${restaurant.tableSeats[tableIndex]}`
}

/**
 * Returns five booleans marking which stars are filled for a rating.
 * @param {number | null} rating
 * @returns {boolean[]}
 */
export function starFlags(rating: number | null): boolean[] {
  return Array.from({ length: STAR_COUNT }, (_, index) => index < Math.round(rating ?? 0))
}

/**
 * Counts bookings per status, in lifecycle order.
 * @param {Booking[]} bookings
 * @returns {{ status: BookingStatus; count: number }[]}
 */
export function countByStatus(bookings: Booking[]): { status: BookingStatus; count: number }[] {
  return Object.values(BOOKING_STATUS).map((status) => ({ status, count: bookings.filter((b) => b.status === status).length }))
}

/**
 * Sums the deposits of bookings that count as revenue.
 * @param {Booking[]} bookings
 * @returns {number} cents
 */
export function revenueCents(bookings: Booking[]): number {
  return bookings.filter((b) => REVENUE_STATUSES.includes(b.status)).length * DEPOSIT_CENTS
}

/**
 * Builds the 30-day reservation trend: the seeded history plus today's bookings.
 * @param {Booking[]} bookings
 * @returns {number[]}
 */
export function buildTrend(bookings: Booking[]): number[] {
  const todayCount = bookings.filter((b) => b.dateLabel === TODAY_LABEL).length
  return Array.from({ length: TREND_DAYS }, (_, day) => (day === TREND_SPIKE_INDEX ? 1 : 0) + (day === TREND_DAYS - 1 ? todayCount : 0))
}
