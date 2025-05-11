/* eslint-disable @typescript-eslint/no-explicit-any */
import useAxiosPost from "@/hooks/useAxiosPost.ts"
import {z} from "zod"
import SectionsTop from "@/components/others/SectionsTop.tsx"
import AddForm from "@/components/others/AddForm.tsx"
import OrdersTable from "@/components/tables/elements/OrdersTable.tsx"
import OrdersFormFields from "@/components/forms/OrdersFormFields.tsx"
import {Button} from "@/components/ui/button.tsx"
import SectionTableSkeleton from "@/components/skeletons/SectionTableSkeleton.tsx"
import usePagination from "@/hooks/usePagination.ts"
import useFilters from "@/hooks/useFilters.ts"
import FiltersBlock from "@/components/others/FiltersBlock.tsx"
import PaginationComponent from "@/components/others/PaginationComponent.tsx"
import useServerSearch from "@/hooks/useServerSearch.ts"
import {useEffect, useState} from "react"
import useQueryString from "@/hooks/useQueryString.ts"
import getUserData from "@/helpers/getUserData.ts"
import {Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger} from "@/components/ui/dialog.tsx"
import {Plus} from "lucide-react"
import {api} from "@/services/api.ts"
import TableDownload from "@/components/others/TableDownload.tsx"
import useNumberFormatter from "@/hooks/useNumberFormatter.ts"

const OrdersSection = () => {
  const ordersFilterState = JSON.parse(localStorage.getItem("orders") || JSON.stringify({
    "currentPage": "",
    "submittedSearch": "",
    "periodFromTimeFormatted": "",
    "periodToTimeFormatted": "",
    "periodFromTime": "",
    "periodToTime": "",
    "industry": "",
    "client": "",
    "status": "",
    "createdUser": "",
    "hasDebt": "",
    "salesman": ""
  }))

  const {userType} = getUserData()
  const { formatter } = useNumberFormatter()
  const {currentPage, setCurrentPage, totalPages, setTotalPages} = usePagination(ordersFilterState)
  const { fromTime, toTime, setToTime, setFromTime, periodFromTime, setPeriodFromTime, periodToTime, setPeriodToTime, periodFromTimeFormatted, periodToTimeFormatted, industry, setIndustry, client, setClient, status, setStatus, createdUser, setCreatedUser, hasDebt, setHasDebt, salesman, setSalesman } = useFilters(ordersFilterState)
  const { searchValue, handleSearch, submittedSearch, submitSearch } = useServerSearch(setCurrentPage)

  const queryParams: any = {
    "page": currentPage,
    "search": submittedSearch,
    "start_date": periodFromTimeFormatted !== null ? periodFromTimeFormatted : "",
    "end_date": periodToTimeFormatted !== null ? periodToTimeFormatted : "",
    "industry": industry !== null && industry !== "null" ? industry : "",
    "client": client !== null && client !== "null" ? client : "",
    "status": status !== null && status !== "null" ? status : "",
    "created_user": createdUser !== null && createdUser !== "null" ? createdUser : "",
    "has_debt": hasDebt !== null && hasDebt !== "null" ? hasDebt : "",
    "salesman": salesman !== null && salesman !== "null" ? salesman : "",
  }

  useEffect(() => {
    localStorage.setItem("orders", JSON.stringify({
      "currentPage": currentPage,
      "submittedSearch": submittedSearch,
      "periodFromTimeFormatted": periodFromTimeFormatted,
      "periodToTimeFormatted": periodToTimeFormatted,
      "periodFromTime": periodFromTime,
      "periodToTime": periodToTime,
      "industry": industry,
      "client": client,
      "status": status,
      "createdUser": createdUser,
      "hasDebt": hasDebt,
      "salesman": salesman,
    }))
  }, [
    currentPage,
    submittedSearch,
    periodFromTimeFormatted,
    periodToTimeFormatted,
    periodFromTime,
    periodToTime,
    industry,
    client,
    status,
    createdUser,
    hasDebt,
    salesman
  ])

  const { queryString: queryStringCollection } = useQueryString(queryParams)
  const [queryString, setQueryString] = useState('')
  const { data, isLoading, isFetching, isError } = api.useGetOrdersQuery({ queryString: queryString })
  const { data: summaryData, isLoading: summaryLoading } = api.useGetOrdersSummaryQuery(queryString)
  // const {data: hasShiftData, isLoading: hasShiftIsLoading} = api.useGetShiftStatusQuery("")
  // const [createShift, {isLoading: openPending}] = api.useCreateShiftMutation<any>()

  const {success, form, onSubmit, pending} = useAxiosPost(
    {
      client: z.string({required_error: "Пожалуйста, выберите клиента"}),
      department: z.string({required_error: "Пожалуйста, выберите отдел"}),
      salesman: z.string().optional(),
      comment: z.string().optional()
    },
    {},
    "api/orders/",
    ["Orders"]
  )

  useEffect(() => {
    setQueryString(queryStringCollection)
  }, [currentPage, submittedSearch])

  return (
    <>
      {isLoading && !summaryLoading ? (
        <SectionTableSkeleton/>
      ) : (
        <section className="w-full flex flex-col gap-8">
          <SectionsTop
            title="Продажи"
            placeholder="Поиск продаж"
            inputValue={searchValue}
            onChange={handleSearch}
            onClick={submitSearch}
          />

          <div
            className="grid grid-cols-3 gap-3 max-[960px]:grid-cols-2 max-[960px]:gap-2 max-[690px]:grid-cols-1">
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium max-[1440px]:text-base">Общая сумма
              продаж: <span
                className="font-bold">{formatter.format(summaryData?.total_sale_with_discount_amount)} сум</span></p>
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium max-[1440px]:text-base">Общая сумма
              долга: <span
                className="font-bold">{formatter.format(summaryData?.total_debt_amount)} сум</span></p>
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium max-[1440px]:text-base">Общая сумма
              скидки: <span className="font-bold">{formatter.format(summaryData?.total_discount_amount)} сум</span></p>
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium max-[1440px]:text-base">Общая сумма
              наценки: <span className="font-bold">{formatter.format(summaryData?.total_charge_amount)} сум</span></p>
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium max-[1440px]:text-base">Общая
              себестоимость: <span
                className="font-bold">{formatter.format(summaryData?.total_self_price_amount)} сум</span></p>
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium max-[1440px]:text-base">Общая
              прибыль: <span className="font-bold">{formatter.format(summaryData?.total_profit_amount)} сум</span></p>
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium max-[1440px]:text-base">Количество открытых заказов: <span className="font-bold">{formatter.format(summaryData?.created_orders_count)} шт</span></p>
          </div>

          <div className="flex items-center justify-center sm:justify-end">
            {userType !== "FLORIST" && userType !== "FLORIST_ASSISTANT" ? (
              <>
                <div className='flex items-center gap-3'>
                  <TableDownload
                    apiUrl={`api/orders/export-excel`}
                    params={queryString}
                    text='Продажи с долгом'
                  />

                  {!success ? (
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button>
                          <Plus className="w-4 h-4 mr-2"/> Добавить продажу
                        </Button>
                      </DialogTrigger>

                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Добавить продажу</DialogTitle>
                          <DialogDescription>Заполните все поля чтобы добавить продажу</DialogDescription>
                        </DialogHeader>

                        <AddForm
                          form={form}
                          onSubmit={onSubmit}
                          success={success}
                          successDesc="Новая продажа успешно добавлена"
                        >
                          <OrdersFormFields form={form}/>
                          <Button className="mt-5" disabled={pending}>Добавить продажу</Button>
                        </AddForm>
                      </DialogContent>

                      {/*{ !hasShiftIsLoading && hasShiftData.has_shift ? (*/}
                      {/*  <DialogContent>*/}
                      {/*    <DialogHeader>*/}
                      {/*      <DialogTitle>Добавить продажу</DialogTitle>*/}
                      {/*      <DialogDescription>Заполните все поля чтобы добавить продажу</DialogDescription>*/}
                      {/*    </DialogHeader>*/}

                      {/*    <AddForm*/}
                      {/*      form={form}*/}
                      {/*      onSubmit={onSubmit}*/}
                      {/*      success={success}*/}
                      {/*      successDesc="Новая продажа успешно добавлена"*/}
                      {/*    >*/}
                      {/*      <OrdersFormFields form={form}/>*/}
                      {/*      <Button className="mt-5" disabled={pending}>Добавить продажу</Button>*/}
                      {/*    </AddForm>*/}
                      {/*  </DialogContent>*/}
                      {/*) : (*/}
                      {/*  <DialogContent>*/}
                      {/*    <DialogHeader>*/}
                      {/*      <DialogTitle>Откройте смену чтобы добавить продажу</DialogTitle>*/}
                      {/*    </DialogHeader>*/}

                      {/*    <Button disabled={openPending} onClick={() => createShift({})}>*/}
                      {/*      <CalendarClock className="w-4 h-4 mr-2"/> Открыть смену*/}
                      {/*    </Button>*/}
                      {/*  </DialogContent>*/}
                      {/*) }*/}
                    </Dialog>
                  ) : null}
                </div>
              </>
            ) : null}
          </div>

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
              setIndustry={setIndustry}
              setClients={setClient}
              setStatus={setStatus}
              setCreatedUser={setCreatedUser}
              setHasDebt={setHasDebt}
              setSalesman={setSalesman}
              statusApiUrl={`api/orders/statuses/`}
              refetchData={() => setQueryString(queryStringCollection)}
              industry={industry}
              client={client}
              status={status}
              createdUserValue={createdUser}
              hasDebtValue={hasDebt}
              salesmanValue={salesman}
              pathName={'orders'}
              hasIndustry
              hasClients
              hasStatus
              hasCreatedUser
              hasDebt
              hasSalesman
              haventPeriods
              hasTimePeriods
            />

            {!isFetching ? (
              <OrdersTable data={data && data?.results}/>
            ) : (
              <SectionTableSkeleton/>
            )}

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

export default OrdersSection