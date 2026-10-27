// Changes the main site domain everywhere:
//   npm run set-domain -- https://studio.k2drive.com
// Updates data/site.ts (canonical, hreflang, sitemap, schema.org)
// and the static pages in public/ (root index.html, short links).
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
