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

## Team panel (login, kanban, calendar, alarms, expenses, income)

A private area for the team at `/<lang>/login` → `/<lang>/panel`. The login link is the user icon in the header (and in the mobile menu and footer). There is **no sign-up**: accounts are created directly in the database.

- **Today** (`/panel/today`, opens first, also as the installed app's start screen): greeting, next alarm, the day's timeline with a "now" line, tasks (overdue / due today / assigned to me — tick to move to the board's last column), money (spent today and this month, monthly payments due with a *Paid* button), quick-add button, Today / Tomorrow switch. Data: `GET /today?date=` (`backend/app/routers/today.py`, user's time zone); events and the alarm are computed from local data, so it works offline. A **morning summary** push (default 07:30) and an optional evening "what is tomorrow" push are set in Settings → Notifications.
- **Study** (`/panel/study`, personal): the semester (dates, days without classes such as holidays or the exam period, reminder N minutes before a class), subjects (teacher, room, color, links to Moodle/Teams, note), the weekly timetable edited as **one table** (a row = a class: subject, day, time, lecture/seminar/lab, room), and deadlines (assignment, coursework, exam, credit test; status, grade). Classes show in the calendar (layer *Classes*, can be hidden) and on Today; deadlines in the calendar, on Today and as pushes 3 days before, 1 day before and on the day (09:00). API: `/study` (`backend/app/routers/study.py`). Deadlines can be added and ticked offline.
- **Tasks** (`/panel`): kanban boards. **Access**: a new board is visible only to its creator; with the **Access** button the creator picks the people who may see and edit it (others get 404). Assignees and mentions are limited to those people. A single card can also be *Only me* (visible only to its author). A column/board holding someone's private cards cannot be deleted. (On upgrade, former team boards stay shared only with people who already had cards on them.) Several boards can be shown **one below another**: drag a board tab down onto the boards (or Ctrl+click it); *Hide* removes it from view, cards can be dragged between the shown boards. Create boards, add/rename/delete columns, add cards; **drag** cards between columns, columns (by their header) and board tabs to reorder; columns can be shown in one scrolling **row** or wrapped into a **grid** (switch next to the board tabs); move a card to another board from its modal; edit a card (description, assignee, column, deadline) in a modal. **Deadlines** show on the card (amber when ≤ 2 days, red when overdue; struck through in the last column, which counts as "done"). **Mentions**: write `@username` in a card title or description (or use the mention buttons in the modal); open cards that mention you or are assigned to you appear under **For me** at the top, with a counter badge on the Tasks menu item. The board refreshes on window focus and every 30 s, so changes from a teammate show up.
- **Expenses** (`/panel/expenses`): personal expense log, visible only to its owner. An amount can be entered in EUR, UAH or USD; it is **stored in EUR** together with the original amount, currency and the rate used. The whole page can be shown in EUR, UAH or USD. Rates live in `backend/.env` (`RATE_UAH=51.5`, `RATE_USD=1.16`, i.e. how much 1 EUR costs); edit them and restart the API. Old entries keep the rate they were saved with. Also: icons per category, month switcher, total vs the previous month, average per day, breakdown by category, a 6-month chart, a list grouped by day (click a row to edit), CSV export for Excel.
- **Calendar** (`/panel/calendar`): personal planner. In **Settings** you choose who may see it (read-only); calendars shared with you can be overlaid on yours (hatched, not editable). Week view with an hour grid (click a slot to add an event, busy time per day, current-time line) and month view. Events are one-off or **weekly** on chosen weekdays with an optional end date (e.g. a class every Monday 11:00–12:30 until the end of the semester); an event can have a **reminder** (5/10/15/30 min, 1 h, 1 day before or a custom number of minutes) that rings like an alarm while the panel is open; one occurrence can be cancelled ("this day only") or the whole series deleted. Kanban deadlines you can see are shown on their days (click → open the board).
- **Monthly templates** (expenses and income): rent, subscriptions, salary… with a day of month and an amount (or *variable*). Each month click **Paid** / **Received** to record it in one click; a variable amount (salary) asks for the sum, prefilled with the last one. Overdue items are highlighted, the block shows what is still expected; an entry can be undone.
- **Own categories**: besides the built-in ones you can add your own expense/income categories (name, icon, color); deleting one moves its entries to "Other".
- **Phones**: below 860 px the sidebar becomes a bottom tab bar (Today, Tasks, Calendar, Finance + More sheet with alarms, settings, language, theme, logout); Finance switches between expenses and income at the top. Kanban columns swipe one per screen (chips above jump to a column), modals open as bottom sheets, the calendar shows 3 days (month: dots + list of the tapped day; swipe to change the range).
- **Moving cards**: drag with the mouse, or press and hold a card ~250 ms with a finger and drag (Pointer Events, `useCardDrag.ts`; edges auto-scroll, Escape or release outside a column cancels). Without dragging: card menu ⋯ → *Move…* (board → column → top/bottom) or *Assign…* (the assignee gets a push notification).
- **Dark theme**: moon/sun button in the sidebar (light / dark / system).
- **Settings** (`/panel/settings`): theme, kanban layout, calendar view and currency are stored **per account** on the server (`/me/settings`), so they are the same on every device; who can see my calendar; overview of board access.
- **Income** (`/panel/income`): the same ledger for income (projects, salary, maintenance, sales, gifts, refunds, other), stored in its own `incomes` table. Both pages show the **month balance** (income − expenses).
- **Alarms** (`/panel/alarms`): personal alarms (time, label, weekdays; no weekday = rings once and then switches itself off). They ring with a sound (plays at the phone's media volume), a full-screen dialog (stop / snooze 5 min) and a notification while the panel is open; snoozed alarms are listed on the page, survive reloads and also come by push when the app is closed. The page also has a **sleep calculator** (`TeamSleepCalc.vue`): pick a bedtime to get wake-up times, or a wake-up time to get bedtimes, based on ~90 min sleep cycles plus the time it takes to fall asleep (5–30 min); click an option to set a one-time alarm right away (when calculating a bedtime, one click sets both the bedtime reminder and the wake-up alarm); options that are already set show a check mark.

### Installable app, offline, notifications

- **Install (PWA)**: Android Chrome → menu ⋮ → *Install app* (or the *Install app* button in the panel sidebar / Settings). iPhone: Safari → Share → *Add to Home Screen*. The app opens `/panel` (redirects to the language used last), without the address bar. Manifest: `/panel.webmanifest` (panel pages only; the public site keeps `/site.webmanifest`). Icons and iOS splash screens: `node scripts/pwa-assets.mjs`; install-dialog screenshots: `node scripts/pwa-assets.mjs --screens http://localhost:3000 <user> <password>`.
- **Updates**: every build gets a new service worker (`pwa/sw.js`, filled in by `modules/pwa.mjs`). When a new version is deployed the app shows *A new version is available → Update*; the build version is in Settings. The worker only handles panel pages, `/_nuxt/` files, icons and Google Fonts — never public pages, `/robots.txt`, `/sitemap.xml`, `/llms.txt` or the API. Needs HTTPS in production.
- **Offline**: the app shell is precached; API responses are kept in IndexedDB (`utils/teamStore.ts`) and shown at once, then refreshed. Alarms, calendar events, expenses/income, cards (incl. moves) and settings can be changed offline: changes wait in an outbox and are sent in order when the network is back (temp ids → real ids). Conflicts: the later change wins (`backend/app/sync.py`); the user sees a message if an offline change was not applied or replaced a newer one. Status chip: *Offline* / *Not synced: N* / *Synced*. Logging out needs the network and wipes local data. Boards/columns, sharing, categories and templates need the network.
- **Notifications (Web Push)**: alarms, calendar reminders, deadlines due today (9:00), @mentions, assignments, monthly payments due (9:00). Settings → *Notifications*: turn on per device, choose types, quiet hours, send a test. The API sends them (`backend/app/notify.py`, a scheduler inside the API process — run **one** uvicorn process) using the user's time zone, which the panel stores in the account settings. Web push is not a system alarm: battery saver can delay it and there is no loud full-screen ringing when the app is closed; on iOS it works only in the Home Screen app (16.4+).

### Android app (APK, optional)

`android/` is a small Trusted Web Activity wrapper: the panel full screen from the site (it updates with the site; rebuild the APK only when the wrapper changes — icon, name, permissions), site notifications as the app's own, and **To system clock** on every alarm: the page opens `duostudio://alarm?…`, `AlarmActivity.java` hands it to the system Clock app (loud, works when the phone sleeps). Install by hand, no Play Store.

1. Signing key, once (keep the file and passwords safe — the same key is needed for every update): `keytool -genkeypair -v -keystore duo-panel.jks -alias duo -keyalg RSA -keysize 2048 -validity 10000`
2. Its fingerprint: `keytool -list -v -keystore duo-panel.jks -alias duo` → the `SHA256:` line → `NUXT_TWA_SHA256=` in the site's `.env` (served at `/.well-known/assetlinks.json`; without it the app shows an address bar).
3. GitHub → Settings → Secrets → Actions: `ANDROID_KEYSTORE_BASE64` (PowerShell: `[Convert]::ToBase64String([IO.File]::ReadAllBytes("duo-panel.jks"))`), `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS` (`duo`), `ANDROID_KEY_PASSWORD`.
4. GitHub → Actions → *Android APK* → Run workflow → download the APK from the run → open it on the phone (allow installing from this source).

Domain and package live in `android/app/src/main/res/values/strings.xml` and `android/app/build.gradle` (change them together with `npm run set-domain`).

**Calendar privacy**: calendars are visible only to their owner while `CALENDAR_SHARING=false` (default, `backend/.env`); set it to `true` to let owners share theirs in Settings (shares saved earlier come back).

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

Push notifications: run `python -m app.cli vapid` once, put the three printed lines (`VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`, `VAPID_SUBJECT=mailto:…`) into `backend/.env` and restart the API (keep the keys: new keys invalidate every subscription). Without them the panel works, notifications come only while it is open. Keep a single uvicorn process (no `--workers`), otherwise scheduled notifications are sent more than once.

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
  pages/login.vue, panel.vue, panel/   team panel: login, kanban, alarms, expenses, income (useTeam.ts, Team*.vue)
  (city pages are rendered by pages/[slug]/index.vue → components/CityPage.vue)
  components/                sections, ProfileDev, ProfileCreative, Concept*, Proto*, DesignModal, GeoLangHint…
  composables/useSite.ts     texts for the current language
  composables/useSiteSeo.ts  meta tags and JSON-LD
  composables/useGeoLang.ts  visitor country and language choice
  plugins/motion.ts          animations: v-reveal, v-tilt, v-magnetic, v-spot
data/                        content and settings (site, locales, cities, cases, privacy, concepts)
server/api/contact.post.ts   contact form → Telegram + Web3Forms
server/api/team/             proxy to the team panel backend
backend/                     FastAPI + PostgreSQL: auth, kanban, alarms, expenses/income (app/), user CLI (app/cli.py)
server/routes/               sitemap.xml, robots.txt, llms.txt, site.webmanifest
public/                      images, root index.html and short links (language by country)
```
