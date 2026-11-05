// Quick input parser (app/utils/quickParse.ts). Run: npm test  (Node 22+, no test libraries)
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { parseQuick } from '../app/utils/quickParse.ts'

// Thursday 5 November 2026
const ctx = {
  today: '2026-11-05',
  currency: 'EUR',
  clients: [{ id: 1, name: 'Anna Kováčová', company: 'Kaviareň Anna' }, { id: 2, name: 'Peter Novák' }, { id: 3, name: 'Олег' }],
  users: [{ id: 10, username: 'roman', name: 'Roman' }, { id: 11, username: 'seb', name: 'Sebastian' }],
  subjects: [{ id: 5, name: 'Právo IT' }, { id: 6, name: 'Databázové systémy' }, { id: 7, name: 'Математика' }],
}
const parse = (s) => parseQuick(s, ctx)
// [phrase, expected fields]
const CASES = [
  // Expenses
  ['кофе 3.5€', { kind: 'expense', amount: 3.5, currency: 'EUR', category: 'food', title: 'Кофе', date: '2026-11-05' }],
  ['обед 120 грн', { kind: 'expense', amount: 120, currency: 'UAH', category: 'food' }],
  ['káva 2,80 €', { kind: 'expense', amount: 2.8, currency: 'EUR', category: 'food' }],
  ['coffee $4', { kind: 'expense', amount: 4, currency: 'USD', category: 'food' }],
  ['таксі 250 грн', { kind: 'expense', amount: 250, currency: 'UAH', category: 'transport' }],
  ['hosting 49 eur', { kind: 'expense', amount: 49, category: 'software' }],
  ['нájom 450€', { kind: 'expense', amount: 450 }],
  ['аренда 450 евро', { kind: 'expense', amount: 450, currency: 'EUR', category: 'home' }],
  ['lekáreň 12.40€ včera', { kind: 'expense', amount: 12.4, category: 'health' }],
  ['kino 9 € zajtra', { kind: 'expense', category: 'fun', date: '2026-11-06' }],
  ['€15 netflix', { kind: 'expense', amount: 15, category: 'software' }],
  ['обід 85', { kind: 'expense', amount: 85, currency: 'EUR', category: 'food' }],
  ['ноутбук 1 200 €', { kind: 'expense', amount: 1200, category: 'tech' }],
  // Income
  ['+500€ Анна сайт', { kind: 'income', amount: 500, client_id: 1, category: 'projects' }],
  ['+1200 зарплата', { kind: 'income', amount: 1200, category: 'salary' }],
  ['получил 300€ от Олега за лендинг', { kind: 'income', amount: 300, client_id: 3, category: 'projects' }],
  ['received $800 from Peter', { kind: 'income', amount: 800, currency: 'USD', client_id: 2 }],
  ['príjem 250 € web pre Annu', { kind: 'income', amount: 250, client_id: 1, category: 'projects' }],
  // Events
  ['завтра 14:00 созвон с Анной', { kind: 'event', date: '2026-11-06', time: '14:00', end: '15:00', client_id: 1, title: 'Созвон с Анной' }],
  ['zajtra o 10:30 stretnutie s Petrom', { kind: 'event', date: '2026-11-06', time: '10:30', client_id: 2 }],
  ['meeting with Anna on friday at 3pm', { kind: 'event', date: '2026-11-06', time: '15:00', client_id: 1 }],
  ['в понедельник 9:00 планёрка', { kind: 'event', date: '2026-11-09', time: '09:00' }],
  ['dnes 18:00 tréning', { kind: 'event', date: '2026-11-05', time: '18:00' }],
  ['15.12 19:00 vianočný večierok', { kind: 'event', date: '2026-12-15', time: '19:00' }],
  ['післязавтра о 16 зустріч', { kind: 'event', date: '2026-11-07', time: '16:00' }],
  // Tasks
  ['сделать лендинг до пятницы @Roman', { kind: 'task', date: '2026-11-06', assignee_id: 10, title: 'Сделать лендинг' }],
  ['urobiť faktúru do piatku', { kind: 'task', date: '2026-11-06' }],
  ['fix login bug by monday @seb', { kind: 'task', date: '2026-11-09', assignee_id: 11 }],
  ['зробити дизайн до 20.11', { kind: 'task', date: '2026-11-20' }],
  ['napísať Petrovi', { kind: 'task', client_id: 2 }],
  // Alarms
  ['будильник 6:30', { kind: 'alarm', time: '06:30', days: [] }],
  ['budík 7:15 cez týždeň', { kind: 'alarm', time: '07:15', days: [1, 2, 3, 4, 5] }],
  ['alarm 5:45 every day', { kind: 'alarm', time: '05:45', days: [0, 1, 2, 3, 4, 5, 6] }],
  ['розбуди о 8:00', { kind: 'alarm', time: '08:00' }],
  // Study
  ['зачёт по праву 15.12', { kind: 'work', workKind: 'credit', date: '2026-12-15', subject_id: 5 }],
  ['skúška z databáz 20. januára', { kind: 'work', workKind: 'exam', date: '2027-01-20', subject_id: 6 }],
  ['іспит з математики 10.01', { kind: 'work', workKind: 'exam', date: '2027-01-10', subject_id: 7 }],
  ['homework Právo IT friday', { kind: 'work', workKind: 'assignment', date: '2026-11-06', subject_id: 5 }],
  ['курсовая 01.12', { kind: 'work', workKind: 'project', date: '2026-12-01' }],
]

for (const [phrase, expected] of CASES) {
  test(phrase, () => {
    const r = parse(phrase)
    for (const [key, value] of Object.entries(expected)) assert.deepEqual(r[key], value, `${key} of "${phrase}": ${JSON.stringify(r)}`)
    assert.ok(r.confidence >= 0.6, `confident: ${JSON.stringify(r)}`)
  })
}

test('unclear text asks to clarify', () => {
  const r = parse('что-то непонятное')
  assert.ok(r.confidence < 0.6)
})
test('empty text', () => assert.equal(parse('   ').kind, null))
test('plain numbers in a title are not money', () => assert.equal(parse('сделать 3 баннера до пятницы').kind, 'task'))
