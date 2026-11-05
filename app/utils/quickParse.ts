// Quick input: one line → expense / income / event / task / alarm / study deadline.
// Rule based (works offline, no AI), Russian, Ukrainian, Slovak, Czech and English.
// confidence < 0.6 → the UI asks to clarify (the place where an AI parser can plug in later).
// Pure module: no Nuxt imports, so it runs in node tests (tests/quick-parse.test.mjs).

export type QuickKind = 'expense' | 'income' | 'event' | 'task' | 'alarm' | 'work'
export interface QuickCtx {
  today: string // YYYY-MM-DD (local)
  currency?: 'EUR' | 'UAH' | 'USD' // default for amounts without a currency
  clients?: { id: number; name: string; company?: string }[]
  users?: { id: number; username: string; name: string }[]
  subjects?: { id: number; name: string }[]
}
export interface QuickResult {
  kind: QuickKind | null
  confidence: number
  title?: string // task / event / work title, or the money note
  amount?: number
  currency?: 'EUR' | 'UAH' | 'USD'
  category?: string
  date?: string // YYYY-MM-DD: money day, event day, task / work deadline
  time?: string // HH:MM: event start, alarm time
  end?: string // event end
  days?: number[] // alarm weekdays (JS, 0 = Sunday)
  client_id?: number
  assignee_id?: number
  subject_id?: number
  workKind?: 'assignment' | 'project' | 'exam' | 'credit'
}

// ===== Text helpers =====
const CYR: Record<string, string> = {
  а: 'a', б: 'b', в: 'v', г: 'g', ґ: 'g', д: 'd', е: 'e', ё: 'e', є: 'je', ж: 'z', з: 'z', и: 'i', і: 'i', ї: 'ji', й: 'j', к: 'k', л: 'l',
  м: 'm', н: 'n', о: 'o', п: 'p', р: 'r', с: 's', т: 't', у: 'u', ф: 'f', х: 'h', ц: 'c', ч: 'c', ш: 's', щ: 's', ъ: '', ы: 'y', ь: '', э: 'e',
  ю: 'ju', я: 'ja', "'": '', 'ʼ': '', '’': '',
}
// Latin, no diacritics, Cyrillic transliterated: "Анной" → "annoj", "Právo" → "pravo"
export function fold(s: string) {
  return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[а-яёєіїґʼ’']/g, (ch) => CYR[ch] ?? ch)
}
const words = (s: string) => s.split(/[\s,;!?()]+/).filter(Boolean)
// A word is a form of a name when it starts with the name's stem ("Анной", "Anne" ~ "Anna")
function sameStem(word: string, name: string) {
  const w = fold(word).replace(/[^a-z0-9]/g, '')
  const n = fold(name).replace(/[^a-z0-9]/g, '')
  if (n.length < 3 || w.length < 3) return false
  // Endings change with grammatical case; long names compare by their first 6 letters
  const stem = n.length > 4 ? n.slice(0, Math.min(n.length - 2, 6)) : n.slice(0, n.length - 1)
  return w.startsWith(stem) && w.length <= n.length + 3
}
const pad = (n: number) => String(n).padStart(2, '0')
const iso = (d: Date) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
const addDays = (day: string, n: number) => {
  const d = new Date(`${day}T12:00:00`)
  d.setDate(d.getDate() + n)
  return iso(d)
}

// ===== Vocabulary (folded, prefixes) =====
const TODAY = ['segodna', 'sogodni', 'sjogodni', 'sohodni', 'dnes', 'today']
const TOMORROW = ['zavtra', 'zajtra', 'zitra', 'tomorrow']
const AFTER = ['poslezavtra', 'pislazavtra', 'pisljazavtra', 'pozajtra', 'pozitri']
// JS weekday → prefixes in all languages
const WEEKDAYS: [number, string[]][] = [
  [1, ['ponedel', 'ponedil', 'pondel', 'pondeli', 'monday', 'mon']],
  [2, ['vtornik', 'vivtor', 'utor', 'uter', 'tuesday', 'tue']],
  [3, ['sred', 'sered', 'stred', 'wednesday', 'wed']],
  [4, ['cetverg', 'cetver', 'stvrt', 'ctvrt', 'thursday', 'thu']],
  [5, ['patnic', 'pjatnic', 'piat', 'patek', 'patk', 'friday', 'fri']],
  [6, ['subot', 'sobot', 'saturday', 'sat']],
  [0, ['voskres', 'nedil', 'nedel', 'sunday', 'sun']],
]
const MONTHS: string[][] = [
  ['janvar', 'sicn', 'januar', 'leden', 'ledn', 'jan'], ['fevral', 'ljut', 'lut', 'februar', 'unor', 'feb'], ['mart', 'berez', 'marec', 'marc', 'brez', 'mar'],
  ['aprel', 'kvit', 'april', 'duben', 'dubn', 'apr'], ['maj', 'maja', 'trav', 'kveten', 'kvetn', 'may'], ['ijun', 'cerv', 'jun'],
  ['ijul', 'lip', 'jul', 'cervenec'], ['avgust', 'serp', 'august', 'srpen', 'srpn', 'aug'], ['sentjabr', 'veres', 'septemb', 'zari', 'sep'],
  ['oktjabr', 'zovt', 'oktob', 'rijen', 'rijn', 'oct'], ['nojabr', 'listopad', 'novemb', 'nov'], ['dekabr', 'grud', 'hrud', 'decemb', 'prosin', 'dec'],
]
const DEADLINE = ['do', 'by', 'until', 'till', 'deadline', 'dedlajn']
const ALARM = ['budilnik', 'budylnyk', 'budik', 'alarm', 'razbud', 'rozbud', 'zobud', 'wake']
const MEETING = ['sozvon', 'zvonok', 'dzvinok', 'vstreca', 'zustric', 'meeting', 'call', 'stretnut', 'schodz', 'schuz', 'hovor', 'porada', 'zoom', 'teams']
const TASK = ['sdelat', 'zrobit', 'zrobyty', 'urobit', 'spravit', 'udelat', 'todo', 'task', 'zadaca', 'zavdann', 'uloha', 'ukol', 'napisat', 'napysat', 'fix', 'pocinit']
const INCOME = ['polucil', 'otrimav', 'otrymav', 'zarobil', 'zarobyv', 'zarplat', 'oplata ot', 'prijem', 'prijal', 'vyplat', 'income', 'salary', 'received', 'got paid', 'honorar']
const WORKS: [QuickResult['workKind'], string[]][] = [
  ['credit', ['zacet', 'zalik', 'zapocet', 'credit']],
  ['exam', ['ekzamen', 'ispit', 'skusk', 'zkousk', 'exam']],
  ['project', ['kursov', 'semestraln', 'projekt po', 'coursework', 'term paper']],
  ['assignment', ['zadanie', 'domask', 'domasn', 'referat', 'assignment', 'homework', 'esej', 'essay', 'uloha z', 'ukol z']],
]
// Expense / income categories by keyword prefixes
const EXPENSE_CATS: [string, string[]][] = [
  ['food', ['kof', 'kav', 'coffee', 'cofe', 'cappuc', 'latte', 'obed', 'obid', 'lunch', 'uzin', 'vecer', 'dinner', 'zavtrak', 'snidan', 'ranajk', 'breakfast', 'eda', 'jidl', 'jedl', 'food',
    'produkt', 'potravin', 'groceries', 'grocer', 'lidl', 'billa', 'tesco', 'kaufland', 'atb', 'silpo', 'restoran', 'restaur', 'kafe', 'cafe', 'pizz', 'pic', 'burger', 'sushi', 'pivo', 'beer', 'caj', 'tea', 'cokolad', 'chleb', 'hleb', 'mleko', 'moloko']],
  ['transport', ['taksi', 'taxi', 'uber', 'bolt', 'benzin', 'palivo', 'fuel', 'gas', 'avtobus', 'autobus', 'bus', 'tramvaj', 'tram', 'metro', 'vlak', 'poezd', 'pojizd', 'train', 'mhd', 'proezd', 'proizd', 'parkov', 'parking', 'bilet', 'listok', 'jizdenk', 'ticket']],
  ['home', ['arend', 'orend', 'najom', 'najem', 'rent', 'kvartir', 'byt', 'kommunal', 'komunal', 'svet', 'elektr', 'electric', 'plyn', 'voda', 'water', 'domov']],
  ['software', ['hosting', 'host', 'domen', 'domain', 'podpisk', 'pidpysk', 'predplatn', 'subscript', 'netflix', 'spotify', 'github', 'chatgpt', 'claude', 'figma', 'adobe', 'icloud', 'google one', 'vpn', 'licenc', 'license', 'internet', 'mobil', 'telefon']],
  ['tech', ['noutbuk', 'laptop', 'notebook', 'monitor', 'klaviatur', 'keyboard', 'mys', 'mouse', 'naushnik', 'navusnyk', 'sluchadl', 'headphon', 'kabel', 'cable', 'zarjad', 'charger', 'ssd', 'disk', 'iphone', 'pixel', 'samsung']],
  ['fun', ['kino', 'cinema', 'film', 'igr', 'hra', 'game', 'steam', 'koncert', 'concert', 'bar', 'klub', 'club', 'teatr', 'divadl', 'theatre', 'theater', 'podarok dlja']],
  ['health', ['apte', 'lekar', 'lekarn', 'pharm', 'vrac', 'likar', 'doctor', 'stomat', 'zubn', 'dentist', 'tabletk', 'liek', 'lik', 'medic', 'sport', 'fitnes', 'gym', 'posilov', 'bazen', 'pool']],
]
const INCOME_CATS: [string, string[]][] = [
  ['salary', ['zarplat', 'vyplat', 'plat ', 'salary', 'mzd']],
  ['projects', ['sajt', 'web', 'lending', 'landing', 'proekt', 'projekt', 'project', 'dizajn', 'design', 'kod', 'code', 'aplikac', 'app', 'eshop', 'e-shop']],
  ['support', ['podderzk', 'pidtrymk', 'podpor', 'udrzb', 'support', 'maintenance', 'servis']],
  ['gift', ['podar', 'darcek', 'darek', 'gift']],
  ['refund', ['vozvrat', 'povernen', 'vratk', 'vratenie', 'refund', 'cashback', 'kesbek']],
  ['sale', ['prodaz', 'prodal', 'predaj', 'predal', 'prodej', 'sale', 'sold']],
]
const CURRENCY_WORDS: [QuickResult['currency'], RegExp][] = [
  ['EUR', /^(€|eur|euro|eura|eur[oa]?|evro|jevro|evra)$/],
  ['UAH', /^(₴|uah|grn|hrn|griven|grivn|hryvn\w*|hrivn\w*)$/],
  ['USD', /^(\$|usd|dol+ar\w*|dollars?|bucks?)$/],
]
const has = (folded: string, list: string[]) => list.some((w) => new RegExp(`(^|[^a-z])${w.replace(/ /g, '\\s')}`).test(folded))
const catOf = (folded: string, cats: [string, string[]][]) => cats.find(([, keys]) => has(folded, keys))?.[0]

// ===== Main =====
export function parseQuick(input: string, ctx: QuickCtx): QuickResult {
  const text = input.trim().replace(/\s+/g, ' ')
  if (!text) return { kind: null, confidence: 0 }
  let rest = ` ${text} ` // original-case text; recognised parts are cut out of it
  const cut = (part: string) => (rest = rest.replace(part, ' '))
  const f = fold(text)

  // --- Amount and currency: "3.5€", "€3,50", "120 грн", "+500€", "1 200 Kč" ---
  let amount: number | undefined
  let currency: QuickResult['currency']
  let plus = false
  const money = text.match(/(^|\s)([+−-]?)\s*(€|\$|₴)?\s*(\d{1,3}(?:[  ]\d{3})+|\d+)(?:[.,](\d{1,2}))?\s*(€|\$|₴|[a-zA-Zа-яА-ЯёЁєЄіІїЇ]{2,9}\.?)?(?=\s|$|[,;!?])/u)
  if (money) {
    const sym = money[3] || money[6] || ''
    const cur = CURRENCY_WORDS.find(([, rx]) => rx.test(fold(sym.replace(/\.$/, ''))))?.[0]
    const value = Number(`${money[4]!.replace(/[  ]/g, '')}.${money[5] ?? '0'}`)
    // A number with ":" is a time; a bare number counts only with a currency or "+"
    const isTime = /^\d{1,2}$/.test(money[4]!) && /[:.]\d{2}(?!\d)/.test(text.slice(money.index! + money[0].indexOf(money[4]!))) && !cur
    if (!isTime && (cur || money[2] === '+' || money[5] !== undefined || catOf(f, EXPENSE_CATS))) {
      amount = value
      currency = cur
      plus = money[2] === '+'
      cut(money[0].trim())
    }
  }

  // --- Dates ---
  let date: string | undefined
  let deadline = false
  const fwords = words(fold(rest))
  const owords = words(rest)
  const take = (i: number) => {
    const w = owords[i]
    if (w) cut(w)
    // "до" / "do" / "by" right before the date = deadline
    if (i > 0 && DEADLINE.includes(fwords[i - 1]!)) {
      deadline = true
      if (owords[i - 1]) cut(owords[i - 1]!)
    }
    // "в" / "v" / "on" / "o" before the date
    else if (i > 0 && ['v', 'vo', 'u', 'on', 'na'].includes(fwords[i - 1]!) && owords[i - 1]) cut(owords[i - 1]!)
  }
  fwords.forEach((w, i) => {
    if (date) return
    if (TODAY.some((x) => w.startsWith(x))) {
      date = ctx.today
      take(i)
    } else if (AFTER.some((x) => w.startsWith(x))) {
      date = addDays(ctx.today, 2)
      take(i)
    } else if (TOMORROW.some((x) => w.startsWith(x))) {
      date = addDays(ctx.today, 1)
      take(i)
    } else {
      const wd = WEEKDAYS.find(([, keys]) => keys.some((k) => (k.length <= 3 ? w === k : w.startsWith(k))))
      if (wd) {
        const now = new Date(`${ctx.today}T12:00:00`).getDay()
        date = addDays(ctx.today, ((wd[0] - now + 7) % 7) || 7)
        take(i)
      }
    }
  })
  // "15.12", "15.12.2026", "15/12"
  if (!date) {
    const m = rest.match(/(^|\s)(\d{1,2})[./](\d{1,2})(?:[./](\d{2,4}))?\.?(?=\s|$)/)
    if (m && Number(m[3]) >= 1 && Number(m[3]) <= 12 && Number(m[2]) >= 1 && Number(m[2]) <= 31 && !/[:]/.test(m[0])) {
      const [y] = ctx.today.split('-').map(Number)
      let year = m[4] ? Number(m[4].length === 2 ? `20${m[4]}` : m[4]) : y!
      let d = `${year}-${pad(Number(m[3]))}-${pad(Number(m[2]))}`
      if (!m[4] && d < ctx.today) d = `${++year}-${pad(Number(m[3]))}-${pad(Number(m[2]))}`
      date = d
      const idx = words(rest).indexOf(m[0].trim())
      if (idx > 0 && DEADLINE.includes(fold(words(rest)[idx - 1]!))) {
        deadline = true
        cut(words(rest)[idx - 1]!)
      }
      cut(m[0].trim())
    }
  }
  // "15 декабря", "15. decembra", "Dec 15"
  if (!date) {
    const ws = words(rest)
    for (let i = 0; i < ws.length && !date; i++) {
      const month = MONTHS.findIndex((keys) => keys.some((k) => (k.length <= 3 ? fold(ws[i]!).replace(/\.$/, '') === k : fold(ws[i]!).startsWith(k))))
      if (month < 0) continue
      const num = [ws[i - 1], ws[i + 1]].map((x) => Number((x ?? '').replace(/\.$/, ''))).find((n) => n >= 1 && n <= 31)
      if (!num) continue
      const [y] = ctx.today.split('-').map(Number)
      let d = `${y}-${pad(month + 1)}-${pad(num)}`
      if (d < ctx.today) d = `${y! + 1}-${pad(month + 1)}-${pad(num)}`
      date = d
      cut(ws[i]!)
      cut(String((ws[i - 1] ?? '').replace(/\.$/, '')) === String(num) ? ws[i - 1]! : ws[i + 1]!)
      if (i > 1 && DEADLINE.includes(fold(ws[i - 2]!))) {
        deadline = true
        cut(ws[i - 2]!)
      }
    }
  }

  // --- Time: "14:00", "6.30", "в 14", "o 9h", "2pm" ---
  let time: string | undefined
  const tm = rest.match(/(^|\s)(?:(?:в|о|об|o|at|um|na)\s+)?(\d{1,2})(?:[:.](\d{2})|\s*(am|pm|h|ч|час\w*|hod\w*)|(?=\s|$))(?=\s|$|[,;])/i)
  if (tm && (tm[3] || tm[4] || /\s(в|о|об|o|at|na)\s+\d/i.test(` ${tm[0]}`))) {
    let h = Number(tm[2])
    const min = Number(tm[3] ?? 0)
    if (/pm/i.test(tm[4] ?? '') && h < 12) h += 12
    if (/am/i.test(tm[4] ?? '') && h === 12) h = 0
    if (h <= 23 && min <= 59) {
      time = `${pad(h)}:${pad(min)}`
      cut(tm[0].trim())
    }
  }

  // --- People: @mention (task assignee), client by name ---
  let assignee_id: number | undefined
  const at = rest.match(/@([\w.-]+)/)
  if (at) {
    const u = ctx.users?.find((x) => x.username.toLowerCase() === at[1]!.toLowerCase() || sameStem(at[1]!, x.name.split(' ')[0] ?? ''))
    if (u) {
      assignee_id = u.id
      cut(at[0])
    }
  }
  let client_id: number | undefined
  for (const c of ctx.clients ?? []) {
    const names = [c.name, ...c.name.split(' '), c.company ?? ''].filter((n) => n.length >= 3)
    const hit = words(rest).find((w) => names.some((n) => sameStem(w, n)))
    if (hit) {
      client_id = c.id
      // "с Анной" / "for Anna" / "pre Annu": the client's name stays in the title, the money note drops it
      break
    }
  }

  const clean = (s: string) => s.replace(/\s+/g, ' ').replace(/^[\s,.:;–-]+|[\s,.:;–-]+$/g, '').trim()
  const cap = (s: string) => s.charAt(0).toUpperCase() + s.slice(1)

  // --- Alarm ---
  if (has(f, ALARM) && time) {
    const days = has(f, ['budn', 'buden', 'weekday', 'pracovn', 'v tyzdni', 'cez tyzden', 'po-pi', 'po–pi'])
      ? [1, 2, 3, 4, 5] : has(f, ['kazd', 'kozn', 'every day', 'daily', 'denne', 'kazdy den', 'kazdyj den']) ? [0, 1, 2, 3, 4, 5, 6] : []
    const label = clean(rest.replace(new RegExp(`(^|\\s)(${['будильник', 'budík', 'budik', 'alarm', 'разбуди', 'розбуди', 'zobuď', 'wake me up', 'wake up', 'по будням', 'каждый день', 'кожен день', 'every day', 'weekdays', 'denne'].join('|')})(?=\\s|$)`, 'gi'), ' '))
    return { kind: 'alarm', confidence: 0.95, time, days, title: label ? cap(label) : undefined }
  }

  // --- Study deadline ---
  const work = WORKS.find(([, keys]) => has(f, keys))
  if (work && amount === undefined) {
    let subject_id: number | undefined
    for (const s of ctx.subjects ?? []) {
      if (words(rest).some((w) => s.name.split(/\s+/).some((n) => n.length >= 3 && sameStem(w, n)))) {
        subject_id = s.id
        break
      }
    }
    return { kind: 'work', confidence: date ? 0.9 : 0.55, workKind: work[0], title: cap(clean(rest)), date, time, subject_id }
  }

  // --- Money ---
  if (amount !== undefined) {
    const income = plus || has(f, INCOME)
    const category = catOf(f, income ? INCOME_CATS : EXPENSE_CATS) ?? (income && client_id ? 'projects' : 'other')
    let note = rest
    if (client_id && income) note = note.replace(/(^|\s)(от|від|od|from|pre|for)(?=\s)/gi, ' ')
    note = clean(note.replace(/(^|\s)(за|na|for|pre)(?=\s|$)/gi, ' '))
    return {
      kind: income ? 'income' : 'expense', confidence: currency || plus ? 0.9 : 0.7,
      amount, currency: currency ?? ctx.currency ?? 'EUR', category, title: note ? cap(note) : undefined, date: date ?? ctx.today, client_id,
    }
  }

  // --- Event (time given) vs task (deadline, @mention, task words) ---
  const title = cap(clean(rest))
  const isTask = deadline || assignee_id !== undefined || has(f, TASK)
  if (time && !deadline) {
    const [h, m] = time.split(':').map(Number)
    const endMin = Math.min(h! * 60 + m! + 60, 23 * 60 + 59)
    return { kind: 'event', confidence: date || has(f, MEETING) ? 0.9 : 0.7, title, date: date ?? ctx.today, time, end: `${pad(Math.floor(endMin / 60))}:${pad(endMin % 60)}`, client_id }
  }
  if (isTask) return { kind: 'task', confidence: 0.85, title, date, assignee_id, client_id }
  if (has(f, MEETING) && date) return { kind: 'event', confidence: 0.6, title, date, time: '09:00', end: '10:00', client_id }
  // Nothing recognised: a task is the safest guess, but ask
  return { kind: 'task', confidence: 0.4, title, date, client_id }
}
