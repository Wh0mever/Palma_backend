import DashboardLayout from '@/components/elements/DashboardLayout.tsx'
import {useParams} from 'react-router-dom'
import InputFormField from '@/components/others/InputFormField.tsx'
import EditSection from '@/components/sections/EditSection.tsx'
import useAxiosPut from '@/hooks/useAxiosPut.ts'
import {z} from 'zod'
import useValues from '@/hooks/useValues.ts'
import EditSectionSkeleton from '@/components/skeletons/EditSectionSkeleton.tsx'
import CheckboxFormField from '@/components/others/CheckboxFormField.tsx'
import {useEffect, useState} from 'react'
import ReactSelectFormField from "@/components/others/ReactSelectFormField.tsx"
import {api} from "@/services/api.ts"

interface CheckboxValues {
  isComposite: boolean
  isForSale: boolean
}

const CategoriesEditPage = () => {
  const { id } = useParams()
  const { data, isLoading } = api.useGetCategoriesQuery(id)
  const { data: industriesData, isLoading: industriesLoading } = api.useGetIndustriesQuery('')
  const [checkboxValues, setCheckboxValues] = useState<CheckboxValues>({
    isComposite: !isLoading && data ? data.is_composite : false,
    isForSale: !isLoading && data ? data.is_for_sale : false
  })
  const { success, form, onSubmit } = useAxiosPut(
    {
      name: z.string().optional(),
      industry: z.string().optional(),
      is_composite: z.boolean().default(false).optional(),
      is_for_sale: z.boolean().default(false).optional(),
    },
    {
      "is_composite": checkboxValues.isComposite,
      "is_for_sale": checkboxValues.isForSale
    },
    'api/categories',
    id,
    ["Categories"]
  )
  const { inputValues, handleInputChange } = useValues(
    {
      name: '',
    },
    {
      name: data && data?.name || '',
    },
    isLoading,
    data
  )

  useEffect(() => {
    setCheckboxValues({
      isComposite: !isLoading && data ? data.is_composite : false,
      isForSale: !isLoading && data ? data.is_for_sale : false
    })
  }, [isLoading, data])

  const handleCheckboxChange = (key: keyof CheckboxValues, value: boolean) => {
    setCheckboxValues({
      ...checkboxValues,
      [key]: value
    })
  }

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
            <div className='flex flex-col gap-3'>
              <CheckboxFormField
                form={form.control}
                _checked={checkboxValues.isComposite}
                _onCheckedChange={(e: any) => handleCheckboxChange('isComposite', e)}
                name='is_composite'
                label='Категория для ингридиентов?'
              />
              <CheckboxFormField
                form={form.control}
                _checked={checkboxValues.isForSale}
                _onCheckedChange={(e: any) => handleCheckboxChange('isForSale', e)}
                name='is_for_sale'
                label='Категория для товаров на продажу?'
              />
            </div>
          </EditSection>
        ) : (
          <EditSectionSkeleton/>
        )}
      </DashboardLayout>
    </>
  )
}

export default CategoriesEditPage