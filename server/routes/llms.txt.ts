import site from '../../data/site'
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

> ${site.brand} is a two-person freelance studio based in ${site.location.city}, Slovakia. We build fast websites and web applications (Nuxt, FastAPI), automate business processes with AI and programming (chatbots, document processing, API integrations, automatic reports), do UI/UX design, SEO and GEO (generative engine optimization). Clients in Slovakia, Czech Republic and Ukraine. We work in Slovak, Czech and Ukrainian.

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

## Pages
${site.languages
  .map((l) => `- [${all[l]!.label} (${langName[l]})](${site.domain}/${l})${site.people.map((p) => ` · [${p.shortName}](${site.domain}/${l}/${p.slug})`).join('')}`)
  .join('\n')}

## Contact
- Email: ${site.email}
- Phone: ${site.phone}
`
})
