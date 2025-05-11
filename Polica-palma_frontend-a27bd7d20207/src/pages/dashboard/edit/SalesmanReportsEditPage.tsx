import DashboardLayout from '@/components/elements/DashboardLayout.tsx'
import {useNavigate, useParams} from 'react-router-dom'
import {ChevronLeft} from 'lucide-react'
import {Button} from '@/components/ui/button.tsx'
import EditSectionSkeleton from '@/components/skeletons/EditSectionSkeleton.tsx'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import SalesmanReportsIncomesTable from '@/components/tables/elements/SalesmanReportsIncomesTable.tsx'
import SalesmanReportsOrdersTable from '@/components/tables/elements/SalesmanReportsOrdersTable.tsx'
import SalesmanReportsPaymentsTable from '@/components/tables/elements/SalesmanReportsPaymentsTable.tsx'
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

const SalesmanReportsEditPage = () => {
  const salesmanReportsEditFilterState = JSON.parse(localStorage.getItem("salesmanReportsEdit") || JSON.stringify({
    "ordersPage": "",
    "incomesPage": "",
    "paymentsPage": "",
    "ordersSubmittedSearch": "",
    "incomesSubmittedSearch": "",
    "paymentsSubmittedSearch": "",
    "periodFromTimeFormatted": "",
    "periodToTimeFormatted": "",
    "periodFromTime": "",
    "periodToTime": "",
    "incomeReason": "",
  }))

  const { id } = useParams()
  const navigate = useNavigate()
  const { formatter } = useNumberFormatter()
  const { fromTime, toTime, setToTime, setFromTime, periodFromTime, setPeriodFromTime, periodToTime, setPeriodToTime, periodFromTimeFormatted, periodToTimeFormatted, incomeReason, setIncomeReason } = useFilters(salesmanReportsEditFilterState)
  const { currentPage: ordersPage, setCurrentPage: ordersSetCurrentPage, totalPages: ordersTotalPages, setTotalPages: ordersSetTotalPages } = usePagination(salesmanReportsEditFilterState)
  const { currentPage: incomesPage, setCurrentPage: incomesSetCurrentPage, totalPages: incomesTotalPages, setTotalPages: incomesSetTotalPages } = usePagination(salesmanReportsEditFilterState)
  const { currentPage: paymentsPage, setCurrentPage: paymentsSetCurrentPage, totalPages: paymentsTotalPages, setTotalPages: paymentsSetTotalPages } = usePagination(salesmanReportsEditFilterState)
  const { searchValue: ordersSearchValue, handleSearch: ordersHandleSearch, submitSearch: ordersSubmitSearch, submittedSearch: ordersSubmittedSearch } = useServerSearch(ordersSetCurrentPage)
  const { searchValue: incomesSearchValue, handleSearch: incomesHandleSearch, submitSearch: incomesSubmitSearch, submittedSearch: incomesSubmittedSearch } = useServerSearch(ordersSetCurrentPage)
  const { searchValue: paymentsSearchValue, handleSearch: paymentsHandleSearch, submitSearch: paymentsSubmitSearch, submittedSearch: paymentsSubmittedSearch } = useServerSearch(ordersSetCurrentPage)

  const summaryQueryParams: any = {
    'start_date': periodFromTimeFormatted !== null ? periodFromTimeFormatted : '',
    'end_date': periodToTimeFormatted !== null ? periodToTimeFormatted : '',
  }

  const incomesQueryParams: any = {
    'page': incomesPage,
    'search': incomesSubmittedSearch,
    'start_date': periodFromTimeFormatted !== null ? periodFromTimeFormatted : '',
    'end_date': periodToTimeFormatted !== null ? periodToTimeFormatted : '',
    'income_reason': incomeReason !== null ? incomeReason : ''
  }

  const ordersQueryParams: any = {
    'page': ordersPage,
    'search': ordersSubmittedSearch,
    'start_date': periodFromTimeFormatted !== null ? periodFromTimeFormatted : '',
    'end_date': periodToTimeFormatted !== null ? periodToTimeFormatted : '',
  }

  const paymentsQueryParams: any = {
    'page': paymentsPage,
    'search': paymentsSubmittedSearch,
    'start_date': periodFromTimeFormatted !== null ? periodFromTimeFormatted : '',
    'end_date': periodToTimeFormatted !== null ? periodToTimeFormatted : '',
  }

  useEffect(() => {
    localStorage.setItem("salesmanReportsEdit", JSON.stringify({
      "ordersPage": ordersPage,
      "incomesPage": incomesPage,
      "paymentsPage": paymentsPage,
      "ordersSubmittedSearch": ordersSubmittedSearch,
      "incomesSubmittedSearch": incomesSubmittedSearch,
      "paymentsSubmittedSearch": paymentsSubmittedSearch,
      "periodFromTimeFormatted": periodFromTimeFormatted,
      "periodToTimeFormatted": periodToTimeFormatted,
      "periodFromTime": periodFromTime,
      "periodToTime": periodToTime,
      "incomeReason": incomeReason,
    }))
  }, [
    ordersPage,
    incomesPage,
    paymentsPage,
    ordersSubmittedSearch,
    incomesSubmittedSearch,
    paymentsSubmittedSearch,
    periodFromTimeFormatted,
    periodToTimeFormatted,
    periodFromTime,
    periodToTime,
    incomeReason
  ])

  const { queryString: summaryQueryStringCollection } = useQueryString(summaryQueryParams)
  const { queryString: incomesQueryStringCollection } = useQueryString(incomesQueryParams)
  const { queryString: ordersQueryStringCollection } = useQueryString(ordersQueryParams)
  const { queryString: paymentsQueryStringCollection } = useQueryString(paymentsQueryParams)

  const [summaryQueryString, setSummaryQueryString] = useState('')
  const [incomesQueryString, setIncomesQueryString] = useState('')
  const [ordersQueryString, setOrdersQueryString] = useState('')
  const [paymentsQueryString, setPaymentsQueryString] = useState('')

  const { data, isLoading } = api.useGetSalesmanReportsQuery({ id: id, queryString: summaryQueryString })
  const { data: incomesData, isLoading: incomesLoading, isFetching: incomesFetching, isError: incomesError } = api.useGetSalesmanReportsQuery({ id: id, queryString: incomesQueryString, item: 'incomes' })
  const { data: ordersData, isLoading: ordersLoading, isFetching: ordersFetching, isError: ordersError } = api.useGetSalesmanReportsQuery({ id: id, queryString: ordersQueryString, item: 'orders' })
  const { data: paymentsData, isLoading: paymentsLoading, isFetching: paymentsFetching, isError: paymentsError } = api.useGetSalesmanReportsQuery({ id: id, queryString: paymentsQueryString, item: 'payments' })

  useEffect(() => {
    setIncomesQueryString(incomesQueryStringCollection)
  }, [incomesPage, incomesSubmittedSearch])

  useEffect(() => {
    setOrdersQueryString(ordersQueryStringCollection)
  }, [ordersPage, ordersSubmittedSearch])

  useEffect(() => {
    setPaymentsQueryString(paymentsQueryStringCollection)
  }, [paymentsPage, paymentsSubmittedSearch])

  return (
    <>
      <DashboardLayout>
        { !isLoading && !incomesLoading && !ordersLoading && !paymentsLoading ? (
          <section className='w-full flex flex-col gap-8'>
            <Button className='w-48' variant='outline' onClick={() => navigate(-1)}>
              <ChevronLeft className='w-4 h-4 mr-2'/> Вернуться назад
            </Button>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 text-sm">
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Имя продавца: <span className="font-bold">{data?.name}</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Магазин: <span className="font-bold">{data?.industry?.name || "-"}</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Текущий баланс: <span className="font-bold">{formatter.format(data?.balance)} сум</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Количество продаж: <span className="font-bold">{formatter.format(data?.orders_count)} шт</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Сумма продаж: <span className="font-bold">{formatter.format(data?.order_total_sum)} сум</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Сумма начислений на период: <span className="font-bold">{formatter.format(data?.income_sum)} сум</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Сумма платежей: <span className="font-bold">{formatter.format(data?.payment_sum)} сум</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Сумма начислений за продажи: <span className="font-bold">{formatter.format(data?.income_for_orders_sum)} сум</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Сумма начислений за букеты: <span className="font-bold">{formatter.format(data?.income_for_factories_sum)} сум</span></p>
            </div>

            <div className="mt-12 flex flex-col gap-16">
              <div className="flex flex-col gap-8">
                <FiltersBlock
                  fromTime={fromTime}
                  toTime={toTime}
                  periodFromTime={periodFromTime}
                  periodToTime={periodToTime}
                  setFromTime={setFromTime}
                  setToTime={setToTime}
                  setPeriodFromTime={setPeriodFromTime}
                  setPeriodToTime={setPeriodToTime}
                  setIncomeReason={setIncomeReason}
                  refetchData={() => {
                    setSummaryQueryString(summaryQueryStringCollection)
                    setIncomesQueryString(incomesQueryStringCollection)
                    setOrdersQueryString(ordersQueryStringCollection)
                    setPaymentsQueryString(paymentsQueryStringCollection)
                  }}
                  incomeReason={incomeReason}
                  pathName={'salesmanReportsEdit'}
                  haventPeriods
                  hasTimePeriods
                  hasIncomeReason
                />

                <SectionsTop
                  title='Начисления'
                  placeholder='Поиск начислений'
                  inputValue={incomesSearchValue}
                  onChange={incomesHandleSearch}
                  onClick={incomesSubmitSearch}
                />

                <div className='w-full h-full relative flex flex-col gap-3'>
                  { !incomesFetching ? (
                    <SalesmanReportsIncomesTable data={incomesData?.results} />
                  ) : (
                    <SectionTableSkeleton />
                  ) }

                  <PaginationComponent
                    data={!incomesError && incomesData}
                    currentPage={incomesPage}
                    totalPages={incomesTotalPages}
                    setCurrentPage={incomesSetCurrentPage}
                    setTotalPages={incomesSetTotalPages}
                    refetchData={() => setIncomesQueryString(incomesQueryStringCollection)}
                  />
                </div>
              </div>

              <div className='flex flex-col gap-8'>
                <SectionsTop
                  title='Продажи'
                  placeholder='Поиск продаж'
                  inputValue={ordersSearchValue}
                  onChange={ordersHandleSearch}
                  onClick={ordersSubmitSearch}
                />

                <div className='w-full h-full relative flex flex-col gap-3'>
                  { !ordersFetching ? (
                    <SalesmanReportsOrdersTable data={ordersData?.results} />
                  ) : (
                    <SectionTableSkeleton />
                  ) }

                  <PaginationComponent
                    data={!ordersError && ordersData}
                    currentPage={ordersPage}
                    totalPages={ordersTotalPages}
                    setCurrentPage={ordersSetCurrentPage}
                    setTotalPages={ordersSetTotalPages}
                    refetchData={() => setOrdersQueryString(ordersQueryStringCollection)}
                  />
                </div>
              </div>

              <div className='flex flex-col gap-8'>
                <SectionsTop
                  title='Платежи'
                  placeholder='Поиск платежей'
                  inputValue={paymentsSearchValue}
                  onChange={paymentsHandleSearch}
                  onClick={paymentsSubmitSearch}
                />

                <div className='w-full h-full relative flex flex-col gap-3'>
                  { !paymentsFetching ? (
                    <SalesmanReportsPaymentsTable data={paymentsData?.results} />
                  ) : (
                    <SectionTableSkeleton />
                  ) }

                  <PaginationComponent
                    data={!paymentsError && paymentsData}
                    currentPage={paymentsPage}
                    totalPages={paymentsTotalPages}
                    setCurrentPage={paymentsSetCurrentPage}
                    setTotalPages={paymentsSetTotalPages}
                    refetchData={() => setPaymentsQueryString(paymentsQueryStringCollection)}
                  />
                </div>
              </div>
            </div>
          </section>
        ) : (
          <EditSectionSkeleton/>
        )}
      </DashboardLayout>
    </>
  )
}

export default SalesmanReportsEditPage