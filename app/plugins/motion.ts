// Директивы анимаций: v-reveal (появление при прокрутке), v-tilt (3D-наклон),
// v-magnetic (магнитные кнопки), v-spot (световое пятно за курсором).
import type { Directive } from 'vue'

export default defineNuxtPlugin((nuxtApp) => {
  const client = import.meta.client
  const reduce = client && matchMedia('(prefers-reduced-motion: reduce)').matches
  const fine = client && matchMedia('(hover: hover) and (pointer: fine)').matches && !reduce

  const io = client
    ? new IntersectionObserver(
        (entries) =>
          entries.forEach((e) => {
            if (!e.isIntersecting) return
            const el = e.target as HTMLElement
            el.classList.add('is-in')
            io!.unobserve(el)
            // после появления убираем задержку, чтобы hover реагировал сразу
            setTimeout(() => el.style.setProperty('--d', '0ms'), 1400)
          }),
        { threshold: 0.15, rootMargin: '0px 0px -40px 0px' }
      )
    : null

  const reveal: Directive<HTMLElement> = {
    getSSRProps: () => ({ 'data-reveal': '' }),
    mounted(el) {
      el.setAttribute('data-reveal', '')
      io!.observe(el)
    },
    unmounted(el) {
      io?.unobserve(el)
    },
  }

  const follow =
    (onMove: (el: HTMLElement, x: number, y: number, r: DOMRect) => void, onLeave?: (el: HTMLElement) => void): Directive<HTMLElement> => ({
      getSSRProps: () => ({}),
      mounted(el) {
        if (!fine) return
        el.addEventListener('pointermove', (e) => {
          const r = el.getBoundingClientRect()
          onMove(el, e.clientX - r.left, e.clientY - r.top, r)
        })
        if (onLeave) el.addEventListener('pointerleave', () => onLeave(el))
      },
    })

  const tilt = follow(
    (el, x, y, r) => {
      const max = Number(el.dataset.tilt || 5)
      el.style.setProperty('--rx', `${(-(y / r.height - 0.5) * max).toFixed(2)}deg`)
      el.style.setProperty('--ry', `${((x / r.width - 0.5) * max).toFixed(2)}deg`)
    },
    (el) => {
      el.style.setProperty('--rx', '0deg')
      el.style.setProperty('--ry', '0deg')
    }
  )

  const magnetic = follow(
    (el, x, y, r) => {
      el.style.setProperty('--mx', `${(x - r.width / 2) * 0.25}px`)
      el.style.setProperty('--my', `${(y - r.height / 2) * 0.35}px`)
    },
    (el) => {
      el.style.setProperty('--mx', '0px')
      el.style.setProperty('--my', '0px')
    }
  )

  const spot = follow((el, x, y) => {
    el.style.setProperty('--mx', `${x}px`)
    el.style.setProperty('--my', `${y}px`)
  })

  nuxtApp.vueApp.directive('reveal', reveal)
  nuxtApp.vueApp.directive('tilt', tilt)
  nuxtApp.vueApp.directive('magnetic', magnetic)
  nuxtApp.vueApp.directive('spot', spot)

  return { provide: { motion: { reduce, fine } } }
})
