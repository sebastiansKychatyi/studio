<script setup lang="ts">
// Одноуровневые страницы: личные (/sk/sebastian, /cs/roman) и страницы городов (/sk/bratislava, /uk/kyiv)
import { cities } from '~~/data/cities'

const route = useRoute()
const { people } = useSite()
const person = computed(() => people.value.find((p) => p.slug === route.params.slug))
const city = computed(() => cities.find((c) => c.slug === route.params.slug))

if (!person.value && !city.value) {
  throw createError({ statusCode: 404, statusMessage: 'Page not found', fatal: true })
}

// SEO личной страницы; у страницы города своё SEO внутри CityPage
if (person.value) useSiteSeo(person)
</script>

<template>
  <CityPage v-if="city" :city="city" />
  <div v-else-if="person">
    <ProfileDev v-if="person.theme === 'dev'" :person="person" />
    <ProfileCreative v-else :person="person" />
    <ClientOnly><GeoLangHint /></ClientOnly>
    <DesignModal />
  </div>
</template>
