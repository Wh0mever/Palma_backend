import NewAddDialog from '@/components/others/NewAddDialog.tsx'
import ProvidersFormFields from '@/components/forms/ProvidersFormFields.tsx'
import TextareaFormField from '@/components/others/TextareaFormField.tsx'
import {FormFieldsProps} from '@/typing/interfaces.ts'
import useAxiosPost from '@/hooks/useAxiosPost.ts'
import {z} from 'zod'
import ReactSelectFormField from "@/components/others/ReactSelectFormField.tsx"
import {api} from "@/services/api.ts"

const IncomesFormFields = ({ form }: FormFieldsProps) => {
  const { data: providerData, isLoading: providersLoading } = api.useGetProvidersQuery('')
  const { success: providerSuccess, form: providerForm, onSubmit: providerSubmit, pending } = useAxiosPost(
    {
      full_name: z.string({ required_error: "Пожалуйста, введите имя поставщика" }),
      phone_number: z.string().optional(),
      org_name: z.string().optional(),
      comment: z.string().optional()
    },
    {},
    'api/providers/',
    ["Providers"]
  )

  return (
    <>
      <div className='flex items-end gap-2'>
        <ReactSelectFormField
          idData={providerData}
          isLoading={providersLoading}
          control={form.control}
          name='provider'
          label='Выберите поставщика'
          placeholder='Выберите поставщика'
        />

        { !providerSuccess ? (
          <NewAddDialog
            pending={pending}
            form={providerForm}
            submit={providerSubmit}
            success={providerSuccess}
            successDesc='Новый поставщик успешно добавлен'
            btnText='Добавить нового поставщика'
            dialogTitle='Добавить нового поставщика'
            dialogDesc='Заполните все поля чтобы добавить нового поставщика'
          >
            <ProvidersFormFields form={providerForm}/>
          </NewAddDialog>
        ) : null }
      </div>
      <TextareaFormField control={form.control} name='comment' label='Комментарий'/>
    </>
  )
}

export default IncomesFormFields