<script setup lang="ts">
import {
  CHECKOUT_THEMES,
  EMAIL_PATTERN,
  MAX_MONTHS,
  MAX_SLOTS,
  MIN_MONTHS,
  MIN_SLOTS,
  PAYMENT_DELAY_MS,
  PAYMENT_METHODS,
  PIECE_PLAN_ID,
  PRICE_PER_SLOT_CENTS,
  SLOT_PLANS,
  networkColor,
  type CheckoutThemeId,
  type PaymentMethod,
  type SlotPlan,
} from '~~/data/checkout'
import { formatUsd, newId } from '~/utils/prototype'

defineProps<{ preview?: boolean }>()

type OrderStatus = 'pending' | 'paid'

interface Order {
  id: string
  amountCents: number
  methodLabel: string
  summary: string
  status: OrderStatus
}

const PERCENT = 100

const themeId = ref<CheckoutThemeId>('violet')
const email = ref('')
const planId = ref(PIECE_PLAN_ID)
const pieceSlots = ref(MIN_SLOTS)
const months = ref(MIN_MONTHS)
const methodId = ref<string | null>(null)
const order = ref<Order | null>(null)
let settleTimer: ReturnType<typeof setTimeout> | undefined

const isPiecePlan = computed(() => planId.value === PIECE_PLAN_ID)
const plan = computed(() => SLOT_PLANS.find((p) => p.id === planId.value))
const method = computed(() => PAYMENT_METHODS.find((m) => m.id === methodId.value))
const emailValid = computed(() => EMAIL_PATTERN.test(email.value))
const emailInvalid = computed(() => email.value.length > 0 && !emailValid.value)
const monthlyCents = computed(() => (plan.value ? plan.value.priceCents : pieceSlots.value * PRICE_PER_SLOT_CENTS))
const totalCents = computed(() => monthlyCents.value * months.value)
const canBuy = computed(() => emailValid.value && method.value !== undefined && order.value === null)

const slotsLabel = (slots: number | null) => (slots === null ? 'Unlimited slots' : `${slots} ${slots === 1 ? 'slot' : 'slots'}`)
const methodLabel = (m: PaymentMethod) => `${m.ticker}-${m.network}`
const discountPercent = (p: SlotPlan) =>
  p.slots === null ? 0 : Math.round((1 - p.priceCents / (p.slots * PRICE_PER_SLOT_CENTS)) * PERCENT)

function buy() {
  if (!canBuy.value || !method.value) return
  const purchasedSlots = plan.value ? plan.value.slots : pieceSlots.value
  order.value = {
    id: `#${newId().toUpperCase()}`,
    amountCents: totalCents.value,
    methodLabel: methodLabel(method.value),
    summary: `${slotsLabel(purchasedSlots)} for ${months.value} ${months.value === 1 ? 'month' : 'months'}`,
    status: 'pending',
  }
  settleTimer = setTimeout(() => {
    if (order.value) order.value.status = 'paid'
  }, PAYMENT_DELAY_MS)
}

function startNewOrder() {
  clearTimeout(settleTimer)
  order.value = null
  methodId.value = null
}

onBeforeUnmount(() => clearTimeout(settleTimer))
</script>

<template>
  <div class="ck" :class="[`ck--${themeId}`, { 'is-preview': preview }]" :inert="preview || undefined">
    <div class="ck-title">
      <h1>Payments</h1>
      <div class="ck-themes" role="group" aria-label="Checkout theme">
        <button
          v-for="theme in CHECKOUT_THEMES"
          :key="theme.id"
          type="button"
          :class="{ on: theme.id === themeId }"
          @click="themeId = theme.id"
        >
          {{ theme.label }}
        </button>
      </div>
    </div>

    <div class="ck-layout">
      <section class="ck-panel ck-main">
        <div class="ck-block">
          <div class="ck-step"><span>01</span><b>Buy Slots</b></div>
          <input v-model="email" class="ck-input" :class="{ invalid: emailInvalid }" type="email" placeholder="mail" aria-label="Email">
        </div>

        <div class="ck-block">
          <div class="ck-step"><span>02</span><b>Select Plan:</b></div>
          <div class="ck-or"><i /><b>or</b><i /></div>
        </div>

        <div class="ck-plans-row">
          <div
            class="ck-piece"
            :class="{ on: isPiecePlan }"
            role="button"
            tabindex="0"
            @click="planId = PIECE_PLAN_ID"
            @keydown.enter="planId = PIECE_PLAN_ID"
          >
            <b class="ck-piece-title">Slots by piece</b>
            <div class="ck-field">
              <span>Slots</span>
              <CheckoutStepper v-model="pieceSlots" :min="MIN_SLOTS" :max="MAX_SLOTS" label="slots" @click="planId = PIECE_PLAN_ID" />
            </div>
            <div class="ck-sum">
              <p><span>Price per slots</span><span>{{ formatUsd(PRICE_PER_SLOT_CENTS) }}</span></p>
              <p class="ck-sum-total"><b>Total</b><strong>{{ formatUsd(pieceSlots * PRICE_PER_SLOT_CENTS) }}</strong></p>
            </div>
            <span v-if="isPiecePlan" class="ck-check"><svg viewBox="0 0 16 16" width="14" height="14"><path d="M3.5 8.5l3 3 6-7" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" /></svg></span>
          </div>

          <span class="ck-vline" />

          <div class="ck-plans">
            <button v-for="p in SLOT_PLANS" :key="p.id" type="button" class="ck-plan" :class="{ on: p.id === planId }" @click="planId = p.id">
              <span class="ck-plan-name">{{ p.name }}</span>
              <span class="ck-plan-slots">
                <b>{{ p.slots ?? '∞' }}</b>
                <em>Slots</em>
              </span>
              <span class="ck-plan-price">
                <em>/month</em>
                <b>{{ formatUsd(p.priceCents) }}</b>
                <em :class="{ hidden: p.slots === null }">-{{ discountPercent(p) }}%</em>
              </span>
            </button>
          </div>
        </div>
      </section>

      <section class="ck-panel ck-side">
        <div class="ck-block">
          <div class="ck-step"><span>03</span><b>Select a month:</b></div>
          <div class="ck-months">
            <span>Months</span>
            <CheckoutStepper v-model="months" :min="MIN_MONTHS" :max="MAX_MONTHS" label="months" />
          </div>
        </div>

        <div class="ck-block">
          <div class="ck-step"><span>04</span><b>Payment</b></div>

          <div v-if="order" class="ck-order">
            <p class="ck-order-id">Invoice {{ order.id }}</p>
            <p class="ck-order-amount">{{ formatUsd(order.amountCents) }}</p>
            <p class="ck-order-method">in {{ order.methodLabel }}</p>
            <span class="ck-status" :class="order.status">{{ order.status === 'paid' ? 'Paid' : 'Waiting for payment…' }}</span>
            <p v-if="order.status === 'paid'" class="ck-order-result">Payment confirmed. {{ order.summary }} activated for {{ email }}.</p>
            <button type="button" class="ck-buy on" :disabled="order.status === 'pending'" @click="startNewOrder">New order</button>
          </div>

          <template v-else>
            <div class="ck-methods">
              <span>Available payment methods:</span>
              <div class="ck-coins">
                <button
                  v-for="m in PAYMENT_METHODS"
                  :key="m.id"
                  type="button"
                  class="ck-coin"
                  :class="{ on: m.id === methodId }"
                  :data-label="methodLabel(m)"
                  :aria-label="methodLabel(m)"
                  :aria-pressed="m.id === methodId"
                  @click="methodId = m.id"
                >
                  <i class="ck-coin-face" :class="{ dark: m.darkGlyph }" :style="{ background: m.color }">{{ m.glyph }}</i>
                  <i v-if="networkColor(m.network) && m.network !== m.ticker" class="ck-coin-net" :style="{ background: networkColor(m.network)! }" />
                </button>
              </div>
            </div>
            <button type="button" class="ck-buy" :class="{ on: canBuy }" :disabled="!canBuy" @click="buy">Buy {{ formatUsd(totalCents) }}</button>
          </template>
        </div>
      </section>
    </div>
  </div>
</template>

<style>
.ck { --line: rgba(255, 255, 255, .12); --muted: #767C86; --label: #F2F4FC; width: 1200px; height: 760px; display: flex; flex-direction: column; gap: 12px; padding: 12px 16px; overflow: hidden; border-radius: 16px; background: var(--bg); color: #fff; font-family: var(--font); text-align: left; letter-spacing: normal; box-shadow: 0 30px 70px -30px rgba(0, 0, 0, .55); }
.ck--violet { --bg: #0E0D12; --accent: #8D78F9; --card-from: #1A1A24; --card-to: #272740; --raised: #1A1A24; --font: 'Roboto', system-ui, sans-serif; --total: linear-gradient(90deg, #9F6FDD, #F38081); }
.ck--azure { --bg: #12181F; --accent: #2187FF; --card-from: #283641; --card-to: #394962; --raised: #36485E; --font: 'Orbitron', system-ui, sans-serif; --total: linear-gradient(90deg, #2187FF, #2187FF); }
.ck button { font: inherit; color: inherit; cursor: pointer; }
.ck.is-preview { pointer-events: none; }
.ck-title { display: flex; align-items: center; justify-content: space-between; padding: 0 0 0 0; }
.ck-title h1 { margin: 0; font-size: 24px; line-height: 1.25; font-weight: 600; }
.ck-themes { display: flex; gap: 2px; padding: 3px; border-radius: 999px; border: 1px solid var(--line); }
.ck-themes button { border: 0; background: none; padding: 5px 14px; border-radius: 999px; font-size: 12px; color: var(--muted); transition: background .2s, color .2s; }
.ck-themes button.on { background: var(--accent); color: #fff; }
.ck-layout { display: flex; gap: 16px; align-items: flex-start; }
.ck-panel { display: flex; flex-direction: column; gap: 16px; padding: 16px; border: 1px solid var(--line); border-radius: 12px; }
.ck-main { flex: 1; min-width: 0; }
.ck-side { flex: none; width: 344px; }
.ck-block { display: flex; flex-direction: column; gap: 16px; }
.ck-step { display: flex; align-items: flex-start; gap: 16px; font-size: 18px; font-weight: 600; line-height: 1.55; }
.ck-step span { color: var(--accent); }
.ck-input { width: 100%; max-width: 487px; height: 52px; padding: 0 16px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, .6); background: transparent; color: #fff; font: inherit; font-size: 14px; outline: none; transition: border-color .2s; }
.ck-input::placeholder { color: rgba(255, 255, 255, .31); letter-spacing: -.5px; }
.ck-input:focus { border-color: var(--accent); }
.ck-input.invalid { border-color: #F87171; }
.ck-or { display: flex; align-items: center; gap: 41px; }
.ck-or i { height: 1px; background: var(--line); }
.ck-or i:first-child { width: 100%; max-width: 195px; }
.ck-or i:last-child { flex: 1; }
.ck-or b { font-size: 20px; font-weight: 600; }
.ck-plans-row { display: flex; gap: 16px; align-items: stretch; }
.ck-piece { position: relative; flex: none; width: 230px; display: flex; flex-direction: column; gap: 12px; padding: 12px 16px; border: 2px solid var(--line); border-radius: 12px; background: var(--raised); cursor: pointer; outline: none; transition: border-color .2s; }
.ck-piece.on, .ck-piece:focus-visible { border-color: var(--accent); }
.ck-piece-title { font-size: 18px; font-weight: 600; }
.ck-field { display: flex; flex-direction: column; gap: 10px; font-size: 16px; color: var(--label); }
.ck-sum { display: flex; flex-direction: column; gap: 7px; font-size: 16px; letter-spacing: -.5px; }
.ck-sum p { display: flex; align-items: center; justify-content: space-between; margin: 0; }
.ck-sum p span:first-child { color: #9CA3AF; }
.ck-sum-total { padding: 9px 0; border-top: 1px solid var(--line); }
.ck-sum-total b { font-weight: 600; }
.ck-sum-total strong { font-size: 20px; font-weight: 700; background: var(--total); -webkit-background-clip: text; background-clip: text; color: transparent; }
.ck-check { position: absolute; top: -6px; right: -7.6px; width: 24px; height: 24px; display: grid; place-items: center; border-radius: 6px; background: var(--accent); border: 1.5px solid var(--accent); }
.ck-vline { flex: none; width: 1px; background: var(--line); }
.ck-plans { flex: 1; display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; align-content: start; }
.ck-plan { display: grid; grid-template-rows: 40px 1fr auto; gap: 8px; height: 196px; padding: 16px 12px; text-align: center; border: 2px solid var(--line); border-radius: 12px; background: linear-gradient(to bottom, var(--card-from), var(--card-to)); transition: border-color .2s, transform .2s; }
.ck-plan:hover { border-color: rgba(255, 255, 255, .3); }
.ck-plan.on { border-color: var(--accent); }
.ck-plan-name { display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 500; text-transform: uppercase; line-height: 1.25; }
.ck-plan-slots { display: flex; flex-direction: column; align-items: center; justify-content: center; }
.ck-plan-slots b { font-size: 24px; font-weight: 500; line-height: .94; }
.ck-plan-slots em, .ck-plan-price em { font-style: normal; font-size: 12px; color: var(--muted); }
.ck-plan-slots em { font-weight: 500; }
.ck-plan-price { display: flex; flex-direction: column; align-items: center; gap: 2px; align-self: end; letter-spacing: -.5px; }
.ck-plan-price b { font-size: 18px; font-weight: 700; line-height: 1; }
.ck-plan-price em { display: flex; align-items: center; height: 18px; }
.ck-plan-price em.hidden { visibility: hidden; }
.ck-months { display: flex; flex-direction: column; gap: 8px; padding: 12px; border: 1px solid var(--line); border-radius: 12px; background: var(--raised); font-size: 16px; color: var(--label); }
.ck-methods { display: flex; flex-direction: column; gap: 8px; padding: 12px; border: 1px solid #323543; border-radius: 12px; font-size: 16px; letter-spacing: -.5px; box-shadow: 0 1px 2px rgba(0, 0, 0, .05); }
.ck-coins { display: grid; grid-template-columns: repeat(5, 40px); gap: 6px 21px; width: fit-content; padding: 12px; margin: -12px; }
.ck-coin { position: relative; width: 40px; height: 40px; padding: 0; border: 0; border-radius: 50%; background: none; transition: box-shadow .2s; }
.ck-coin:hover, .ck-coin.on { box-shadow: 0 0 0 2px var(--accent), 0 0 14px var(--accent); }
.ck-coin-face { width: 100%; height: 100%; display: grid; place-items: center; border-radius: 50%; font-style: normal; font-size: 18px; font-weight: 700; color: #fff; font-family: system-ui, sans-serif; }
.ck-coin-face.dark { color: #20222C; }
.ck-coin-net { position: absolute; top: -2px; right: -2px; width: 14px; height: 14px; border-radius: 50%; border: 2px solid var(--bg); box-sizing: content-box; }
.ck-coin::after { content: attr(data-label); position: absolute; left: 50%; bottom: calc(100% + 10px); z-index: 5; padding: 8px 14px; border-radius: 8px; background: linear-gradient(to bottom, #4A5B73, #2B3748); color: #fff; font-size: 14px; font-weight: 700; letter-spacing: normal; white-space: nowrap; opacity: 0; transform: translate(-50%, 4px); pointer-events: none; transition: opacity .15s, transform .15s; }
.ck-coin:hover::after { opacity: 1; transform: translate(-50%, 0); }
.ck-buy { width: 100%; height: 52px; padding: 13px 16px; border: 0; border-radius: 12px; background: var(--card-from); color: rgba(255, 255, 255, .5); font-size: 20px; font-weight: 400; transition: background .2s, color .2s, filter .2s; }
.ck-buy:disabled { cursor: not-allowed; }
.ck-buy.on { background: var(--total); color: #fff; }
.ck-buy.on:hover:not(:disabled) { filter: brightness(1.1); }
.ck-buy.on:disabled { opacity: .5; }
.ck-order { display: flex; flex-direction: column; align-items: flex-start; gap: 10px; padding: 16px; border: 1px solid var(--line); border-radius: 12px; background: var(--raised); }
.ck-order p { margin: 0; }
.ck-order-id { font-size: 14px; color: var(--muted); }
.ck-order-amount { font-size: 32px; font-weight: 700; letter-spacing: -.5px; }
.ck-order-method { font-size: 16px; color: var(--label); }
.ck-status { padding: 4px 12px; border-radius: 999px; font-size: 12px; font-weight: 600; }
.ck-status.pending { background: rgba(251, 191, 36, .16); color: #FBBF24; }
.ck-status.paid { background: rgba(52, 211, 153, .16); color: #34D399; }
.ck-order-result { font-size: 14px; line-height: 1.5; color: var(--label); }
.ck-order .ck-buy { margin-top: 6px; }
</style>
