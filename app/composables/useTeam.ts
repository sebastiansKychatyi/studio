// Private team panel: session user, API client and shared state.
// API is FastAPI (backend/), proxied by Nuxt at /api/team.

export interface TeamUser { id: number; username: string; name: string }
export interface TeamCard {
  id: number
  column_id: number
  title: string
  description: string
  assignee_id: number | null
  created_by: number | null
  position: number
  updated_at: string
}
export interface TeamColumn { id: number; title: string; position: number; cards: TeamCard[] }
export interface TeamBoard { id: number; title: string }
export interface TeamBoardFull extends TeamBoard { columns: TeamColumn[] }
// days: JS weekdays (0 = Sunday); empty = ring once
export interface TeamAlarm { id: number; time: string; label: string; days: number[]; enabled: boolean }

export const httpStatus = (e: unknown) => (e as { status?: number })?.status ?? 0

export function useTeam() {
  // undefined = not checked yet, null = signed out
  const user = useState<TeamUser | null | undefined>('team-user', () => undefined)
  const users = useState<TeamUser[]>('team-users', () => [])
  const alarms = useState<TeamAlarm[]>('team-alarms', () => [])
  const api = $fetch.create({ baseURL: '/api/team' })

  async function refresh() {
    try {
      user.value = (await api<{ user: TeamUser | null }>('/auth/me')).user
    } catch {
      user.value = null
    }
    return user.value
  }

  async function login(username: string, password: string) {
    user.value = await api<TeamUser>('/auth/login', { method: 'POST', body: { username, password } })
  }

  async function logout() {
    await api('/auth/logout', { method: 'POST' }).catch(() => {})
    user.value = null
  }

  const loadUsers = async () => (users.value = await api<TeamUser[]>('/users'))
  const loadAlarms = async () => (alarms.value = await api<TeamAlarm[]>('/alarms'))

  return { user, users, alarms, api, refresh, login, logout, loadUsers, loadAlarms }
}
