import { useState } from "react"
import { api } from "@/services/api.ts"
import Preloader from "@/components/elements/Preloader.tsx"
import { Check, Circle } from "lucide-react"

const BouquetsListSection = () => {
  const { data, isLoading, isFetching } = api.useGetFactoriesForSaleQuery('')
  const [checkedItems, setCheckedItems] = useState<any[]>([])

  const handleCheck = (item: any) => {
    setCheckedItems(prevState => {
      if (prevState.includes(item)) {
        return prevState.filter(i => i !== item)
      } else {
        return [...prevState, item]
      }
    })
  }

  const sortedData = [...(data || [])].sort((a, b) => {
    const isAChecked = checkedItems.includes(a)
    const isBChecked = checkedItems.includes(b)
    return isAChecked === isBChecked ? 0 : isAChecked ? 1 : -1
  })

  return (
    <>
      <div className="w-full flex flex-col gap-4">
        { !isLoading && !isFetching ? sortedData.map((item: any) => (
          <div
            key={item.id}
            onClick={() => handleCheck(item)}
            className={`w-full p-4 flex items-center gap-4 bg-neutral-100 cursor-pointer rounded-lg font-semibold select-none ${checkedItems.includes(item) ? 'opacity-60 line-through' : ''}`}
          >
            { checkedItems.includes(item) ? (
              <Check className="w-4 h-4" />
            ) : (
              <Circle className="w-4 h-4" />
            ) }
            {item.name}
          </div>
        )) : (
          <Preloader />
        )}

        { data?.length === 0 && <p>Букеты не найдены</p> }
      </div>
    </>
  )
}

export default BouquetsListSection