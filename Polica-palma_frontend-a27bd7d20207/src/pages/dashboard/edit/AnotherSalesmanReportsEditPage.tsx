import DashboardLayout from "@/components/elements/DashboardLayout.tsx"
import {useNavigate, useParams} from "react-router-dom"
import useNumberFormatter from "@/hooks/useNumberFormatter.ts"
import useFilters from "@/hooks/useFilters.ts"
import usePagination from "@/hooks/usePagination.ts"
import useServerSearch from "@/hooks/useServerSearch.ts"
import useQueryString from "@/hooks/useQueryString.ts"
import {useEffect, useState} from "react"
import SectionTableSkeleton from "@/components/skeletons/SectionTableSkeleton.tsx"
import {ChevronLeft} from "lucide-react"
import {Button} from "@/components/ui/button.tsx"
import FiltersBlock from "@/components/others/FiltersBlock.tsx"
import SectionsTop from "@/components/others/SectionsTop.tsx"
import PaginationComponent from "@/components/others/PaginationComponent.tsx"
import AnotherSalesmanPaymentsTable from "@/components/tables/elements/AnotherSalesmanPaymentsTable.tsx"
import {api} from "@/services/api.ts"

const AnotherSalesmanReportsEditPage = () => {
  const anotherSalesmanReportsFilterState = JSON.parse(localStorage.getItem("anotherSalesmanReportsEdit") || JSON.stringify({
    "currentPage": "",
    "submittedSearch": "",
    "periodFromTimeFormatted": "",
    "periodToTimeFormatted": "",
    "periodFromTime": "",
    "periodToTime": "",
  }))

  const { id } = useParams()
  const navigate = useNavigate()
  const { formatter } = useNumberFormatter()
  const { fromTime, toTime, setToTime, setFromTime, periodFromTime, setPeriodFromTime, periodToTime, setPeriodToTime, periodFromTimeFormatted, periodToTimeFormatted } = useFilters(anotherSalesmanReportsFilterState)
  const { currentPage, setCurrentPage, totalPages, setTotalPages } = usePagination(anotherSalesmanReportsFilterState)
  const { searchValue, handleSearch, submitSearch, submittedSearch } = useServerSearch(setCurrentPage)

  const summaryQueryParams: any = {
    'start_date': periodFromTimeFormatted !== null ? periodFromTimeFormatted : '',
    'end_date': periodToTimeFormatted !== null ? periodToTimeFormatted : '',
  }

  const paymentsQueryParams: any = {
    'page': currentPage,
    'search': submittedSearch,
    'start_date': periodFromTimeFormatted !== null ? periodFromTimeFormatted : '',
    'end_date': periodToTimeFormatted !== null ? periodToTimeFormatted : '',
  }

  useEffect(() => {
    localStorage.setItem("anotherSalesmanReportsEdit", JSON.stringify({
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
    periodToTime,
  ])

  const { queryString: summaryQueryStringCollection } = useQueryString(summaryQueryParams)
  const { queryString: paymentsQueryStringCollection } = useQueryString(paymentsQueryParams)

  const [summaryQueryString, setSummaryQueryString] = useState('')
  const [paymentsQueryString, setPaymentsQueryString] = useState('')

  const { data, isLoading } = api.useGetAnotherWorkersReportsQuery({ id: id, queryString: summaryQueryString })
  const { data: paymentsData, isLoading: paymentsLoading, isFetching: paymentsFetching, isError: paymentsError } = api.useGetAnotherWorkersReportsQuery({ id: id, queryString: paymentsQueryString, item: 'payments' })

  useEffect(() => {
    setPaymentsQueryString(paymentsQueryStringCollection)
  }, [currentPage, submittedSearch])

  return (
    <>
      <DashboardLayout>
        { isLoading && paymentsLoading ? (
          <SectionTableSkeleton />
        ) : (
          <section className='w-full flex flex-col gap-8'>
            <Button className='w-48' variant='outline' onClick={() => navigate(-1)}>
              <ChevronLeft className='w-4 h-4 mr-2'/> Вернуться назад
            </Button>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 text-sm">
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Имя продавца: <span className="font-bold">{data.name}</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Текущий баланс: <span className="font-bold">{formatter.format(data.balance)} сум</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Сумма платежей: <span className="font-bold">{formatter.format(data.payment_sum)} сум</span></p>
            </div>

            <div className='flex flex-col gap-8'>
              <FiltersBlock
                fromTime={fromTime}
                toTime={toTime}
                periodFromTime={periodFromTime}
                periodToTime={periodToTime}
                setFromTime={setFromTime}
                setToTime={setToTime}
                setPeriodFromTime={setPeriodFromTime}
                setPeriodToTime={setPeriodToTime}
                refetchData={() => {
                  setSummaryQueryString(summaryQueryStringCollection)
                  setPaymentsQueryString(paymentsQueryStringCollection)
                }}
                pathName={'anotherSalesmanReportsEdit'}
                haventPeriods
                hasTimePeriods
              />

              <SectionsTop
                title='Платежи'
                placeholder='Поиск платежей'
                inputValue={searchValue}
                onChange={handleSearch}
                onClick={submitSearch}
              />

              <div className='w-full h-full relative flex flex-col gap-3'>
                { !paymentsFetching ? (
                  <AnotherSalesmanPaymentsTable data={paymentsData?.results} />
                ) : (
                  <SectionTableSkeleton />
                ) }

                <PaginationComponent
                  data={!paymentsError && paymentsData}
                  currentPage={currentPage}
                  totalPages={totalPages}
                  setCurrentPage={setCurrentPage}
                  setTotalPages={setTotalPages}
                  refetchData={() => setPaymentsQueryString(paymentsQueryStringCollection)}
                />
              </div>
            </div>
          </section>
        )}
      </DashboardLayout>
    </>
  )
}

export default AnotherSalesmanReportsEditPage