<script setup lang="ts">
// Résumé page (A4); "Download PDF" uses the browser print dialog
const route = useRoute()
const { t, cfg, people, projects } = useSite()
const localePath = useLocalePath()

const person = computed(() => people.value.find((p) => p.slug === route.params.slug))
if (!person.value) {
  throw createError({ statusCode: 404, statusMessage: 'Page not found', fatal: true })
}
useSiteSeo(person, { cv: true })

const p = computed(() => person.value!)
const cv = computed(() => t.value.personal.cv)
const myProjects = computed(() => projects.value.filter((x) => x.author === p.value.id && !x.placeholder))
const email = computed(() => p.value.email || cfg.email)
const profileUrl = computed(() => `${cfg.domain.replace(/^https?:\/\//, '')}/${p.value.slug}`)
const links = computed(() =>
  Object.entries(p.value.links)
    .filter(([, href]) => href && href !== '#')
    .map(([k, href]) => ({ k, href, label: href.replace(/^https?:\/\/(www\.)?/, '') }))
)
const host = (u: string) => u.replace(/^https?:\/\/(www\.)?/, '').replace(/\/$/, '')

const print = () => window.print()
</script>

<template>
  <div v-if="person" class="cv-page" :style="{ '--cv-accent': p.colors[0], '--cv-accent-2': p.colors[1] }">
    <div class="cv-toolbar">
      <NuxtLink class="cv-tool" :to="localePath(`/${p.slug}`)"><AppIcon name="back" /> {{ cv.fullProfile }}</NuxtLink>
      <div class="cv-toolbar-right">
        <LangSwitch />
        <button type="button" class="btn btn-primary btn-sm" @click="print"><AppIcon name="doc" /> {{ cv.download }}</button>
      </div>
    </div>

    <article class="cv-sheet">
      <aside class="cv-side">
        <div class="cv-avatar">
          <img v-if="p.photo" :src="p.photo" :alt="p.name" width="120" height="120">
          <span v-else>{{ p.initials }}</span>
        </div>

        <section>
          <h2>{{ cv.contact }}</h2>
          <ul class="cv-list">
            <li><AppIcon name="mail" /><a :href="`mailto:${email}`">{{ email }}</a></li>
            <li v-if="p.phone"><AppIcon name="phone" /><a :href="`tel:${p.phone.replace(/\s/g, '')}`">{{ p.phone }}</a></li>
            <li><AppIcon name="web" /><a :href="localePath(`/${p.slug}`)">{{ profileUrl }}</a></li>
            <li v-for="l in links" :key="l.k"><AppIcon :name="l.k" /><a :href="l.href" target="_blank" rel="noopener">{{ l.label }}</a></li>
          </ul>
        </section>

        <section>
          <h2>{{ cv.info }}</h2>
          <dl class="cv-facts">
            <div v-for="f in p.page.facts" :key="f.k"><dt>{{ f.k }}</dt><dd>{{ f.v }}</dd></div>
          </dl>
        </section>

        <section>
          <h2>{{ cv.skills }}</h2>
          <template v-if="p.skillGroups.length">
            <div v-for="g in p.skillGroups" :key="g.k" class="cv-group">
              <h3>{{ g.k }}</h3>
              <ul class="cv-skills"><li v-for="s in g.v" :key="s">{{ s }}</li></ul>
            </div>
          </template>
          <ul v-else class="cv-skills"><li v-for="s in p.skills" :key="s">{{ s }}</li></ul>
        </section>

        <section v-if="p.page.languages.length">
          <h2>{{ cv.languages }}</h2>
          <dl class="cv-facts cv-langs">
            <div v-for="l in p.page.languages" :key="l.k"><dt>{{ l.k }}</dt><dd>{{ l.v }}</dd></div>
          </dl>
        </section>
      </aside>

      <div class="cv-main">
        <header class="cv-head">
          <p class="cv-kicker">{{ cv.title }}</p>
          <h1>{{ p.degree ? `${p.degree} ` : '' }}{{ p.name }}</h1>
          <p class="cv-role">{{ p.role }}</p>
        </header>

        <section>
          <h2>{{ cv.summary }}</h2>
          <p class="cv-lead">{{ p.page.intro }}</p>
          <p v-for="(b, i) in p.page.bio" :key="i">{{ b }}</p>
        </section>

        <section>
          <h2>{{ cv.experience }}</h2>
          <ol class="cv-timeline">
            <li v-for="(item, i) in p.page.timeline" :key="i">
              <span>{{ item.year }}</span>
              <div>
                <h3>{{ item.title }}</h3>
                <p v-for="(line, lineIndex) in splitLines(item.text)" :key="lineIndex">{{ line }}</p>
              </div>
            </li>
          </ol>
        </section>

        <section v-if="p.page.education.length">
          <h2>{{ cv.education }}</h2>
          <ol class="cv-timeline">
            <li v-for="(e, i) in p.page.education" :key="i">
              <span>{{ e.year }}</span>
              <div><h3>{{ e.title }}</h3><p>{{ e.text }}</p></div>
            </li>
          </ol>
        </section>

        <section v-if="myProjects.length">
          <h2>{{ cv.projects }}</h2>
          <ul class="cv-projects">
            <li v-for="pr in myProjects" :key="pr.id">
              <div class="cv-project-head">
                <h3>{{ pr.title }}</h3>
                <span>{{ pr.year }}</span>
              </div>
              <p>{{ pr.desc }}</p>
              <p class="cv-project-meta">
                {{ pr.tags.join(' · ') }}
                <template v-if="pr.url"> — <a :href="pr.url" target="_blank" rel="noopener">{{ host(pr.url) }}</a></template>
                <template v-else-if="pr.repo"> — <a :href="pr.repo" target="_blank" rel="noopener">{{ host(pr.repo) }}</a></template>
              </p>
            </li>
          </ul>
        </section>
      </div>
    </article>
  </div>
</template>

<style>
.cv-page { min-height: 100vh; background: #ECEBE6; padding: 20px 16px 60px; }
.cv-toolbar { max-width: 210mm; margin: 0 auto 18px; display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; }
.cv-toolbar-right { display: flex; align-items: center; gap: 10px; }
.cv-tool { display: inline-flex; align-items: center; gap: 8px; font-weight: 700; padding: 8px 14px 8px 10px; border-radius: 999px; background: #fff; }
.cv-tool:hover { background: var(--ink); color: #fff; }
.cv-page .lang-dd-btn { background: #fff; }

.cv-sheet {
  max-width: 210mm; min-height: 297mm; margin: 0 auto; background: #fff; display: grid; grid-template-columns: 34% 1fr;
  box-shadow: 0 30px 80px -30px rgba(18, 18, 22, .35); border-radius: 6px; overflow: hidden;
  font-size: 10.5pt; line-height: 1.5; color: #1D1D22; animation: fadeUp .7s var(--ease);
}
.cv-sheet h2 { font-size: 8.5pt; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; margin-bottom: 10px; }
.cv-sheet a { color: inherit; }

.cv-side { background: color-mix(in srgb, var(--cv-accent) 8%, #fff); padding: 34px 26px; display: grid; gap: 26px; align-content: start; border-right: 1px solid color-mix(in srgb, var(--cv-accent) 15%, #fff); }
.cv-side h2 { color: var(--cv-accent); }
.cv-avatar { width: 110px; height: 110px; border-radius: 30px; overflow: hidden; display: grid; place-items: center; background: linear-gradient(135deg, var(--cv-accent), var(--cv-accent-2)); color: #fff; font-family: var(--font-display); font-size: 2.4rem; font-weight: 600; }
.cv-avatar img { width: 100%; height: 100%; object-fit: cover; }
.cv-list { display: grid; gap: 8px; }
.cv-list li { display: grid; grid-template-columns: 16px 1fr; gap: 8px; align-items: center; overflow-wrap: anywhere; font-size: 9.5pt; }
.cv-list .ico { width: 15px; height: 15px; color: var(--cv-accent); }
.cv-facts { display: grid; gap: 8px; }
.cv-facts dt { font-size: 8pt; color: #6B6B78; }
.cv-facts dd { font-weight: 700; }
.cv-skills { display: flex; flex-wrap: wrap; gap: 5px; }
.cv-skills li { padding: 3px 9px; border-radius: 999px; background: #fff; border: 1px solid color-mix(in srgb, var(--cv-accent) 25%, #fff); font-size: 8.5pt; font-weight: 700; }

.cv-main { padding: 34px 34px 40px; display: grid; gap: 24px; align-content: start; }
.cv-head { padding-bottom: 18px; border-bottom: 2px solid var(--cv-accent); }
.cv-kicker { font-size: 8.5pt; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; color: #6B6B78; }
.cv-head h1 { font-family: var(--font-display); font-weight: 600; font-size: 26pt; line-height: 1.1; letter-spacing: -.03em; margin: 4px 0; }
.cv-role { font-size: 12pt; font-weight: 700; color: var(--cv-accent); }
.cv-main h2 { color: #1D1D22; display: flex; align-items: center; gap: 10px; }
.cv-main h2::after { content: ''; flex: 1; height: 1px; background: #E4E3DE; }
.cv-main p + p { margin-top: 6px; }
.cv-lead { font-weight: 700; }
.cv-timeline { display: grid; gap: 12px; }
.cv-timeline li { display: grid; grid-template-columns: 86px 1fr; gap: 12px; }
.cv-group + .cv-group { margin-top: 10px; }
.cv-group h3 { font-size: 8.5pt; font-weight: 800; color: #44444E; margin-bottom: 5px; }
.cv-langs div { display: flex; justify-content: space-between; gap: 8px; }
.cv-langs dt { font-size: 9pt; color: #1D1D22; }
.cv-langs dd { color: var(--cv-accent); }
.cv-timeline li > span { font-weight: 800; color: var(--cv-accent); font-size: 9.5pt; }
.cv-timeline h3, .cv-projects h3 { font-size: 10.5pt; font-weight: 800; }
.cv-timeline p, .cv-projects p { color: #44444E; }
.cv-projects { display: grid; gap: 12px; }
.cv-project-head { display: flex; justify-content: space-between; gap: 10px; }
.cv-project-head span { color: #6B6B78; font-size: 9pt; }
.cv-project-meta { font-size: 8.5pt; color: #6B6B78 !important; margin-top: 2px !important; }
.cv-project-meta a { color: var(--cv-accent) !important; font-weight: 700; }

@media (max-width: 720px) {
  .cv-sheet { grid-template-columns: 1fr; min-height: 0; font-size: 10pt; }
  .cv-side { border-right: 0; }
  .cv-main { padding: 26px 22px; }
}

/* Print: sheet only */
@media print {
  @page { size: A4; margin: 0; }
  html, body { background: #fff !important; }
  .cv-page { padding: 0; background: #fff; }
  .cv-toolbar, .geo-hint, .skip-link, .progress { display: none !important; }
  .cv-sheet { box-shadow: none; border-radius: 0; max-width: none; width: 210mm; min-height: 297mm; animation: none; }
  .cv-sheet, .cv-side, .cv-avatar { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .cv-projects li, .cv-timeline li { break-inside: avoid; }
}
</style>
