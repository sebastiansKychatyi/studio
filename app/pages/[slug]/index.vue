<script setup lang="ts">
// Personal pages (/sk/sebastian) and city pages (/sk/bratislava)
import { cities } from '~~/data/cities'

const route = useRoute()
const { people } = useSite()
const person = computed(() => people.value.find((p) => p.slug === route.params.slug))
const city = computed(() => cities.find((c) => c.slug === route.params.slug))

if (!person.value && !city.value) {
  throw createError({ statusCode: 404, statusMessage: 'Page not found', fatal: true })
}

// City pages handle their own SEO in CityPage
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
