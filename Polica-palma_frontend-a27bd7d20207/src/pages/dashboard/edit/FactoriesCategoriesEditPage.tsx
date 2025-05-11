import {useParams} from 'react-router-dom'
import useAxiosPut from '@/hooks/useAxiosPut.ts'
import {z} from 'zod'
import useValues from '@/hooks/useValues.ts'
import DashboardLayout from '@/components/elements/DashboardLayout.tsx'
import EditSection from '@/components/sections/EditSection.tsx'
import InputFormField from '@/components/others/InputFormField.tsx'
import EditSectionSkeleton from '@/components/skeletons/EditSectionSkeleton.tsx'
import NumberFormField from '@/components/others/NumberFormField.tsx'
import ReactSelectFormField from "@/components/others/ReactSelectFormField.tsx"
import {api} from "@/services/api.ts"

const FactoriesCategoriesEditPage = () => {
  const { id } = useParams()
  const { data, isLoading } = api.useGetFactoriesCategoriesQuery(id)
  const { data: industriesData, isLoading: industriesLoading } = api.useGetIndustriesQuery('')
  const { success, form, onSubmit } = useAxiosPut(
    {
      name: z.string().optional(),
      industry: z.string().optional(),
      charge_percent: z.string().optional(),
    },
    {},
    'api/product-factory-categories/product-factory-categories',
    id,
    ["FactoriesCategories"]
  )
  const { inputValues, handleInputChange } = useValues(
    {
      name: '',
      charge_percent: '',
    },
    {
      name: data && data?.name || '',
      charge_percent: data && data?.charge_percent || ''
    },
    isLoading,
    data
  )

  return (
    <>
      <DashboardLayout>
        { !isLoading && data ? (
          <EditSection form={form} onSubmit={onSubmit} success={success}>
            <InputFormField
              control={form.control}
              type='text'
              name='name'
              label='Введите новое название категории'
              _value={inputValues.name}
              _onChange={(e: any) => handleInputChange('name', e.target.value)}
            />

            <ReactSelectFormField
              idData={industriesData}
              isLoading={industriesLoading}
              control={form.control}
              name='industry'
              label='Магазин'
              placeholder={data.industry?.name}
            />

            <NumberFormField
              control={form.control}
              name='charge_percent'
              label='Наценка'
              _value={inputValues.charge_percent}
              _onChange={(e: any) => handleInputChange('charge_percent', e)}
            />
          </EditSection>
        ) : (
          <EditSectionSkeleton />
        ) }
      </DashboardLayout>
    </>
  )
}

export default FactoriesCategoriesEditPage