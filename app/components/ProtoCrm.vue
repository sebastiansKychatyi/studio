<script setup lang="ts">
defineProps<{ preview?: boolean }>()

type Role = 'owner' | 'admin' | 'agent'
type Section = 'overview' | 'team' | 'accounts'

interface Member {
  id: number
  name: string
  role: Role
  online: boolean
  revenue: number
}

interface NavItem {
  id: Section
  label: string
  allowedRoles: Role[]
}

const ROLE_OWNER: Role = 'owner'
const ROLE_ADMIN: Role = 'admin'
const ROLE_AGENT: Role = 'agent'
const ROLES: Role[] = [ROLE_OWNER, ROLE_ADMIN, ROLE_AGENT]
const MAX_REVENUE_BAR_PERCENT = 100
const WEEK_DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const WEEK_SALES = [42, 58, 51, 74, 69, 88, 63]

const NAV: NavItem[] = [
  { id: 'overview', label: 'Overview', allowedRoles: [ROLE_OWNER, ROLE_ADMIN, ROLE_AGENT] },
  { id: 'team', label: 'Team', allowedRoles: [ROLE_OWNER, ROLE_ADMIN] },
  { id: 'accounts', label: 'Accounts', allowedRoles: [ROLE_OWNER] },
]

const members = ref<Member[]>([
  { id: 1, name: 'Anna K.', role: ROLE_ADMIN, online: true, revenue: 4820 },
  { id: 2, name: 'Martin P.', role: ROLE_AGENT, online: true, revenue: 3310 },
  { id: 3, name: 'Olena S.', role: ROLE_AGENT, online: false, revenue: 2975 },
  { id: 4, name: 'Jakub H.', role: ROLE_AGENT, online: true, revenue: 2140 },
])
const accounts = ref([
  { id: 1, handle: 'studio-north', status: 'active' },
  { id: 2, handle: 'studio-east', status: 'active' },
  { id: 3, handle: 'studio-west', status: 'paused' },
])

const role = ref<Role>(ROLE_OWNER)
const section = ref<Section>('overview')
const newMemberName = ref('')

const visibleNav = computed(() => NAV.filter((n) => n.allowedRoles.includes(role.value)))
const topRevenue = computed(() => Math.max(...members.value.map((m) => m.revenue)))
const totalRevenue = computed(() => members.value.reduce((sum, m) => sum + m.revenue, 0))
const peakSale = Math.max(...WEEK_SALES)
const canManageTeam = computed(() => role.value !== ROLE_AGENT)

watch(role, () => {
  if (!visibleNav.value.some((n) => n.id === section.value)) section.value = 'overview'
})

function addMember() {
  const name = newMemberName.value.trim()
  if (!name || !canManageTeam.value) return
  members.value.push({ id: Date.now(), name, role: ROLE_AGENT, online: false, revenue: 0 })
  newMemberName.value = ''
}

function removeMember(id: number) {
  if (!canManageTeam.value) return
  members.value = members.value.filter((m) => m.id !== id)
}

function toggleAccount(id: number) {
  const account = accounts.value.find((a) => a.id === id)
  if (account && role.value === ROLE_OWNER) account.status = account.status === 'active' ? 'paused' : 'active'
}
</script>

<template>
  <div class="crm" :class="{ 'is-preview': preview }" :inert="preview || undefined">
    <div class="crm-title"><i /><i /><i /><span>Team CRM</span></div>
    <div class="crm-shell">
      <aside>
        <p class="crm-logo">◐ Team CRM</p>
        <nav>
          <button v-for="n in visibleNav" :key="n.id" type="button" :class="{ on: section === n.id }" @click="section = n.id">{{ n.label }}</button>
        </nav>
        <div class="crm-role">
          <p>Signed in as</p>
          <div role="group" aria-label="Role">
            <button v-for="r in ROLES" :key="r" type="button" :class="{ on: role === r }" @click="role = r">{{ r }}</button>
          </div>
        </div>
      </aside>

      <main>
        <template v-if="section === 'overview'">
          <h3>Overview</h3>
          <div class="crm-stats">
            <div><span>Team revenue</span><strong>${{ totalRevenue.toLocaleString('en-US') }}</strong></div>
            <div><span>Online now</span><strong>{{ members.filter((m) => m.online).length }}/{{ members.length }}</strong></div>
            <div><span>Active accounts</span><strong>{{ accounts.filter((a) => a.status === 'active').length }}</strong></div>
          </div>
          <p class="crm-cap">Sales this week</p>
          <div class="crm-chart">
            <div v-for="(v, i) in WEEK_SALES" :key="WEEK_DAYS[i]" class="crm-col">
              <i :style="{ height: `${(v / peakSale) * MAX_REVENUE_BAR_PERCENT}%` }" :class="{ peak: v === peakSale }" />
              <span>{{ WEEK_DAYS[i] }}</span>
            </div>
          </div>
        </template>

        <template v-else-if="section === 'team'">
          <h3>Team</h3>
          <ul class="crm-members">
            <li v-for="m in members" :key="m.id">
              <span class="crm-avatar" :class="{ on: m.online }">{{ m.name[0] }}</span>
              <div><b>{{ m.name }}</b><em>{{ m.role }}</em></div>
              <div class="crm-bar"><i :style="{ width: `${(m.revenue / topRevenue) * MAX_REVENUE_BAR_PERCENT}%` }" /></div>
              <strong>${{ m.revenue.toLocaleString('en-US') }}</strong>
              <button type="button" class="crm-x" :aria-label="`Remove ${m.name}`" @click="removeMember(m.id)">✕</button>
            </li>
          </ul>
          <form class="crm-add" @submit.prevent="addMember">
            <input v-model="newMemberName" placeholder="New member name" aria-label="New member name">
            <button type="submit">Add agent</button>
          </form>
        </template>

        <template v-else>
          <h3>Accounts</h3>
          <ul class="crm-accounts">
            <li v-for="a in accounts" :key="a.id">
              <b>{{ a.handle }}</b>
              <span class="crm-chip" :class="a.status">{{ a.status }}</span>
              <button type="button" @click="toggleAccount(a.id)">{{ a.status === 'active' ? 'Pause' : 'Resume' }}</button>
            </li>
          </ul>
          <p class="crm-hint">Only the owner role can see and change accounts. Switch the role on the left to see the menu change.</p>
        </template>
      </main>
    </div>
  </div>
</template>

<style>
.crm { width: 960px; height: 600px; border-radius: 14px; overflow: hidden; display: flex; flex-direction: column; background: #0F172A; color: #E2E8F0; font-family: 'Manrope', system-ui, sans-serif; text-align: left; box-shadow: 0 30px 70px -30px rgba(0, 0, 0, .6); }
.crm button { font: inherit; color: inherit; cursor: pointer; }
.crm.is-preview { pointer-events: none; }
.crm-title { display: flex; align-items: center; gap: 6px; padding: 9px 14px; background: #0B1222; font-size: 12px; color: #94A3B8; }
.crm-title > i { width: 10px; height: 10px; border-radius: 50%; background: #334155; }
.crm-title > span { margin: 0 auto; transform: translateX(-20px); }
.crm-shell { flex: 1; min-height: 0; display: grid; grid-template-columns: 210px 1fr; }
.crm aside { background: #111C33; padding: 20px 14px; display: flex; flex-direction: column; gap: 22px; border-right: 1px solid #1E293B; }
.crm-logo { font-weight: 800; font-size: 15px; padding: 0 8px; }
.crm aside nav { display: grid; gap: 4px; }
.crm aside nav button { border: 0; background: none; text-align: left; padding: 10px 12px; border-radius: 10px; font-size: 13px; font-weight: 700; color: #94A3B8; }
.crm aside nav button.on, .crm aside nav button:hover { background: #1E3A5F; color: #fff; }
.crm-role { margin-top: auto; font-size: 11px; color: #64748B; }
.crm-role p { margin-bottom: 8px; text-transform: uppercase; letter-spacing: .08em; font-weight: 800; }
.crm-role div { display: flex; background: #0B1222; border-radius: 999px; padding: 3px; }
.crm-role button { flex: 1; border: 0; background: none; padding: 5px 0; border-radius: 999px; font-size: 11px; font-weight: 700; text-transform: capitalize; color: #94A3B8; }
.crm-role button.on { background: #0EA5E9; color: #04121F; }
.crm main { padding: 22px 26px; overflow: auto; }
.crm main h3 { font-size: 22px; letter-spacing: -.02em; margin-bottom: 16px; }
.crm-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 22px; }
.crm-stats div { background: #16233F; border: 1px solid #1E293B; border-radius: 14px; padding: 14px 16px; display: grid; gap: 4px; }
.crm-stats span, .crm-cap { font-size: 11px; color: #64748B; text-transform: uppercase; letter-spacing: .08em; font-weight: 800; }
.crm-stats strong { font-size: 24px; letter-spacing: -.02em; }
.crm-cap { margin-bottom: 12px; }
.crm-chart { display: grid; grid-template-columns: repeat(7, 1fr); gap: 12px; height: 190px; align-items: end; background: #16233F; border: 1px solid #1E293B; border-radius: 14px; padding: 18px 18px 10px; }
.crm-col { height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center; gap: 8px; }
.crm-col i { width: 100%; border-radius: 8px 8px 3px 3px; background: #1E5A86; transition: height .6s; }
.crm-col i.peak { background: #0EA5E9; }
.crm-col span { font-size: 11px; color: #64748B; }
.crm-members, .crm-accounts { display: grid; gap: 8px; }
.crm-members li { display: grid; grid-template-columns: 36px 1fr 180px 80px 28px; align-items: center; gap: 14px; background: #16233F; border: 1px solid #1E293B; border-radius: 12px; padding: 10px 14px; font-size: 13px; }
.crm-members b { display: block; }
.crm-members em { font-style: normal; font-size: 11px; color: #64748B; text-transform: capitalize; }
.crm-avatar { position: relative; width: 32px; height: 32px; border-radius: 50%; display: grid; place-items: center; background: #1E3A5F; font-weight: 800; }
.crm-avatar.on::after { content: ''; position: absolute; right: -1px; bottom: -1px; width: 9px; height: 9px; border-radius: 50%; background: #22C55E; border: 2px solid #16233F; }
.crm-bar { height: 6px; border-radius: 999px; background: #0B1222; overflow: hidden; }
.crm-bar i { display: block; height: 100%; background: #0EA5E9; border-radius: inherit; transition: width .5s; }
.crm-x { border: 0; background: none; color: #64748B; font-size: 12px; }
.crm-x:hover { color: #F87171; }
.crm-add { display: flex; gap: 10px; margin-top: 14px; }
.crm-add input { flex: 1; background: #0B1222; border: 1px solid #1E293B; border-radius: 10px; padding: 9px 12px; color: #E2E8F0; font: inherit; font-size: 13px; }
.crm-add button, .crm-accounts button { padding: 9px 16px; border-radius: 10px; border: 0; background: #0EA5E9; color: #04121F; font-weight: 800; font-size: 12px; }
.crm-accounts li { display: flex; align-items: center; gap: 14px; background: #16233F; border: 1px solid #1E293B; border-radius: 12px; padding: 12px 16px; }
.crm-accounts b { flex: 1; font-size: 14px; }
.crm-chip { padding: 3px 10px; border-radius: 999px; font-size: 11px; font-weight: 800; }
.crm-chip.active { background: #064E3B; color: #6EE7B7; }
.crm-chip.paused { background: #422006; color: #FCD34D; }
.crm-hint { margin-top: 16px; font-size: 12px; color: #64748B; line-height: 1.5; }
</style>
