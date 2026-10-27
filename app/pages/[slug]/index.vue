<script setup lang="ts">
// Личная страница: /sk/sebastian, /cs/roman … У каждого человека свой дизайн (theme в data/site.ts)
const route = useRoute()
const { people } = useSite()
const person = computed(() => people.value.find((p) => p.slug === route.params.slug))

if (!person.value) {
  throw createError({ statusCode: 404, statusMessage: 'Page not found', fatal: true })
}

useSiteSeo(person)
</script>

<template>
  <div v-if="person">
    <ProfileDev v-if="person.theme === 'dev'" :person="person" />
    <ProfileCreative v-else :person="person" />
    <ClientOnly><GeoLangHint /></ClientOnly>
    <DesignModal />
  </div>
</template>
