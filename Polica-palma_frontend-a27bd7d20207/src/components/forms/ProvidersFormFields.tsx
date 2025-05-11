import InputFormField from '@/components/others/InputFormField.tsx'
import PhoneFormField from '@/components/others/PhoneFormField.tsx'
import TextareaFormField from '@/components/others/TextareaFormField.tsx'
import {FormFieldsProps} from '@/typing/interfaces.ts'

const ProvidersFormFields = ({ form }: FormFieldsProps) => {
  return (
    <>
      <InputFormField control={form.control} type='text' name='full_name' label='Имя поставщика'/>
      <PhoneFormField control={form.control} name='phone_number' label='Номер телефона поставщика' />
      <InputFormField control={form.control} type='text' name='org_name' label='Название организации'/>
      <TextareaFormField control={form.control} name='comment' label='Комментарий'/>
    </>
  )
}

export default ProvidersFormFields