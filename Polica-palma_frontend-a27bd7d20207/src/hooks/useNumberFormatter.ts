const useNumberFormatter = () => {
  const formatter = new Intl.NumberFormat('ru-RU', { style: 'decimal' })

  return { formatter }
}

export default useNumberFormatter