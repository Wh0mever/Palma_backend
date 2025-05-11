import SectionsTop from '@/components/others/SectionsTop.tsx'
import useSearch from '@/hooks/useSearch.ts'
import AddDialog from '@/components/others/AddDialog.tsx'
import AddForm from '@/components/others/AddForm.tsx'
import useAxiosPost from '@/hooks/useAxiosPost.ts'
import CategoriesTable from '@/components/tables/elements/CategoriesTable.tsx'
import CategoriesFormFields from '@/components/forms/CategoriesFormFields.tsx'
import {Button} from '@/components/ui/button.tsx'
import SectionTableSkeleton from '@/components/skeletons/SectionTableSkeleton.tsx'
import {z} from 'zod'
import {useState} from 'react'
import {api} from "@/services/api.ts"

interface CheckboxValues {
  isComposite: boolean
  isForSale: boolean
}

const CategoriesSection = () => {
  const { data, isLoading } = api.useGetCategoriesQuery('')
  const { filteredData, searchTerm, handleSearchChange, handleSearch } = useSearch(data, 'name')
  const [checkboxValues, setCheckboxValues] = useState<CheckboxValues>({
    isComposite: false,
    isForSale: false
  })
  const { success, form, onSubmit, pending } = useAxiosPost(
    {
      name: z.string({ required_error: "Пожалуйста, введите название категории" }),
      industry: z.string({ required_error: "Пожалуйста, выберите магазин" }),
      is_composite: z.boolean().default(false).optional(),
      is_for_sale: z.boolean().default(false).optional(),
    },
    {
      "is_composite": checkboxValues.isComposite,
      "is_for_sale": checkboxValues.isForSale
    },
    'api/categories/',
    ["Categories"]
  )

  const handleCheckboxChange = (key: keyof CheckboxValues, value: boolean) => {
    setCheckboxValues({
      ...checkboxValues,
      [key]: value
    })
  }

  return (
    <>
      { isLoading ? (
        <SectionTableSkeleton />
      ) : (
        <section className='w-full h-full relative flex flex-col gap-8'>
          <SectionsTop
            title='Категории'
            placeholder='Поиск категории'
            inputValue={searchTerm}
            onChange={handleSearchChange}
            onClick={handleSearch}
          />

          <div className='flex items-center justify-center sm:justify-end'>
            {!success ? (
              <AddDialog btnText='Добавить категорию' dialogTitle='Добавить категорию' dialogDesc='Заполните все поля чтобы добавить категорию'>
                <AddForm
                  form={form}
                  onSubmit={onSubmit}
                  success={success}
                  successDesc='Новая категория успешно добавлена'
                >
                  <CategoriesFormFields
                    form={form}
                    checkIsComposite={checkboxValues.isComposite}
                    checkIsForSale={checkboxValues.isForSale}
                    onCheckedChangeComposite={(e: any) => handleCheckboxChange('isComposite', e)}
                    onCheckedChangeForSale={(e: any) => handleCheckboxChange('isForSale', e)}
                  />
                  <Button className='mt-5' disabled={pending}>Добавить категорию</Button>
                </AddForm>
              </AddDialog>
            ) : null}
          </div>

          <CategoriesTable data={filteredData}/>
        </section>
      )}
    </>
  )
}

export default CategoriesSection