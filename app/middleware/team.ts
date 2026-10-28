// Team panel guard: no session → login page
export default defineNuxtRouteMiddleware(async () => {
  if (import.meta.server) return
  const { user, refresh } = useTeam()
  if (user.value === undefined) await refresh()
  if (!user.value) return navigateTo(useLocalePath()('/login'))
})
