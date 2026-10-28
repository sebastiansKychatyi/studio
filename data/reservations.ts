export const THEME = { dark: 'dark', light: 'light' } as const
export const DEVICE = { desktop: 'desktop', mobile: 'mobile' } as const
export const ROLE = { customer: 'customer', owner: 'owner', admin: 'admin' } as const
export const BOOKING_STATUS = {
  pending: 'pending',
  confirmed: 'confirmed',
  completed: 'completed',
  noShow: 'no_show',
  cancelled: 'cancelled',
} as const

export type RvThemeId = (typeof THEME)[keyof typeof THEME]
export type RvDeviceId = (typeof DEVICE)[keyof typeof DEVICE]
export type RvRoleId = (typeof ROLE)[keyof typeof ROLE]
export type BookingStatus = (typeof BOOKING_STATUS)[keyof typeof BOOKING_STATUS]

export interface RvOption<T extends string> {
  id: T
  label: string
}

export interface MenuItem {
  name: string
  priceCents: number
}

export interface MenuSection {
  title: string
  items: MenuItem[]
}

export interface RestaurantReview {
  author: string
  rating: number
  text: string
}

export interface Restaurant {
  id: string
  name: string
  cuisine: string
  priceLevel: number
  city: string
  address: string
  ownerId: string
  ownerName: string
  rating: number | null
  reviewCount: number
  about: string
  tags: string[]
  colors: [string, string]
  tableSeats: number[]
  menu: MenuSection[]
  reviews: RestaurantReview[]
  active: boolean
}

export interface Booking {
  id: string
  restaurantId: string
  guest: string
  dateLabel: string
  time: string
  party: number
  tableIndex: number
  status: BookingStatus
}

export interface RvUser {
  id: string
  name: string
  email: string
  role: RvRoleId
  locked: boolean
}

export const RV_THEMES: RvOption<RvThemeId>[] = [
  { id: THEME.dark, label: 'Dark' },
  { id: THEME.light, label: 'Light' },
]

export const RV_DEVICES: RvOption<RvDeviceId>[] = [
  { id: DEVICE.desktop, label: 'Desktop' },
  { id: DEVICE.mobile, label: 'Mobile' },
]

export const RV_ROLES: RvOption<RvRoleId>[] = [
  { id: ROLE.customer, label: 'Customer' },
  { id: ROLE.owner, label: 'Owner' },
  { id: ROLE.admin, label: 'Admin' },
]

export const ROLE_NAV_LABEL: Record<RvRoleId, string> = {
  [ROLE.customer]: 'Search',
  [ROLE.owner]: 'Dashboard',
  [ROLE.admin]: 'Admin',
}

export const ROLE_AVATAR: Record<RvRoleId, string> = {
  [ROLE.customer]: 'MH',
  [ROLE.owner]: 'PN',
  [ROLE.admin]: 'AU',
}

export const STATUS_LABEL: Record<BookingStatus, string> = {
  [BOOKING_STATUS.pending]: 'Pending',
  [BOOKING_STATUS.confirmed]: 'Confirmed',
  [BOOKING_STATUS.completed]: 'Completed',
  [BOOKING_STATUS.noShow]: 'No show',
  [BOOKING_STATUS.cancelled]: 'Cancelled',
}

export const ACTIVE_STATUSES: BookingStatus[] = [BOOKING_STATUS.pending, BOOKING_STATUS.confirmed]
export const REVENUE_STATUSES: BookingStatus[] = [BOOKING_STATUS.confirmed, BOOKING_STATUS.completed]

export const BRAND_NAME = 'ReserveIt'
export const GUEST_NAME = 'Martin Horvath'
export const CURRENT_OWNER_ID = 'peter'
export const TODAY_LABEL = 'Wed, Oct 28, 2026'
export const YESTERDAY_LABEL = 'Tue, Oct 27, 2026'

export const PARTY_SIZES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
export const DEFAULT_PARTY_SIZE = 2
export const DEFAULT_TIME = '7:00 PM'
export const SLOT_TIMES = ['5:00 PM', '5:30 PM', '6:00 PM', '6:30 PM', '6:45 PM', '7:00 PM', '7:15 PM', '7:30 PM', '8:00 PM', '8:30 PM', '9:00 PM']
export const QUICK_SLOTS = ['6:30 PM', '6:45 PM', '7:00 PM', '7:15 PM', '7:30 PM']
export const CARD_SLOT_COUNT = 3
export const DINING_DURATION_MINUTES = 90
export const DEPOSIT_CENTS = 500
export const PAYMENT_CONFIRM_DELAY_MS = 2200
export const PHONE_PATTERN = /^\+?[\d\s]{9,15}$/
export const REQUESTS_MAX_LENGTH = 500
export const TREND_DAYS = 30
export const TREND_SPIKE_INDEX = 27

export const RESTAURANTS: Restaurant[] = [
  {
    id: 'sushi-zen', name: 'Sushi Zen', cuisine: 'Japanese', priceLevel: 3, city: 'Bratislava', address: 'Obchodna 8, Bratislava',
    ownerId: CURRENT_OWNER_ID, ownerName: 'Peter Novak', rating: 5, reviewCount: 1, colors: ['#0F766E', '#134E4A'], tableSeats: [2, 2, 2, 4, 4, 6],
    about: 'Hand-cut nigiri and seasonal rolls at a quiet counter in the old town.',
    tags: ['Chef counter', 'Vegetarian options'],
    menu: [
      { title: 'Rolls', items: [{ name: 'Salmon avocado roll', priceCents: 1180 }, { name: 'Spicy tuna roll', priceCents: 1260 }] },
      { title: 'Nigiri', items: [{ name: 'Sake nigiri (2 pcs)', priceCents: 640 }, { name: 'Unagi nigiri (2 pcs)', priceCents: 790 }] },
    ],
    reviews: [{ author: 'Martin', rating: 5, text: 'Super fresh fish, friendly staff.' }], active: true,
  },
  {
    id: 'bella-italia', name: 'Bella Italia', cuisine: 'Italian', priceLevel: 2, city: 'Bratislava', address: 'Obchodna 12, Bratislava',
    ownerId: CURRENT_OWNER_ID, ownerName: 'Peter Novak', rating: 4.5, reviewCount: 2, colors: ['#B45309', '#78350F'], tableSeats: [2, 2, 4, 4, 6, 6],
    about: 'Handmade pasta and wood-fired pizza in the heart of the old town.',
    tags: ['Outdoor seating', 'Vegetarian options'],
    menu: [
      { title: 'Pizza', items: [{ name: 'Margherita', priceCents: 950 }, { name: 'Diavola', priceCents: 1190 }] },
      { title: 'Pasta', items: [{ name: 'Carbonara', priceCents: 1250 }, { name: 'Tagliatelle al ragu', priceCents: 1320 }] },
    ],
    reviews: [
      { author: 'Martin', rating: 5, text: 'Best carbonara in town!' },
      { author: 'Lucia', rating: 4, text: 'Great pizza, a bit crowded on Friday.' },
    ],
    active: true,
  },
  {
    id: 'slovak-koliba', name: 'Slovak Koliba', cuisine: 'Slovak', priceLevel: 1, city: 'Kosice', address: 'Hlavna 44, Kosice',
    ownerId: 'jana', ownerName: 'Jana Kovacova', rating: 4, reviewCount: 1, colors: ['#4D7C0F', '#365314'], tableSeats: [4, 4, 6, 6, 8, 8, 10],
    about: 'Halusky, pierogi and grilled meats in a wooden mountain-lodge dining room.',
    tags: ['Large groups', 'Live music on Fridays'],
    menu: [
      { title: 'Mains', items: [{ name: 'Bryndzove halusky', priceCents: 890 }, { name: 'Pork knuckle', priceCents: 1490 }] },
      { title: 'Desserts', items: [{ name: 'Parene buchty', priceCents: 560 }] },
    ],
    reviews: [{ author: 'Lucia', rating: 4, text: 'Authentic food and cozy place.' }], active: true,
  },
  {
    id: 'le-petit-bistro', name: 'Le Petit Bistro', cuisine: 'French', priceLevel: 4, city: 'Bratislava', address: 'Michalska 3, Bratislava',
    ownerId: 'jana', ownerName: 'Jana Kovacova', rating: null, reviewCount: 0, colors: ['#9D174D', '#500724'], tableSeats: [2, 2, 4],
    about: 'A tasting menu of classic French plates in an intimate twelve-table room.',
    tags: ['Tasting menu', 'Wine pairing'],
    menu: [{ title: 'Tasting menu', items: [{ name: 'Five courses', priceCents: 6800 }, { name: 'Wine pairing', priceCents: 3200 }] }],
    reviews: [], active: true,
  },
]

export const SEED_BOOKINGS: Booking[] = [
  { id: 'RSV-0001', restaurantId: 'bella-italia', guest: GUEST_NAME, dateLabel: YESTERDAY_LABEL, time: '7:00 PM', party: 2, tableIndex: 0, status: BOOKING_STATUS.confirmed },
]

export const SEED_USERS: RvUser[] = [
  { id: 'u1', name: 'Martin Horvath', email: 'martin@example.com', role: ROLE.customer, locked: false },
  { id: 'u2', name: 'Lucia Szabo', email: 'lucia@example.com', role: ROLE.customer, locked: false },
  { id: 'u3', name: 'Admin User', email: 'admin@example.com', role: ROLE.admin, locked: false },
  { id: 'u4', name: 'Peter Novak', email: 'peter@example.com', role: ROLE.owner, locked: false },
  { id: 'u5', name: 'Jana Kovacova', email: 'jana@example.com', role: ROLE.owner, locked: false },
]

export const ADMIN_SELF_ID = 'u3'
