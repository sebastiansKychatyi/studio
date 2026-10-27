// Project id shown in the prototype dialog (or null)
export function useDesignModal() {
  const openId = useState<string | null>('design-modal', () => null)
  return {
    openId,
    show: (id: string) => (openId.value = id),
    close: () => (openId.value = null),
  }
}
