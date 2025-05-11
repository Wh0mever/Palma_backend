import {FormFieldsProps} from '@/typing/interfaces.ts'
import InputFormField from '@/components/others/InputFormField.tsx'
import NewAddDialog from '@/components/others/NewAddDialog.tsx'
import IndustriesFormFields from '@/components/forms/IndustriesFormFields.tsx'
import getUserData from '@/helpers/getUserData.ts'
import {useState} from 'react'
import useAxiosPost from '@/hooks/useAxiosPost.ts'
import {z} from 'zod'
import NumberFormField from '@/components/others/NumberFormField.tsx'
import ReactSelectFormField from "@/components/others/ReactSelectFormField.tsx"
import {api} from "@/services/api.ts"

interface CheckboxValues {
  hasSaleCompensation: boolean
}


const FactoriesCategoriesFormFields = ({ form }: FormFieldsProps) => {
  const { userType } = getUserData()
  const { data: industriesData, isLoading: industriesLoading } = api.useGetIndustriesQuery('')
  const [checkboxValues, setCheckboxValues] = useState<CheckboxValues>({
    hasSaleCompensation: false
  })

  const { success: industriesSuccess, form: industriesForm, onSubmit: industriesSubmit, pending } = useAxiosPost(
    {
      name: z.string({ required_error: "Пожалуйста, введите название магазина" }),
      sale_compensation_percent: z.string().optional(),
      has_sale_compensation: z.boolean().optional()
    },
    {},
    'api/industries/',
    ["Industries"]
  )

  const handleCheckboxChange = (key: keyof CheckboxValues, value: boolean) => {
    setCheckboxValues({
      ...checkboxValues,
      [key]: value
    })
  }

  return (
    <>
      <InputFormField control={form.control} type='text' name='name' label='Название категории'/>

      <div className='flex items-end gap-2'>
        <ReactSelectFormField
          idData={industriesData}
          isLoading={industriesLoading}
          control={form.control}
          name='industry'
          label='Магазин'
          placeholder='Выберите магазин'
        />

        {!industriesSuccess && userType === 'ADMIN' ? (
          <NewAddDialog
            form={industriesForm}
            submit={industriesSubmit}
            success={industriesSuccess}
            successDesc='Новый магазин успешно добавлен'
            btnText='Добавить новый магазин'
            dialogTitle='Добавить новый магазин'
            dialogDesc='Заполните все поля чтобы добавить новый магазин'
            pending={pending}
          >
            <IndustriesFormFields
              form={industriesForm}
              checked={checkboxValues.hasSaleCompensation}
              onCheckedChange={(e: any) => handleCheckboxChange('hasSaleCompensation', e)}
            />
          </NewAddDialog>
        ) : null}
      </div>

      <NumberFormField control={form.control} name='charge_percent' label='Наценка' />
    </>
  )
}

export default FactoriesCategoriesFormFields