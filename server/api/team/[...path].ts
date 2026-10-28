// Team panel API → FastAPI backend (backend/). Same origin keeps the session cookie first-party.
// Target from NUXT_TEAM_API_URL (default http://127.0.0.1:8000).

export default defineEventHandler((event) => {
  const { teamApiUrl } = useRuntimeConfig(event)
  return proxyRequest(event, `${teamApiUrl.replace(/\/$/, '')}${event.path}`, {
    headers: { 'x-forwarded-for': getRequestIP(event, { xForwardedFor: true }) || '' },
  })
})
