// Какой дизайн-проект сейчас открыт в окне с прототипом (id проекта или null)
export function useDesignModal() {
  const openId = useState<string | null>('design-modal', () => null)
  return {
    openId,
    show: (id: string) => (openId.value = id),
    close: () => (openId.value = null),
  }
}
