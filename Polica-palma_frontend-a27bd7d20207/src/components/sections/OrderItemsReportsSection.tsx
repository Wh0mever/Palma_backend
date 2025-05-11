import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import useFilters from '@/hooks/useFilters.ts'
import usePagination from '@/hooks/usePagination.ts'
import SectionTableSkeleton from '@/components/skeletons/SectionTableSkeleton.tsx'
import SectionsTop from '@/components/others/SectionsTop.tsx'
import FiltersBlock from '@/components/others/FiltersBlock.tsx'
import PaginationComponent from '@/components/others/PaginationComponent.tsx'
import OrderItemsReportsTable from '@/components/tables/elements/OrderItemsReportsTable.tsx'
import useServerSearch from '@/hooks/useServerSearch.ts'
import {useEffect, useState} from "react"
import TableDownload from '@/components/others/TableDownload.tsx'
import useQueryString from '@/hooks/useQueryString.ts'
import {Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger} from "@/components/ui/dialog.tsx"
import {Button} from "@/components/ui/button.tsx"
import {Eye} from "lucide-react"
import {api} from "@/services/api.ts"

const OrderItemsReportsSection = () => {
  const orderItemsReportsFilterState = JSON.parse(localStorage.getItem("orderItemsReports") || JSON.stringify({
    "productsCurrentPage": "",
    "bouquetsCurrentPage": "",
    "productsSubmittedSearch": "",
    "bouquetsSubmittedSearch": "",
    "periodFromTimeFormatted": "",
    "periodToTimeFormatted": "",
    "periodFromTime": "",
    "periodToTime": "",
    "industry": "",
    "client": "",
    "salesman": "",
    "createdUser": ""
  }))

  const { formatter } = useNumberFormatter()
  const { fromTime, toTime, setToTime, setFromTime, periodFromTime, setPeriodFromTime, periodToTime, setPeriodToTime, periodFromTimeFormatted, periodToTimeFormatted, industry, setIndustry, client, setClient, salesman, setSalesman, createdUser, setCreatedUser } = useFilters(orderItemsReportsFilterState)
  const { currentPage: productsCurrentPage, setCurrentPage: productsSetCurrentPage, totalPages: productsTotalPages, setTotalPages: productsSetTotalPages } = usePagination(orderItemsReportsFilterState)
  const { currentPage: bouquetsCurrentPage, setCurrentPage: bouquetsSetCurrentPage, totalPages: bouquetsTotalPages, setTotalPages: bouquetsSetTotalPages } = usePagination(orderItemsReportsFilterState)
  const { searchValue: productsSearchValue, handleSearch: productsHandleSearch, submittedSearch: productsSubmittedSearch, submitSearch: productsSubmitSearch } = useServerSearch(productsSetCurrentPage)
  const { searchValue: bouquetsSearchValue, handleSearch: bouquetsHandleSearch, submittedSearch: bouquetsSubmittedSearch, submitSearch: bouquetsSubmitSearch } = useServerSearch(bouquetsSetCurrentPage)

  const summaryQueryParams: any = {
    'start_date': periodFromTimeFormatted !== null ? periodFromTimeFormatted : '',
    'end_date': periodToTimeFormatted !== null ? periodToTimeFormatted : '',
    'industry': industry !== null && industry !== 'null' ? industry : '',
    'client': client !== null && client !== 'null' ? client : '',
    'salesman': salesman !== null && salesman !== 'null' ? salesman : '',
    'created_user': createdUser !== null && createdUser !== 'null' ? createdUser : '',
  }

  const productsQueryParams: any = {
    'page': productsCurrentPage,
    'search': productsSubmittedSearch,
    'start_date': periodFromTimeFormatted !== null ? periodFromTimeFormatted : '',
    'end_date': periodToTimeFormatted !== null ? periodToTimeFormatted : '',
    'industry': industry !== null && industry !== 'null' ? industry : '',
    'client': client !== null && client !== 'null' ? client : '',
    'salesman': salesman !== null && salesman !== 'null' ? salesman : '',
    'created_user': createdUser !== null && createdUser !== 'null' ? createdUser : '',
  }

  const bouquetsQueryParams: any = {
    'page': bouquetsCurrentPage,
    'search': bouquetsSubmittedSearch,
    'start_date': periodFromTimeFormatted !== null ? periodFromTimeFormatted : '',
    'end_date': periodToTimeFormatted !== null ? periodToTimeFormatted : '',
    'industry': industry !== null && industry !== 'null' ? industry : '',
    'client': client !== null && client !== 'null' ? client : '',
    'salesman': salesman !== null && salesman !== 'null' ? salesman : '',
    'created_user': createdUser !== null && createdUser !== 'null' ? createdUser : '',
  }

  useEffect(() => {
    localStorage.setItem("orderItemsReports", JSON.stringify({
      "productsCurrentPage": productsCurrentPage,
      "bouquetsCurrentPage": bouquetsCurrentPage,
      "productsSubmittedSearch": productsSubmittedSearch,
      "bouquetsSubmittedSearch": bouquetsSubmittedSearch,
      "periodFromTimeFormatted": periodFromTimeFormatted,
      "periodToTimeFormatted": periodToTimeFormatted,
      "periodFromTime": periodFromTime,
      "periodToTime": periodToTime,
      "industry": industry,
      "client": client,
      "salesman": salesman,
      "createdUser": createdUser
    }))
  }, [
    productsCurrentPage,
    bouquetsCurrentPage,
    productsSubmittedSearch,
    bouquetsSubmittedSearch,
    periodFromTimeFormatted,
    periodToTimeFormatted,
    periodFromTime,
    periodToTime,
    industry,
    client,
    salesman,
    createdUser
  ])

  const { queryString: summaryQueryCollection } = useQueryString(summaryQueryParams)
  const { queryString: productsQueryCollection } = useQueryString(productsQueryParams)
  const { queryString: bouquetsQueryCollection } = useQueryString(bouquetsQueryParams)

  const [summaryQueryString, setSummaryQueryString] = useState('')
  const [productsQueryString, setProductsQueryString] = useState('')
  const [bouquetsQueryString, setBouquetsQueryString] = useState('')

  const { data, isLoading } = api.useGetOrderItemsReportQuery({ queryString: summaryQueryString })
  const { data: productsData, isLoading: productsLoading, isFetching: productsFetching, isError: productsError } = api.useGetOrderItemsReportQuery({ queryString: productsQueryString, item: 'order_items' })
  const { data: bouquetsData, isLoading: bouquetsLoading, isFetching: bouquetsFetching, isError: bouquetsError } = api.useGetOrderItemsReportQuery({ queryString: bouquetsQueryString, item: 'order_item_factories' })

  useEffect(() => {
    setProductsQueryString(productsQueryCollection)
  }, [productsCurrentPage, productsSubmittedSearch])

  useEffect(() => {
    setBouquetsQueryString(bouquetsQueryCollection)
  }, [bouquetsCurrentPage, bouquetsSubmittedSearch])

  return (
    <>
      { isLoading && productsLoading && bouquetsLoading ? (
        <SectionTableSkeleton />
      ) : (
        <section className='w-full flex flex-col gap-8'>
          <div className='flex flex-col gap-2'>
            <div className="grid items-center grid-cols-3 gap-3 max-[960px]:grid-cols-2 max-[960px]:gap-2 max-[690px]:grid-cols-1">
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium max-[1440px]:text-base">Общая сумма продаж: <span className="font-bold">{formatter.format(data?.total_sum)} сум</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium max-[1440px]:text-base">Общая себестоимость: <span className="font-bold">{formatter.format(data?.total_self_price_sum)} сум</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium max-[1440px]:text-base">Чистая прибыль: <span className="font-bold">{formatter.format(data?.total_profit_sum)} сум</span></p>
            </div>

            <div className="flex justify-end">
              <Dialog>
                <DialogTrigger>
                  <Button variant="outline">
                    <Eye className="w-4 h-4 mr-2"/> Дополнительная информация
                  </Button>
                </DialogTrigger>

                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Дополнительная информация</DialogTitle>
                  </DialogHeader>

                  <p className="mt-4 px-4 py-2 bg-neutral-100/70 rounded-lg font-medium max-[1440px]:text-base">Общее количество товаров: <span className="font-bold">{formatter.format(data?.total_count_sum)} шт</span></p>
                  <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium max-[1440px]:text-base">Общее количество возврата: <span className="font-bold">{formatter.format(data?.total_returned_count_sum)} шт</span>
                  </p>
                  <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium max-[1440px]:text-base">Общая сумма скидки: <span className="font-bold">{formatter.format(data?.total_discount_sum)} сум</span></p>
                  <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium max-[1440px]:text-base">Общая сумма наценки: <span className="font-bold">{formatter.format(data?.total_charge_sum)} сум</span></p>
                </DialogContent>
              </Dialog>
            </div>
          </div>

          <TableDownload
            apiUrl={`api/reports/order-items-report/excel-report`}
            params={summaryQueryString}
          />

          <FiltersBlock
            fromTime={fromTime}
            toTime={toTime}
            periodFromTime={periodFromTime}
            periodToTime={periodToTime}
            setFromTime={setFromTime}
            setToTime={setToTime}
            setPeriodFromTime={setPeriodFromTime}
            setPeriodToTime={setPeriodToTime}
            setSalesman={setSalesman}
            setCreatedUser={setCreatedUser}
            refetchData={() => {
              setSummaryQueryString(summaryQueryCollection)
              setProductsQueryString(productsQueryCollection)
              setBouquetsQueryString(bouquetsQueryCollection)
            }}
            setIndustry={setIndustry}
            setClients={setClient}
            industry={industry}
            client={client}
            salesmanValue={salesman}
            createdUserValue={createdUser}
            pathName={'orderItemsReports'}
            hasIndustry
            hasClients
            hasSalesman
            haventPeriods
            hasTimePeriods
            hasCreatedUser
          />

          <div className='w-full flex flex-col gap-8'>
            <SectionsTop
              title='Товары'
              placeholder='Поиск товаров'
              inputValue={productsSearchValue}
              onChange={productsHandleSearch}
              onClick={productsSubmitSearch}
            />

            <div className='flex flex-col gap-3'>
              { !productsFetching ? (
                <OrderItemsReportsTable data={productsData?.results} />
              ) : (
                <SectionTableSkeleton />
              ) }

              <PaginationComponent
                data={!productsError && productsData}
                currentPage={productsCurrentPage}
                totalPages={productsTotalPages}
                setCurrentPage={productsSetCurrentPage}
                setTotalPages={productsSetTotalPages}
                refetchData={() => setProductsQueryString(productsQueryCollection)}
              />
            </div>
          </div>

          <div className='w-full mt-10 flex flex-col gap-8'>
            <SectionsTop
              title='Букеты'
              placeholder='Поиск букетов'
              inputValue={bouquetsSearchValue}
              onChange={bouquetsHandleSearch}
              onClick={bouquetsSubmitSearch}
            />

            <div className='flex flex-col gap-3'>
              { !bouquetsFetching ? (
                <OrderItemsReportsTable data={bouquetsData?.results} hasntEye isBouquet />
              ) : (
                <SectionTableSkeleton />
              ) }

              <PaginationComponent
                data={!bouquetsError && bouquetsData}
                currentPage={bouquetsCurrentPage}
                totalPages={bouquetsTotalPages}
                setCurrentPage={bouquetsSetCurrentPage}
                setTotalPages={bouquetsSetTotalPages}
                refetchData={() => setBouquetsQueryString(bouquetsQueryCollection)}
              />
            </div>
          </div>
        </section>
      )}
    </>
  )
}

export default OrderItemsReportsSection