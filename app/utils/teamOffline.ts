// Offline rules of the team panel: which changes can wait in the outbox, what they look like
// right away (optimistic result) and how waiting changes are laid over cached API responses.
import type { OutboxOp } from './teamStore'

// API JSON as stored in the cache
type Obj = Record<string, any>

const ID = '(-?\\d+)'
// Changes that work offline: alarms, calendar events, expenses/income, kanban cards, settings
const QUEUEABLE: [string, RegExp][] = [
  ['POST', /^\/alarms$/], ['PATCH', new RegExp(`^/alarms/${ID}$`)], ['DELETE', new RegExp(`^/alarms/${ID}$`)],
  ['POST', /^\/events$/], ['PATCH', new RegExp(`^/events/${ID}$`)], ['DELETE', new RegExp(`^/events/${ID}$`)],
  ['POST', new RegExp(`^/events/${ID}/skip$`)],
  ['POST', /^\/(expenses|income)$/], ['PATCH', new RegExp(`^/(expenses|income)/${ID}$`)], ['DELETE', new RegExp(`^/(expenses|income)/${ID}$`)],
  ['POST', new RegExp(`^/columns/${ID}/cards$`)], ['PATCH', new RegExp(`^/cards/${ID}$`)], ['DELETE', new RegExp(`^/cards/${ID}$`)],
  ['PATCH', /^\/me\/settings$/],
  ['POST', new RegExp(`^/(expenses|income)/recurring/${ID}/pay$`)],
  ['POST', /^\/time\/(start|stop)$/], ['POST', /^\/time$/], ['PATCH', new RegExp(`^/time/${ID}$`)], ['DELETE', new RegExp(`^/time/${ID}$`)],
  ['POST', new RegExp(`^/clients/${ID}/log$`)], ['PATCH', new RegExp(`^/client-log/${ID}$`)],
  ['POST', /^\/study\/works$/], ['PATCH', new RegExp(`^/study/works/${ID}$`)], ['DELETE', new RegExp(`^/study/works/${ID}$`)],
]
export const queueable = (method: string, url: string) => QUEUEABLE.some(([m, re]) => m === method && re.test(url))

// Cache key of a GET: path + sorted query
export function cacheKey(url: string, query?: Obj) {
  const q = Object.entries(query ?? {}).filter(([, v]) => v !== undefined && v !== null).sort(([a], [b]) => a.localeCompare(b))
  return q.length ? `${url}?${new URLSearchParams(q.map(([k, v]) => [k, String(v)])).toString()}` : url
}

// Id of the item a PATCH/DELETE is about
export const targetId = (url: string) => Number(url.match(new RegExp(`/${ID}(?:/skip)?$`))?.[1])

export interface Ctx { rates: Obj; meId: number | null }

// What the server would return for a created item
function created(op: OutboxOp, ctx: Ctx): Obj {
  const b = op.body ?? {}
  if (op.url === '/alarms') return { id: op.temp, label: '', days: [], enabled: true, ...b, updated_at: null }
  if (op.url === '/events') return { id: op.temp, skip: [], note: '', remind: null, until: null, days: [], ...b, updated_at: null }
  if (op.url.endsWith('/pay')) return { id: op.temp, ...b }
  if (op.url === '/time/start' || op.url === '/time') return { id: op.temp, client_id: null, project_id: null, card_id: null, note: '', end: null, invoice_id: null, ...b }
  if (/^\/clients\/-?\d+\/log$/.test(op.url)) return { id: op.temp, client_id: Number(op.url.split('/')[2]), followup: null, followup_done: false, ...b }
  if (op.url === '/study/works') return { id: op.temp, subject_id: null, kind: 'assignment', due_time: null, status: 'todo', grade: '', note: '', ...b, updated_at: null }
  if (/^\/(expenses|income)$/.test(op.url)) return money({ id: op.temp, recurring_id: null, note: '', category: 'other', updated_at: null }, b, ctx)
  const col = Number(op.url.split('/')[2])
  return {
    id: op.temp, column_id: col, description: '', assignee_id: null, created_by: ctx.meId, position: 1e6,
    due_date: null, is_private: false, ...b, updated_at: op.at,
  }
}

// Entry amounts: entered amount + currency, stored in EUR with the known rate
function money(entry: Obj, b: Obj, ctx: Ctx) {
  const out = { ...entry, ...b }
  if (b.amount !== undefined || b.currency !== undefined) {
    const currency = b.currency ?? entry.currency ?? 'EUR'
    const original = Number(b.amount ?? entry.original_amount)
    const rate = Number(ctx.rates[currency] ?? 1)
    Object.assign(out, { currency, original_amount: original, rate, amount: Math.round((original / rate) * 100) / 100 })
  }
  return out
}

// One waiting change applied to a list of items
function onList(list: Obj[], op: OutboxOp, base: string, ctx: Ctx) {
  const id = targetId(op.url)
  if (op.method === 'POST' && op.url === base) return [...list, created(op, ctx)]
  if (op.method === 'DELETE') return list.filter((x) => x.id !== id)
  if (op.url.endsWith('/skip')) return list.map((x) => (x.id === id ? { ...x, skip: [...x.skip, op.body?.date] } : x))
  if (op.method === 'PATCH') {
    return list.map((x) => (x.id !== id ? x : /^\/(expenses|income)/.test(base) ? money(x, op.body ?? {}, ctx) : { ...x, ...op.body }))
  }
  return list
}

// Waiting changes laid over a cached or fresh GET response
export function overlay(key: string, data: unknown, ops: OutboxOp[], ctx: Ctx): unknown {
  if (!ops.length || (data == null && key !== '/time/running')) return data
  const [path, qs] = key.split('?')
  const query = new URLSearchParams(qs)
  const mine = (prefix: RegExp) => ops.filter((op) => prefix.test(op.url))

  if (path === '/alarms') {
    return mine(/^\/alarms/).reduce((l, op) => onList(l, op, '/alarms', ctx), data as Obj[])
      .sort((a, b) => String(a.time).localeCompare(String(b.time)))
  }
  if (path === '/events' && !query.get('user')) return mine(/^\/events/).reduce((l, op) => onList(l, op, '/events', ctx), data as Obj[])
  const kind = path?.match(/^\/(expenses|income)$/)?.[1]
  if (kind && query.get('month')) {
    const month = query.get('month')!
    const list = mine(new RegExp(`^/${kind}(/|$)`)).reduce((l, op) => onList(l, op, `/${kind}`, ctx), data as Obj[])
    return list
      .filter((x) => String(x.spent_on).startsWith(month))
      .sort((a, b) => String(b.spent_on).localeCompare(String(a.spent_on)) || (b.id < 0 ? 1e12 : b.id) - (a.id < 0 ? 1e12 : a.id))
  }
  if (/^\/boards\/\d+$/.test(path!)) return board(data as Obj, mine(/^\/(cards|columns)\//), ctx)
  // Timer started / stopped offline: the last such change decides
  if (path === '/time/running') {
    const last = mine(/^\/time\/(start|stop)$/).at(-1)
    return !last ? data : last.url === '/time/stop' ? null : created(last, ctx)
  }
  if (path === '/study') {
    const s = data as Obj
    const works = mine(/^\/study\/works/).reduce((l, op) => onList(l, op, '/study/works', ctx), s.works as Obj[])
    return { ...s, works: works.sort((a, b) => String(a.due).localeCompare(String(b.due))) }
  }
  if (path === '/me/settings') {
    const out = { ...(data as Obj) }
    for (const op of mine(/^\/me\/settings$/)) {
      for (const [k, v] of Object.entries((op.body?.data ?? {}) as Obj)) {
        if (v === null) delete out[k]
        else out[k] = v
      }
    }
    return out
  }
  return data
}

// Kanban board: created, edited, moved and deleted cards
function board(data: Obj, ops: OutboxOp[], ctx: Ctx) {
  const b = { ...data, columns: data.columns.map((c: Obj) => ({ ...c, cards: [...c.cards] })) }
  const find = (id: number) => {
    for (const col of b.columns) {
      const i = col.cards.findIndex((c: Obj) => c.id === id)
      if (i >= 0) return { col, i }
    }
  }
  for (const op of ops) {
    if (op.method === 'POST') {
      const col = b.columns.find((c: Obj) => c.id === Number(op.url.split('/')[2]))
      col?.cards.push(created(op, ctx))
      continue
    }
    const at = find(targetId(op.url))
    if (!at) continue
    const [card] = at.col.cards.splice(at.i, 1)
    if (op.method === 'DELETE') continue
    const next = { ...card, ...op.body }
    const target = b.columns.find((c: Obj) => c.id === next.column_id)
    if (!target) continue // moved to a board that is not this one
    const pos = op.body?.position ?? (next.column_id === card.column_id ? at.i : target.cards.length)
    target.cards.splice(Math.min(Number(pos), target.cards.length), 0, next)
  }
  return b
}

// Optimistic answer for a queued change (what the page gets back instead of the server reply)
export function optimistic(op: OutboxOp, current: Obj | undefined, ctx: Ctx): unknown {
  if (op.method === 'DELETE' || op.url === '/time/stop') return null
  if (op.method === 'POST' && !op.url.endsWith('/skip')) return created(op, ctx)
  if (op.url === '/me/settings') return overlay('/me/settings', current ?? {}, [op], ctx)
  if (!current) return { id: targetId(op.url), ...op.body }
  if (op.url.endsWith('/skip')) return { ...current, skip: [...(current.skip ?? []), op.body?.date] }
  return /^\/(expenses|income)\//.test(op.url) ? money(current, op.body ?? {}, ctx) : { ...current, ...op.body }
}

// Where to look in the cache for the item of a PATCH/DELETE
export function searchKeys(url: string, keys: string[]) {
  const kind = url.split('/')[1]
  if (kind === 'cards') return keys.filter((k) => /^\/boards\/\d+$/.test(k))
  if (kind === 'study') return keys.filter((k) => k === '/study')
  if (kind === 'expenses' || kind === 'income') return keys.filter((k) => k.startsWith(`/${kind}?`) && k.includes('month='))
  return keys.filter((k) => k === `/${kind}`)
}

// Find an item by id in a cached response (cards sit inside board columns)
export function findIn(data: unknown, id: number): Obj | undefined {
  if (Array.isArray(data)) return data.find((x) => x?.id === id)
  const works = (data as Obj | undefined)?.works
  if (Array.isArray(works)) return works.find((x) => x?.id === id)
  const cols = (data as Obj | undefined)?.columns
  if (Array.isArray(cols)) for (const c of cols) for (const card of c.cards ?? []) if (card.id === id) return card
}

// Text for sync messages
export const labelOf = (body: Obj | undefined, current: Obj | undefined) =>
  String(body?.title ?? body?.label ?? body?.note ?? current?.title ?? current?.label ?? current?.note ?? current?.time ?? '').slice(0, 60)
