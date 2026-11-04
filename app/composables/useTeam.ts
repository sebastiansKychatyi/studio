// Private team panel: session user, API client and shared state.
// API is FastAPI (backend/), proxied by Nuxt at /api/team.
import type { Ref } from 'vue'
import { cacheKey, findIn, labelOf, optimistic, overlay, queueable, searchKeys, targetId, type Ctx } from '~/utils/teamOffline'
import { clearLocal, localCache, outbox, type OutboxOp } from '~/utils/teamStore'

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
// "Today" screen (GET /today), built on the server in the user's time zone
export interface TodayCard { id: number; title: string; due_date: string | null; assignee_id: number | null; board_id: number; board_title: string; column_title: string; done_column_id: number }
export interface TodayBill { id: number; title: string; category: string; amount: number | null; currency: Currency; day: number; overdue: boolean }
export interface TeamToday {
  date: string
  now: string
  tz: string
  next_alarm: { id: number; time: string; label: string; at: string } | null
  events: Pick<TeamEvent, 'id' | 'title' | 'start' | 'end' | 'color' | 'repeat' | 'note'>[]
  tasks: { overdue: TodayCard[]; today: TodayCard[]; assigned: TodayCard[] }
  money: { month: string; spent_today: number; spent_month: number; bills: TodayBill[] } // EUR
}
// Study: current semester, subjects with weekly classes (lessons), assignments and exams (works)
export type LessonKind = 'lecture' | 'seminar' | 'lab'
export type WorkKind = 'assignment' | 'project' | 'exam' | 'credit'
export interface StudySemester { id: number; title: string; start: string; end: string; breaks: { from: string; to: string }[]; remind: number | null }
export interface StudyLesson { id: number; subject_id: number; weekday: number; start: string; end: string; kind: LessonKind; room: string }
export interface StudySubject { id: number; name: string; teacher: string; room: string; color: string; links: { title: string; url: string }[]; note: string; lessons: StudyLesson[] }
export interface StudyWork { id: number; subject_id: number | null; kind: WorkKind; title: string; due: string; due_time: string | null; status: 'todo' | 'doing' | 'done'; grade: string; note: string; updated_at: string | null }
export interface TeamStudy { semester: StudySemester | null; subjects: StudySubject[]; works: StudyWork[] }

// Is there this class on the day (YYYY-MM-DD): weekday, semester dates, breaks (same rule as the API)
export function hasClass(l: StudyLesson, s: StudySemester | null, day: string) {
  if (!s || day < s.start || day > s.end) return false
  return new Date(`${day}T12:00:00`).getDay() === l.weekday && !s.breaks.some((b) => day >= b.from && day <= b.to)
}
// Classes of a day, sorted, with their subject
export function classesOn(study: TeamStudy, day: string) {
  return study.subjects
    .flatMap((s) => s.lessons.filter((l) => hasClass(l, study.semester, day)).map((l) => ({ lesson: l, subject: s })))
    .sort((a, b) => a.lesson.start.localeCompare(b.lesson.start))
}

// Kanban card with a deadline, for the calendar
export interface TeamDue { id: number; title: string; due_date: string; board_id: number; board_title: string; column_title: string; done: boolean; study?: boolean }
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

// 0 = no answer at all (offline, server down) — never a reason to sign out
export const httpStatus = (e: unknown) => (e as { status?: number })?.status ?? 0
// Action that needs the network was tried offline
export const isOffline = (e: unknown) => (e as { offline?: boolean })?.offline === true
const offlineError = () => Object.assign(new Error('Offline'), { offline: true, status: 0 })

// ===== Offline layer =====
// GET: network, then the local copy (IndexedDB) when there is no answer. Alarms, events,
// expenses/income, cards and settings can also be changed offline: the change waits in the
// outbox, the page gets an optimistic result and the outbox is sent in order once online.
export interface SyncNotice { id: number; kind: 'overwrote' | 'discarded' | 'rejected'; label: string }
interface ApiOpts { method?: string; body?: object; query?: Record<string, unknown> }
type Fetcher = ReturnType<typeof $fetch.create>

let fetcher: Fetcher | undefined
const raw = () => (fetcher ??= $fetch.create({ baseURL: '/api/team', timeout: 12000 }))
let ops: OutboxOp[] | undefined // same order as the outbox store
let opsLoading: Promise<OutboxOp[]> | undefined
let tempSeq = -Date.now() // ids of items created offline
const realIds = new Map<number, number>() // temp id → server id, once sent
let flushing: Promise<void> | null = null
let sync: { online: Ref<boolean>; pending: Ref<number>; synced: Ref<number>; notices: Ref<SyncNotice[]>; user: Ref<TeamUser | null | undefined> } | undefined

const loadOps = () => (opsLoading ??= outbox.all().catch(() => []).then((list) => (ops = list)))
const KNOWN = 'team-user' // last signed-in user, for starting offline
const known = (): TeamUser | null => {
  try {
    return JSON.parse(localStorage.getItem(KNOWN) ?? 'null')
  } catch {
    return null
  }
}

async function ctx(): Promise<Ctx> {
  const rates = await localCache.get<Record<string, number>>('/rates').catch(() => undefined)
  return { rates: rates ?? { EUR: 1 }, meId: sync?.user.value?.id ?? null }
}
async function overlaid(key: string, data: unknown) {
  const list = await loadOps()
  return list.length ? overlay(key, data, list, await ctx()) : data
}
function setOnline(on: boolean) {
  if (sync && sync.online.value !== on) sync.online.value = on
}

async function peek<T>(url: string, query?: Record<string, unknown>): Promise<T | undefined> {
  if (import.meta.server) return undefined
  const key = cacheKey(url, query)
  const hit = await localCache.get(key).catch(() => undefined)
  return hit === undefined ? undefined : ((await overlaid(key, hit)) as T)
}

async function get<T>(url: string, query?: Record<string, unknown>): Promise<T> {
  const key = cacheKey(url, query)
  if (navigator.onLine) {
    try {
      const data = await raw()<T>(url, { query })
      setOnline(true)
      localCache.set(key, data).catch(() => {})
      return (await overlaid(key, data)) as T
    } catch (e) {
      if (httpStatus(e)) throw e
      setOnline(false)
    }
  }
  const hit = await peek<T>(url, query)
  if (hit === undefined) throw offlineError()
  return hit
}

async function change<T>(method: string, url: string, body?: object): Promise<T> {
  // The page may still show an item created offline under its temp id
  url = url.replace(/\/(-\d+)(?=\/|$)/, (m, id) => (realIds.has(Number(id)) ? `/${realIds.get(Number(id))}` : m))
  const list = await loadOps()
  const canQueue = queueable(method, url)
  // Online with nothing waiting: straight to the server (keeps the order of changes)
  if (navigator.onLine && (!canQueue || !list.length)) {
    try {
      const res = await raw()<T>(url, { method: method as 'POST', body })
      setOnline(true)
      return res
    } catch (e) {
      if (httpStatus(e)) throw e
      setOnline(false)
    }
  }
  if (!canQueue) throw offlineError()
  return (await enqueue(method as OutboxOp['method'], url, body as Record<string, unknown> | undefined)) as T
}

async function enqueue(method: OutboxOp['method'], url: string, body?: Record<string, unknown>) {
  const list = await loadOps()
  const creating = method === 'POST' && !url.endsWith('/skip')
  // The item as the user sees it now (for the result, the conflict check and messages)
  let current: Record<string, unknown> | undefined
  let base: string | null = null
  if (url === '/me/settings') current = await peek('/me/settings')
  else if (!creating) {
    const id = targetId(url)
    for (const key of searchKeys(url, await localCache.keys().catch(() => []))) {
      const data = await localCache.get(key)
      const hit = findIn(data, id)
      const shown = findIn(await overlaid(key, data), id)
      if (hit || shown) {
        base = (hit?.updated_at as string | undefined) ?? null
        current = shown ?? hit
        break
      }
    }
  }
  const op: OutboxOp = { method, url, body, at: new Date().toISOString(), base, label: labelOf(body, current), temp: creating ? tempSeq-- : undefined }
  op.seq = await outbox.add(op)
  list.push(op)
  if (sync) sync.pending.value = list.length
  // Background Sync (Chrome) wakes the app's worker when the network is back
  navigator.serviceWorker?.ready
    .then((r) => (r as ServiceWorkerRegistration & { sync?: { register: (tag: string) => Promise<void> } }).sync?.register('team-sync'))
    .catch(() => {})
  if (navigator.onLine) flushOutbox()
  return optimistic(op, current, await ctx())
}

// Send waiting changes in order; temp ids become real ones; stops at the first network error
export function flushOutbox() {
  if (import.meta.server) return Promise.resolve()
  // One tab at a time (installed app + a browser tab share the outbox), and always the stored outbox:
  // another tab may have sent part of it already
  const exclusive = (fn: () => Promise<void>) => (navigator.locks ? navigator.locks.request('duo-outbox', fn) : fn())
  flushing ??= exclusive(async () => {
    const list = await loadOps()
    list.splice(0, list.length, ...(await outbox.all().catch(() => list)))
    let changed = false
    const notice = (kind: SyncNotice['kind'], label: string) => sync?.notices.value.push({ id: Date.now() + Math.random(), kind, label })
    while (list.length) {
      const op = list[0]!
      try {
        const res = await raw().raw(op.url, {
          method: op.method,
          body: op.body,
          headers: { 'x-offline-at': op.at, 'x-client-now': new Date().toISOString(), ...(op.base ? { 'x-base-updated': op.base } : {}) },
        })
        setOnline(true)
        if (res.headers.get('x-overwrote')) notice('overwrote', op.label)
        const id = (res._data as { id?: number } | undefined)?.id
        if (op.temp && id) {
          realIds.set(op.temp, id)
          for (const next of list.slice(1)) {
            const url = next.url.replace(new RegExp(`/${op.temp}(?=/|$)`), `/${id}`)
            if (url !== next.url) await outbox.put({ ...next, url }).then(() => (next.url = url))
          }
        }
      } catch (e) {
        const status = httpStatus(e)
        // No answer, server error, signed out, rate limit: keep the outbox and retry later
        if (!status || status >= 500 || status === 401 || status === 429) {
          if (!status) setOnline(false)
          break
        }
        // 404 gone, 409 changed later elsewhere, 422 invalid: drop it (and what depends on it)
        notice(status === 409 ? 'discarded' : 'rejected', op.label)
        if (op.temp) {
          for (const next of list.slice(1).filter((x) => new RegExp(`/${op.temp}(/|$)`).test(x.url))) {
            list.splice(list.indexOf(next), 1)
            await outbox.remove(next.seq!)
          }
        }
      }
      changed = true
      list.shift()
      await outbox.remove(op.seq!)
      if (sync) sync.pending.value = list.length
    }
    if (sync) sync.pending.value = list.length
    if (changed && sync) sync.synced.value++
  }).finally(() => (flushing = null))
  return flushing
}

export function useTeam() {
  // undefined = not checked yet, null = signed out
  const user = useState<TeamUser | null | undefined>('team-user', () => undefined)
  const users = useState<TeamUser[]>('team-users', () => [])
  const alarms = useState<TeamAlarm[]>('team-alarms', () => [])
  const mentions = useState<TeamMention[]>('team-mentions', () => [])
  const events = useState<TeamEvent[]>('team-events', () => [])
  const study = useState<TeamStudy>('team-study', () => ({ semester: null, subjects: [], works: [] }))
  const online = useState('team-online', () => true)
  const pending = useState('team-pending', () => 0)
  const synced = useState('team-synced', () => 0) // bumped after the outbox was sent: pages reload
  const notices = useState<SyncNotice[]>('team-sync-notices', () => [])
  if (import.meta.client) sync ??= { online, pending, synced, notices, user }

  const api = <T = unknown>(url: string, opts: ApiOpts = {}): Promise<T> => {
    const method = (opts.method ?? 'GET').toUpperCase()
    if (import.meta.server) return raw()<T>(url, opts as never)
    return method === 'GET' ? get<T>(url, opts.query) : change<T>(method, url, opts.body)
  }

  async function refresh() {
    try {
      user.value = (await raw()<{ user: TeamUser | null }>('/auth/me')).user
      if (user.value) localStorage.setItem(KNOWN, JSON.stringify(user.value))
    } catch (e) {
      // Offline: stay signed in as the last known user (the data is local)
      user.value = httpStatus(e) ? null : known()
    }
    return user.value
  }

  async function login(username: string, password: string) {
    const next = await raw()<TeamUser>('/auth/login', { method: 'POST', body: { username, password } })
    // Another account on this device: drop the previous one's local data
    if (known()?.id !== next.id) await resetLocal()
    localStorage.setItem(KNOWN, JSON.stringify(next))
    user.value = next
  }

  // Needs the network (the session cookie is cleared by the server); local data is wiped
  async function logout() {
    await raw()('/auth/logout', { method: 'POST' }).catch((e) => {
      if (!httpStatus(e)) throw offlineError()
    })
    await resetLocal()
    localStorage.removeItem(KNOWN)
    user.value = null
  }

  async function resetLocal() {
    await clearLocal().catch(() => {})
    ops = []
    opsLoading = Promise.resolve(ops)
    pending.value = 0
  }

  // Local copy first (instant, also offline), then the network
  async function load<T>(url: string, target: Ref<T>) {
    const cached = await peek<T>(url)
    if (cached !== undefined) target.value = cached
    target.value = await api<T>(url)
    return target.value
  }
  const loadUsers = () => load('/users', users)
  const loadAlarms = () => load('/alarms', alarms)
  const loadMentions = () => load('/mentions', mentions)
  const loadEvents = () => load('/events', events)
  const loadStudy = () => load('/study', study)

  // From the panel shell: count waiting changes, send them when the network is back
  function startSync() {
    loadOps().then((list) => {
      pending.value = list.length
      flushOutbox()
    })
    online.value = navigator.onLine
    addEventListener('online', () => {
      online.value = true
      flushOutbox()
    })
    addEventListener('offline', () => (online.value = false))
    document.addEventListener('visibilitychange', () => document.visibilityState === 'visible' && pending.value && flushOutbox())
    navigator.serviceWorker?.addEventListener('message', (e) => e.data === 'flush' && flushOutbox())
    setInterval(() => pending.value && navigator.onLine && flushOutbox(), 30000)
  }

  // Changes still waiting in the outbox (screens hide what is already done locally)
  const waiting = async () => [...(await loadOps())]

  return {
    user, users, alarms, mentions, events, online, pending, synced, notices, waiting,
    study, api, peek, refresh, login, logout, loadUsers, loadAlarms, loadMentions, loadEvents, loadStudy, startSync, flush: flushOutbox,
  }
}

// Per-account UI settings, stored on the server (/me/settings) and merged key by key
let prefTimer: ReturnType<typeof setTimeout> | undefined
let prefPending: Record<string, unknown> = {}

export function usePrefs() {
  const prefs = useState<Record<string, unknown>>('team-prefs', () => ({}))
  const ready = useState('team-prefs-ready', () => false)
  const { api, peek } = useTeam()

  async function loadPrefs() {
    try {
      const cached = await peek<Record<string, unknown>>('/me/settings')
      if (cached) {
        prefs.value = cached
        ready.value = true
      }
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
