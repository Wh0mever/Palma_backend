import InputFormField from '@/components/others/InputFormField.tsx'
import TextareaFormField from '@/components/others/TextareaFormField.tsx'
import {FormFieldsProps} from '@/typing/interfaces.ts'
import ReactSelectFormField from "@/components/others/ReactSelectFormField.tsx"
import {api} from "@/services/api.ts"

const OutlaysFormFields = ({ form }: FormFieldsProps) => {
  const { data: outlaysTypesData, isLoading: outlaysTypesLoading } = api.useGetOutlaysTypesQuery('')
  const { data: industriesData, isLoading: industriesLoading } = api.useGetIndustriesQuery('')

  return (
    <>
      <InputFormField control={form.control} type='text' name='title' label='Название' />
      <ReactSelectFormField
        isValue
        valueData={outlaysTypesData}
        isLoading={outlaysTypesLoading}
        control={form.control}
        name='outlay_type'
        placeholder='Выберите тип расхода' label='Тип расхода'
      />
      <ReactSelectFormField
        idData={industriesData}
        isLoading={industriesLoading}
        control={form.control}
        name='industry'
        placeholder='Выберите магазин'
        label='Магазин'
      />
      <TextareaFormField control={form.control} name='comment' label='Комментарий' />
    </>
  )
}

export default OutlaysFormFields