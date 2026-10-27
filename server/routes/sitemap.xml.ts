import site from '../../data/site'

// sitemap.xml с hreflang-альтернативами: общая страница + личные страницы на каждом языке
export default defineEventHandler((event) => {
  const today = new Date().toISOString().slice(0, 10)
  const paths = ['', ...site.people.map((p) => `/${p.slug}`)]

  const entries = paths.flatMap((path) => {
    const alternates = site.languages
      .map((l) => `    <xhtml:link rel="alternate" hreflang="${l}" href="${site.domain}/${l}${path}"/>`)
      .concat(`    <xhtml:link rel="alternate" hreflang="x-default" href="${site.domain}/${site.defaultLang}${path}"/>`)
      .join('\n')
    return site.languages.map(
      (l) => `  <url>
    <loc>${site.domain}/${l}${path}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>${path ? '0.8' : l === site.defaultLang ? '1.0' : '0.9'}</priority>
${alternates}
  </url>`
    )
  })

  setHeader(event, 'Content-Type', 'application/xml; charset=utf-8')
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
${entries.join('\n')}
</urlset>
`
})
