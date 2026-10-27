const ID_LENGTH = 6
const CENTS_PER_DOLLAR = 100

export function formatUsd(cents: number): string {
  const dollars = (cents / CENTS_PER_DOLLAR).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  return `$${dollars}`
}

export function newId(): string {
  return Math.random().toString(36).slice(2, 2 + ID_LENGTH)
}
