import SectionTableSkeleton from '@/components/skeletons/SectionTableSkeleton.tsx'
import SectionsTop from '@/components/others/SectionsTop.tsx'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import OrdersReportsTable from '@/components/tables/elements/OrdersReportsTable.tsx'
import usePagination from '@/hooks/usePagination.ts'
import PaginationComponent from '@/components/others/PaginationComponent.tsx'
import useFilters from '@/hooks/useFilters.ts'
import FiltersBlock from '@/components/others/FiltersBlock.tsx'
import TableDownload from '@/components/others/TableDownload.tsx'
import useServerSearch from '@/hooks/useServerSearch.ts'
import {useEffect, useState} from "react"
import useQueryString from '@/hooks/useQueryString.ts'
import {api} from "@/services/api.ts"

const OrdersReportsSection = () => {
  const ordersReportsFilterState = JSON.parse(localStorage.getItem("ordersReports") || JSON.stringify({
    "currentPage": "",
    "submittedSearch": "",
    "periodFromTimeFormatted": "",
    "periodToTimeFormatted": "",
    "periodFromTime": "",
    "periodToTime": "",
    "industry:": "",
    "status": "",
    "client": "",
    "salesman": "",
    "createdUser": "",
  }))

  const { formatter } = useNumberFormatter()
  const { fromTime, toTime, setToTime, setFromTime, periodFromTime, setPeriodFromTime, periodToTime, setPeriodToTime, periodFromTimeFormatted, periodToTimeFormatted, industry, setIndustry, status, setStatus, client, setClient, salesman, setSalesman, createdUser, setCreatedUser } = useFilters(ordersReportsFilterState)
  const { currentPage, setCurrentPage, totalPages, setTotalPages } = usePagination(ordersReportsFilterState)
  const { searchValue, handleSearch, submittedSearch, submitSearch } = useServerSearch(setCurrentPage)

  const queryParams: any = {
    'page': currentPage,
    'search': submittedSearch,
    'start_date': periodFromTimeFormatted !== null ? periodFromTimeFormatted : '',
    'end_date': periodToTimeFormatted !== null ? periodToTimeFormatted : '',
    'industry': industry !== null && industry !== 'null' ? industry : '',
    'status': status !== null && status !== 'null' ? status : '',
    'client': client !== null && client !== 'null' ? client : '',
    'salesman': salesman !== null && salesman !== 'null' ? salesman : '',
    'created_user': createdUser !== null && createdUser !== 'null' ? createdUser : '',
  }

  useEffect(() => {
    localStorage.setItem("ordersReports", JSON.stringify({
      "currentPage": currentPage,
      "submittedSearch": submittedSearch,
      "periodFromTimeFormatted": periodFromTimeFormatted,
      "periodToTimeFormatted": periodToTimeFormatted,
      "periodFromTime": periodFromTime,
      "periodToTime": periodToTime,
      "industry:": industry,
      "status": status,
      "client": client,
      "salesman": salesman,
      "createdUser": createdUser,
    }))
  }, [
    currentPage,
    submittedSearch,
    periodFromTimeFormatted,
    periodToTimeFormatted,
    periodFromTime,
    periodToTime,
    industry,
    status,
    client,
    salesman,
    createdUser
  ])

  const { queryString: queryStringCollection } = useQueryString(queryParams)
  const [queryString, setQueryString] = useState('')
  const { data, isLoading, isFetching, isError } = api.useGetOrderReportQuery(queryString)

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
            title='Отчеты по продажам'
            placeholder='Поиск продаж'
            inputValue={searchValue}
            onChange={handleSearch}
            onClick={submitSearch}
          />

          <div
            className="grid grid-cols-3 gap-3 max-[960px]:grid-cols-2 max-[960px]:gap-2 max-[690px]:grid-cols-1">
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium max-[1440px]:text-base">Общая сумма
              продаж: <span
                className="font-bold">{formatter.format(data.results?.total_sale_with_discount_amount)} сум</span></p>
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium max-[1440px]:text-base">Общая сумма
              долга: <span
                className="font-bold">{formatter.format(data.results?.total_debt_amount)} сум</span></p>
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium max-[1440px]:text-base">Общая сумма
              скидки: <span className="font-bold">{formatter.format(data.results?.total_discount_amount)} сум</span></p>
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium max-[1440px]:text-base">Общая сумма
              наценки: <span className="font-bold">{formatter.format(data.results?.total_charge_amount)} сум</span></p>
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium max-[1440px]:text-base">Общая
              себестоимость: <span
                className="font-bold">{formatter.format(data.results?.total_self_price_amount)} сум</span></p>
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium max-[1440px]:text-base">Общая
              прибыль: <span className="font-bold">{formatter.format(data.results?.total_profit_amount)} сум</span></p>
          </div>

          <TableDownload
            apiUrl={`api/reports/orders-report/excel-export`}
            params={queryString}
          />

          <div className="w-full h-full relative flex flex-col gap-3">
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
              setIndustry={setIndustry}
              setStatus={setStatus}
              setClients={setClient}
              setSalesman={setSalesman}
              setCreatedUser={setCreatedUser}
              statusApiUrl={`api/orders/statuses/`}
              industry={industry}
              status={status}
              client={client}
              salesmanValue={salesman}
              createdUserValue={createdUser}
              pathName={'ordersReports'}
              hasIndustry
              hasStatus
              hasClients
              hasSalesman
              hasCreatedUser
              haventPeriods
              hasTimePeriods
            />

            { !isFetching ? (
              <OrdersReportsTable data={data?.results?.orders} />
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

export default OrdersReportsSection