import {useNavigate, useParams} from 'react-router-dom'
import DashboardLayout from '@/components/elements/DashboardLayout.tsx'
import EditSectionSkeleton from '@/components/skeletons/EditSectionSkeleton.tsx'
import {ChevronLeft} from 'lucide-react'
import {Button} from '@/components/ui/button.tsx'
import translatedData from '@/data/translatedData.ts'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import FloristsReportsEditTable from '@/components/tables/elements/FloristsReportsEditTable.tsx'
import usePagination from '@/hooks/usePagination.ts'
import PaginationComponent from '@/components/others/PaginationComponent.tsx'
import SectionsTop from '@/components/others/SectionsTop.tsx'
import SalesmanReportsIncomesTable from '@/components/tables/elements/SalesmanReportsIncomesTable.tsx'
import SalesmanReportsPaymentsTable from '@/components/tables/elements/SalesmanReportsPaymentsTable.tsx'
import useFilters from '@/hooks/useFilters.ts'
import FiltersBlock from '@/components/others/FiltersBlock.tsx'
import useServerSearch from '@/hooks/useServerSearch.ts'
import {useEffect, useState} from "react"
import useQueryString from '@/hooks/useQueryString.ts'
import {api} from "@/services/api.ts"
import SectionTableSkeleton from "@/components/skeletons/SectionTableSkeleton.tsx"

const FloristsReportsEditPage = () => {
  const floristsReportsEditFilterState = JSON.parse(localStorage.getItem("floristsReportsEdit") || JSON.stringify({
    "factoriesPage": "",
    "incomesPage": "",
    "paymentsPage": "",
    "paymentsSubmittedSearch": "",
    "factoriesSubmittedSearch": "",
    "incomesSubmittedSearch": "",
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
  const { fromTime, toTime, setToTime, setFromTime, periodFromTime, setPeriodFromTime, periodToTime, setPeriodToTime, periodFromTimeFormatted, periodToTimeFormatted, status, setStatus, incomeType, setIncomeType, incomeReason, setIncomeReason } = useFilters(floristsReportsEditFilterState)
  const { currentPage: factoriesPage, setCurrentPage: factoriesSetCurrentPage, totalPages: factoriesTotalPages, setTotalPages: factoriesSetTotalPages } = usePagination(floristsReportsEditFilterState)
  const { currentPage: incomesPage, setCurrentPage: incomesSetCurrentPage, totalPages: incomesTotalPages, setTotalPages: incomesSetTotalPages } = usePagination(floristsReportsEditFilterState)
  const { currentPage: paymentsPage, setCurrentPage: paymentsSetCurrentPage, totalPages: paymentsTotalPages, setTotalPages: paymentsSetTotalPages } = usePagination(floristsReportsEditFilterState)
  const { searchValue: factoriesSearchValue, handleSearch: factoriesHandleSearch, submittedSearch: factoriesSubmittedSearch, submitSearch: factoriesSubmitSearch } = useServerSearch(factoriesSetCurrentPage)
  const { searchValue: incomesSearchValue, handleSearch: incomesHandleSearch, submittedSearch: incomesSubmittedSearch, submitSearch: incomesSubmitSearch } = useServerSearch(incomesSetCurrentPage)
  const { searchValue: paymentsSearchValue, handleSearch: paymentsHandleSearch, submittedSearch: paymentsSubmittedSearch, submitSearch: paymentsSubmitSearch } = useServerSearch(paymentsSetCurrentPage)

  const summaryQueryParams: any = {
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

  const factoriesQueryParams: any = {
    'page': factoriesPage,
    'search': factoriesSubmittedSearch,
    'status': status !== null && status !== 'null' ? status : '',
    'start_date': periodFromTimeFormatted !== null ? periodFromTimeFormatted : '',
    'end_date': periodToTimeFormatted !== null ? periodToTimeFormatted : '',
  }

  useEffect(() => {
    localStorage.setItem("floristsReportsEdit", JSON.stringify({
      "factoriesPage": factoriesPage,
      "incomesPage": incomesPage,
      "paymentsPage": paymentsPage,
      "paymentsSubmittedSearch": paymentsSubmittedSearch,
      "factoriesSubmittedSearch": factoriesSubmittedSearch,
      "incomesSubmittedSearch": incomesSubmittedSearch,
      "periodFromTimeFormatted": periodFromTimeFormatted,
      "periodToTimeFormatted": periodToTimeFormatted,
      "periodFromTime": periodFromTime,
      "periodToTime": periodToTime,
      "status": status,
      "incomeType": incomeType,
      "incomeReason": incomeReason,
    }))
  }, [
    factoriesPage,
    incomesPage,
    paymentsPage,
    paymentsSubmittedSearch,
    factoriesSubmittedSearch,
    incomesSubmittedSearch,
    periodFromTimeFormatted,
    periodToTimeFormatted,
    periodFromTime,
    periodToTime,
    status,
    incomeType,
    incomeReason
  ])

  const { queryString: summaryQueryStringCollection } = useQueryString(summaryQueryParams)
  const { queryString: incomesQueryStringCollection } = useQueryString(incomesQueryParams)
  const { queryString: paymentsQueryStringCollection } = useQueryString(paymentsQueryParams)
  const { queryString: factoriesQueryStringCollection } = useQueryString(factoriesQueryParams)

  const [summaryQueryString, setSummaryQueryString] = useState('')
  const [incomesQueryString, setIncomesQueryString] = useState('')
  const [paymentsQueryString, setPaymentsQueryString] = useState('')
  const [factoriesQueryString, setFactoriesQueryString] = useState('')

  const { data, isLoading } = api.useGetFloristsReportsQuery({ id: id, queryString: summaryQueryString })
  const { data: incomesData, isLoading: incomesLoading, isFetching: incomesFetching, isError: incomesError } = api.useGetFloristsReportsQuery({ id: id, queryString: incomesQueryString, item: 'incomes' })
  const { data: paymentsData, isLoading: paymentsLoading, isFetching: paymentsFetching, isError: paymentsError } = api.useGetFloristsReportsQuery({ id: id, queryString: paymentsQueryString, item: 'payments' })
  const { data: factoriesData, isLoading: factoriesLoading, isFetching: factoriesFetching, isError: factoriesError } = api.useGetFloristsReportsQuery({ id: id, queryString: factoriesQueryString, item: 'factories' })

  useEffect(() => {
    setIncomesQueryString(incomesQueryStringCollection)
  }, [incomesPage, incomesSubmittedSearch])

  useEffect(() => {
    setPaymentsQueryString(paymentsQueryStringCollection)
  }, [paymentsPage, paymentsSubmittedSearch])

  useEffect(() => {
    setFactoriesQueryString(factoriesQueryStringCollection)
  }, [factoriesPage, factoriesSubmittedSearch])

  return (
    <>
      <DashboardLayout>
        { !isLoading && !factoriesLoading && !incomesLoading && !paymentsLoading ? (
          <section className='w-full flex flex-col gap-8'>
            <Button className='w-48' variant='outline' onClick={() => navigate(-1)}>
              <ChevronLeft className='w-4 h-4 mr-2'/> Вернуться назад
            </Button>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3 text-sm">
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Имя флориста: <span
                className="font-bold">{data.name}</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Тип флориста: <span
                className="font-bold">{translatedData(data.type)}</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общее количество букетов: <span
                className="font-bold">{formatter.format(data.total_product_count)} шт</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Количество собранных букетов: <span
                className="font-bold">{formatter.format(data.finished_product_count)} шт</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Количество проданных букетов: <span
                className="font-bold">{formatter.format(data.sold_product_count)} шт</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Количество списанных букетов: <span
                className="font-bold">{formatter.format(data.written_off_product_count)} шт</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Сумма начислений: <span
                className="font-bold">{formatter.format(data.income_sum)} сум</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Сумма платежей: <span
                className="font-bold">{formatter.format(data.payment_sum)} сум</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Баланс: <span
                className="font-bold">{formatter.format(data.balance)} сум</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Сумма начислений за продажи: <span className="font-bold">{formatter.format(data?.income_for_orders_sum)} сум</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Сумма начислений за букеты: <span className="font-bold">{formatter.format(data?.income_for_factories_sum)} сум</span></p>
            </div>

            <div className="w-full mt-12 flex flex-col gap-20">
              <div className="w-full flex flex-col gap-8">
                <FiltersBlock
                  fromTime={fromTime}
                  toTime={toTime}
                  periodFromTime={periodFromTime}
                  periodToTime={periodToTime}
                  setFromTime={setFromTime}
                  setToTime={setToTime}
                  setPeriodFromTime={setPeriodFromTime}
                  setPeriodToTime={setPeriodToTime}
                  setStatus={setStatus}
                  setIncomeType={setIncomeType}
                  setIncomeReason={setIncomeReason}
                  statusApiUrl={`api/factories/product-factories/statuses/`}
                  refetchData={() => {
                    setSummaryQueryString(summaryQueryStringCollection)
                    setIncomesQueryString(incomesQueryStringCollection)
                    setPaymentsQueryString(paymentsQueryStringCollection)
                    setFactoriesQueryString(factoriesQueryStringCollection)
                  }}
                  status={status}
                  incomeType={incomeType}
                  incomeReason={incomeReason}
                  pathName={'floristsReportsEdit'}
                  hasStatus
                  haventPeriods
                  hasTimePeriods
                  hasIncomeType
                  hasIncomeReason
                />

                <SectionsTop
                  title='Букеты'
                  placeholder='Поиск букетов'
                  inputValue={factoriesSearchValue}
                  onChange={factoriesHandleSearch}
                  onClick={factoriesSubmitSearch}
                />

                <div className='w-full h-full relative flex flex-col gap-3'>
                  { !factoriesFetching ? (
                    <FloristsReportsEditTable data={factoriesData?.results} />
                  ) : (
                    <SectionTableSkeleton />
                  ) }

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

              <div className='w-full flex flex-col gap-8'>
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

export default FloristsReportsEditPage