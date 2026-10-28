# Duo Studio — portfolio website (Nuxt 4 + Vue 3)

Website of a development team from **Bratislava and Nitra**: AI automation, website and app development, mini games, process optimization through code automation and AI integration.
Available in three languages: **Slovak** (`/sk`), **Czech** (`/cs`) and **Ukrainian** (`/uk`).

## Pages

| Page | URL | Design |
|---|---|---|
| Studio page (services, AI automation, portfolio, Lab, FAQ) | `/sk` | light, gradients |
| Sebastian's personal page | `/sk/sebastian` | "developer": terminal, monospace, activity grid |
| Roman's personal page | `/sk/roman` | "developer": terminal, monospace, activity grid (same theme as Sebastian, blue accent) |
| Résumé (A4 sheet, "Download PDF" button) | `/sk/sebastian/cv`, `/sk/roman/cv` | clean, for employers |
| Lab concepts | `/sk/lab/noir`, `/pulse`, `/kinetic`, `/verde` | four different styles |
| City pages (local SEO) | `/sk/bratislava`, `/sk/nitra`, `/cs/praha`, `/uk/kyiv`, `/uk/uzhhorod` (every city in all 3 languages) | studio style + map pin |
| Case studies | `/sk/case/e-drivebook`, `/sk/case/expertsk` | challenge → solution → features → results |
| Privacy policy (GDPR) | `/sk/privacy` | simple legal page |

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
- **City pages** (`data/cities.ts`): each city has its own title, description, H1, local benefits, local FAQ, projects and schema.org `Service` + `FAQPage` + `BreadcrumbList`. They are linked from the footer on every page. Add a city = add an object to `cities` (texts in sk / cs / uk with the correct grammatical case, e.g. "v Bratislave", "v Praze", "у Києві").
- **Case studies** (`data/cases.ts`): long pages Google likes, linked from the portfolio cards ("Prípadová štúdia"). Only verifiable facts — no invented numbers.

## Links to share as a résumé

| For | Link | Opens |
|---|---|---|
| Clients / social media | `studio.k2drive.com/roman` | Roman's personal page in the visitor's language |
| Employers | `studio.k2drive.com/roman/cv` | Roman's résumé (downloadable as PDF) |
| Same for Sebastian | `studio.k2drive.com/sebastian`, `/sebastian/cv` | |

- Short links are files `public/<slug>/index.html` and `public/<slug>/cv/index.html` (they pick the language via `public/go.js`). If you change a person's `slug`, rename these folders too.
- Link previews (Telegram, LinkedIn, Messenger) show the person's name and role: `public/og-sebastian.png`, `public/og-roman.png`.
- Résumé pages are `noindex` so they don't compete with the personal pages in search.
- PDF: click "Stiahnuť PDF" → choose "Save as PDF" in the print dialog.

## Portfolio

- Real projects with screenshots and links: e-Drivebook (e-drivebook.com), Expert SK, Bratislava Technical Company, ONYX Business Residence, Hodinový manžel Nitra, AmStars, Travel Planner API.
- Roman's real projects: Restaurant Reservation System (FastAPI + React, bachelor thesis), the Sharkrise Studio website and a GTM platform homepage UI concept.
- **Clickable product prototypes** (Roman's work rebuilt with demo data, no customer data or proprietary code): Classifieds Platform (listings, VIP and bump, crypto top-up with signed-webhook confirmation and idempotent replay), Subscription Billing (themed crypto checkout that settles an invoice and activates slots) and ReserveIt on the Restaurant Reservation System card (customer, owner and admin roles, dark and light theme, desktop and mobile preview). Team CRM and Leads Workspace prototypes are hidden for now: their components stay in `app/components/` and can be restored by re-adding the entries in `data/site.ts`. Clicking a card or the "Open prototype" button opens a dialog with the interactive prototype; the card cover is a live scaled-down copy. Sizes: `data/prototypes.ts`. Code: `app/components/Proto*.vue`, `DesignModal.vue`. Screenshots: `docs/roman-profile/`.

## Lab — design concepts

Four sites for fictional brands in very different styles, labelled "Koncept — fiktívna značka".

| Concept | URL | Style and interactions |
|---|---|---|
| Noir — restaurant | `/sk/lab/noir` | dark + gold, self-drawing plate, menu with cursor preview, table booking |
| Pulse — SaaS / AI | `/sk/lab/pulse` | glass and gradients, live dashboard, AI chat (simulated), pricing toggle |
| Kinetic — e-shop | `/sk/lab/kinetic` | brutalism, working cart, "flying" product, draggable lookbook |
| Verde — real estate | `/sk/lab/verde` | parallax illustration, sticky story, apartment picker on the facade |

Code: `app/components/Concept*.vue`; texts in all three languages live inside each component (`useConceptCopy`); list: `data/concepts.ts`. Covers `public/img/concepts/*.jpg` are screenshots of the pages themselves (`?cover=1` hides the studio bar).

## Contact form → Telegram + e-mail

The form posts to `/api/contact` (`server/api/contact.post.ts`), which sends the enquiry to **Telegram** and/or **e-mail via Web3Forms**. Spam protection: honeypot field, server-side validation, 5 requests / 10 min per IP. A GDPR consent checkbox is required.

1. Copy `.env.example` to `.env`.
2. Telegram: create a bot with @BotFather → `NUXT_TELEGRAM_BOT_TOKEN`; send the bot a message, open `https://api.telegram.org/bot<TOKEN>/getUpdates` and copy `chat.id` → `NUXT_TELEGRAM_CHAT_ID`.
3. E-mail: get a free access key at web3forms.com → `NUXT_WEB3FORMS_KEY`.

The API needs the site to run as a **Node server** (see Deployment). If no key is set or the site is hosted as plain static files, the form automatically falls back to opening the visitor's mail app.

## Team panel (login, kanban, alarms, expenses)

A private area for the team at `/<lang>/login` → `/<lang>/panel`. The login link is the user icon in the header (and in the mobile menu and footer). There is **no sign-up**: accounts are created directly in the database.

- **Tasks** (`/panel`): shared kanban boards. Create boards, add/rename/reorder/delete columns, add cards, drag cards between columns, edit a card (description, assignee, column) in a modal. The board refreshes on window focus and every 30 s, so changes from a teammate show up.
- **Expenses** (`/panel/expenses`): personal expense log in EUR, visible only to its owner. Month switcher, monthly total vs the previous month, average per day, breakdown by category, a 6-month chart, a list grouped by day (click a row to edit), CSV export for Excel.
- **Alarms** (`/panel/alarms`): personal alarms (time, label, weekdays; no weekday = rings once and then switches itself off). They ring with a sound, a full-screen dialog (stop / snooze 5 min) and a browser notification while the panel is open in some tab.

Architecture: the Nuxt pages are client-only (`routeRules`, noindex). Nuxt proxies `/api/team/**` to a **FastAPI + PostgreSQL** backend in `backend/` (`server/api/team/[...path].ts`, target `NUXT_TEAM_API_URL`), so the session cookie stays first-party (httpOnly, 30 days). Passwords are bcrypt; 10 failed logins per 15 min per IP.

### Backend setup

```bash
cd backend
python -m venv .venv && .venv\Scripts\activate          # Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                                  # set DATABASE_URL; COOKIE_SECURE=false for http://localhost
createdb -U postgres duo                              # or CREATE DATABASE duo; in psql
uvicorn app.main:app --port 8000                      # creates tables on start; Swagger: /api/team/docs
```

Then run `npm run dev` as usual; Nuxt forwards `/api/team` to port 8000.

### Creating accounts

With the CLI (asks for the password):

```bash
python -m app.cli add sebastian --name "Sebastian"
python -m app.cli add roman --name "Roman"
python -m app.cli passwd roman      # change password (logs out everywhere)
python -m app.cli list
python -m app.cli remove roman
```

Or straight in SQL; pgcrypto's bcrypt hashes are compatible:

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;
INSERT INTO users (username, name, password_hash)
VALUES ('roman', 'Roman', crypt('his-password', gen_salt('bf', 12)));
```

Usernames are matched case-insensitively; store them in lowercase.

## Analytics, Search Console, Bing

All switched on from `data/site.ts` — nothing loads until you fill it in:

- **Cookie-less analytics** (no consent banner needed): Umami → `analytics.umami.src` + `websiteId`, or Plausible → `analytics.plausible.domain`.
- **Google Search Console**: add a property for your domain → "HTML tag" method → paste the `content` value into `verification.google` → deploy → verify → submit `https://<domain>/sitemap.xml`.
- **Bing Webmaster Tools**: same with `verification.bing` (or import from Search Console).

## Google Business Profile (manual)

Has to be created from your own Google account at business.google.com:

1. Business name **Duo Studio**, category "Website designer" (+ "Software company", "Internet marketing service").
2. Choose **service-area business** (no public address) and add service areas: Bratislava, Nitra, (optionally) Prague, Kyiv, Uzhhorod.
3. Phone and website (the `/sk` URL), opening hours, a short description with "AI automatizácia, tvorba webov, aplikácie, mini hry".
4. Verify (postcard / phone / video), then add photos (logo `public/og-image.png`, project screenshots) and ask the first clients for reviews.
5. Use the same name, phone and e-mail as on the website — consistency helps local SEO.

## Getting started

```bash
npm install
npm run dev        # http://localhost:3000
npm run generate   # static build in .output/public — upload this folder to hosting (form falls back to e-mail)
npm run build      # Node server build with the /api/contact endpoint
```

### Deployment (recommended: Node server, e.g. a VPS with Caddy)

```bash
npm ci && npm run build
NUXT_TELEGRAM_BOT_TOKEN=... NUXT_TELEGRAM_CHAT_ID=... NUXT_WEB3FORMS_KEY=... PORT=3000 node .output/server/index.mjs
```

Pages listed in `nitro.prerender` are still pre-rendered as static HTML; only `/api/contact` runs on the server. Example Caddyfile:

```
studio.k2drive.com {
  reverse_proxy localhost:3000
}
```

Team panel backend on the same VPS (systemd unit or similar), listening on localhost only:

```bash
cd backend && .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Set `COOKIE_SECURE=true` and `DOCS=false` in `backend/.env` in production. Nuxt reaches it through `NUXT_TEAM_API_URL` (default `http://127.0.0.1:8000`).

> Nuxt 4.6 expects Node.js ≥ 22.21 (or 24.11+). It runs on 22.16 but prints a warning.

## Where to edit content

| What | File |
|---|---|
| Domain, e-mail, phone, cities, people (name, slug, design, skills, links), projects | `data/site.ts` |
| All texts: studio page, personal pages (`personal`), project descriptions, FAQ | `data/locales/sk.ts`, `cs.ts`, `uk.ts` |
| Project screenshots | `public/img/projects/*.jpg` (1200×750) |
| Colors and animations of the studio page | `app/assets/css/main.css` |
| Personal page designs | `app/components/ProfileDev.vue`, `ProfileCreative.vue` |

**Before going live:** fill in `.env`, analytics and verification (see above), set the main domain with `npm run set-domain -- https://your-domain` (updates `data/site.ts` and the static pages in `public/`), and add Roman's photo and phone number if wanted (`data/site.ts`, `people[1]`).

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
  pages/case/[id].vue        case studies
  pages/privacy.vue          GDPR privacy policy
  pages/login.vue, panel.vue, panel/   team panel: login, kanban, alarms, expenses (useTeam.ts, Team*.vue)
  (city pages are rendered by pages/[slug]/index.vue → components/CityPage.vue)
  components/                sections, ProfileDev, ProfileCreative, Concept*, Proto*, DesignModal, GeoLangHint…
  composables/useSite.ts     texts for the current language
  composables/useSiteSeo.ts  meta tags and JSON-LD
  composables/useGeoLang.ts  visitor country and language choice
  plugins/motion.ts          animations: v-reveal, v-tilt, v-magnetic, v-spot
data/                        content and settings (site, locales, cities, cases, privacy, concepts)
server/api/contact.post.ts   contact form → Telegram + Web3Forms
server/api/team/             proxy to the team panel backend
backend/                     FastAPI + PostgreSQL: auth, kanban, alarms, expenses (app/), user CLI (app/cli.py)
server/routes/               sitemap.xml, robots.txt, llms.txt, site.webmanifest
public/                      images, root index.html and short links (language by country)
```
