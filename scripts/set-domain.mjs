// Меняет основной домен сайта во всех местах сразу:
//   npm run set-domain -- https://studio.k2drive.com
// Обновляет data/site.ts (canonical, hreflang, sitemap, schema.org берут домен оттуда)
// и статические файлы в public/ (корневой index.html и короткие ссылки /sebastian, /roman …).
import { readFileSync, writeFileSync, readdirSync, statSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const arg = process.argv[2]

if (!arg || !/^https?:\/\/[^\s/]+$/.test(arg.replace(/\/$/, ''))) {
  console.error('Usage: npm run set-domain -- https://example.com')
  process.exit(1)
}
const next = arg.replace(/\/$/, '')

const sitePath = join(root, 'data/site.ts')
const site = readFileSync(sitePath, 'utf8')
const current = site.match(/domain: '([^']+)'/)?.[1]
if (!current) {
  console.error('Could not find `domain` in data/site.ts')
  process.exit(1)
}
if (current === next) {
  console.log(`Domain is already ${next}`)
  process.exit(0)
}

const files = [sitePath]
const walk = (dir) => {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name)
    if (statSync(p).isDirectory()) walk(p)
    else if (p.endsWith('.html')) files.push(p)
  }
}
walk(join(root, 'public'))

let changed = 0
for (const file of files) {
  const text = readFileSync(file, 'utf8')
  const updated = text.split(current).join(next)
  if (updated !== text) {
    writeFileSync(file, updated)
    changed++
    console.log('updated', file.replace(root, '.'))
  }
}
console.log(`\n${current} → ${next} (${changed} files). Rebuild the site to apply.`)
console.log('Note: the domain text drawn inside public/og-*.png images is not changed.')
