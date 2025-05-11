import SectionsTop from '@/components/others/SectionsTop.tsx'
import useAxiosPost from '@/hooks/useAxiosPost.ts'
import {z} from 'zod'
import AddDialog from '@/components/others/AddDialog.tsx'
import AddForm from '@/components/others/AddForm.tsx'
import {Button} from '@/components/ui/button.tsx'
import BouquetsFormFields from '@/components/forms/BouquetsFormFields.tsx'
import SectionTableSkeleton from '@/components/skeletons/SectionTableSkeleton.tsx'
import usePagination from '@/hooks/usePagination.ts'
import useFilters from '@/hooks/useFilters.ts'
import BouquetsTable from '@/components/tables/elements/BouquetsTable.tsx'
import FiltersBlock from '@/components/others/FiltersBlock.tsx'
import PaginationComponent from '@/components/others/PaginationComponent.tsx'
import useServerSearch from '@/hooks/useServerSearch.ts'
import {useEffect, useState} from "react"
import getUserData from '@/helpers/getUserData.ts'
import useQueryString from '@/hooks/useQueryString.ts'
import {api} from "@/services/api.ts"
import {Skeleton} from "@/components/ui/skeleton.tsx"
import useNumberFormatter from "@/hooks/useNumberFormatter.ts"

const BouquetsSection = () => {
  const bouquetsFilterState = JSON.parse(localStorage.getItem("bouquets") || JSON.stringify({
    "currentPage": "",
    "submittedSearch": "",
    "periodFromFormatted": "",
    "periodToFormatted": "",
    "periodFrom": "",
    "periodTo": "",
    "status": "",
    "salesType": "",
    "industry": "",
    "florist": "",
    "client": "",
  }))

  const { userType } = getUserData()
  const { formatter } = useNumberFormatter()
  const { currentPage, setCurrentPage, totalPages, setTotalPages } = usePagination(bouquetsFilterState)
  const { fromTime, toTime, setToTime, setFromTime, periodFromTime, setPeriodFromTime, periodToTime, setPeriodToTime, periodFromTimeFormatted, periodToTimeFormatted, status, setStatus, salesType, setSalesType, industry, setIndustry, florist, setFlorist, client, setClient } = useFilters(bouquetsFilterState)
  const { searchValue, handleSearch, submittedSearch, submitSearch } = useServerSearch(setCurrentPage)

  const queryParams: any = {
    'page': currentPage,
    'search': submittedSearch,
    "start_date": periodFromTimeFormatted !== null ? periodFromTimeFormatted : "",
    "end_date": periodToTimeFormatted !== null ? periodToTimeFormatted : "",
    'status': status !== null && status !== 'null' ? status : '',
    'sales_type': salesType !== null && salesType !== 'null' ? salesType : '',
    'industry': industry !== null && industry !== 'null' ? industry : '',
    'florist': florist !== null && florist !== 'null' ? florist : '',
    'client': client !== null && client !== 'null' ? client : '',
  }

  useEffect(() => {
    localStorage.setItem("bouquets", JSON.stringify({
      "currentPage": currentPage,
      "submittedSearch": submittedSearch,
      "periodFromTimeFormatted": periodFromTimeFormatted,
      "periodToTimeFormatted": periodToTimeFormatted,
      "periodFromTime": periodFromTime,
      "periodToTime": periodToTime,
      "status": status,
      "salesType": salesType,
      "industry": industry,
      "florist": florist,
      "client": client,
    }))
  }, [
    currentPage,
    submittedSearch,
    periodFromTimeFormatted,
    periodToTimeFormatted,
    periodFromTime,
    periodToTime,
    status,
    salesType,
    industry,
    florist,
    client
  ])

  const { queryString: queryStringCollection } = useQueryString(queryParams)
  const [queryString, setQueryString] = useState('')
  const { data, isLoading, isFetching, isError } = api.useGetBouquetsQuery({ queryString: queryString })
  const { data: summaryData, isLoading: summaryLoading, isFetching: summaryFetching } = api.useGetBouquetsSummaryQuery(queryString)

  const { success, form, onSubmit, pending } = useAxiosPost(
     userType !== 'CRAFTER' ? {
      category: z.string({ required_error: "Пожалуйста, выберите категорию" }),
      sales_type: z.string({ required_error: "Пожалуйста, выберите тип продажи" }),
      florist: z.string({ required_error: "Пожалуйста, выберите флориста" }),
    } : {
       category: z.string({ required_error: "Пожалуйста, выберите категорию" }),
       sales_type: z.string({ required_error: "Пожалуйста, выберите тип продажи" }),
     },
    {},
    'api/factories/product-factories/',
    ["Bouquets"]
  )

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
            title='Букеты'
            placeholder='Поиск букетов'
            inputValue={searchValue}
            onChange={handleSearch}
            onClick={submitSearch}
          />

          <div className='flex items-center justify-center sm:justify-end'>
            {!success && userType !== 'FLORIST' && userType !== 'FLORIST_PERCENT' && userType !== 'SALESMAN' ? (
              <AddDialog btnText='Создать букет' dialogTitle='Создать букет' dialogDesc='Заполните все поля чтобы создать букет'>
                <AddForm
                  form={form}
                  onSubmit={onSubmit}
                  success={success}
                  successDesc='Новый букет успешно добавлен'
                >
                  <BouquetsFormFields form={form}/>
                  <Button className='mt-5' disabled={pending}>Создать букет</Button>
                </AddForm>
              </AddDialog>
            ) : null}
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
              setStatus={setStatus}
              setFlorist={setFlorist}
              setIndustry={setIndustry}
              setSalesType={setSalesType}
              setClients={setClient}
              statusApiUrl={`api/factories/product-factories/statuses/`}
              refetchData={() => setQueryString(queryStringCollection)}
              status={status}
              salesType={salesType}
              industry={industry}
              florist={florist}
              pathName={'bouquets'}
              hasStatus
              hasFlorist
              hasClients
              hasIndustry
              hasSalesType
              haventPeriods
              hasTimePeriods
            />

            { summaryLoading || summaryFetching ? (
              <Skeleton className='w-full h-8' />
            ) : (
              <div className="w-full my-3 flex items-center justify-between gap-3">
                <div className="w-full p-3 text-sm font-semibold rounded-xl bg-neutral-100">
                  Общее количество букетов: {formatter.format(summaryData?.total_count)} шт
                </div>
                <div className="w-full p-3 text-sm font-semibold rounded-xl bg-neutral-100">
                  Общая сумма продаж: {formatter.format(summaryData?.total_sale_price_sum)} сум
                </div>
                <div className="w-full p-3 text-sm font-semibold rounded-xl bg-neutral-100">
                  Общая себестоимость: {formatter.format(summaryData?.total_self_price_sum)} сум
                </div>
                <div className="w-full p-3 text-sm font-semibold rounded-xl bg-neutral-100">
                  Общая прибыль: {formatter.format(summaryData?.total_profit_sum)} сум
                </div>
              </div>
            )}

            {!isFetching ? (
              <BouquetsTable data={data?.results}/>
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

export default BouquetsSection