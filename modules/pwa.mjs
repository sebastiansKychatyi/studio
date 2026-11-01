// Team panel service worker: pwa/sw.js + this build's version + the list of hashed build files
// to precache, written to the public output as /sw.js. Not served in dev (no stale caches while coding).
// Also sets runtimeConfig.public.appVersion (shown in panel settings).
import { execSync } from 'node:child_process'
import { readdirSync, readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { defineNuxtModule } from 'nuxt/kit'

/** @param {string} dir @returns {string[]} */
function walk(dir) {
  return readdirSync(dir, { withFileTypes: true }).flatMap((e) => (e.isDirectory() ? walk(join(dir, e.name)).map((f) => `${e.name}/${f}`) : [e.name]))
}

// Build time + commit; every deploy gets a new worker
function version() {
  let commit = ''
  try {
    commit = execSync('git rev-parse --short HEAD', { stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim()
  } catch { /* not a git checkout */ }
  return `${new Date().toISOString().slice(0, 16).replace('T', ' ')}${commit ? ` · ${commit}` : ''}`
}

export default defineNuxtModule({
  meta: { name: 'pwa' },
  setup(_, nuxt) {
    const appVersion = version()
    nuxt.options.runtimeConfig.public.appVersion = appVersion
    if (nuxt.options.dev) return
    nuxt.hook('nitro:build:public-assets', (nitro) => {
      const out = nitro.options.output.publicDir
      const base = nuxt.options.app.buildAssetsDir.replace(/^\/|\/$/g, '')
      // Scripts, styles, fonts and route meta; latest.json must stay fresh
      const files = walk(join(out, base))
        .filter((f) => /\.(js|css|woff2?)$/.test(f) || (f.startsWith('builds/meta/') && f.endsWith('.json')))
        .map((f) => `/${base}/${f}`)
      const fontCss = nuxt.options.app.head.link?.find((l) => String(l.href).startsWith('https://fonts.googleapis.com/css'))?.href ?? ''
      const sw = readFileSync(join(nuxt.options.rootDir, 'pwa/sw.js'), 'utf8')
        .replace('__VERSION__', JSON.stringify(appVersion))
        .replace('__PRECACHE__', JSON.stringify(files))
        .replace('__FONT_CSS__', JSON.stringify(fontCss))
      writeFileSync(join(out, 'sw.js'), sw)
      console.info(`[pwa] sw.js: ${files.length} files to precache`)
    })
  },
})
