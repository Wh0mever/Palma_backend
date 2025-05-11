import InputFormField from '@/components/others/InputFormField.tsx'
import {FormFieldsProps} from '@/typing/interfaces.ts'
import CheckboxFormField from '@/components/others/CheckboxFormField.tsx'
import NumberFormField from '@/components/others/NumberFormField.tsx'

interface IndustriesFormFieldsProps extends FormFieldsProps {
  checked: boolean
  onCheckedChange: (e: any) => void
  numberValue?: string
  numberChange?: (e: any) => void
}

const IndustriesFormFields = ({ form, checked, onCheckedChange, numberChange, numberValue }: IndustriesFormFieldsProps) => {
  return (
    <>
      <InputFormField control={form.control} type='text' name='name' label='Название магазина' />
      <NumberFormField
        control={form.control}
        name='sale_compensation_percent'
        label='Процент с продажи'
        placeholder='от 0 до 100%'
        _value={numberValue}
        _onChange={numberChange}
      />
      <CheckboxFormField
        form={form.control}
        _checked={checked}
        _onCheckedChange={onCheckedChange}
        name='has_sale_compensation'
        label='Есть доля с продаж?'
      />
    </>
  )
}

export default IndustriesFormFields