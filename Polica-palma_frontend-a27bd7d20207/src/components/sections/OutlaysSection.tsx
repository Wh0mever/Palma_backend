import SectionsTop from '@/components/others/SectionsTop.tsx'
import AddDialog from '@/components/others/AddDialog.tsx'
import useAxiosPost from '@/hooks/useAxiosPost.ts'
import {z} from 'zod'
import AddForm from '@/components/others/AddForm.tsx'
import OutlaysTable from '@/components/tables/elements/OutlaysTable.tsx'
import OutlaysFormFields from '@/components/forms/OutlaysFormFields.tsx'
import {Button} from '@/components/ui/button.tsx'
import SectionTableSkeleton from '@/components/skeletons/SectionTableSkeleton.tsx'
import usePagination from '@/hooks/usePagination.ts'
import useFilters from '@/hooks/useFilters.ts'
import FiltersBlock from '@/components/others/FiltersBlock.tsx'
import PaginationComponent from '@/components/others/PaginationComponent.tsx'
import useServerSearch from '@/hooks/useServerSearch.ts'
import {useEffect, useState} from "react"
import useQueryString from '@/hooks/useQueryString.ts'
import {api} from "@/services/api.ts"

const OutlaysSection = () => {
  const outlaysFilterState = JSON.parse(localStorage.getItem("outlays") || JSON.stringify({
    "currentPage": "",
    "submittedSearch": "",
    "outlayType": "",
  }))

  const { currentPage, setCurrentPage, totalPages, setTotalPages } = usePagination(outlaysFilterState)
  const { outlayType, setOutlayType } = useFilters(outlaysFilterState)
  const { searchValue, handleSearch, submittedSearch, submitSearch } = useServerSearch(setCurrentPage)

  const queryParams: any = {
    'page': currentPage,
    'search': submittedSearch,
    'outlay_type': outlayType !== null && outlayType !== 'null' ? outlayType : ''
  }

  useEffect(() => {
    localStorage.setItem("outlays", JSON.stringify({
      "currentPage": currentPage,
      "submittedSearch": submittedSearch,
      "outlayType": outlayType,
    }))
  }, [
    currentPage,
    submittedSearch,
    outlayType
  ])

  const { queryString: queryStringCollection } = useQueryString(queryParams)
  const [queryString, setQueryString] = useState('')
  const { data, isLoading, isFetching, isError } = api.useGetOutlaysQuery({ queryString: queryString })

  const { form, success, onSubmit, pending } = useAxiosPost(
    {
      title: z.string({ required_error: "Пожалуйста, введите название" }),
      outlay_type: z.string({ required_error: "Пожалуйста, выберите тип расхода" }),
      industry: z.string().optional(),
      comment: z.string().optional(),
    },
    {},
    `api/outlays/`,
    ["Outlays"]
  )

  const sortedData = data && data.results && Array.isArray(data.results) && data?.results?.slice().sort((a: any, b: any) => {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-expect-error
    return new Date(b?.created_at) - new Date(a?.created_at)
  })

  useEffect(() => {
    setQueryString(queryStringCollection)
  }, [currentPage, submittedSearch])

  return (
    <>
      { isLoading ? (
        <SectionTableSkeleton />
      ) : (
        <section className='w-full flex flex-col gap-8'>
          <SectionsTop
            title='Причины расхода'
            placeholder='Поиск причины расхода'
            inputValue={searchValue}
            onChange={handleSearch}
            onClick={submitSearch}
          />

          <div className='flex items-center justify-center sm:justify-end'>
            {!success ? (
              <AddDialog btnText='Добавить причину расхода' dialogTitle='Добавить причину расхода' dialogDesc='Заполните все поля чтобы добавить причину расхода'>
                <AddForm
                  form={form}
                  onSubmit={onSubmit}
                  success={success}
                  successDesc='Причина расхода успешно добавлена'
                >
                  <OutlaysFormFields form={form}/>
                  <Button className='mt-5' disabled={pending}>Добавить причину расхода</Button>
                </AddForm>
              </AddDialog>
            ) : null}
          </div>

          <div className='w-full h-full relative flex flex-col gap-3'>
            <FiltersBlock
              setOutlayType={setOutlayType}
              refetchData={() => setQueryString(queryStringCollection)}
              outlayType={outlayType}
              pathName={'outlays'}
              haventPeriods
              hasOutlayType
            />

            { !isFetching ? (
              <OutlaysTable data={sortedData} />
            ) : (
              <SectionTableSkeleton />
            ) }

            <PaginationComponent
              data={!isError && data}
              currentPage={currentPage}
              totalPages={totalPages}
              setCurrentPage={setCurrentPage}
              setTotalPages={setTotalPages}
              refetchData={() => setQueryString(queryStringCollection)}
            />
          </div>
        </section>
      )}
    </>
  )
}

export default OutlaysSection