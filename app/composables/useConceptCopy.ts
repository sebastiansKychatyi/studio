// Picks a concept's copy for the current language
import type { Lang } from '~~/data/site'

export function useConceptCopy<T>(dict: Record<Lang, T>) {
  const { locale } = useI18n()
  return computed<T>(() => dict[locale.value as Lang] ?? dict.en)
}
