// Local copy of the team panel (IndexedDB): last API responses and changes made offline.
// Wiped on logout. Tiny wrapper instead of a library: two stores, a handful of calls.

export interface OutboxOp {
  seq?: number
  method: 'POST' | 'PATCH' | 'DELETE'
  url: string // API path, e.g. /alarms/12 (negative id = not created on the server yet)
  body?: Record<string, unknown>
  temp?: number // id given to the created item until the server answers
  at: string // when the change was made (ISO)
  base?: string | null // updated_at the user saw (conflict check)
  label: string // shown in sync messages
}

let opened: Promise<IDBDatabase> | undefined
// Plain JSON copy (Vue proxies cannot be stored)
const plain = <T>(v: T): T => JSON.parse(JSON.stringify(v))

function db() {
  opened ??= new Promise((resolve, reject) => {
    const req = indexedDB.open('duo-team', 1)
    req.onupgradeneeded = () => {
      req.result.createObjectStore('cache')
      req.result.createObjectStore('outbox', { keyPath: 'seq', autoIncrement: true })
    }
    req.onsuccess = () => resolve(req.result)
    req.onerror = () => reject(req.error)
  })
  return opened
}

async function run<T>(store: 'cache' | 'outbox', mode: IDBTransactionMode, fn: (s: IDBObjectStore) => IDBRequest<T>) {
  const s = (await db()).transaction(store, mode).objectStore(store)
  return new Promise<T>((resolve, reject) => {
    const req = fn(s)
    req.onsuccess = () => resolve(req.result)
    req.onerror = () => reject(req.error)
  })
}

export const localCache = {
  get: <T>(key: string) => run<T | undefined>('cache', 'readonly', (s) => s.get(key)),
  set: (key: string, value: unknown) => run('cache', 'readwrite', (s) => s.put(plain(value), key)),
  keys: () => run<IDBValidKey[]>('cache', 'readonly', (s) => s.getAllKeys()).then((k) => k.map(String)),
}

export const outbox = {
  all: () => run<OutboxOp[]>('outbox', 'readonly', (s) => s.getAll()),
  add: (op: OutboxOp) => run<IDBValidKey>('outbox', 'readwrite', (s) => s.add(plain(op))).then(Number),
  put: (op: OutboxOp) => run('outbox', 'readwrite', (s) => s.put(plain(op))),
  remove: (seq: number) => run('outbox', 'readwrite', (s) => s.delete(seq)),
}

export async function clearLocal() {
  await run('cache', 'readwrite', (s) => s.clear())
  await run('outbox', 'readwrite', (s) => s.clear())
}
