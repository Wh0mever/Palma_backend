import InputFormField from '@/components/others/InputFormField.tsx'
import NewAddDialog from '@/components/others/NewAddDialog.tsx'
import CategoriesFormFields from '@/components/forms/CategoriesFormFields.tsx'
import ImageFormField from '@/components/others/ImageFormField.tsx'
import {FormFieldsProps} from '@/typing/interfaces.ts'
import useAxiosPost from '@/hooks/useAxiosPost.ts'
import {z} from 'zod'
import NumberFormField from '../others/NumberFormField'
import {useState} from 'react'
import ReactSelectFormField from "@/components/others/ReactSelectFormField.tsx"
import {api} from "@/services/api.ts"

interface ProductsFormFieldsProps extends FormFieldsProps {
  inputValue: string
  onChange: (e: any) => void
  numberValue?: string
  numberChange?: (newValue: any) => void
}

interface CheckboxValues {
  isComposite: boolean
  isForSale: boolean
}

const ProductsFormFields = ({ form, inputValue, onChange, numberChange, numberValue }: ProductsFormFieldsProps) => {
  const { data: categoriesData, isLoading: categoriesLoading } = api.useGetCategoriesQuery('')
  const { data: optionsData, isLoading: optionsLoading } = api.useGetProductsOptionsQuery('')
  const { success: categoriesSuccess, form: categoriesForm, onSubmit: categoriesSubmit, pending } = useAxiosPost(
    {
      name: z.string({ required_error: "Пожалуйста, введите название категории" }),
      industry: z.string({ required_error: "Пожалуйста, выберите магазин" }),
      is_composite: z.boolean().default(false).optional(),
      is_for_sale: z.boolean().default(false).optional(),
    },
    {},
    'api/categories/',
    ["Categories"]
  )
  const [checkboxValues, setCheckboxValues] = useState<CheckboxValues>({
    isComposite: false,
    isForSale: false
  })

  const handleCheckboxChange = (key: keyof CheckboxValues, value: boolean) => {
    setCheckboxValues({
      ...checkboxValues,
      [key]: value
    })
  }

  return (
    <>
      <InputFormField control={form.control} type='text' name='name' label='Название товара' />
      <ReactSelectFormField
        isValue
        valueData={optionsData}
        isLoading={optionsLoading}
        control={form.control}
        name='unit_type'
        label='Единица измерения'
        placeholder='Выберите единицу измерения'
      />
      <NumberFormField _value={numberValue} _onChange={numberChange} control={form.control} name='price' label='Цена продажи' />
      <div className='flex items-end gap-2'>
        <ReactSelectFormField
          idData={categoriesData}
          isLoading={categoriesLoading}
          control={form.control}
          name='category'
          label='Категория'
          placeholder='Выберите категорию'
        />

        { !categoriesSuccess ? (
          <NewAddDialog
            pending={pending}
            form={categoriesForm}
            submit={categoriesSubmit}
            success={categoriesSuccess}
            successDesc='Новая категория успешно добавлена'
            btnText='Добавить новую категорию'
            dialogTitle='Добавить новую категорию'
            dialogDesc='Заполните все поля чтобы добавить новую категорию'
          >
            <CategoriesFormFields
              form={categoriesForm}
              checkIsComposite={checkboxValues.isComposite}
              checkIsForSale={checkboxValues.isForSale}
              onCheckedChangeComposite={(e: any) => handleCheckboxChange('isComposite', e)}
              onCheckedChangeForSale={(e: any) => handleCheckboxChange('isForSale', e)}
            />
          </NewAddDialog>
        ) : null }
      </div>
      <ImageFormField
        form={form.control}
        name='image'
        label='Изображение'
        _value={inputValue}
        _onChange={onChange}
      />
    </>
  )
}

export default ProductsFormFields