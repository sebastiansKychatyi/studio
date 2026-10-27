# Duo Studio — portfolio website (Nuxt 4 + Vue 3)

Website of a development team from **Bratislava and Nitra**: AI automation, website and app development, mini games, process optimization through code automation and AI integration.
Available in three languages: **Slovak** (`/sk`), **Czech** (`/cs`) and **Ukrainian** (`/uk`).

## Pages

| Page | URL | Design |
|---|---|---|
| Studio page (services, AI automation, portfolio, Lab, FAQ) | `/sk` | light, gradients |
| Sebastian's personal page | `/sk/sebastian` | "developer": terminal, monospace, activity grid |
| Roman's personal page | `/sk/roman` | "creative": serif type, stickers, shapes, blob cursor |
| Résumé (A4 sheet, "Download PDF" button) | `/sk/sebastian/cv`, `/sk/roman/cv` | clean, for employers |
| Lab concepts | `/sk/lab/noir`, `/pulse`, `/kinetic`, `/verde` | four different styles |

## Language by visitor location

- **Root `/`** picks the language in this order: language chosen manually (cookie `lang`) → country by IP (SK → `sk`, CZ → `cs`, UA → `uk`) → browser language → Slovak.
- **Language pages** never redirect automatically (Googlebot crawls from the US and must see every version). Instead, a hint is shown in the visitor's language, e.g. "Схоже, ви з України — перейти на українську?".
- The country is detected with the free `api.country.is` service (no API key). Country → language mapping: `geoLanguages` in `data/site.ts`.

## Local SEO

Target cities in priority order: **Bratislava, Nitra → Prague → Kyiv, Uzhhorod** (`cities` in `data/site.ts`).

- Each language version targets its own market: SK — Bratislava & Nitra, CZ — Prague, UA — Kyiv & Uzhhorod (titles, descriptions, texts, FAQ).
- schema.org `ProfessionalService` lists the cities in `areaServed`, plus `geo.*` meta tags.
- Server-rendered page per language and person: title, description, canonical, `hreflang` + x-default, Open Graph.
- schema.org (JSON-LD): ProfessionalService, Person, ProfilePage, services, FAQPage, portfolio with links to live sites and GitHub.
- `/sitemap.xml` (all languages and pages with hreflang), `/robots.txt` explicitly allowing AI crawlers, `/llms.txt` for AI assistants (GEO).

## Links to share as a résumé

| For | Link | Opens |
|---|---|---|
| Clients / social media | `duostudio.sk/roman` | Roman's personal page in the visitor's language |
| Employers | `duostudio.sk/roman/cv` | Roman's résumé (downloadable as PDF) |
| Same for Sebastian | `duostudio.sk/sebastian`, `/sebastian/cv` | |

- Short links are files `public/<slug>/index.html` and `public/<slug>/cv/index.html` (they pick the language via `public/go.js`). If you change a person's `slug`, rename these folders too.
- Link previews (Telegram, LinkedIn, Messenger) show the person's name and role: `public/og-sebastian.png`, `public/og-roman.png`.
- Résumé pages are `noindex` so they don't compete with the personal pages in search.
- PDF: click "Stiahnuť PDF" → choose "Save as PDF" in the print dialog.

## Portfolio

- Real projects with screenshots and links: e-Drivebook (e-drivebook.com), Expert SK, Bratislava Technical Company, ONYX Business Residence, Hodinový manžel Nitra, AmStars, Travel Planner API.
- **Clickable design prototypes** (Roman's design concepts): Nordic Living (furniture e-shop + UI kit), Slnečné Byty (real-estate mobile app), FitFlow (fitness app with dark mode). Clicking a card opens a dialog with an interactive prototype; the card cover is a live scaled-down copy. Code: `app/components/Proto*.vue`, `DesignModal.vue`.

## Lab — design concepts

Four sites for fictional brands in very different styles, labelled "Koncept — fiktívna značka".

| Concept | URL | Style and interactions |
|---|---|---|
| Noir — restaurant | `/sk/lab/noir` | dark + gold, self-drawing plate, menu with cursor preview, table booking |
| Pulse — SaaS / AI | `/sk/lab/pulse` | glass and gradients, live dashboard, AI chat (simulated), pricing toggle |
| Kinetic — e-shop | `/sk/lab/kinetic` | brutalism, working cart, "flying" product, draggable lookbook |
| Verde — real estate | `/sk/lab/verde` | parallax illustration, sticky story, apartment picker on the facade |

Code: `app/components/Concept*.vue`; texts in all three languages live inside each component (`useConceptCopy`); list: `data/concepts.ts`. Covers `public/img/concepts/*.jpg` are screenshots of the pages themselves (`?cover=1` hides the studio bar).

## Getting started

```bash
npm install
npm run dev        # http://localhost:3000
npm run generate   # static build in .output/public — upload this folder to hosting
```

> Nuxt 4.6 expects Node.js ≥ 22.21 (or 24.11+). It runs on 22.16 but prints a warning.

## Where to edit content

| What | File |
|---|---|
| Domain, e-mail, phone, cities, people (name, slug, design, skills, links), projects | `data/site.ts` |
| All texts: studio page, personal pages (`personal`), project descriptions, FAQ | `data/locales/sk.ts`, `cs.ts`, `uk.ts` |
| Project screenshots | `public/img/projects/*.jpg` (1200×750) |
| Colors and animations of the studio page | `app/assets/css/main.css` |
| Personal page designs | `app/components/ProfileDev.vue`, `ProfileCreative.vue` |

**Before going live:** replace `domain` in `data/site.ts` and `https://duostudio.sk` in `public/index.html` and the short-link pages, and fill in Roman's details (surname, texts in `personal.people.p2`, real projects instead of the `placeholder: true` concepts).

### Adding a portfolio project
1. Add an object to `projects` in `data/site.ts` (`author: 'p1'` or `'p2'`, links `url` / `repo`).
2. Add `work.projects['id'].desc` to all three `data/locales/*` files.
3. Screenshot: `public/img/projects/<id>.jpg`, path in `image`. Without a screenshot a CSS mock is drawn (`layout: 4` — "code/API" mock).

## Structure

```
app/
  pages/index.vue            studio page
  pages/[slug]/index.vue     personal pages
  pages/[slug]/cv.vue        résumé pages
  pages/lab/[id].vue         Lab concepts
  components/                sections, ProfileDev, ProfileCreative, Concept*, Proto*, DesignModal, GeoLangHint…
  composables/useSite.ts     texts for the current language
  composables/useSiteSeo.ts  meta tags and JSON-LD
  composables/useGeoLang.ts  visitor country and language choice
  plugins/motion.ts          animations: v-reveal, v-tilt, v-magnetic, v-spot
data/                        content and settings
server/routes/               sitemap.xml, robots.txt, llms.txt, site.webmanifest
public/                      images, root index.html and short links (language by country)
```
