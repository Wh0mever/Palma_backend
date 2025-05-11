import DashboardLayout from '@/components/elements/DashboardLayout.tsx'
import EditSection from '@/components/sections/EditSection.tsx'
import {useParams} from 'react-router-dom'
import useAxiosPut from '@/hooks/useAxiosPut.ts'
import {z} from 'zod'
import useValues from '@/hooks/useValues.ts'
import {useState} from 'react'
import NumberFormField from '@/components/others/NumberFormField.tsx'
import EditSectionSkeleton from '@/components/skeletons/EditSectionSkeleton.tsx'
import {api} from "@/services/api.ts"

const IncomeItemsEditPage = () => {
  const { id, incomeId } = useParams()
  const { data, isLoading } = api.useGetIncomesIncomeItemsQuery({ id: id, incomeId: incomeId })
  const [countValue, setCountValue] = useState<string>('')
  const [priceValue, setPriceValue] = useState<string>('')
  const { inputValues } = useValues(
    {
      count: '',
      price: ''
    },
    {
      count: data && data?.count,
      price: data && data?.price
    },
    isLoading,
    data
  )

  const { success, form, onSubmit } = useAxiosPut(
    {
      count: z.string().optional(),
      price: z.string().optional(),
    },
    {
      "count": countValue ? countValue.replace(/\s/g, '') : Number(inputValues.count),
      "price": priceValue ? priceValue.replace(/\s/g, '') : Number(inputValues.price)
    },
    'api/incomes',
    `${id}/income-items/${incomeId}`,
    ["Incomes"]
  )

  const handleCountChange = (newValue: any) => setCountValue(newValue)
  const handlePriceChange = (newValue: any) => setPriceValue(newValue)

  return (
    <>
      <DashboardLayout>
        { !isLoading && data ? (
          <>
            <EditSection form={form.control} onSubmit={onSubmit} success={success}>
              <NumberFormField
                control={form.control}
                name='count'
                label='Введите новое количество'
                _value={!countValue ? inputValues.count : countValue}
                _onChange={handleCountChange}
              />
              <NumberFormField
                control={form.control}
                name='price'
                label='Введите новую цену закупа'
                _value={!priceValue ? inputValues.price : priceValue}
                _onChange={handlePriceChange}
              />
            </EditSection>
          </>
        ) : (
          <EditSectionSkeleton />
        ) }
      </DashboardLayout>
    </>
  )
}

export default IncomeItemsEditPage