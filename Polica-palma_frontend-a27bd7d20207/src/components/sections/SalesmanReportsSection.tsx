import SectionsTop from '@/components/others/SectionsTop.tsx'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import SectionTableSkeleton from '@/components/skeletons/SectionTableSkeleton.tsx'
import SalesmanReportsTable from '@/components/tables/elements/SalesmanReportsTable.tsx'
import usePagination from '@/hooks/usePagination.ts'
import PaginationComponent from '@/components/others/PaginationComponent.tsx'
import useFilters from '@/hooks/useFilters.ts'
import FiltersBlock from '@/components/others/FiltersBlock.tsx'
import TableDownload from '@/components/others/TableDownload.tsx'
import useServerSearch from '@/hooks/useServerSearch.ts'
import {useEffect, useState} from "react"
import useQueryString from '@/hooks/useQueryString.ts'
import {api} from "@/services/api.ts"
import {Skeleton} from "@/components/ui/skeleton.tsx"

const SalesmanReportsSection = () => {
  const salesmanReportsFilterState = JSON.parse(localStorage.getItem("salesmanReportsEdit") || JSON.stringify({
    "currentPage": "",
    "submittedSearch": "",
    "periodFromTimeFormatted": "",
    "periodToTimeFormatted": "",
    "periodFromTime": "",
    "periodToTime": "",
    "industry": "",
  }))

  const { formatter } = useNumberFormatter()
  const [generateReport, setGenerateReport] = useState(false)
  const { fromTime, toTime, setToTime, setFromTime, periodFromTime, setPeriodFromTime, periodToTime, setPeriodToTime, periodFromTimeFormatted, periodToTimeFormatted, industry, setIndustry } = useFilters(salesmanReportsFilterState)
  const { currentPage, setCurrentPage, totalPages, setTotalPages } = usePagination(salesmanReportsFilterState)
  const { searchValue, handleSearch, submitSearch, submittedSearch } = useServerSearch(setCurrentPage)

  const queryParams: any = {
    'page': currentPage,
    'search': searchValue,
    'start_date': periodFromTimeFormatted !== null ? periodFromTimeFormatted : '',
    'end_date': periodToTimeFormatted !== null ? periodToTimeFormatted : '',
    'industry': industry !== null && industry !== 'null' ? industry : ''
  }

  useEffect(() => {
    localStorage.setItem("salesmanReportsEdit", JSON.stringify({
      "currentPage": currentPage,
      "submittedSearch": submittedSearch,
      "periodFromTimeFormatted": periodFromTimeFormatted,
      "periodToTimeFormatted": periodToTimeFormatted,
      "periodFromTime": periodFromTime,
      "periodToTime": periodToTime,
      "industry": industry,
    }))
  }, [
    currentPage,
    submittedSearch,
    periodFromTimeFormatted,
    periodToTimeFormatted,
    periodFromTime,
    periodToTime,
    industry
  ])

  const { queryString: queryStringCollection } = useQueryString(queryParams)
  const [queryString, setQueryString] = useState('')

  const { data, isLoading, isFetching } = api.useGetSalesmanReportsQuery(
    { queryString: queryString, item: 'summary' },
    { skip: !generateReport }
  )
  const { data: salesmanData, isLoading: salesmanLoading, isFetching: salesmanFetching, isError: salesmanError } = api.useGetSalesmanReportsQuery(
    { queryString: queryString, item: 'salesmen' },
    { skip: !generateReport }
  )

  useEffect(() => {
    setQueryString(queryStringCollection)
  }, [currentPage, submittedSearch])

  return (
    <>
      <section className='w-full flex flex-col gap-8'>
        <SectionsTop
          title='Отчеты по продавцам'
          placeholder='Поиск продавцов'
          inputValue={searchValue}
          onChange={handleSearch}
          onClick={submitSearch}
        />

        <FiltersBlock
          generateText='Сформировать отчет'
          fromTime={fromTime}
          toTime={toTime}
          periodFromTime={periodFromTime}
          periodToTime={periodToTime}
          setFromTime={setFromTime}
          setToTime={setToTime}
          setPeriodFromTime={setPeriodFromTime}
          setPeriodToTime={setPeriodToTime}
          setIndustry={setIndustry}
          refetchData={() => {
            setQueryString(queryStringCollection)
            setGenerateReport(true)
          }}
          industry={industry}
          pathName={'salesmanReportsEdit'}
          hasIndustry
          haventPeriods
          hasTimePeriods
        />

        { generateReport ? (
          <>
            {isLoading || isFetching ? (
              <div className='flex items-center gap-5'>
                <Skeleton className='w-full h-10' />
                <Skeleton className='w-full h-10' />
                <Skeleton className='w-full h-10' />
              </div>
            ) : (
              <div className='grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3 text-sm'>
                <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Общее количество продаж: <span className='font-bold'>{formatter.format(data?.total_orders_count)} шт</span></p>
                <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Общая сумма продаж: <span className='font-bold'>{formatter.format(data?.total_orders_sum)} сум</span></p>
                <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Общая сумма начислений: <span className='font-bold'>{formatter.format(data?.total_income_sum)} сум</span></p>
                <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Общая сумма платежей: <span className='font-bold'>{formatter.format(data?.total_payments_sum)} сум</span></p>
              </div>
            )}

            {salesmanLoading || salesmanFetching ? (
              <SectionTableSkeleton />
            ) : (
              <div className='w-full h-full relative flex flex-col gap-4'>
                <TableDownload
                  apiUrl={`api/reports/salesmen-report/export-excel`}
                  params={queryString}
                />

                <SalesmanReportsTable data={salesmanData?.results}/>

                <PaginationComponent
                  data={!salesmanError && salesmanData}
                  currentPage={currentPage}
                  totalPages={totalPages}
                  setCurrentPage={setCurrentPage}
                  setTotalPages={setTotalPages}
                  refetchData={() => setQueryString(queryStringCollection)}
                />
              </div>
            )}
          </>
        ) : (
          <h3>Сформируйте отчет, чтобы отобразить таблицу</h3>
        ) }
      </section>
    </>
  )
}

export default SalesmanReportsSection