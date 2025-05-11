import useNumberFormatter from "@/hooks/useNumberFormatter"

interface HeaderCashItemProps {
  type: string
  amount: string
}

const translationMap: { [key: string]: string } = {
  BANK: 'Банк',
  CARD: 'Карта',
  CASH: 'Наличные',
}

const HeaderCashItem = ({ type, amount }: HeaderCashItemProps) => {
  const { formatter } = useNumberFormatter()
  const translatedType = translationMap[type] || type

  return (
    <p className="font-medium">
      <span className="font-bold">{translatedType}:</span> {formatter.format(Number(amount)) || 0} сум
    </p>
  )
}

export default HeaderCashItem