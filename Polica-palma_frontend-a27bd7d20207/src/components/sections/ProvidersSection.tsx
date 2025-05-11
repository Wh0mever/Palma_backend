import SectionsTop from '@/components/others/SectionsTop.tsx'
import useAxiosPost from '@/hooks/useAxiosPost.ts'
import {z} from 'zod'
import AddDialog from '@/components/others/AddDialog.tsx'
import AddForm from '@/components/others/AddForm.tsx'
import ProvidersTable from '@/components/tables/elements/ProvidersTable.tsx'
import ProvidersFormFields from '@/components/forms/ProvidersFormFields.tsx'
import {Button} from '@/components/ui/button.tsx'
import SectionTableSkeleton from '@/components/skeletons/SectionTableSkeleton.tsx'
import {api} from "@/services/api.ts"
import useServerSearch from "@/hooks/useServerSearch.ts"
import useQueryString from "@/hooks/useQueryString.ts"
import {useEffect, useState} from "react"

const ProvidersSection = () => {
  const { searchValue, handleSearch, submittedSearch, submitSearch } = useServerSearch()

  const queryParams: any = {
    'search': submittedSearch
  }

  const { queryString: queryStringCollection } = useQueryString(queryParams)
  const [queryString, setQueryString] = useState('')
  const { data, isLoading } = api.useGetProvidersQuery({ queryString: queryString })

  const { success, form, onSubmit, pending } = useAxiosPost(
    {
      full_name: z.string({ required_error: "Пожалуйста, введите имя поставщика" }),
      phone_number: z.string().max(13, { message: 'Номер телефона слишком длинный' }).optional(),
      org_name: z.string().optional(),
      comment: z.string().optional()
    },
    {},
    'api/providers/',
    ["Providers"]
  )

  useEffect(() => {
    setQueryString(queryStringCollection)
  }, [submittedSearch])

  return (
    <>
      { isLoading ? (
        <SectionTableSkeleton />
      ) : (
        <section className='w-full h-full relative flex flex-col gap-8'>
          <SectionsTop
            title='Поставщики'
            placeholder='Поиск поставщиков'
            inputValue={searchValue}
            onChange={handleSearch}
            onClick={submitSearch}
          />

          <div className='flex items-center justify-center sm:justify-end'>
            {!success ? (
              <AddDialog btnText='Добавить поставщика' dialogTitle='Добавить поставщика' dialogDesc='Заполните все поля чтобы добавить поставщика'>
                <AddForm
                  form={form}
                  onSubmit={onSubmit}
                  success={success}
                  successDesc='Новый поставщик успешно добавлен'
                >
                  <ProvidersFormFields form={form}/>
                  <Button className='mt-5' disabled={pending}>Добавить поставщика</Button>
                </AddForm>
              </AddDialog>
            ) : null}
          </div>

          <ProvidersTable data={data}/>
        </section>
      )}
    </>
  )
}

export default ProvidersSection