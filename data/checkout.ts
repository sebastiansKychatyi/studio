export type CheckoutThemeId = 'violet' | 'azure'

export interface CheckoutTheme {
  id: CheckoutThemeId
  label: string
}

export interface SlotPlan {
  id: string
  name: string
  slots: number | null
  priceCents: number
}

export interface PaymentMethod {
  id: string
  ticker: string
  network: string
  color: string
  glyph: string
  darkGlyph: boolean
}

export const CHECKOUT_THEMES: CheckoutTheme[] = [
  { id: 'violet', label: 'Violet' },
  { id: 'azure', label: 'Azure' },
]

export const PIECE_PLAN_ID = 'piece'
export const PRICE_PER_SLOT_CENTS = 900
export const MIN_SLOTS = 1
export const MAX_SLOTS = 500
export const MIN_MONTHS = 1
export const MAX_MONTHS = 12
export const PAYMENT_DELAY_MS = 2400
export const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export const SLOT_PLANS: SlotPlan[] = [
  { id: 'lite', name: 'Lite', slots: 10, priceCents: 4900 },
  { id: 'standard', name: 'Standard', slots: 25, priceCents: 9900 },
  { id: 'pro', name: 'Pro', slots: 50, priceCents: 17900 },
  { id: 'premium', name: 'Premium', slots: null, priceCents: 29900 },
]

const NETWORK_COLORS: Record<string, string> = {
  ETH: '#627EEA',
  BSC: '#F0B90B',
  POLYGON: '#8247E5',
  ARBITRUM: '#28A0F0',
  AVAX: '#E84142',
  SOL: '#9945FF',
  TON: '#0098EA',
  TRX: '#EB0029',
}

/**
 * Returns the badge colour of a payment network, or null for a coin's native chain.
 * @param {string} network
 * @returns {string | null}
 */
export function networkColor(network: string): string | null {
  return NETWORK_COLORS[network] ?? null
}

function method(ticker: string, network: string, color: string, glyph: string, darkGlyph = false): PaymentMethod {
  return { id: `${ticker}-${network}`, ticker, network, color, glyph, darkGlyph }
}

export const PAYMENT_METHODS: PaymentMethod[] = [
  method('AVAX', 'AVAX', '#E84142', '▲'),
  method('BNB', 'BSC', '#F0B90B', '◆'),
  method('BTC', 'BTC', '#F7931A', '₿'),
  method('DAI', 'ETH', '#F5AC37', '◈'),
  method('DAI', 'BSC', '#F5AC37', '◈'),
  method('DAI', 'POLYGON', '#F5AC37', '◈'),
  method('DASH', 'DASH', '#008CE7', 'D'),
  method('DOGE', 'DOGE', '#C2A633', 'Ð'),
  method('ETH', 'ETH', '#ECEEF4', 'Ξ', true),
  method('ETH', 'ARBITRUM', '#ECEEF4', 'Ξ', true),
  method('BCH', 'BCH', '#0AC18E', '₿'),
  method('ETH', 'BSC', '#ECEEF4', 'Ξ', true),
  method('LTC', 'LTC', '#345D9D', 'Ł'),
  method('MATIC', 'POLYGON', '#E9E4FB', '⬡', true),
  method('MATIC', 'ETH', '#E9E4FB', '⬡', true),
  method('SHIB', 'ETH', '#E5421A', 'S'),
  method('SOL', 'SOL', '#14141C', '◎'),
  method('TON', 'TON', '#0098EA', '◇'),
  method('TRX', 'TRX', '#EB0029', '▼'),
  method('USDC', 'ETH', '#2775CA', '$'),
  method('USDC', 'AVAX', '#2775CA', '$'),
  method('USDC', 'BSC', '#2775CA', '$'),
  method('USDC', 'ARBITRUM', '#2775CA', '$'),
  method('USDC', 'POLYGON', '#2775CA', '$'),
  method('USDT', 'BSC', '#26A17B', '₮'),
  method('USDT', 'POLYGON', '#26A17B', '₮'),
  method('USDT', 'ARBITRUM', '#26A17B', '₮'),
  method('USDT', 'AVAX', '#26A17B', '₮'),
  method('USDT', 'ETH', '#26A17B', '₮'),
  method('USDT', 'SOL', '#26A17B', '₮'),
  method('USDT', 'TON', '#26A17B', '₮'),
  method('USDT', 'TRX', '#26A17B', '₮'),
  method('XMR', 'XMR', '#F26822', 'M'),
]
