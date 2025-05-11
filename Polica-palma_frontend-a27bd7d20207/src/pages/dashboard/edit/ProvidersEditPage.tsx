import {useParams} from 'react-router-dom'
import EditSection from '@/components/sections/EditSection.tsx'
import InputFormField from '@/components/others/InputFormField.tsx'
import DashboardLayout from '@/components/elements/DashboardLayout.tsx'
import useAxiosPut from '@/hooks/useAxiosPut.ts'
import {z} from 'zod'
import TextareaFormField from '@/components/others/TextareaFormField.tsx'
import PhoneFormField from '@/components/others/PhoneFormField.tsx'
import useValues from '@/hooks/useValues.ts'
import EditSectionSkeleton from '@/components/skeletons/EditSectionSkeleton.tsx'
import {api} from "@/services/api.ts"

const ProvidersEditPage = () => {
  const { id } = useParams()
  const { data, isLoading } = api.useGetProvidersQuery({ id: id })
  const { success, form, onSubmit } = useAxiosPut(
    {
      full_name: z.string().optional(),
      phone_number: z.string().max(13, { message: 'Номер телефона слишком длинный' }).optional(),
      org_name: z.string().optional(),
      comment: z.string().optional()
    },
    {},
    'api/providers',
    id,
    ["Providers"]
  )
  const { inputValues, handleInputChange } = useValues(
    {
      full_name: '',
      phone_number: '',
      org_name: '',
      comment: ''
    },
    {
      full_name: data && data?.full_name || '',
      phone_number: data && data?.phone_number || '',
      org_name: data && data?.org_name || '',
      comment: data && data?.comment || '',
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
              name='full_name'
              label='Новое имя поставщика'
              _value={inputValues.full_name}
              _onChange={(e: any) => handleInputChange('full_name', e.target.value)}
            />
            <PhoneFormField
              control={form.control}
              name='phone_number'
              label='Новый номер телефона поставщика'
              _value={inputValues.phone_number}
              _onChange={(e: any) => handleInputChange('phone_number', e)}
            />
            <InputFormField
              control={form.control}
              type='text'
              name='org_name'
              label='Новое название организации'
              _value={inputValues.org_name}
              _onChange={(e: any) => handleInputChange('org_name', e.target.value)}
            />
            <TextareaFormField
              control={form.control}
              name='comment'
              label='Новый комментарий'
              _value={inputValues.comment}
              _onChange={(e: any) => handleInputChange('comment', e.target.value)}
            />
          </EditSection>
        ) : (
          <EditSectionSkeleton />
        )}
      </DashboardLayout>
    </>
  )
}

export default ProvidersEditPage