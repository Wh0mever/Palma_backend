import SectionsTop from '@/components/others/SectionsTop.tsx'
import AddDialog from '@/components/others/AddDialog.tsx'
import AddForm from '@/components/others/AddForm.tsx'
import useAxiosPost from '@/hooks/useAxiosPost.ts'
import {z} from 'zod'
import ClientsTable from '@/components/tables/elements/ClientsTable.tsx'
import ClientsFormFields from '@/components/forms/ClientsFormFields.tsx'
import {Button} from '@/components/ui/button.tsx'
import SectionTableSkeleton from '@/components/skeletons/SectionTableSkeleton.tsx'
import useServerSearch from "@/hooks/useServerSearch.ts"
import {api} from "@/services/api.ts"
import useQueryString from "@/hooks/useQueryString.ts"
import {useEffect, useState} from "react"
import ErrorItem from "@/components/items/ErrorItem.tsx"

const ClientsSection = () => {
  const { searchValue, handleSearch, submittedSearch, submitSearch } = useServerSearch()

  const queryParams: any = {
    'search': submittedSearch
  }

  const { queryString: queryStringCollection } = useQueryString(queryParams)
  const [queryString, setQueryString] = useState('')
  const { data, isLoading } = api.useGetClientsQuery({ queryString: queryString })

  const { success, form, onSubmit, pending, error, errorText } = useAxiosPost(
    {
      full_name: z.string({ required_error: "Пожалуйста, введите имя клиента" }),
      phone_number: z.string().max(13, { message: 'Номер телефона слишком длинный' }).optional(),
      discount_percent: z.string().optional(),
      comment: z.string().optional()
    },
    {},
    'api/clients/',
    ["Clients"]
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
            title='Клиенты'
            placeholder='Поиск клиентов'
            inputValue={searchValue}
            onChange={handleSearch}
            onClick={submitSearch}
          />

          <div className='flex items-center justify-center sm:justify-end'>
            {!success ? (
              <AddDialog btnText='Добавить клиента' dialogTitle='Добавить клиента' dialogDesc='Заполните все поля чтобы добавить клиента'>
                { error && (
                  <ErrorItem title='Ошибка' desc={errorText} />
                ) }

                <AddForm
                  form={form}
                  onSubmit={onSubmit}
                  success={success}
                  successDesc='Новый клиент успешно добавлен'
                >
                  <ClientsFormFields form={form}/>

                  <Button className='mt-5' disabled={pending}>Добавить клиента</Button>
                </AddForm>
              </AddDialog>
            ) : null}
          </div>

          <ClientsTable data={data} />
        </section>
      )}
    </>
  )
}

export default ClientsSection