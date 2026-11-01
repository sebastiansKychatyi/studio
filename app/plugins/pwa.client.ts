// Catch the install offer early: it may fire before the team panel is mounted
export default defineNuxtPlugin(() => {
  usePwa().listen()
})
