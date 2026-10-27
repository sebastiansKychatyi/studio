// Тексты концепт-дизайна на текущем языке (у каждого концепта свой небольшой словарь sk / cs / uk)
export function useConceptCopy<T>(dict: { sk: T; cs: T; uk: T }) {
  const { locale } = useI18n()
  return computed<T>(() => dict[locale.value as 'sk' | 'cs' | 'uk'] ?? dict.sk)
}
