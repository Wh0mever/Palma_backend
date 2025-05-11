import DashboardLayout from "@/components/elements/DashboardLayout.tsx"
import {useNavigate, useParams} from "react-router-dom"
import useNumberFormatter from "@/hooks/useNumberFormatter.ts"
import useFilters from "@/hooks/useFilters.ts"
import {useEffect, useState} from "react"
import useQueryString from "@/hooks/useQueryString.ts"
import {api} from "@/services/api.ts"
import {ChevronLeft} from "lucide-react"
import {Button} from "@/components/ui/button.tsx"
import EditSectionSkeleton from "@/components/skeletons/EditSectionSkeleton.tsx"
import SectionsTop from "@/components/others/SectionsTop.tsx"
import SalesmanReportsOrdersTable from "@/components/tables/elements/SalesmanReportsOrdersTable.tsx"
import SectionTableSkeleton from "@/components/skeletons/SectionTableSkeleton.tsx"
import PaginationComponent from "@/components/others/PaginationComponent.tsx"
import usePagination from "@/hooks/usePagination.ts"
import useServerSearch from "@/hooks/useServerSearch.ts"
import FiltersBlock from "@/components/others/FiltersBlock.tsx"
import FloristsReportsEditTable from "@/components/tables/elements/FloristsReportsEditTable.tsx"
import SalesmanReportsIncomesTable from "@/components/tables/elements/SalesmanReportsIncomesTable.tsx"
import SalesmanReportsPaymentsTable from "@/components/tables/elements/SalesmanReportsPaymentsTable.tsx"

const AllWorkersReportsEditPage = () => {
  const allWorkersReportsEditFilterState = JSON.parse(localStorage.getItem("allWorkersReportsEdit") || JSON.stringify({
    "ordersPage": "",
    "factoriesPage": "",
    "incomesPage": "",
    "paymentsPage": "",
    "ordersSubmittedSearch": "",
    "factoriesSubmittedSearch": "",
    "incomesSubmittedSearch": "",
    "paymentsSubmittedSearch": "",
    "periodFromTimeFormatted": "",
    "periodToTimeFormatted": "",
    "periodFromTime": "",
    "periodToTime": "",
    "status": "",
    "incomeType": "",
    "incomeReason": "",
  }))

  const { id } = useParams()
  const navigate = useNavigate()
  const { formatter } = useNumberFormatter()
  const { fromTime, toTime, setToTime, setFromTime, periodFromTime, setPeriodFromTime, periodToTime, setPeriodToTime, periodFromTimeFormatted, periodToTimeFormatted, status, setStatus, incomeType, setIncomeType, incomeReason, setIncomeReason } = useFilters(allWorkersReportsEditFilterState)

  const { currentPage: ordersPage, setCurrentPage: ordersSetCurrentPage, totalPages: ordersTotalPages, setTotalPages: ordersSetTotalPages } = usePagination(allWorkersReportsEditFilterState)
  const { currentPage: factoriesPage, setCurrentPage: factoriesSetCurrentPage, totalPages: factoriesTotalPages, setTotalPages: factoriesSetTotalPages } = usePagination(allWorkersReportsEditFilterState)
  const { currentPage: incomesPage, setCurrentPage: incomesSetCurrentPage, totalPages: incomesTotalPages, setTotalPages: incomesSetTotalPages } = usePagination(allWorkersReportsEditFilterState)
  const { currentPage: paymentsPage, setCurrentPage: paymentsSetCurrentPage, totalPages: paymentsTotalPages, setTotalPages: paymentsSetTotalPages } = usePagination(allWorkersReportsEditFilterState)

  const { searchValue: ordersSearchValue, handleSearch: ordersHandleSearch, submitSearch: ordersSubmitSearch, submittedSearch: ordersSubmittedSearch } = useServerSearch(ordersSetCurrentPage)
  const { searchValue: factoriesSearchValue, handleSearch: factoriesHandleSearch, submittedSearch: factoriesSubmittedSearch, submitSearch: factoriesSubmitSearch } = useServerSearch(factoriesSetCurrentPage)
  const { searchValue: incomesSearchValue, handleSearch: incomesHandleSearch, submittedSearch: incomesSubmittedSearch, submitSearch: incomesSubmitSearch } = useServerSearch(incomesSetCurrentPage)
  const { searchValue: paymentsSearchValue, handleSearch: paymentsHandleSearch, submittedSearch: paymentsSubmittedSearch, submitSearch: paymentsSubmitSearch } = useServerSearch(paymentsSetCurrentPage)

  const dataQueryParams: any = {
    'start_date': periodFromTimeFormatted !== null ? periodFromTimeFormatted : '',
    'end_date': periodToTimeFormatted !== null ? periodToTimeFormatted : '',
  }

  const ordersQueryParams: any = {
    'page': ordersPage,
    'search': ordersSubmittedSearch,
    'start_date': periodFromTimeFormatted !== null ? periodFromTimeFormatted : '',
    'end_date': periodToTimeFormatted !== null ? periodToTimeFormatted : '',
  }

  const factoriesQueryParams: any = {
    'page': factoriesPage,
    'search': factoriesSubmittedSearch,
    'status': status !== null && status !== 'null' ? status : '',
    'start_date': periodFromTimeFormatted !== null ? periodFromTimeFormatted : '',
    'end_date': periodToTimeFormatted !== null ? periodToTimeFormatted : '',
  }

  const incomesQueryParams: any = {
    'page': incomesPage,
    'search': incomesSubmittedSearch,
    'start_date': periodFromTimeFormatted !== null ? periodFromTimeFormatted : '',
    'end_date': periodToTimeFormatted !== null ? periodToTimeFormatted : '',
    'income_type': incomeType !== null ? incomeType : '',
    'income_reason': incomeReason !== null ? incomeReason : ''
  }

  const paymentsQueryParams: any = {
    'page': incomesPage,
    'search': paymentsSubmittedSearch,
    'start_date': periodFromTimeFormatted !== null ? periodFromTimeFormatted : '',
    'end_date': periodToTimeFormatted !== null ? periodToTimeFormatted : '',
  }

  useEffect(() => {
    localStorage.setItem("allWorkersReportsEdit", JSON.stringify({
      "ordersPage": ordersPage,
      "factoriesPage": factoriesPage,
      "incomesPage": incomesPage,
      "paymentsPage": paymentsPage,
      "ordersSubmittedSearch": ordersSubmittedSearch,
      "factoriesSubmittedSearch": factoriesSubmittedSearch,
      "incomesSubmittedSearch": incomesSubmittedSearch,
      "paymentsSubmittedSearch": paymentsSubmittedSearch,
      "periodFromTimeFormatted": periodFromTimeFormatted,
      "periodToTimeFormatted": periodToTimeFormatted,
      "periodFromTime": periodFromTime,
      "periodToTime": periodToTime,
      "status": status,
      "incomeType": incomeType,
      "incomeReason": incomeReason,
    }))
  }, [
    ordersPage,
    factoriesPage,
    incomesPage,
    paymentsPage,
    ordersSubmittedSearch,
    factoriesSubmittedSearch,
    incomesSubmittedSearch,
    paymentsSubmittedSearch,
    periodFromTimeFormatted,
    periodToTimeFormatted,
    periodFromTime,
    periodToTime,
    status,
    incomeType,
    incomeReason
  ])

  const { queryString: dataQueryStringCollection } = useQueryString(dataQueryParams)
  const { queryString: ordersQueryStringCollection } = useQueryString(ordersQueryParams)
  const { queryString: factoriesQueryStringCollection } = useQueryString(factoriesQueryParams)
  const { queryString: incomesQueryStringCollection } = useQueryString(incomesQueryParams)
  const { queryString: paymentsQueryStringCollection } = useQueryString(paymentsQueryParams)

  const [dataQueryString, setDataQueryString] = useState('')
  const [ordersQueryString, setOrdersQueryString] = useState('')
  const [factoriesQueryString, setFactoriesQueryString] = useState('')
  const [incomesQueryString, setIncomesQueryString] = useState('')
  const [paymentsQueryString, setPaymentsQueryString] = useState('')

  const { data, isLoading } = api.useGetAllWorkersReportIdQuery({ id: id, queryString: dataQueryString })
  const { data: ordersData, isLoading: ordersLoading, isFetching: ordersFetching, isError: ordersError } = api.useGetSalesmanReportsQuery({ id: id, queryString: ordersQueryString, item: 'orders' })
  const { data: factoriesData, isLoading: factoriesLoading, isFetching: factoriesFetching, isError: factoriesError } = api.useGetFloristsReportsQuery({ id: id, queryString: factoriesQueryString, item: 'factories' })
  const { data: incomesData, isLoading: incomesLoading, isFetching: incomesFetching, isError: incomesError } = api.useGetFloristsReportsQuery({ id: id, queryString: incomesQueryString, item: 'incomes' })
  const { data: paymentsData, isLoading: paymentsLoading, isFetching: paymentsFetching, isError: paymentsError } = api.useGetFloristsReportsQuery({ id: id, queryString: paymentsQueryString, item: 'payments' })

  useEffect(() => {
    setOrdersQueryString(ordersQueryStringCollection)
  }, [ordersPage, ordersSubmittedSearch])

  useEffect(() => {
    setFactoriesQueryString(factoriesQueryStringCollection)
  }, [factoriesPage, factoriesSubmittedSearch])

  useEffect(() => {
    setIncomesQueryString(incomesQueryStringCollection)
  }, [incomesPage, incomesSubmittedSearch])

  useEffect(() => {
    setPaymentsQueryString(paymentsQueryStringCollection)
  }, [paymentsPage, paymentsSubmittedSearch])

  return (
    <>
      <DashboardLayout>
        { !isLoading && !ordersLoading && !factoriesLoading && !incomesLoading && !paymentsLoading ? (
          <section className='w-full flex flex-col gap-8'>
            <Button className='w-48' variant='outline' onClick={() => navigate(-1)}>
              <ChevronLeft className='w-4 h-4 mr-2'/> Вернуться назад
            </Button>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3 text-sm">
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Имя сотрудника: <span
                className="font-bold">{data.name}</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Сумма платежей: <span
                className="font-bold">{formatter.format(data.payment_sum)} сум</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Сумма начислений: <span
                className="font-bold">{formatter.format(data.income_sum)} сум</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Количество заказов: <span
                className="font-bold">{formatter.format(data.orders_count)} шт</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общая сумма заказов: <span
                className="font-bold">{formatter.format(data.order_total_sum)} сум</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Количество проданных букетов: <span
                className="font-bold">{formatter.format(data.sold_product_count)} шт</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Количество завершенных букетов: <span
                className="font-bold">{formatter.format(data.finished_product_count)} шт</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Количество списанных букетов: <span
                className="font-bold">{formatter.format(data.written_off_product_count)} шт</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общее количество букетов: <span
                className="font-bold">{formatter.format(data.total_product_count)} шт</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Сумма начислений за продажи: <span className="font-bold">{formatter.format(data?.income_for_orders_sum)} сум</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Сумма начислений за букеты: <span className="font-bold">{formatter.format(data?.income_for_factories_sum)} сум</span></p>
            </div>

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
              setStatus={setStatus}
              setIncomeType={setIncomeType}
              statusApiUrl={`api/factories/product-factories/statuses/`}
              refetchData={() => {
                setDataQueryString(dataQueryStringCollection)
                setOrdersQueryString(ordersQueryStringCollection)
                setFactoriesQueryString(factoriesQueryStringCollection)
                setIncomesQueryString(incomesQueryStringCollection)
                setPaymentsQueryString(paymentsQueryStringCollection)
              }}
              status={status}
              incomeType={incomeType}
              incomeReason={incomeReason}
              pathName={'allWorkersReportsEdit'}
              haventPeriods
              hasTimePeriods
              hasIncomeReason
              hasStatus
              hasIncomeType
            />

            <div className='mt-6 flex flex-col gap-16'>
              <div className='flex flex-col gap-8'>
                <SectionsTop
                  title='Продажи'
                  placeholder='Поиск продаж'
                  inputValue={ordersSearchValue}
                  onChange={ordersHandleSearch}
                  onClick={ordersSubmitSearch}
                />

                <div className='w-full h-full relative flex flex-col gap-3'>
                  {!ordersFetching ? (
                    <SalesmanReportsOrdersTable data={ordersData?.results}/>
                  ) : (
                    <SectionTableSkeleton/>
                  )}

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

              <div className="flex flex-col gap-8">
                <SectionsTop
                  title='Букеты'
                  placeholder='Поиск букетов'
                  inputValue={factoriesSearchValue}
                  onChange={factoriesHandleSearch}
                  onClick={factoriesSubmitSearch}
                />

                <div className='w-full h-full relative flex flex-col gap-3'>
                  {!factoriesFetching ? (
                    <FloristsReportsEditTable data={factoriesData?.results}/>
                  ) : (
                    <SectionTableSkeleton/>
                  )}

                  <PaginationComponent
                    data={!factoriesError && factoriesData}
                    currentPage={factoriesPage}
                    totalPages={factoriesTotalPages}
                    setCurrentPage={factoriesSetCurrentPage}
                    setTotalPages={factoriesSetTotalPages}
                    refetchData={() => setFactoriesQueryString(factoriesQueryStringCollection)}
                  />
                </div>
              </div>

              <div className='w-full flex flex-col gap-8'>
                <SectionsTop
                  title='Начисления'
                  placeholder='Поиск начислений'
                  inputValue={incomesSearchValue}
                  onChange={incomesHandleSearch}
                  onClick={incomesSubmitSearch}
                />

                <div className='w-full h-full relative flex flex-col gap-3'>
                  {!incomesFetching ? (
                    <SalesmanReportsIncomesTable data={incomesData?.results}/>
                  ) : (
                    <SectionTableSkeleton/>
                  )}

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

              <div className='w-full flex flex-col gap-8'>
                <SectionsTop
                  title='Платежи'
                  placeholder='Поиск платежей'
                  inputValue={paymentsSearchValue}
                  onChange={paymentsHandleSearch}
                  onClick={paymentsSubmitSearch}
                />

                <div className='w-full h-full relative flex flex-col gap-3'>
                  {!paymentsFetching ? (
                    <SalesmanReportsPaymentsTable data={paymentsData?.results}/>
                  ) : (
                    <SectionTableSkeleton/>
                  )}

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

export default AllWorkersReportsEditPage