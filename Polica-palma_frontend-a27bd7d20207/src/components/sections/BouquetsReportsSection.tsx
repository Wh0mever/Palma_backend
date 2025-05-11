import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import SectionsTop from '@/components/others/SectionsTop.tsx'
import SectionTableSkeleton from '@/components/skeletons/SectionTableSkeleton.tsx'
import BouquetsReportsTable from '@/components/tables/elements/BouquetsReportsTable.tsx'
import usePagination from '@/hooks/usePagination.ts'
import PaginationComponent from '@/components/others/PaginationComponent.tsx'
import useFilters from '@/hooks/useFilters.ts'
import FiltersBlock from '@/components/others/FiltersBlock.tsx'
import TableDownload from '@/components/others/TableDownload.tsx'
import useServerSearch from '@/hooks/useServerSearch.ts'
import {useEffect, useState} from "react"
import useQueryString from '@/hooks/useQueryString.ts'
import {api} from "@/services/api.ts"

const BouquetsReportsSection = () => {
  const bouquetsReportsFilterState = JSON.parse(localStorage.getItem("bouquetsReports") || JSON.stringify({
    "currentPage": "",
    "submittedSearch": "",
    "periodFromFormatted": "",
    "periodToFormatted": "",
    "periodFrom": "",
    "periodTo": "",
    "factoriesCategory": "",
    "status": "",
    "florist": "",
    "salesType": ""
  }))

  const { formatter } = useNumberFormatter()
  const { periodTo, periodFrom, periodFromFormatted, periodToFormatted, setPeriodFrom, setPeriodTo, factoriesCategory, setFactoriesCategory, status, setStatus, florist, setFlorist, salesType, setSalesType } = useFilters(bouquetsReportsFilterState)
  const { currentPage, setCurrentPage, totalPages, setTotalPages } = usePagination(bouquetsReportsFilterState)
  const { searchValue, handleSearch, submitSearch, submittedSearch } = useServerSearch(setCurrentPage)

  const queryParams: any = {
    'page': currentPage,
    'search': submittedSearch,
    'status': status !== null && status !== 'null' ? status : '',
    'start_date': periodFromFormatted !== null ? periodFromFormatted : '',
    'end_date': periodToFormatted !== null ? periodToFormatted : '',
    'category': factoriesCategory !== null && factoriesCategory !== 'null' ? factoriesCategory : '',
    'florist': florist !== null && florist !== 'null' ? florist : '',
    'sales_type': salesType !== null && salesType !== 'null' ? salesType : ''
  }

  useEffect(() => {
    localStorage.setItem("bouquetsReports", JSON.stringify({
      "currentPage": currentPage,
      "submittedSearch": submittedSearch,
      "periodFromFormatted": periodFromFormatted,
      "periodToFormatted": periodToFormatted,
      "periodFrom": periodFrom,
      "periodTo": periodTo,
      "factoriesCategory": factoriesCategory,
      "status": status,
      "florist": florist,
      "salesType": salesType
    }))
  }, [
    currentPage,
    submittedSearch,
    periodFromFormatted,
    periodToFormatted,
    periodFrom,
    periodTo,
    factoriesCategory,
    status,
    florist,
    salesType
  ])

  const { queryString: queryStringCollection } = useQueryString(queryParams)
  const [queryString, setQueryString] = useState('')

  const { data, isLoading } = api.useGetBouquetsReportsQuery({ queryString: queryString, item: 'summary' })
  const { data: factoriesData, isLoading: factoriesLoading, isFetching: factoriesFetching, isError: factoriesError } = api.useGetBouquetsReportsQuery({ queryString: queryString, item: 'products' })

  useEffect(() => {
    setQueryString(queryStringCollection)
  }, [currentPage, submittedSearch])

  return (
    <>
      { isLoading && factoriesLoading ? (
        <SectionTableSkeleton />
      ) : (
        <section className='w-full flex flex-col gap-8'>
          <div className='grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3 text-sm'>
            <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Общая сумма собранных букетов: <span
              className='font-bold'>{formatter.format(data?.total_finished_price)} сум</span></p>
            <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Общая себестоимость собранных
              букетов: <span className='font-bold'>{formatter.format(data?.total_finished_self_price)} сум</span></p>
            <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Общее количество собранных букетов: <span
              className='font-bold'>{formatter.format(data?.total_finished_count)} шт</span></p>
            <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Общая сумма проданных букетов: <span
              className='font-bold'>{formatter.format(data?.total_sold_price)} сум</span></p>
            <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Общая себестоимость проданных
              букетов: <span className='font-bold'>{formatter.format(data?.total_sold_self_price)} сум</span></p>
            <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Общее количество проданных букетов: <span
              className='font-bold'>{formatter.format(data?.total_sold_count)} шт</span></p>
            <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Общая себестоимость списанных
              букетов: <span className='font-bold'>{formatter.format(data?.total_written_off_self_price)} сум</span></p>
            <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Общее количество списанных букетов: <span
              className='font-bold'>{formatter.format(data?.total_written_off_count)} шт</span></p>
            <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Общее количество букетов: <span
              className='font-bold'>{formatter.format(data?.total_product_count)} шт</span></p>
          </div>

          <div className='w-full mt-12 flex flex-col gap-16'>
            <div className='w-full flex flex-col gap-8'>
              <SectionsTop
                title='Букеты'
                placeholder='Поиск букетов'
                inputValue={searchValue}
                onChange={handleSearch}
                onClick={submitSearch}
              />

              <TableDownload
                apiUrl={`api/reports/product-factories-report/excel-report`}
                params={queryString}
              />

              <FiltersBlock
                periodFrom={periodFrom}
                periodTo={periodTo}
                setPeriodFrom={setPeriodFrom}
                setPeriodTo={setPeriodTo}
                setStatus={setStatus}
                setFlorist={setFlorist}
                setFactoriesCategory={setFactoriesCategory}
                setSalesType={setSalesType}
                statusApiUrl={`api/factories/product-factories/statuses/`}
                refetchData={() => setQueryString(queryStringCollection)}
                factoriesCategory={factoriesCategory}
                status={status}
                florist={florist}
                salesType={salesType}
                pathName={'bouquetsReports'}
                hasStatus
                hasFlorist
                hasSalesType
                hasFactoriesCategory
              />

              <div className='w-full h-full relative flex flex-col gap-3'>
                { !factoriesFetching ? (
                  <BouquetsReportsTable data={factoriesData?.results} />
                ) : (
                  <SectionTableSkeleton />
                ) }

                <PaginationComponent
                  data={!factoriesError && factoriesData}
                  currentPage={currentPage}
                  totalPages={totalPages}
                  setCurrentPage={setCurrentPage}
                  setTotalPages={setTotalPages}
                  refetchData={() => setQueryString(queryStringCollection)}
                />
              </div>
            </div>
          </div>
        </section>
      )}
    </>
  )
}

export default BouquetsReportsSection