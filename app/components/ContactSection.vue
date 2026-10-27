<script setup lang="ts">
const { t, cfg } = useSite()

const form = reactive({ name: '', email: '', type: '', message: '' })
const status = ref<'' | 'sent' | 'error'>('')
const sending = ref(false)

watchEffect(() => {
  if (!t.value.contact.form.types.includes(form.type)) form.type = t.value.contact.form.types[0]!
})

async function submit() {
  const f = t.value.contact.form
  status.value = ''
  // Без бэкенда — открываем почтовый клиент с заполненным письмом
  if (!cfg.formEndpoint) {
    const body = `${form.message}\n\n—\n${form.name} <${form.email}>\n${form.type}`
    location.href = `mailto:${cfg.email}?subject=${encodeURIComponent(`${f.subject}: ${form.type}`)}&body=${encodeURIComponent(body)}`
    status.value = 'sent'
    return
  }
  sending.value = true
  try {
    await $fetch(cfg.formEndpoint, { method: 'POST', body: { ...form }, headers: { Accept: 'application/json' } })
    Object.assign(form, { name: '', email: '', message: '' })
    status.value = 'sent'
  } catch {
    status.value = 'error'
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
            <input id="f-name" v-model="form.name" name="name" required autocomplete="name" placeholder=" ">
            <label for="f-name">{{ t.contact.form.name }}</label>
          </div>
          <div class="field">
            <input id="f-email" v-model="form.email" name="email" type="email" required autocomplete="email" placeholder=" ">
            <label for="f-email">{{ t.contact.form.email }}</label>
          </div>
          <fieldset class="types">
            <legend>{{ t.contact.form.type }}</legend>
            <label v-for="ty in t.contact.form.types" :key="ty">
              <input v-model="form.type" type="radio" name="type" :value="ty"><span>{{ ty }}</span>
            </label>
          </fieldset>
          <div class="field">
            <textarea id="f-msg" v-model="form.message" name="message" rows="4" required placeholder=" " />
            <label for="f-msg">{{ t.contact.form.message }}</label>
          </div>
          <button v-magnetic class="btn btn-primary btn-block" type="submit" :disabled="sending">
            {{ t.contact.form.send }} <AppIcon name="send" />
          </button>
          <p class="form-status" :class="{ err: status === 'error' }" role="status" aria-live="polite">
            {{ status === 'sent' ? t.contact.form.sent : status === 'error' ? t.contact.form.error : '' }}
          </p>
        </form>
      </div>
    </div>
  </section>
</template>
