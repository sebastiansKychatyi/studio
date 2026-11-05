<script setup lang="ts">
// Study: semester (dates, breaks, class reminder), week of classes, deadlines (assignments, exams),
// subjects with links, and the whole timetable edited as one table.
import { CATEGORY_COLORS, classesOn, type LessonKind, type StudyLesson, type StudySubject, type StudyWork, type WorkKind } from '~/composables/useTeam'

const { t } = useSite()
const { locale } = useI18n()
const localePath = useLocalePath()
const { api, study, loadStudy } = useTeam()

const p = computed(() => t.value.panel)
const s = computed(() => t.value.panel.study)
const WEEK = [1, 2, 3, 4, 5, 6, 0] // Monday first, JS weekday numbers
const LESSON_KINDS: LessonKind[] = ['lecture', 'seminar', 'lab']
const WORK_KINDS: WorkKind[] = ['assignment', 'project', 'exam', 'credit']

const pad = (n: number) => String(n).padStart(2, '0')
const ymd = (d: Date) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
const addDays = (day: string, n: number) => {
  const d = new Date(`${day}T12:00:00`)
  d.setDate(d.getDate() + n)
  return ymd(d)
}
const today = ymd(new Date())
const fmtDay = (day: string, opts: Intl.DateTimeFormatOptions = { weekday: 'short', day: 'numeric', month: 'short' }) =>
  new Date(`${day}T12:00:00`).toLocaleDateString(locale.value, opts)

const loading = ref(true)
const failed = ref('')
const toast = (e: unknown) => {
  failed.value = isOffline(e) ? p.value.offlineOnly : p.value.errorServer
  setTimeout(() => (failed.value = ''), 3500)
}
onMounted(() => loadStudy().catch(toast).finally(() => (loading.value = false)))
const subjectOf = (id: number | null) => study.value.subjects.find((x) => x.id === id)
const hostOf = (url: string) => url.replace(/^https?:\/\/(www\.)?/, '').split('/')[0]

// ===== Semester =====
const semOpen = ref(false)
const sem = reactive({ title: '', start: '', end: '', breaks: [] as { from: string; to: string }[], remind: null as number | null })
function openSemester() {
  const cur = study.value.semester
  Object.assign(sem, cur
    ? { title: cur.title, start: cur.start, end: cur.end, breaks: cur.breaks.map((b) => ({ ...b })), remind: cur.remind }
    : { title: s.value.semesterPh, start: today, end: addDays(today, 120), breaks: [], remind: 10 })
  semOpen.value = true
}
async function saveSemester() {
  try {
    const breaks = sem.breaks.filter((b) => b.from).map((b) => ({ from: b.from, to: b.to || b.from }))
    await api('/study/semester', { method: 'PUT', body: { ...sem, title: sem.title.trim() || s.value.semesterPh, breaks } })
    semOpen.value = false
    await loadStudy()
  } catch (e) {
    toast(e)
  }
}
const REMINDS = [null, 5, 10, 15, 30]

// ===== Week of classes =====
const weekStart = ref((() => {
  const d = new Date()
  d.setDate(d.getDate() - ((d.getDay() + 6) % 7))
  return ymd(d)
})())
const week = computed(() =>
  WEEK.map((_, i) => {
    const day = addDays(weekStart.value, i)
    const b = study.value.semester?.breaks.find((x) => day >= x.from && day <= x.to)
    return { day, classes: classesOn(study.value, day), isBreak: !!b }
  }).filter((d, i) => i < 5 || d.classes.length))
const weekLabel = computed(() => `${fmtDay(weekStart.value, { day: 'numeric', month: 'short' })} – ${fmtDay(addDays(weekStart.value, 6), { day: 'numeric', month: 'short' })}`)
const roomOf = (l: StudyLesson, sub: StudySubject) => l.room || sub.room

// ===== Deadlines =====
const open = computed(() => study.value.works.filter((w) => w.status !== 'done'))
const done = computed(() => study.value.works.filter((w) => w.status === 'done').reverse())
const showDone = ref(false)
const left = (w: StudyWork) => Math.round((Date.parse(w.due) - Date.parse(today)) / 86400000)
const leftText = (w: StudyWork) => {
  const n = left(w)
  return n < 0 ? s.value.overdue : n === 0 ? s.value.dueToday : n === 1 ? s.value.dueTomorrow : `${s.value.inDays} ${n}`
}
async function patchWork(w: StudyWork, body: Partial<StudyWork>) {
  Object.assign(w, body)
  await api(`/study/works/${w.id}`, { method: 'PATCH', body }).catch(toast)
}
const NEXT = { todo: 'doing', doing: 'done', done: 'todo' } as const
const workForm = reactive({ open: false, title: '', subject_id: null as number | null, kind: 'assignment' as WorkKind, due: today, due_time: '' })
async function addWork() {
  const title = workForm.title.trim()
  if (!title || !workForm.due) return
  try {
    const created = await api<StudyWork>('/study/works', {
      method: 'POST',
      body: { title, subject_id: workForm.subject_id, kind: workForm.kind, due: workForm.due, due_time: workForm.due_time || null },
    })
    study.value = { ...study.value, works: [...study.value.works, created].sort((a, b) => a.due.localeCompare(b.due)) }
    Object.assign(workForm, { open: false, title: '', due_time: '' })
  } catch (e) {
    toast(e)
  }
}
const sureWork = ref<number | null>(null)
async function removeWork(w: StudyWork) {
  if (sureWork.value !== w.id) {
    sureWork.value = w.id
    setTimeout(() => sureWork.value === w.id && (sureWork.value = null), 3000)
    return
  }
  study.value = { ...study.value, works: study.value.works.filter((x) => x !== w) }
  await api(`/study/works/${w.id}`, { method: 'DELETE' }).catch(toast)
}

// ===== Subjects =====
const subjectForm = ref<{ id: number | null; name: string; teacher: string; room: string; color: string; links: { title: string; url: string }[]; note: string } | null>(null)
function openSubject(x?: StudySubject) {
  subjectForm.value = x
    ? { id: x.id, name: x.name, teacher: x.teacher, room: x.room, color: x.color, links: x.links.map((l) => ({ ...l })), note: x.note }
    : { id: null, name: '', teacher: '', room: '', color: CATEGORY_COLORS[study.value.subjects.length % CATEGORY_COLORS.length]!, links: [], note: '' }
}
async function saveSubject() {
  const f = subjectForm.value
  if (!f?.name.trim()) return
  const { id, ...body } = f
  body.links = body.links.filter((l) => /^https?:\/\//.test(l.url.trim())).map((l) => ({ title: l.title.trim(), url: l.url.trim() }))
  try {
    if (id) await api(`/study/subjects/${id}`, { method: 'PATCH', body })
    else await api('/study/subjects', { method: 'POST', body })
    subjectForm.value = null
    await loadStudy()
  } catch (e) {
    toast(e)
  }
}
const sureSubject = ref(false)
async function deleteSubject() {
  if (!sureSubject.value) {
    sureSubject.value = true
    setTimeout(() => (sureSubject.value = false), 3000)
    return
  }
  const id = subjectForm.value?.id
  subjectForm.value = null
  sureSubject.value = false
  if (!id) return
  await api(`/study/subjects/${id}`, { method: 'DELETE' }).catch(toast)
  await loadStudy().catch(() => {})
}

// ===== Timetable: all classes in one table =====
interface Row { subject_id: number; weekday: number; start: string; end: string; kind: LessonKind; room: string }
const rows = ref<Row[] | null>(null)
const rowsError = ref(false)
function editTable() {
  rows.value = study.value.subjects
    .flatMap((x) => x.lessons.map(({ id: _id, ...l }) => ({ ...l })))
    .sort((a, b) => WEEK.indexOf(a.weekday) - WEEK.indexOf(b.weekday) || a.start.localeCompare(b.start))
  if (!rows.value.length) addRow()
}
function addRow() {
  const last = rows.value?.at(-1)
  // Next row continues the previous one: same day, starts when it ends
  const start = last?.end ?? '08:00'
  const min = Math.min(Number(start.slice(0, 2)) * 60 + Number(start.slice(3)) + 90, 23 * 60 + 59) // 90 min class
  const end = `${pad(Math.floor(min / 60))}:${pad(min % 60)}`
  rows.value = [...(rows.value ?? []), { subject_id: last?.subject_id ?? study.value.subjects[0]!.id, weekday: last?.weekday ?? 1, start, end, kind: 'lecture', room: '' }]
}
async function saveTable() {
  if (!rows.value) return
  rowsError.value = rows.value.some((r) => !r.start || !r.end || r.end <= r.start)
  if (rowsError.value) return
  try {
    await api('/study/lessons', { method: 'PUT', body: { lessons: rows.value } })
    rows.value = null
    await loadStudy()
  } catch (e) {
    toast(e)
  }
}
</script>

<template>
  <div class="sd">
    <header class="tp-head">
      <div>
        <h1>{{ s.title }}</h1>
        <p v-if="study.semester">{{ study.semester.title }} · {{ fmtDay(study.semester.start, { day: 'numeric', month: 'short' }) }} – {{ fmtDay(study.semester.end, { day: 'numeric', month: 'short', year: 'numeric' }) }}</p>
        <p v-else>{{ s.subtitle }}</p>
      </div>
      <button type="button" class="btn btn-ghost btn-sm" @click="openSemester"><AppIcon name="calendar" /> {{ study.semester ? s.semester : s.newSemester }}</button>
    </header>

    <div v-if="loading" class="kb-loading"><span class="spinner" /></div>

    <!-- Semester form -->
    <form v-if="semOpen" class="sd-card sd-form" @submit.prevent="saveSemester">
      <h2>{{ s.semester }}</h2>
      <div class="sd-grid3">
        <label class="tp-field"><span>{{ s.semesterName }}</span><input v-model="sem.title" maxlength="120" required></label>
        <label class="tp-field"><span>{{ s.from }}</span><input v-model="sem.start" type="date" required></label>
        <label class="tp-field"><span>{{ s.to }}</span><input v-model="sem.end" type="date" required :min="sem.start"></label>
      </div>
      <div class="tp-field">
        <span>{{ s.breaks }}</span>
        <small class="rc-hint">{{ s.breaksHint }}</small>
        <div v-for="(b, i) in sem.breaks" :key="i" class="sd-break">
          <input v-model="b.from" type="date" class="tp-input" :aria-label="s.from">
          <span>–</span>
          <input v-model="b.to" type="date" class="tp-input" :min="b.from" :aria-label="s.to">
          <button type="button" class="tp-icon-btn sm" :aria-label="p.delete" @click="sem.breaks.splice(i, 1)"><AppIcon name="close" /></button>
        </div>
        <button type="button" class="kb-add" @click="sem.breaks.push({ from: '', to: '' })"><AppIcon name="plus" /> {{ s.addBreak }}</button>
      </div>
      <div class="tp-field">
        <span>{{ s.remind }}</span>
        <div class="ev-remind" role="radiogroup" :aria-label="s.remind">
          <button v-for="m in REMINDS" :key="String(m)" type="button" role="radio" :aria-checked="sem.remind === m" :class="{ on: sem.remind === m }" style="--c: var(--accent)" @click="sem.remind = m">
            {{ m === null ? p.calendar.remindNone : `${m} ${p.calendar.m}` }}
          </button>
        </div>
      </div>
      <div class="rc-form-actions">
        <button class="btn btn-primary btn-sm">{{ p.save }}</button>
        <button type="button" class="btn btn-ghost btn-sm" @click="semOpen = false">{{ p.cancel }}</button>
      </div>
    </form>

    <section v-else-if="!loading && !study.semester" class="kb-empty">
      <span class="kb-empty-icon" aria-hidden="true"><AppIcon name="study" /></span>
      <h2>{{ s.emptyTitle }}</h2>
      <p>{{ s.emptyText }}</p>
      <button type="button" class="btn btn-primary" @click="openSemester"><AppIcon name="plus" /> {{ s.newSemester }}</button>
    </section>

    <template v-if="study.semester && !loading">
      <!-- Week -->
      <section class="sd-card">
        <div class="sd-bar">
          <h2><AppIcon name="calendar" /> {{ s.week }}</h2>
          <div class="ex-month">
            <button type="button" class="tp-icon-btn sm" :aria-label="p.calendar.prev" @click="weekStart = addDays(weekStart, -7)"><AppIcon name="left" /></button>
            <span class="ex-month-label sd-week-label">{{ weekLabel }}</span>
            <button type="button" class="tp-icon-btn sm" :aria-label="p.calendar.next" @click="weekStart = addDays(weekStart, 7)"><AppIcon name="right" /></button>
          </div>
        </div>
        <p v-if="!study.subjects.some((x) => x.lessons.length)" class="sd-muted">{{ s.noTimetable }}</p>
        <div v-else class="sd-week">
          <div v-for="d in week" :key="d.day" class="sd-day" :class="{ today: d.day === today }">
            <h3>{{ fmtDay(d.day) }}<small v-if="d.isBreak">{{ s.breakDay }}</small></h3>
            <p v-if="!d.classes.length" class="sd-muted">—</p>
            <div v-for="c in d.classes" :key="c.lesson.id" class="sd-class" :style="{ '--c': c.subject.color }">
              <span class="sd-time">{{ c.lesson.start }}<small>{{ c.lesson.end }}</small></span>
              <span class="sd-class-text">
                <b>{{ c.subject.name }}</b>
                <small>{{ s.kinds[c.lesson.kind] }}<template v-if="roomOf(c.lesson, c.subject)"> · {{ roomOf(c.lesson, c.subject) }}</template></small>
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- Deadlines -->
      <section class="sd-card">
        <div class="sd-bar">
          <h2><AppIcon name="doc" /> {{ s.deadlines }} <span class="kb-count">{{ open.length }}</span></h2>
          <button type="button" class="btn btn-ghost btn-sm" @click="workForm.open = !workForm.open"><AppIcon name="plus" /> {{ s.addWork }}</button>
        </div>
        <form v-if="workForm.open" class="sd-form sd-workform" @submit.prevent="addWork">
          <label class="tp-field"><span>{{ s.workTitle }}</span><input v-model="workForm.title" maxlength="200" required :placeholder="s.workPh"></label>
          <div class="sd-grid3">
            <label class="tp-field">
              <span>{{ s.subject }}</span>
              <select v-model="workForm.subject_id">
                <option :value="null">—</option>
                <option v-for="x in study.subjects" :key="x.id" :value="x.id">{{ x.name }}</option>
              </select>
            </label>
            <label class="tp-field">
              <span>{{ s.kind }}</span>
              <select v-model="workForm.kind"><option v-for="k in WORK_KINDS" :key="k" :value="k">{{ s.workKinds[k] }}</option></select>
            </label>
            <div class="sd-when">
              <label class="tp-field"><span>{{ s.due }}</span><input v-model="workForm.due" type="date" required></label>
              <label class="tp-field"><span>{{ s.time }}</span><input v-model="workForm.due_time" type="time"></label>
            </div>
          </div>
          <div class="rc-form-actions">
            <button class="btn btn-primary btn-sm">{{ p.add }}</button>
            <button type="button" class="btn btn-ghost btn-sm" @click="workForm.open = false">{{ p.cancel }}</button>
          </div>
        </form>
        <p v-if="!open.length && !workForm.open" class="sd-muted">{{ s.noDeadlines }}</p>
        <TransitionGroup tag="ul" name="kb-card" class="sd-works">
          <li v-for="w in open" :key="w.id" class="sd-work" :class="{ late: left(w) < 0, soon: left(w) >= 0 && left(w) <= 3 }" :style="{ '--c': subjectOf(w.subject_id)?.color ?? 'var(--muted)' }">
            <button type="button" class="sd-status" :class="w.status" :title="s.status[w.status]" :aria-label="`${s.status[w.status]}: ${w.title}`" @click="patchWork(w, { status: NEXT[w.status] })">
              <AppIcon :name="w.status === 'doing' ? 'repeat' : 'check'" />
            </button>
            <span class="sd-work-text">
              <b>{{ w.title }}</b>
              <small>{{ s.workKinds[w.kind] }}<template v-if="subjectOf(w.subject_id)"> · {{ subjectOf(w.subject_id)!.name }}</template> · {{ fmtDay(w.due) }}<template v-if="w.due_time"> {{ w.due_time }}</template></small>
            </span>
            <span class="sd-left">{{ leftText(w) }}</span>
            <button type="button" class="tp-icon-btn sm danger" :class="{ confirm: sureWork === w.id }" :aria-label="sureWork === w.id ? p.sure : p.delete" @click="removeWork(w)"><AppIcon name="trash" /></button>
          </li>
        </TransitionGroup>
        <button v-if="done.length" type="button" class="kb-add" @click="showDone = !showDone"><AppIcon :name="showDone ? 'close' : 'check'" /> {{ s.doneList }} ({{ done.length }})</button>
        <ul v-if="showDone" class="sd-works">
          <li v-for="w in done" :key="w.id" class="sd-work done" :style="{ '--c': subjectOf(w.subject_id)?.color ?? 'var(--muted)' }">
            <button type="button" class="sd-status done" :aria-label="s.status.done" @click="patchWork(w, { status: 'todo' })"><AppIcon name="check" /></button>
            <span class="sd-work-text"><b>{{ w.title }}</b><small>{{ s.workKinds[w.kind] }} · {{ fmtDay(w.due) }}</small></span>
            <input class="tp-input sd-grade" :value="w.grade" maxlength="20" :placeholder="s.grade" :aria-label="s.grade" @change="patchWork(w, { grade: ($event.target as HTMLInputElement).value.trim() })">
          </li>
        </ul>
      </section>

      <!-- Subjects -->
      <section class="sd-card">
        <div class="sd-bar">
          <h2><AppIcon name="study" /> {{ s.subjects }} <span class="kb-count">{{ study.subjects.length }}</span></h2>
          <button type="button" class="btn btn-ghost btn-sm" @click="openSubject()"><AppIcon name="plus" /> {{ s.addSubject }}</button>
        </div>
        <p v-if="!study.subjects.length" class="sd-muted">{{ s.noSubjects }}</p>
        <ul class="sd-subjects">
          <li v-for="x in study.subjects" :key="x.id" class="sd-subject" :style="{ '--c': x.color }">
            <button type="button" class="sd-subject-main" @click="openSubject(x)">
              <b>{{ x.name }}</b>
              <small>{{ [x.teacher, x.room].filter(Boolean).join(' · ') || s.noDetails }}</small>
            </button>
            <span v-if="x.links.length" class="sd-links">
              <a v-for="(l, i) in x.links" :key="i" :href="l.url" target="_blank" rel="noopener">{{ l.title || hostOf(l.url) }}</a>
            </span>
          </li>
        </ul>
      </section>

      <!-- Timetable editor -->
      <section v-if="study.subjects.length" class="sd-card">
        <div class="sd-bar">
          <h2><AppIcon name="grid" /> {{ s.timetable }}</h2>
          <button v-if="!rows" type="button" class="btn btn-ghost btn-sm" @click="editTable"><AppIcon name="edit" /> {{ s.editTimetable }}</button>
        </div>
        <p v-if="!rows" class="sd-muted">{{ s.timetableHint }}</p>
        <form v-else class="sd-table" @submit.prevent="saveTable">
          <div class="sd-row sd-row-head" aria-hidden="true">
            <span>{{ s.subject }}</span><span>{{ s.day }}</span><span>{{ s.start }}</span><span>{{ s.end }}</span><span>{{ s.kind }}</span><span>{{ s.room }}</span><span />
          </div>
          <div v-for="(r, i) in rows" :key="i" class="sd-row">
            <select v-model="r.subject_id" class="tp-input" :aria-label="s.subject"><option v-for="x in study.subjects" :key="x.id" :value="x.id">{{ x.name }}</option></select>
            <select v-model="r.weekday" class="tp-input" :aria-label="s.day"><option v-for="(d, di) in WEEK" :key="d" :value="d">{{ p.alarms.days[di] }}</option></select>
            <input v-model="r.start" type="time" class="tp-input" required :aria-label="s.start">
            <input v-model="r.end" type="time" class="tp-input" required :class="{ invalid: rowsError && r.end <= r.start }" :aria-label="s.end">
            <select v-model="r.kind" class="tp-input" :aria-label="s.kind"><option v-for="k in LESSON_KINDS" :key="k" :value="k">{{ s.kinds[k] }}</option></select>
            <input v-model="r.room" class="tp-input" maxlength="60" :placeholder="subjectOf(r.subject_id)?.room || s.room" :aria-label="s.room">
            <button type="button" class="tp-icon-btn sm" :aria-label="p.delete" @click="rows.splice(i, 1)"><AppIcon name="close" /></button>
          </div>
          <button type="button" class="kb-add" @click="addRow"><AppIcon name="plus" /> {{ s.addRow }}</button>
          <div class="rc-form-actions">
            <button class="btn btn-primary btn-sm">{{ p.save }}</button>
            <button type="button" class="btn btn-ghost btn-sm" @click="rows = null">{{ p.cancel }}</button>
          </div>
        </form>
      </section>
    </template>

    <!-- Subject editor -->
    <div v-if="subjectForm" class="tm-overlay" @click.self="subjectForm = null">
      <form class="tm" role="dialog" aria-modal="true" :aria-label="s.subject" @submit.prevent="saveSubject">
        <header class="tm-head">
          <h2>{{ subjectForm.id ? subjectForm.name : s.addSubject }}</h2>
          <button type="button" class="tp-icon-btn sm" :aria-label="p.close" @click="subjectForm = null"><AppIcon name="close" /></button>
        </header>
        <label class="tp-field"><span>{{ s.subjectName }}</span><input v-model="subjectForm.name" required maxlength="120"></label>
        <div class="tm-row">
          <label class="tp-field"><span>{{ s.teacher }}</span><input v-model="subjectForm.teacher" maxlength="120"></label>
          <label class="tp-field"><span>{{ s.room }}</span><input v-model="subjectForm.room" maxlength="60"></label>
        </div>
        <div class="tp-field">
          <span>{{ p.calendar.color }}</span>
          <div class="ex-catform-colors">
            <button v-for="c in CATEGORY_COLORS" :key="c" type="button" :aria-label="c" :class="{ on: subjectForm.color === c }" :style="{ background: c }" @click="subjectForm.color = c" />
          </div>
        </div>
        <div class="tp-field">
          <span>{{ s.links }}</span>
          <div v-for="(l, i) in subjectForm.links" :key="i" class="sd-link-row">
            <input v-model="l.title" class="tp-input" maxlength="60" :placeholder="s.linkTitle" :aria-label="s.linkTitle">
            <input v-model="l.url" class="tp-input" type="url" maxlength="500" placeholder="https://" :aria-label="s.links">
            <button type="button" class="tp-icon-btn sm" :aria-label="p.delete" @click="subjectForm.links.splice(i, 1)"><AppIcon name="close" /></button>
          </div>
          <button v-if="subjectForm.links.length < 10" type="button" class="kb-add" @click="subjectForm.links.push({ title: '', url: '' })"><AppIcon name="plus" /> {{ s.addLink }}</button>
        </div>
        <label class="tp-field"><span>{{ p.calendar.note }}</span><textarea v-model="subjectForm.note" rows="3" maxlength="5000" /></label>
        <footer class="tm-foot">
          <button v-if="subjectForm.id" type="button" class="btn btn-sm tm-delete" :class="{ sure: sureSubject }" @click="deleteSubject"><AppIcon name="trash" /> {{ sureSubject ? p.sure : p.delete }}</button>
          <div class="tm-foot-right">
            <button type="button" class="btn btn-ghost btn-sm" @click="subjectForm = null">{{ p.cancel }}</button>
            <button class="btn btn-primary btn-sm">{{ p.save }}</button>
          </div>
        </footer>
      </form>
    </div>

    <NuxtLink :to="localePath('/panel/calendar')" class="sd-cal-link"><AppIcon name="calendar" /> {{ s.inCalendar }}</NuxtLink>
    <Transition name="toast"><div v-if="failed" class="tp-toast" role="status">{{ failed }}</div></Transition>
  </div>
</template>

<style>
/* ===== Study ===== */
.sd { display: grid; gap: 14px; max-width: 980px; }
.sd .tp-head { margin-bottom: 4px; }
.sd .btn .ico { width: 16px; height: 16px; }
.sd-form { display: grid; gap: 2px; }
.sd-when { display: grid; grid-template-columns: 1.4fr 1fr; gap: 10px; }
.sd-break { display: flex; align-items: center; gap: 6px; margin-top: 6px; }
.sd-break .tp-input { flex: 1; min-width: 0; }

.sd-week { display: grid; grid-template-columns: repeat(auto-fill, minmax(170px, 1fr)); gap: 10px; }
.sd-day { display: grid; align-content: start; gap: 6px; padding: 10px; border-radius: 16px; background: var(--bg); border: 1px solid var(--line); }
.sd-day.today { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(91, 75, 255, .1); }
.sd-day h3 { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; font-size: .8rem; font-weight: 800; color: var(--muted); text-transform: capitalize; }
.sd-day h3 small { padding: 1px 8px; border-radius: 999px; background: #FFF1D6; color: #A15C00; text-transform: none; }
.sd-class { display: flex; align-items: center; gap: 10px; padding: 8px 10px; border-radius: 12px; border-left: 4px solid var(--c); background: color-mix(in srgb, var(--c) 10%, var(--surface)); }
.sd-time { display: grid; font-weight: 800; font-size: .85rem; font-variant-numeric: tabular-nums; line-height: 1.2; }
.sd-time small { color: var(--muted); font-size: .72rem; }
.sd-class-text { min-width: 0; display: grid; line-height: 1.25; }
.sd-class-text b { font-size: .88rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sd-class-text small { color: var(--muted); font-weight: 600; font-size: .74rem; }

.sd-works { display: grid; gap: 6px; }
.sd-work { display: flex; align-items: center; gap: 8px; padding: 4px 8px 4px 4px; border-radius: 14px; background: var(--bg); border: 1px solid var(--line); border-left: 4px solid var(--c); }
.sd-work.late { border-color: rgba(229, 72, 77, .45); border-left-color: var(--c); }
.sd-work.done { opacity: .75; }
.sd-status { flex: none; display: grid; place-items: center; width: 44px; height: 44px; border: 0; background: none; cursor: pointer; color: transparent; position: relative; }
.sd-status::before { content: ''; position: absolute; width: 22px; height: 22px; border-radius: 50%; border: 2px solid var(--line-2); }
.sd-status .ico { position: relative; width: 13px; height: 13px; }
.sd-status.doing { color: #C27803; }
.sd-status.doing::before { border-color: #F59E0B; background: rgba(245, 158, 11, .12); }
.sd-status.done { color: #fff; }
.sd-status.done::before { border-color: #19C3A6; background: #19C3A6; }
.sd-work-text { flex: 1; min-width: 0; display: grid; line-height: 1.3; padding: 6px 0; }
.sd-work-text b { font-size: .92rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sd-work-text small { color: var(--muted); font-weight: 600; font-size: .76rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sd-left { flex: none; font-size: .75rem; font-weight: 800; color: var(--muted); white-space: nowrap; }
.sd-work.soon .sd-left { color: #C27803; }
.sd-work.late .sd-left { color: #E5484D; }
.sd-grade { width: 90px; }
.sd-works + .kb-add { margin-top: 6px; }

.sd-subjects { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 8px; }
.sd-subject { display: grid; gap: 6px; padding: 10px 12px; border-radius: 16px; background: var(--bg); border: 1px solid var(--line); border-top: 4px solid var(--c); }
.sd-subject-main { display: grid; gap: 2px; padding: 0; border: 0; background: none; text-align: left; cursor: pointer; color: var(--ink); min-height: 44px; }
.sd-subject-main b { font-size: .95rem; }
.sd-subject-main small { color: var(--muted); font-weight: 600; font-size: .78rem; }
.sd-links { display: flex; flex-wrap: wrap; gap: 6px; }
.sd-links a { display: inline-flex; align-items: center; min-height: 32px; padding: 0 10px; border-radius: 999px; background: color-mix(in srgb, var(--c) 14%, var(--surface)); color: var(--ink); font-weight: 700; font-size: .78rem; }
.sd-link-row { display: grid; grid-template-columns: 1fr 1.6fr auto; gap: 6px; margin-top: 6px; }

.sd-table { display: grid; gap: 6px; }
.sd-row { display: grid; grid-template-columns: 1.6fr .8fr .8fr .8fr 1fr 1fr auto; gap: 6px; align-items: center; }
.sd-row .tp-input { width: 100%; padding: 8px 10px; }
.sd-row .tp-input.invalid { border-color: #E5484D; }
.sd-row-head span { font-size: .72rem; font-weight: 800; color: var(--muted); text-transform: uppercase; letter-spacing: .03em; }
.sd-cal-link { justify-self: start; display: inline-flex; align-items: center; gap: 8px; min-height: 44px; color: var(--accent); font-weight: 800; font-size: .9rem; }
.sd-cal-link .ico { width: 16px; height: 16px; }
.tp.dark .sd-row .tp-input, .tp.dark .sd-break .tp-input, .tp.dark .sd-link-row .tp-input, .tp.dark .sd-grade { background: var(--field); color: var(--ink); }
.tp.dark .sd-day h3 small { background: rgba(245, 158, 11, .16); color: #FBBF5A; }

@media (max-width: 640px) {
  .sd-week { grid-template-columns: 1fr; }
  .sd-week-label { min-width: 0; font-size: .85rem; }
  .sd-subjects { grid-template-columns: 1fr; }
  .sd-link-row { grid-template-columns: 1fr auto; }
  .sd-link-row input:first-child { grid-column: 1 / -1; }
  /* Timetable row = small card: subject on top, day / times, kind / room */
  .sd-row-head { display: none; }
  /* subject + delete / from – to / day + kind / room */
  .sd-row { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) 40px; padding: 8px; border-radius: 14px; background: var(--bg); border: 1px solid var(--line); }
  .sd-row > :nth-child(1) { grid-area: 1 / 1 / 2 / 3; }
  .sd-row > :nth-child(7) { grid-area: 1 / 3; }
  .sd-row > :nth-child(3) { grid-area: 2 / 1; }
  .sd-row > :nth-child(4) { grid-area: 2 / 2 / 3 / 4; }
  .sd-row > :nth-child(2) { grid-area: 3 / 1; }
  .sd-row > :nth-child(5) { grid-area: 3 / 2 / 4 / 4; }
  .sd-row > :nth-child(6) { grid-area: 4 / 1 / 5 / 4; }
}
</style>
