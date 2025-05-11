import SectionsTop from '@/components/others/SectionsTop.tsx'
import SectionTableSkeleton from '@/components/skeletons/SectionTableSkeleton.tsx'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import FloristReportsTable from '@/components/tables/elements/FloristReportsTable.tsx'
import usePagination from '@/hooks/usePagination.ts'
import PaginationComponent from '@/components/others/PaginationComponent.tsx'
import useFilters from '@/hooks/useFilters.ts'
import FiltersBlock from '@/components/others/FiltersBlock.tsx'
import TableDownload from '@/components/others/TableDownload.tsx'
import useServerSearch from '@/hooks/useServerSearch.ts'
import {useEffect, useState} from "react"
import useQueryString from '@/hooks/useQueryString.ts'
import {api} from "@/services/api.ts"

const FloristsReportsSection = () => {
  const floristsReportsFilterState = JSON.parse(localStorage.getItem("floristsReports") || JSON.stringify({
    "currentPage": "",
    "submittedSearch": "",
    "periodFromTimeFormatted": "",
    "periodToTimeFormatted": "",
    "periodFromTime": "",
    "periodToTime": "",
    "industry": "",
  }))

  const { formatter } = useNumberFormatter()
  const { fromTime, toTime, setToTime, setFromTime, periodFromTime, setPeriodFromTime, periodToTime, setPeriodToTime, periodFromTimeFormatted, periodToTimeFormatted, industry, setIndustry } = useFilters(floristsReportsFilterState)
  const { currentPage, setCurrentPage, totalPages, setTotalPages } = usePagination(floristsReportsFilterState)
  const { searchValue, handleSearch, submittedSearch, submitSearch } = useServerSearch(setCurrentPage)

  const queryParams: any = {
    'page': currentPage,
    'search': submittedSearch,
    'start_date': periodFromTimeFormatted !== null ? periodFromTimeFormatted : '',
    'end_date': periodToTimeFormatted !== null ? periodToTimeFormatted : '',
    'industry': industry !== null && industry !== 'null' ? industry : ''
  }

  useEffect(() => {
    localStorage.setItem("floristsReports", JSON.stringify({
      "currentPage": currentPage,
      "submittedSearch": submittedSearch,
      "periodFromTimeFormatted": periodFromTimeFormatted,
      "periodToTimeFormatted": periodToTimeFormatted,
      "periodFromTime": periodFromTime,
      "periodToTime": periodToTime,
      "industry:": industry,
    }))
  }, [
    currentPage,
    submittedSearch,
    periodFromTimeFormatted,
    periodToTimeFormatted,
    periodFromTime,
    periodToTime,
    industry,
  ])

  const { queryString: queryStringCollection } = useQueryString(queryParams)
  const [queryString, setQueryString] = useState('')

  const { data, isLoading } = api.useGetFloristsReportsQuery({ item: 'summary', queryString: queryString })
  const { data: floristsData, isLoading: floristsLoading, isFetching: floristsFetching, isError: floristsError } = api.useGetFloristsReportsQuery({ item: 'forists', queryString: queryString })

  useEffect(() => {
    setQueryString(queryStringCollection)
  }, [currentPage, submittedSearch])

  return (
    <>
      { isLoading && floristsLoading ? (
        <SectionTableSkeleton />
      ) : (
        <section className='w-full flex flex-col gap-8'>
          <SectionsTop
            title='Отчеты по флористам'
            placeholder='Поиск флористов'
            inputValue={searchValue}
            onChange={handleSearch}
            onClick={submitSearch}
          />

          <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-3 text-sm'>
            <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Общее количество проданных букетов: <span className='font-bold'>{formatter.format(data?.total_sold_product_count)} шт</span></p>
            <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Общее количество собранных букетов: <span className='font-bold'>{formatter.format(data?.total_finished_product_count)} шт</span></p>
            <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Общее количество списанных букетов: <span className='font-bold'>{formatter.format(data?.total_written_off_product_count)} шт</span></p>
            <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Общая сумма начислений: <span className='font-bold'>{formatter.format(data?.total_income_sum)} сум</span></p>
            <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Общая сумма платежей: <span className='font-bold'>{formatter.format(data?.total_payment_sum)} сум</span></p>
          </div>

          <TableDownload
            apiUrl={`api/reports/florists-report/export-excel`}
            params={queryString}
          />

          <div className='w-full h-screen relative flex flex-col gap-3'>
            <FiltersBlock
              fromTime={fromTime}
              toTime={toTime}
              periodFromTime={periodFromTime}
              periodToTime={periodToTime}
              setFromTime={setFromTime}
              setToTime={setToTime}
              setPeriodFromTime={setPeriodFromTime}
              setPeriodToTime={setPeriodToTime}
              setIndustry={setIndustry}
              refetchData={() => setQueryString(queryStringCollection)}
              industry={industry}
              pathName={'floristsReports'}
              hasIndustry
              haventPeriods
              hasTimePeriods
            />

            { !floristsFetching ? (
              <FloristReportsTable data={floristsData?.results} />
            ) : (
              <SectionTableSkeleton />
            ) }

            <PaginationComponent
              data={!floristsError && floristsData}
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

export default FloristsReportsSection