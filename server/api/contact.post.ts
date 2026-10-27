// Приём заявок из контактной формы → уведомление в Telegram и письмо на e-mail через Web3Forms.
// Ключи задаются переменными окружения (см. .env.example). Работает при запуске Nuxt как сервера
// (`npm run build` + `node .output/server/index.mjs`); на чисто статическом хостинге форма откроет почту.

const hits = new Map<string, number[]>() // простое ограничение: 5 заявок за 10 минут с одного IP
const WINDOW = 10 * 60 * 1000

function rateLimited(ip: string) {
  const now = Date.now()
  const recent = (hits.get(ip) || []).filter((t) => now - t < WINDOW)
  recent.push(now)
  hits.set(ip, recent)
  return recent.length > 5
}

const clean = (v: unknown, max: number) => String(v ?? '').trim().slice(0, max)

export default defineEventHandler(async (event) => {
  const body = await readBody<Record<string, unknown>>(event)

  // Ловушка для ботов: скрытое поле, которое человек не заполняет
  if (clean(body?.company, 200)) return { ok: true }

  const name = clean(body?.name, 120)
  const email = clean(body?.email, 160)
  const type = clean(body?.type, 80)
  const message = clean(body?.message, 5000)
  const lang = clean(body?.lang, 5)
  const page = clean(body?.page, 300)

  if (!name || !message || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    throw createError({ statusCode: 400, statusMessage: 'Invalid form data' })
  }
  if (body?.consent !== true) {
    throw createError({ statusCode: 400, statusMessage: 'Consent required' })
  }

  const ip = getRequestIP(event, { xForwardedFor: true }) || 'unknown'
  if (rateLimited(ip)) throw createError({ statusCode: 429, statusMessage: 'Too many requests' })

  const config = useRuntimeConfig(event)
  const tasks: Promise<unknown>[] = []

  if (config.telegramBotToken && config.telegramChatId) {
    const text = [`🆕 Nový dopyt z webu`, ``, `👤 ${name}`, `✉️ ${email}`, `🏷 ${type}`, `🌐 ${lang.toUpperCase()} · ${page}`, ``, message].join('\n')
    tasks.push(
      $fetch(`https://api.telegram.org/bot${config.telegramBotToken}/sendMessage`, {
        method: 'POST',
        body: { chat_id: config.telegramChatId, text, disable_web_page_preview: true },
      })
    )
  }

  if (config.web3formsKey) {
    tasks.push(
      $fetch('https://api.web3forms.com/submit', {
        method: 'POST',
        body: {
          access_key: config.web3formsKey,
          subject: `Duo Studio — nový dopyt: ${type}`,
          from_name: 'Duo Studio web',
          replyto: email,
          name,
          email,
          type,
          language: lang,
          page,
          message,
        },
      })
    )
  }

  if (!tasks.length) {
    // Ничего не настроено — клиент откроет почтовую программу
    throw createError({ statusCode: 503, statusMessage: 'Contact delivery is not configured' })
  }

  const results = await Promise.allSettled(tasks)
  if (results.every((r) => r.status === 'rejected')) {
    console.error('[contact] delivery failed', results)
    throw createError({ statusCode: 502, statusMessage: 'Delivery failed' })
  }
  return { ok: true }
})
