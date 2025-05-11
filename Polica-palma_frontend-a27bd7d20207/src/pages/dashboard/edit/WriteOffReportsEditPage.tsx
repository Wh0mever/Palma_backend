import DashboardLayout from '@/components/elements/DashboardLayout.tsx'
import {useNavigate, useParams} from 'react-router-dom'
import EditSectionSkeleton from '@/components/skeletons/EditSectionSkeleton.tsx'
import {ChevronLeft} from 'lucide-react'
import {Button} from '@/components/ui/button.tsx'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import WriteOffReportsEditTable from '@/components/tables/elements/WriteOffReportsEditTable.tsx'
import SectionsTop from '@/components/others/SectionsTop.tsx'
import usePagination from '@/hooks/usePagination.ts'
import PaginationComponent from '@/components/others/PaginationComponent.tsx'
import useFilters from '@/hooks/useFilters.ts'
import FiltersBlock from '@/components/others/FiltersBlock.tsx'
import useServerSearch from '@/hooks/useServerSearch.ts'
import {useEffect, useState} from "react"
import useQueryString from '@/hooks/useQueryString.ts'
import {api} from "@/services/api.ts"
import SectionTableSkeleton from "@/components/skeletons/SectionTableSkeleton.tsx"

const WriteOffReportsEditPage = () => {
  const writeOffReportsEditFilterState = JSON.parse(localStorage.getItem("writeOffReportsEdit") || JSON.stringify({
    "currentPage": "",
    "submittedSearch": "",
    "periodFromFormatted": "",
    "periodToFormatted": "",
    "periodFrom": "",
    "periodTo": "",
  }))

  const { id } = useParams()
  const navigate = useNavigate()
  const { formatter } = useNumberFormatter()
  const { currentPage, setCurrentPage, totalPages, setTotalPages } = usePagination(writeOffReportsEditFilterState)
  const { periodTo, periodFrom, periodFromFormatted, periodToFormatted, setPeriodFrom, setPeriodTo } = useFilters(writeOffReportsEditFilterState)
  const { searchValue, handleSearch, submittedSearch, submitSearch } = useServerSearch(setCurrentPage)

  const queryParams: any = {
    'page': currentPage,
    'search': submittedSearch,
    'start_date': periodFromFormatted !== null ? periodFromFormatted : '',
    'end_date': periodToFormatted !== null ? periodToFormatted : ''
  }

  useEffect(() => {
    localStorage.setItem("writeOffReportsEdit", JSON.stringify({
      "currentPage": currentPage,
      "submittedSearch": submittedSearch,
      "periodFromFormatted": periodFromFormatted,
      "periodToFormatted": periodToFormatted,
      "periodFrom": periodFrom,
      "periodTo": periodTo,
    }))
  }, [
    currentPage,
    submittedSearch,
    periodFromFormatted,
    periodToFormatted,
    periodFrom,
    periodTo
  ])

  const { queryString: queryStringCollection } = useQueryString(queryParams)
  const [queryString, setQueryString] = useState('')

  const { data, isLoading } = api.useGetWriteOffsReportsQuery({ id: id, queryString: queryString })
  const { data: writeOffsData, isLoading: writeOffsLoading, isFetching: writeOffsFetching, isError: writeOffsError } = api.useGetWriteOffsReportsQuery({ id: id, queryString: queryString, item: 'write-offs' })

  useEffect(() => {
    setQueryString(queryStringCollection)
  }, [currentPage, submittedSearch])

  return (
    <>
      <DashboardLayout>
        { !isLoading && !writeOffsLoading ? (
          <section className='w-full flex flex-col gap-8'>
            <Button className='w-48' variant='outline' onClick={() => navigate(-1)}>
              <ChevronLeft className='w-4 h-4 mr-2'/> Вернуться назад
            </Button>

            <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-3 text-sm'>
              <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Товар: <span className='font-bold'>{data.name}</span></p>
              <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Категория: <span className='font-bold'>{data.category?.name}</span></p>
              <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Общая себестоимость: <span className='font-bold'>{formatter.format(data.self_price_sum)} сум</span></p>
              <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Количество списания: <span className='font-bold'>{formatter.format(data.product_count)} шт</span></p>
              <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Код товара: <span className='font-bold'>{data.code}</span></p>
            </div>

            <SectionsTop
              title='Списания'
              placeholder='Поиск списаний'
              inputValue={searchValue}
              onChange={handleSearch}
              onClick={submitSearch}
            />

            <div className='w-full h-full relative flex flex-col gap-3'>
              <FiltersBlock
                periodFrom={periodFrom}
                periodTo={periodTo}
                setPeriodFrom={setPeriodFrom}
                setPeriodTo={setPeriodTo}
                refetchData={() => setQueryString(queryStringCollection)}
              />

              { !writeOffsFetching ? (
                <WriteOffReportsEditTable data={writeOffsData?.results} />
              ) : (
                <SectionTableSkeleton />
              ) }

              <PaginationComponent
                data={!writeOffsError && writeOffsData}
                currentPage={currentPage}
                totalPages={totalPages}
                setCurrentPage={setCurrentPage}
                setTotalPages={setTotalPages}
                refetchData={() => setQueryString(queryStringCollection)}
              />
            </div>
          </section>
        ) : (
          <EditSectionSkeleton/>
        )}
      </DashboardLayout>
    </>
  )
}

export default WriteOffReportsEditPage