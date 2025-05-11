import useNumberFormatter from "@/hooks/useNumberFormatter.ts"
import useFilters from "@/hooks/useFilters.ts"
import usePagination from "@/hooks/usePagination.ts"
import useServerSearch from "@/hooks/useServerSearch.ts"
import {useEffect, useState} from "react"
import useQueryString from "@/hooks/useQueryString.ts"
import {api} from "@/services/api.ts"
import SectionTableSkeleton from "@/components/skeletons/SectionTableSkeleton.tsx"
import SectionsTop from "@/components/others/SectionsTop.tsx"
import FiltersBlock from "@/components/others/FiltersBlock.tsx"
import PaginationComponent from "@/components/others/PaginationComponent.tsx"
import AllWorkersReportsTable from "@/components/tables/elements/AllWorkersReportsTable.tsx"
import TableDownload from "@/components/others/TableDownload.tsx"
import {Skeleton} from "@/components/ui/skeleton.tsx"

const AllWorkersReportsSection = () => {
  const allWorkersReportsFilterState = JSON.parse(localStorage.getItem("allWorkersReports") || JSON.stringify({
    "currentPage": "",
    "submittedSearch": "",
    "periodFromTimeFormatted": "",
    "periodToTimeFormatted": "",
    "periodFromTime": "",
    "periodToTime": "",
    "workerType": "",
  }))

  const { formatter } = useNumberFormatter()
  const [generateReport, setGenerateReport] = useState(false)
  const { fromTime, toTime, setToTime, setFromTime, periodFromTime, setPeriodFromTime, periodToTime, setPeriodToTime, periodFromTimeFormatted, periodToTimeFormatted, workerType, setWorkerType } = useFilters(allWorkersReportsFilterState)
  const { currentPage, setCurrentPage, totalPages, setTotalPages } = usePagination(allWorkersReportsFilterState)
  const { searchValue, handleSearch, submittedSearch, submitSearch } = useServerSearch(setCurrentPage)

  const queryParams: any = {
    'page': currentPage,
    'search': submittedSearch,
    'start_date': periodFromTimeFormatted !== null ? periodFromTimeFormatted : '',
    'end_date': periodToTimeFormatted !== null ? periodToTimeFormatted : '',
    'worker_type': workerType !== null && workerType !== 'null' ? workerType : ''
  }

  useEffect(() => {
    localStorage.setItem("allWorkersReports", JSON.stringify({
      "currentPage": currentPage,
      "submittedSearch": submittedSearch,
      "periodFromTimeFormatted": periodFromTimeFormatted,
      "periodToTimeFormatted": periodToTimeFormatted,
      "periodFromTime": periodFromTime,
      "periodToTime": periodToTime,
      "workerType:": workerType,
    }))
  }, [
    currentPage,
    submittedSearch,
    periodFromTimeFormatted,
    periodToTimeFormatted,
    periodFromTime,
    periodToTime,
    workerType,
  ])

  const { queryString: queryStringCollection } = useQueryString(queryParams)
  const [queryString, setQueryString] = useState('')

  const { data: summaryData, isLoading: summaryLoading, isFetching: summaryFetching } = api.useGetAllWorkersReportSummaryQuery(
    queryString,
    { skip: !generateReport }
  )
  const { data: workersData, isLoading: workersLoading, isFetching: workersFetching, isError: workersError } = api.useGetAllWorkersReportWorkersQuery(
    queryString,
    { skip: !generateReport }
  )

  useEffect(() => {
    setQueryString(queryStringCollection)
  }, [currentPage, submittedSearch])

  return (
    <>
      <section className='w-full flex flex-col gap-8'>
        <SectionsTop
          title='Отчеты по сотрудникам'
          placeholder='Поиск сотрудников'
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
          setWorkerType={setWorkerType}
          refetchData={() => {
            setQueryString(queryStringCollection)
            setGenerateReport(true)
          }}
          workerType={workerType}
          pathName={'allWorkersReports'}
          hasWorkerType
          haventPeriods
          hasTimePeriods
        />

        {generateReport ? (
          <>
            {summaryLoading || summaryFetching ? (
              <div className='flex items-center gap-5'>
                <Skeleton className='w-full h-10'/>
                <Skeleton className='w-full h-10'/>
                <Skeleton className='w-full h-10'/>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 text-sm">
                <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общая сумма платежей: <span className="font-bold">{formatter.format(summaryData?.total_payments_sum)} сум</span></p>
                <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общая сумма начислений: <span className="font-bold">{formatter.format(summaryData?.total_income_sum)} сум</span></p>
                <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общее количество заказов: <span className="font-bold">{formatter.format(summaryData?.total_orders_count)} шт</span></p>
                <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общая сумма заказов: <span className="font-bold">{formatter.format(summaryData?.total_orders_sum)} сум</span></p>
                <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общее количество проданных букетов: <span className="font-bold">{formatter.format(summaryData?.total_sold_product_count)} шт</span></p>
                <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общее количество завершенных букетов: <span className="font-bold">{formatter.format(summaryData?.total_finished_product_count)} шт</span></p>
                <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общее количество списанных букетов: <span className="font-bold">{formatter.format(summaryData?.total_written_off_product_count)} шт</span></p>
              </div>
            )}

            {workersLoading || workersFetching ? (
              <SectionTableSkeleton/>
            ) : (
              <div className='w-full h-screen relative flex flex-col gap-3'>
                <TableDownload
                  apiUrl={`api/reports/all-workers-report/export-excel`}
                  params={queryString}
                />

                <AllWorkersReportsTable data={workersData?.results}/>

                <PaginationComponent
                  data={!workersError && workersData}
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
        )}
      </section>
    </>
  )
}

export default AllWorkersReportsSection