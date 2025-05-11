import InputFormField from '@/components/others/InputFormField.tsx'
import PhoneFormField from '@/components/others/PhoneFormField.tsx'
import TextareaFormField from '@/components/others/TextareaFormField.tsx'
import {FormFieldsProps} from '@/typing/interfaces.ts'

const ClientsFormFields = ({ form }: FormFieldsProps) => {
  return (
    <>
      <InputFormField control={form.control} type='text' name='full_name' label='Имя клиента' />
      <PhoneFormField control={form.control} name='phone_number' label='Номер телефона клиента' />
      <InputFormField control={form.control} type='text' name='discount_percent' label='Процент скидки' />
      <TextareaFormField control={form.control} name='comment' label='Комментарий' />
    </>
  )
}

export default ClientsFormFields