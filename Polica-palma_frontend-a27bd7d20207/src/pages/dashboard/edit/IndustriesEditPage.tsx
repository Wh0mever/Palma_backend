import DashboardLayout from '@/components/elements/DashboardLayout.tsx'
import {useParams} from 'react-router-dom'
import InputFormField from '@/components/others/InputFormField.tsx'
import EditSection from '@/components/sections/EditSection.tsx'
import useAxiosPut from '@/hooks/useAxiosPut.ts'
import {z} from 'zod'
import useValues from '@/hooks/useValues.ts'
import EditSectionSkeleton from '@/components/skeletons/EditSectionSkeleton.tsx'
import {useEffect, useState} from 'react'
import CheckboxFormField from '@/components/others/CheckboxFormField.tsx'
import NumberFormField from '@/components/others/NumberFormField.tsx'
import {api} from "@/services/api.ts"
import ErrorItem from "@/components/items/ErrorItem.tsx"

interface CheckboxValues {
  hasSaleCompensation: boolean
}

const IndustriesEditPage = () => {
  const { id } = useParams()
  const { data, isLoading } = api.useGetIndustriesQuery(id)
  const [checkboxValues, setCheckboxValues] = useState<CheckboxValues>({
    hasSaleCompensation: false
  })

  const { inputValues, handleInputChange } = useValues(
    {
      name: '',
      sale_compensation_percent: '',
    },
    {
      name: data && data?.name || '',
      sale_compensation_percent: data && data?.sale_compensation_percent || '',
    },
    isLoading,
    data
  )

  const { success, form, onSubmit, error, errorText } = useAxiosPut(
    {
      name: z.string().optional(),
      sale_compensation_percent: z.string().optional(),
      has_sale_compensation: z.boolean().optional()
    },
    {
      "sale_compensation_percent": String(inputValues.sale_compensation_percent).replace(/\s/g, '')
    },
    'api/industries',
    id,
    ["Industries"]
  )

  useEffect(() => {
    setCheckboxValues({
      hasSaleCompensation: !isLoading && data ? data.has_sale_compensation : false,
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
            { error && (
              <ErrorItem title='Ошибка' desc={errorText} />
            ) }

            <InputFormField
              control={form.control}
              type='text'
              name='name'
              label='Введите новое название магазина'
              _value={inputValues.name}
              _onChange={(e: any) => handleInputChange('name', e.target.value)}
            />
            <NumberFormField
              control={form.control}
              name='sale_compensation_percent'
              label='Процент с продажи'
              _value={inputValues.sale_compensation_percent}
              _onChange={(e: any) => handleInputChange('sale_compensation_percent', e)}
            />
            <CheckboxFormField
              form={form.control}
              _checked={checkboxValues.hasSaleCompensation}
              _onCheckedChange={(e: any) => handleCheckboxChange('hasSaleCompensation', e)}
              name='has_sale_compensation'
              label='Есть доля с продаж?'
            />
          </EditSection>
        ) : (
          <EditSectionSkeleton />
        )}
      </DashboardLayout>
    </>
  )
}

export default IndustriesEditPage