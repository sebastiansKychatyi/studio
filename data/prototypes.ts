export type PrototypeKind = 'classifieds' | 'billing' | 'crm' | 'leads' | 'reservations'

export interface PrototypeSpec {
  width: number
  height: number
}

export const PROTOTYPE_SPECS: Record<PrototypeKind, PrototypeSpec> = {
  classifieds: { width: 960, height: 600 },
  billing: { width: 1200, height: 760 },
  crm: { width: 960, height: 600 },
  leads: { width: 960, height: 600 },
  reservations: { width: 1200, height: 760 },
}
