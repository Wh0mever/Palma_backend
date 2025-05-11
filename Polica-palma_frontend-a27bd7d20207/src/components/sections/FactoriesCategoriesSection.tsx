import SectionsTop from '@/components/others/SectionsTop.tsx'
import useSearch from '@/hooks/useSearch.ts'
import useAxiosPost from '@/hooks/useAxiosPost.ts'
import {z} from 'zod'
import AddDialog from '@/components/others/AddDialog.tsx'
import AddForm from '@/components/others/AddForm.tsx'
import {Button} from '@/components/ui/button.tsx'
import FactoriesCategoriesFormFields from '@/components/forms/FactoriesCategoriesFormFields.tsx'
import FactoriesCategoriesTable from '@/components/tables/elements/FactoriesCategoriesTable.tsx'
import SectionTableSkeleton from '@/components/skeletons/SectionTableSkeleton.tsx'
import {api} from "@/services/api.ts"

const FactoriesCategoriesSection = () => {
  const { data, isLoading } = api.useGetFactoriesCategoriesQuery('')
  const { filteredData, searchTerm, handleSearchChange, handleSearch } = useSearch(data, 'name')
  const { success, form, onSubmit, pending } = useAxiosPost(
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
                  <FactoriesCategoriesFormFields form={form}/>
                  <Button className='mt-5' disabled={pending}>Добавить категорию</Button>
                </AddForm>
              </AddDialog>
            ) : null}
          </div>

          <FactoriesCategoriesTable data={filteredData}/>
        </section>
      )}
    </>
  )
}

export default FactoriesCategoriesSection