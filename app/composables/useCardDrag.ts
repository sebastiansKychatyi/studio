// Kanban card drag on Pointer Events: one code path for mouse and finger.
// Mouse starts after a 5 px move, touch after a ~250 ms press (moving earlier = scroll).
// A floating copy follows the pointer, a placeholder shows the drop place, the page and
// the columns row scroll near the edges. Escape or release outside a column cancels.

export interface CardDrop { col: number; index: number }

const PRESS_MS = 250
const EDGE = 70 // px from an edge where auto-scroll starts

export function useCardDrag(onDrop: (cardId: number, fromCol: number, target: CardDrop) => void) {
  // Same shape the template uses for the dragged card and the placeholder
  const drag = ref<{ id: number; from: number } | null>(null)
  const drop = ref<CardDrop | null>(null)

  let pending: { x: number; y: number; pointer: number; el: HTMLElement; id: number; from: number; timer?: ReturnType<typeof setTimeout> } | null = null
  let ghost: HTMLElement | null = null
  let grab = { x: 0, y: 0 }
  let last = { x: 0, y: 0 }
  let frame = 0
  let clickBlocked = false

  function down(e: PointerEvent, id: number, from: number) {
    if (e.button !== 0 || pending || drag.value) return
    if ((e.target as HTMLElement).closest('button, a, input, textarea, select')) return
    const el = e.currentTarget as HTMLElement
    pending = { x: e.clientX, y: e.clientY, pointer: e.pointerId, el, id, from }
    last = { x: e.clientX, y: e.clientY }
    if (e.pointerType !== 'mouse') pending.timer = setTimeout(begin, PRESS_MS)
    addEventListener('pointermove', move, { passive: false })
    addEventListener('pointerup', up)
    addEventListener('pointercancel', cancel)
    addEventListener('touchmove', blockScroll, { passive: false })
    addEventListener('contextmenu', blockMenu)
    addEventListener('keydown', key)
  }

  function begin() {
    if (!pending) return
    const r = pending.el.getBoundingClientRect()
    grab = { x: pending.x - r.left, y: pending.y - r.top }
    ghost = pending.el.cloneNode(true) as HTMLElement
    ghost.classList.add('kb-floating')
    Object.assign(ghost.style, { width: `${r.width}px`, left: '0', top: '0' })
    ;(pending.el.closest('.tp') ?? document.body).appendChild(ghost)
    drag.value = { id: pending.id, from: pending.from }
    document.documentElement.classList.add('kb-dragging')
    navigator.vibrate?.(20)
    place()
    frame = requestAnimationFrame(tick)
  }

  function move(e: PointerEvent) {
    if (!pending || e.pointerId !== pending.pointer) return
    last = { x: e.clientX, y: e.clientY }
    if (!drag.value) {
      const dist = Math.hypot(e.clientX - pending.x, e.clientY - pending.y)
      if (pending.timer) {
        if (dist > 10) finish() // finger moved before the press: it is a scroll
      } else if (dist > 5) begin()
      return
    }
    e.preventDefault()
    place()
  }

  // Ghost position + drop target under the pointer
  function place() {
    if (ghost) ghost.style.transform = `translate(${last.x - grab.x}px, ${last.y - grab.y}px) rotate(1.5deg)`
    const col = document.elementFromPoint(last.x, last.y)?.closest<HTMLElement>('[data-col]')
    if (!col) return (drop.value = null)
    let index = 0
    col.querySelectorAll<HTMLElement>('[data-card]').forEach((el) => {
      if (Number(el.dataset.card) === drag.value?.id) return
      const r = el.getBoundingClientRect()
      if (last.y > r.top + r.height / 2) index++
    })
    const id = Number(col.dataset.col)
    if (drop.value?.col !== id || drop.value.index !== index) drop.value = { col: id, index }
  }

  // Auto-scroll: window vertically, the columns row horizontally
  function tick() {
    if (!drag.value) return
    const speed = (d: number) => Math.ceil(((EDGE - d) / EDGE) * 18)
    const bottom = innerHeight - (matchMedia('(max-width: 860px)').matches ? 80 : 0)
    let moved = false
    if (last.y < EDGE) moved = scroll(window, 0, -speed(last.y))
    else if (last.y > bottom - EDGE) moved = scroll(window, 0, speed(bottom - last.y))
    const row = document.elementFromPoint(last.x, last.y)?.closest<HTMLElement>('.kb-columns')
    if (row && row.scrollWidth > row.clientWidth) {
      const r = row.getBoundingClientRect()
      if (last.x < r.left + EDGE) moved = scroll(row, -speed(Math.max(last.x - r.left, 0)), 0) || moved
      else if (last.x > r.right - EDGE) moved = scroll(row, speed(Math.max(r.right - last.x, 0)), 0) || moved
    }
    if (moved) place()
    frame = requestAnimationFrame(tick)
  }
  function scroll(el: Window | HTMLElement, x: number, y: number) {
    const before = el instanceof Window ? scrollY + scrollX * 1e6 : el.scrollTop + el.scrollLeft * 1e6
    el.scrollBy(x, y)
    return before !== (el instanceof Window ? scrollY + scrollX * 1e6 : el.scrollTop + el.scrollLeft * 1e6)
  }

  function up(e: PointerEvent) {
    if (!pending || e.pointerId !== pending.pointer) return
    const d = drag.value
    const target = drop.value
    if (d) clickBlocked = true // the click after a drag must not open the card
    finish()
    if (d && target) onDrop(d.id, d.from, target)
  }

  function cancel() {
    finish()
  }

  function key(e: KeyboardEvent) {
    if (e.key === 'Escape' && drag.value) {
      e.stopPropagation()
      clickBlocked = true
      finish()
    }
  }

  const blockScroll = (e: TouchEvent) => drag.value && e.cancelable && e.preventDefault()
  const blockMenu = (e: Event) => e.preventDefault()

  function finish() {
    clearTimeout(pending?.timer)
    pending = null
    cancelAnimationFrame(frame)
    ghost?.remove()
    ghost = null
    drag.value = null
    drop.value = null
    document.documentElement.classList.remove('kb-dragging')
    removeEventListener('pointermove', move)
    removeEventListener('pointerup', up)
    removeEventListener('pointercancel', cancel)
    removeEventListener('touchmove', blockScroll)
    removeEventListener('contextmenu', blockMenu)
    removeEventListener('keydown', key)
    setTimeout(() => (clickBlocked = false), 0)
  }

  // Card click handler asks this first
  const dragged = () => clickBlocked

  onBeforeUnmount(finish)
  return { drag, drop, down, dragged }
}
