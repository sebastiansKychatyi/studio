// Private team panel: session user, API client and shared state.
// API is FastAPI (backend/), proxied by Nuxt at /api/team.

export interface TeamUser { id: number; username: string; name: string }
export interface TeamCard {
  id: number
  column_id: number
  title: string
  description: string
  assignee_id: number | null
  created_by: number | null
  position: number
  due_date: string | null // YYYY-MM-DD
  is_private: boolean // visible only to created_by
  updated_at: string
}
// Open card that mentions or is assigned to the current user
export interface TeamMention extends TeamCard { board_id: number; board_title: string; column_title: string }
export interface TeamColumn { id: number; title: string; position: number; cards: TeamCard[] }
// Board visible to its creator + member_ids; is_private = shared with nobody
export interface TeamBoard { id: number; title: string; created_by: number | null; member_ids: number[]; is_private: boolean }
export interface TeamBoardItem extends TeamBoard { columns: { id: number; title: string }[] }
export interface TeamBoardFull extends TeamBoard { columns: TeamColumn[] }
// days: JS weekdays (0 = Sunday); empty = ring once
export interface TeamAlarm { id: number; time: string; label: string; days: number[]; enabled: boolean }
// Calendar event; weekly ones repeat on `days` (JS weekdays) until `until`, minus `skip` dates
export interface TeamEvent {
  id: number
  title: string
  date: string // first day, YYYY-MM-DD
  start: string // HH:MM
  end: string
  repeat: 'none' | 'weekly'
  days: number[]
  until: string | null
  skip: string[]
  color: string
  note: string
  remind: number | null // minutes before start
}
export type EventDraft = Omit<TeamEvent, 'id' | 'skip'>

// Does the event happen on this day (YYYY-MM-DD)?
export function eventOccursOn(e: TeamEvent, day: string) {
  if (e.repeat === 'none') return e.date === day
  const weekday = new Date(`${day}T12:00:00`).getDay()
  return day >= e.date && (!e.until || day <= e.until) && e.days.includes(weekday) && !e.skip.includes(day)
}
// Kanban card with a deadline, for the calendar
export interface TeamDue { id: number; title: string; due_date: string; board_id: number; board_title: string; column_title: string; done: boolean }
export const EXPENSE_CATEGORIES = ['food', 'transport', 'home', 'software', 'tech', 'fun', 'health', 'other'] as const
export type ExpenseCategory = (typeof EXPENSE_CATEGORIES)[number]
export const INCOME_CATEGORIES = ['projects', 'salary', 'support', 'sale', 'gift', 'refund', 'other'] as const
export type IncomeCategory = (typeof INCOME_CATEGORIES)[number]
export type MoneyKind = 'expenses' | 'income'
// Category as shown in the UI (built-in or the user's own, key "c<id>")
export interface MoneyCat { key: string; name: string; icon: string; color: string }
export interface CustomCategory { id: number; key: string; name: string; icon: string; color: string }
// Icons offered for own categories
export const CATEGORY_ICONS = ['tag', 'food', 'car', 'home', 'code', 'laptop', 'game', 'heart', 'cart', 'gift', 'cash', 'briefcase', 'repeat', 'wallet', 'phone', 'globe', 'pen', 'plug', 'chart', 'shield', 'spark', 'doc', 'mail', 'pin', 'user', 'bell'] as const
export const CATEGORY_COLORS = ['#FF7A59', '#F59E0B', '#19C3A6', '#0E9F85', '#3B82F6', '#5B4BFF', '#8B5CF6', '#EC4899', '#E5484D', '#9CA3AF']
export const CURRENCIES = ['EUR', 'UAH', 'USD'] as const
export type Currency = (typeof CURRENCIES)[number]
// Expense or income entry. amount in EUR; original_amount in `currency` (1 EUR = rate); spent_on = YYYY-MM-DD
export interface TeamMoney {
  id: number
  amount: number
  original_amount: number
  currency: Currency
  rate: number
  category: string
  note: string
  spent_on: string
  recurring_id: number | null // created from a monthly template
}

// Text split into plain parts and @mentions of known users
export function mentionParts(text: string, users: TeamUser[]) {
  const parts: { text: string; user?: TeamUser }[] = []
  let last = 0
  for (const m of text.matchAll(/@([\w.-]+)/g)) {
    const user = users.find((u) => u.username.toLowerCase() === m[1]!.toLowerCase())
    if (!user) continue
    if (m.index > last) parts.push({ text: text.slice(last, m.index) })
    parts.push({ text: m[0], user })
    last = m.index + m[0].length
  }
  if (last < text.length) parts.push({ text: text.slice(last) })
  return parts
}

// Deadline state relative to today (local dates)
export function dueState(due: string | null) {
  if (!due) return null
  const d = new Date()
  const today = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  const days = Math.round((Date.parse(due) - Date.parse(today)) / 86400000)
  return days < 0 ? 'overdue' : days === 0 ? 'today' : days <= 2 ? 'soon' : 'later'
}

export const httpStatus = (e: unknown) => (e as { status?: number })?.status ?? 0

export function useTeam() {
  // undefined = not checked yet, null = signed out
  const user = useState<TeamUser | null | undefined>('team-user', () => undefined)
  const users = useState<TeamUser[]>('team-users', () => [])
  const alarms = useState<TeamAlarm[]>('team-alarms', () => [])
  const mentions = useState<TeamMention[]>('team-mentions', () => [])
  const events = useState<TeamEvent[]>('team-events', () => [])
  const api = $fetch.create({ baseURL: '/api/team' })

  async function refresh() {
    try {
      user.value = (await api<{ user: TeamUser | null }>('/auth/me')).user
    } catch {
      user.value = null
    }
    return user.value
  }

  async function login(username: string, password: string) {
    user.value = await api<TeamUser>('/auth/login', { method: 'POST', body: { username, password } })
  }

  async function logout() {
    await api('/auth/logout', { method: 'POST' }).catch(() => {})
    user.value = null
  }

  const loadUsers = async () => (users.value = await api<TeamUser[]>('/users'))
  const loadAlarms = async () => (alarms.value = await api<TeamAlarm[]>('/alarms'))
  const loadMentions = async () => (mentions.value = await api<TeamMention[]>('/mentions'))
  const loadEvents = async () => (events.value = await api<TeamEvent[]>('/events'))

  return { user, users, alarms, mentions, events, api, refresh, login, logout, loadUsers, loadAlarms, loadMentions, loadEvents }
}

// Per-account UI settings, stored on the server (/me/settings) and merged key by key
let prefTimer: ReturnType<typeof setTimeout> | undefined
let prefPending: Record<string, unknown> = {}

export function usePrefs() {
  const prefs = useState<Record<string, unknown>>('team-prefs', () => ({}))
  const ready = useState('team-prefs-ready', () => false)
  const { api } = useTeam()

  async function loadPrefs() {
    try {
      prefs.value = await api<Record<string, unknown>>('/me/settings')
    } finally {
      ready.value = true
    }
  }

  function setPref(key: string, value: unknown) {
    prefs.value = { ...prefs.value, [key]: value }
    prefPending[key] = value
    clearTimeout(prefTimer)
    prefTimer = setTimeout(() => {
      const data = prefPending
      prefPending = {}
      api('/me/settings', { method: 'PATCH', body: { data } }).catch(() => {})
    }, 400)
  }

  // Two-way computed for one setting
  const pref = <T>(key: string, fallback: T) =>
    computed<T>({ get: () => (prefs.value[key] ?? fallback) as T, set: (v) => setPref(key, v) })

  return { prefs, ready, loadPrefs, pref, setPref }
}
