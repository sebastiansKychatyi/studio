// Концепт-дизайны для вымышленных брендов — показывают, в каких стилях мы умеем работать.
// Страницы: /sk/lab/<id>. Тексты карточек — data/locales/<lang>.ts -> lab.items[id]
// Обложки: public/img/concepts/<id>.jpg (скриншоты самих страниц)

export const concepts = [
  { id: 'noir', name: 'Noir', colors: ['#0E0D0B', '#C9A45C'], tags: ['Fine dining', 'Dark UI', 'Serif'] },
  { id: 'pulse', name: 'Pulse', colors: ['#5B4BFF', '#22D3EE'], tags: ['SaaS', 'AI chat', 'Dashboard'] },
  { id: 'kinetic', name: 'Kinetic', colors: ['#111111', '#D7FF3A'], tags: ['E-shop', 'Brutalism', 'Cart'] },
  { id: 'verde', name: 'Verde', colors: ['#1F3D2B', '#A8C3A0'], tags: ['Real estate', 'Parallax', 'Picker'] },
] as const

export type ConceptId = (typeof concepts)[number]['id']
