import {FormFieldsProps} from '@/typing/interfaces.ts'
import NewAddDialog from '@/components/others/NewAddDialog.tsx'
import FactoriesCategoriesFormFields from '@/components/forms/FactoriesCategoriesFormFields.tsx'
import useAxiosPost from '@/hooks/useAxiosPost.ts'
import {z} from 'zod'
import getUserData from '@/helpers/getUserData.ts'
import ReactSelectFormField from "@/components/others/ReactSelectFormField.tsx"
import {api} from "@/services/api.ts"

const BouquetsFormFields = ({ form }: FormFieldsProps) => {
  const { userType } = getUserData()
  const { data: factoriesCategoriesData, isLoading: factoriesCategoriesLoading } = api.useGetFactoriesCategoriesQuery('')
  const { data: salesTypesData, isLoading: salesTypesLoading } = api.useGetFactoriesSalesTypesQuery('')
  const { data: floristData, isLoading: floristLoading } = api.useGetFloristsQuery('')

  const { success: categoriesSuccess, form: categoriesForm, onSubmit: categoriesSubmit, pending: categoriesPending } = useAxiosPost(
    {
      name: z.string({ required_error: "Пожалуйста, введите название категории" }),
      industry: z.string({ required_error: "Пожалуйста, выберите магазин" }),
      charge_percent: z.string().optional()
    },
    {},
    'api/product-factory-categories/product-factory-categories/',
    ["FactoriesCategories", "Factories"]
  )

  return (
    <>
      <div className='flex items-end gap-2'>
        <ReactSelectFormField
          idData={factoriesCategoriesData}
          isLoading={factoriesCategoriesLoading}
          control={form.control}
          name='category'
          placeholder='Выберите категорию'
          label='Категория'
        />

        { !categoriesSuccess ? (
          <NewAddDialog
            pending={categoriesPending}
            form={categoriesForm}
            submit={categoriesSubmit}
            success={categoriesSuccess}
            successDesc='Новая категория успешно добавлена'
            btnText='Добавить новую категорию'
            dialogTitle='Добавить новую категорию'
            dialogDesc='Заполните все поля чтобы добавить новую категорию'
          >
            <FactoriesCategoriesFormFields form={categoriesForm} />
          </NewAddDialog>
        ) : null }
      </div>

      <ReactSelectFormField
        isValue
        valueData={salesTypesData}
        isLoading={salesTypesLoading}
        control={form.control}
        name='sales_type'
        placeholder='Выберите тип продажи'
        label='Тип продажи'
      />

      { userType !== 'CRAFTER' && (
        <ReactSelectFormField
          idData={floristData}
          isLoading={floristLoading}
          control={form.control}
          name='florist'
          placeholder='Выберите флориста'
          label='Флорист'
        />
      ) }
    </>
  )
}

export default BouquetsFormFields