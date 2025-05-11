import useNumberFormatter from "@/hooks/useNumberFormatter.ts"
import useFilters from "@/hooks/useFilters.ts"
import usePagination from "@/hooks/usePagination.ts"
import useServerSearch from "@/hooks/useServerSearch.ts"
import useQueryString from "@/hooks/useQueryString.ts"
import {useEffect, useState} from "react"
import SectionTableSkeleton from "@/components/skeletons/SectionTableSkeleton.tsx"
import SectionsTop from "@/components/others/SectionsTop.tsx"
import FiltersBlock from "@/components/others/FiltersBlock.tsx"
import PaginationComponent from "@/components/others/PaginationComponent.tsx"
import AnotherSalesmanReportsTable from "@/components/tables/elements/AnotherSalesmanReportsTable.tsx"
import {api} from "@/services/api.ts"

const AnotherSalesmanReportsSection = () => {
  const anotherSalesmanReportsFilterState = JSON.parse(localStorage.getItem("anotherSalesmanReports") || JSON.stringify({
    "currentPage": "",
    "submittedSearch": "",
    "periodFromTimeFormatted": "",
    "periodToTimeFormatted": "",
    "periodFromTime": "",
    "periodToTime": "",
  }))

  const { formatter } = useNumberFormatter()
  const { fromTime, toTime, setToTime, setFromTime, periodFromTime, setPeriodFromTime, periodToTime, setPeriodToTime, periodFromTimeFormatted, periodToTimeFormatted } = useFilters(anotherSalesmanReportsFilterState)
  const { currentPage, setCurrentPage, totalPages, setTotalPages } = usePagination(anotherSalesmanReportsFilterState)
  const { searchValue, handleSearch, submitSearch, submittedSearch } = useServerSearch(setCurrentPage)

  const queryParams: any = {
    'page': currentPage,
    'search': submittedSearch,
    'start_date': periodFromTimeFormatted !== null ? periodFromTimeFormatted : '',
    'end_date': periodToTimeFormatted !== null ? periodToTimeFormatted : '',
  }

  useEffect(() => {
    localStorage.setItem("anotherSalesmanReports", JSON.stringify({
      "currentPage": currentPage,
      "submittedSearch": submittedSearch,
      "periodFromTimeFormatted": periodFromTimeFormatted,
      "periodToTimeFormatted": periodToTimeFormatted,
      "periodFromTime": periodFromTime,
      "periodToTime": periodToTime,
    }))
  }, [
    currentPage,
    submittedSearch,
    periodFromTimeFormatted,
    periodToTimeFormatted,
    periodFromTime,
    periodToTime
  ])

  const { queryString: queryStringCollection } = useQueryString(queryParams)
  const [queryString, setQueryString] = useState('')

  const { data, isLoading } = api.useGetAnotherWorkersReportsQuery({ queryString: queryString, item: 'summary' })
  const { data: anotherSalesmanData, isLoading: anotherSalesmanLoading, isFetching: anotherSalesmanFetching, isError: anotherSalesmanError } = api.useGetAnotherWorkersReportsQuery({ queryString: queryString, item: 'workers' })

  useEffect(() => {
    setQueryString(queryStringCollection)
  }, [currentPage, submittedSearch])

  return (
    <>
      { isLoading && anotherSalesmanLoading ? (
        <SectionTableSkeleton />
      ) : (
        <section className='w-full flex flex-col gap-8'>
          <SectionsTop
            title='Отчеты по прочим работникам'
            placeholder='Поиск работников'
            inputValue={searchValue}
            onChange={handleSearch}
            onClick={submitSearch}
          />

          <div className='grid grid-cols-1 gap-3'>
            <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Общая сумма платежей: <span className='font-bold'>{formatter.format(data?.total_payments_sum)} сум</span></p>
          </div>

          <div className='w-full h-full relative flex flex-col gap-3'>
            <FiltersBlock
              fromTime={fromTime}
              toTime={toTime}
              periodFromTime={periodFromTime}
              periodToTime={periodToTime}
              setFromTime={setFromTime}
              setToTime={setToTime}
              setPeriodFromTime={setPeriodFromTime}
              setPeriodToTime={setPeriodToTime}
              refetchData={() => setQueryString(queryStringCollection)}
              pathName={'anotherSalesmanReports'}
              haventPeriods
              hasTimePeriods
            />

            { !anotherSalesmanFetching ? (
              <AnotherSalesmanReportsTable data={anotherSalesmanData?.results} />
            ) : (
              <SectionTableSkeleton />
            ) }

            <PaginationComponent
              data={!anotherSalesmanError && anotherSalesmanData}
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

export default AnotherSalesmanReportsSection