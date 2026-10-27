<script setup lang="ts">
const { t, cfg } = useSite()
const { locale } = useI18n()
const localePath = useLocalePath()

const form = reactive({ name: '', email: '', type: '', message: '', consent: false, company: '' })
const status = ref<'' | 'sent' | 'mail' | 'error'>('')
const sending = ref(false)

watchEffect(() => {
  if (!t.value.contact.form.types.includes(form.type)) form.type = t.value.contact.form.types[0]!
})

// Fallback: open the mail client
function openMail() {
  const f = t.value.contact.form
  const body = `${form.message}\n\n—\n${form.name} <${form.email}>\n${form.type}`
  location.href = `mailto:${cfg.email}?subject=${encodeURIComponent(`${f.subject}: ${form.type}`)}&body=${encodeURIComponent(body)}`
  status.value = 'mail'
}

async function submit() {
  status.value = ''
  sending.value = true
  try {
    await $fetch(cfg.contactApi, {
      method: 'POST',
      body: { ...form, lang: locale.value, page: location.pathname },
    })
    Object.assign(form, { name: '', email: '', message: '', consent: false })
    status.value = 'sent'
  } catch (e: unknown) {
    const code = (e as { statusCode?: number }).statusCode
    // 404 = static hosting, 503 = no keys configured → mail fallback
    if (!code || code === 404 || code === 405 || code === 503) openMail()
    else status.value = 'error'
  } finally {
    sending.value = false
  }
}
</script>

<template>
  <section id="contact" class="section">
    <div class="container">
      <div v-reveal class="contact-card">
        <div class="contact-copy">
          <p class="eyebrow">{{ t.contact.eyebrow }}</p>
          <h2>{{ t.contact.title }}</h2>
          <p class="section-text">{{ t.contact.text }}</p>
          <p class="direct-label">{{ t.contact.direct }}</p>
          <ul class="direct">
            <li><a :href="`mailto:${cfg.email}`"><AppIcon name="mail" /> {{ cfg.email }}</a></li>
            <li><a :href="`tel:${cfg.phone.replace(/\s/g, '')}`"><AppIcon name="phone" /> {{ cfg.phone }}</a></li>
            <li v-if="cfg.telegram"><a :href="cfg.telegram" target="_blank" rel="noopener"><AppIcon name="send" /> Telegram</a></li>
          </ul>
        </div>

        <form class="contact-form" @submit.prevent="submit">
          <div class="field">
            <input id="f-name" v-model="form.name" name="name" required maxlength="120" autocomplete="name" placeholder=" ">
            <label for="f-name">{{ t.contact.form.name }}</label>
          </div>
          <div class="field">
            <input id="f-email" v-model="form.email" name="email" type="email" required maxlength="160" autocomplete="email" placeholder=" ">
            <label for="f-email">{{ t.contact.form.email }}</label>
          </div>
          <fieldset class="types">
            <legend>{{ t.contact.form.type }}</legend>
            <label v-for="ty in t.contact.form.types" :key="ty">
              <input v-model="form.type" type="radio" name="type" :value="ty"><span>{{ ty }}</span>
            </label>
          </fieldset>
          <div class="field">
            <textarea id="f-msg" v-model="form.message" name="message" rows="4" required maxlength="5000" placeholder=" " />
            <label for="f-msg">{{ t.contact.form.message }}</label>
          </div>
          <!-- Honeypot for spam bots -->
          <input v-model="form.company" class="hp" type="text" name="company" tabindex="-1" autocomplete="off" aria-hidden="true">
          <label class="consent">
            <input v-model="form.consent" type="checkbox" required>
            <span>{{ t.contact.form.consent }} <NuxtLink :to="localePath('/privacy')" target="_blank">{{ t.contact.form.consentLink }}</NuxtLink>.</span>
          </label>
          <button v-magnetic class="btn btn-primary btn-block" type="submit" :disabled="sending">
            {{ sending ? t.contact.form.sending : t.contact.form.send }} <AppIcon name="send" />
          </button>
          <p class="form-status" :class="{ err: status === 'error' }" role="status" aria-live="polite">
            {{ status === 'sent' || status === 'mail' ? t.contact.form.sent : status === 'error' ? t.contact.form.error : '' }}
          </p>
        </form>
      </div>
    </div>
  </section>
</template>
