import {useParams} from 'react-router-dom'
import useAxiosPut from '@/hooks/useAxiosPut.ts'
import {z} from 'zod'
import DashboardLayout from '@/components/elements/DashboardLayout.tsx'
import EditSection from '@/components/sections/EditSection.tsx'
import InputFormField from '@/components/others/InputFormField.tsx'
import TextareaFormField from '@/components/others/TextareaFormField.tsx'
import PhoneFormField from '@/components/others/PhoneFormField.tsx'
import useValues from '@/hooks/useValues.ts'
import EditSectionSkeleton from '@/components/skeletons/EditSectionSkeleton.tsx'
import {api} from "@/services/api.ts"
import ErrorItem from "@/components/items/ErrorItem.tsx"

const ClientsEditPage = () => {
  const { id } = useParams()
  const { data, isLoading } = api.useGetClientsQuery({ id: id })
  const { success, form, onSubmit, error, errorText } = useAxiosPut(
    {
      full_name: z.string().optional(),
      phone_number: z.string().max(13, { message: 'Номер телефона слишком длинный' }).optional(),
      discount_percent: z.string().optional(),
      comment: z.string().optional()
    },
    {},
    'api/clients',
    id,
    ["Clients"]
  )
  const { inputValues, handleInputChange } = useValues(
    {
      full_name: '',
      phone_number: '',
      discount_percent: '',
      comment: ''
    },
    {
      full_name: data && data?.full_name || '',
      phone_number: data && data?.phone_number || '',
      discount_percent: data && data?.discount_percent || '',
      comment: data && data?.comment || ''
    },
    isLoading,
    data
  )

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
              name='full_name'
              label='Новое имя клиента'
              _value={inputValues.full_name}
              _onChange={(e: any) => handleInputChange('full_name', e.target.value)}
            />
            <PhoneFormField
              control={form.control}
              name='phone_number'
              label='Новый номер телефона клиента'
              _value={inputValues.phone_number}
              _onChange={(e: any) => handleInputChange('phone_number', e)}
            />
            <InputFormField
              control={form.control}
              type='text'
              name='discount_percent'
              label='Процент скидки'
              _value={inputValues.discount_percent}
              _onChange={(e: any) => handleInputChange('discount_percent', e.target.value)}
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

export default ClientsEditPage