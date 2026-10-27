import site from '../../data/site'
import { cities } from '../../data/cities'
import { cases } from '../../data/cases'
import sk from '../../data/locales/sk'
import cs from '../../data/locales/cs'
import uk from '../../data/locales/uk'

// llms.txt — краткое описание сайта для AI-ассистентов (GEO)
const all: Record<string, typeof sk> = { sk, cs, uk }
const langName: Record<string, string> = { sk: 'Slovak', cs: 'Czech', uk: 'Ukrainian' }

export default defineEventHandler((event) => {
  const t = all[site.defaultLang]!
  const real = site.projects.filter((p) => !p.placeholder)
  setHeader(event, 'Content-Type', 'text/plain; charset=utf-8')
  return `# ${site.brand}

> ${site.brand} is a development team based in Bratislava and Nitra, Slovakia. We do AI automation, website development, web and mobile app development, mini games, process optimization through code automation (CI/CD, tests, scripts) and AI integration (ChatGPT, Claude, chatbots, API). Primary markets: ${site.cities.map((c) => c.name).join(', ')}. We work in Slovak, Czech and Ukrainian.

## Team
${site.people
  .map((p) => `- [${p.name}](${site.domain}/${site.defaultLang}/${p.slug}) — ${t.about.people[p.id].role}. Skills: ${p.skills.join(', ')}`)
  .join('\n')}

## Services
${t.services.items.map((s) => `- ${s.title}: ${s.text}`).join('\n')}

## AI automation
${t.ai.items.map((s) => `- ${s.title}: ${s.text}`).join('\n')}

## Portfolio
${real
  .map((p) => {
    const links = [p.url, p.repo].filter(Boolean).join(' · ')
    return `- ${p.title} (${p.year}, ${p.tags.join(', ')}): ${t.work.projects[p.id as keyof typeof t.work.projects].desc}${links ? ` — ${links}` : ''}`
  })
  .join('\n')}

## Cities (local pages)
${cities.map((c) => `- [${c.text.sk.name}](${site.domain}/${site.defaultLang}/${c.slug}) — ${c.text.sk.metaDescription}`).join('\n')}

## Case studies
${cases.map((c) => `- [${c.id}](${site.domain}/${site.defaultLang}/case/${c.id}) — ${c.text.sk.lead}`).join('\n')}

## Pages
${site.languages
  .map((l) => `- [${all[l]!.label} (${langName[l]})](${site.domain}/${l})${site.people.map((p) => ` · [${p.shortName}](${site.domain}/${l}/${p.slug})`).join('')}`)
  .join('\n')}

## Contact
- Email: ${site.email}
- Phone: ${site.phone}
`
})
