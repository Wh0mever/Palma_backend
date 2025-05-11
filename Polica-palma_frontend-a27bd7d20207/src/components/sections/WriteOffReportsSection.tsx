import SectionsTop from '@/components/others/SectionsTop.tsx'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import SectionTableSkeleton from '@/components/skeletons/SectionTableSkeleton.tsx'
import WriteOffReportsTable from '@/components/tables/elements/WriteOffReportsTable.tsx'
import usePagination from '@/hooks/usePagination.ts'
import PaginationComponent from '@/components/others/PaginationComponent.tsx'
import useFilters from '@/hooks/useFilters.ts'
import FiltersBlock from '@/components/others/FiltersBlock.tsx'
import TableDownload from '@/components/others/TableDownload.tsx'
import useServerSearch from '@/hooks/useServerSearch.ts'
import {useEffect, useState} from "react"
import useQueryString from '@/hooks/useQueryString.ts'
import {api} from "@/services/api.ts"

const WriteOffReportsSection = () => {
  const writeOffReportsFilterState = JSON.parse(localStorage.getItem("writeOffReports") || JSON.stringify({
    "productsPage": "",
    "factoriesPage": "",
    "productsSubmittedSearch": "",
    "factoriesSubmittedSearch": "",
    "periodFromFormatted": "",
    "periodToFormatted": "",
    "periodFrom": "",
    "periodTo": "",
    "productsCategory": "",
    "factoriesCategory": "",
    "industry": "",
  }))

  const { formatter } = useNumberFormatter()
  const { periodTo, periodFrom, periodFromFormatted, periodToFormatted, setPeriodFrom, setPeriodTo, productsCategory, factoriesCategory, setProductsCategory, setFactoriesCategory, industry, setIndustry } = useFilters(writeOffReportsFilterState)
  const { currentPage: productsPage, setCurrentPage: productsSetCurrentPage, totalPages: productsTotalPages, setTotalPages: productsSetTotalPages } = usePagination(writeOffReportsFilterState)
  const { currentPage: factoriesPage, setCurrentPage: factoriesSetCurrentPage, totalPages: factoriesTotalPages, setTotalPages: factoriesSetTotalPages } = usePagination(writeOffReportsFilterState)
  const { searchValue: productsSearchValue, handleSearch: productsHandleSearch, submittedSearch: productsSubmittedSearch, submitSearch: productsSubmitSearch } = useServerSearch(productsSetCurrentPage)
  const { searchValue: factoriesSearchValue, handleSearch: factoriesHandleSearch, submittedSearch: factoriesSubmittedSearch, submitSearch: factoriesSubmitSearch } = useServerSearch(factoriesSetCurrentPage)

  const summaryQueryParams: any = {
    'start_date': periodFromFormatted !== null ? periodFromFormatted : '',
    'end_date': periodToFormatted !== null ? periodToFormatted : '',
    'industry': industry !== null && industry !== 'null' ? industry : '',
    'category': productsCategory !== null && productsCategory !== 'null' ? productsCategory : '',
    'factory_category': factoriesCategory !== null && factoriesCategory !== 'null' ? factoriesCategory : '',
  }

  const productsQueryParams: any = {
    'page': productsPage,
    'search': productsSubmittedSearch,
    'start_date': periodFromFormatted !== null ? periodFromFormatted : '',
    'end_date': periodToFormatted !== null ? periodToFormatted : '',
    'industry': industry !== null && industry !== 'null' ? industry : '',
    'category': productsCategory !== null && productsCategory !== 'null' ? productsCategory : ''
  }

  const factoriesQueryParams: any = {
    'page': factoriesPage,
    'search': factoriesSubmittedSearch,
    'start_date': periodFromFormatted !== null ? periodFromFormatted : '',
    'end_date': periodToFormatted !== null ? periodToFormatted : '',
    'factory_category': factoriesCategory !== null && factoriesCategory !== 'null' ? factoriesCategory : ''
  }

  useEffect(() => {
    localStorage.setItem("writeOffReports", JSON.stringify({
      "productsPage": productsPage,
      "factoriesPage": factoriesPage,
      "productsSubmittedSearch": productsSubmittedSearch,
      "factoriesSubmittedSearch": factoriesSubmittedSearch,
      "periodFromFormatted": periodFromFormatted,
      "periodToFormatted": periodToFormatted,
      "periodFrom": periodFrom,
      "periodTo": periodTo,
      "productsCategory": productsCategory,
      "factoriesCategory": factoriesCategory,
      "industry": industry,
    }))
  }, [
    productsPage,
    factoriesPage,
    productsSubmittedSearch,
    factoriesSubmittedSearch,
    periodFromFormatted,
    periodToFormatted,
    periodFrom,
    periodTo,
    productsCategory,
    factoriesCategory,
    industry
  ])

  const { queryString: summaryQueryStringCollection } = useQueryString(summaryQueryParams)
  const { queryString: productsQueryStringCollection } = useQueryString(productsQueryParams)
  const { queryString: factoriesQueryStringCollection } = useQueryString(factoriesQueryParams)

  const [summaryQueryString, setSummaryQueryString] = useState('')
  const [productsQueryString, setProductsQueryString] = useState('')
  const [factoriesQueryString, setFactoriesQueryString] = useState('')

  const { data, isLoading } = api.useGetWriteOffsReportsQuery({ queryString: summaryQueryString, item: 'summary' })
  const { data: productsData, isLoading: productsLoading, isFetching: productsFetching, isError: productsError } = api.useGetWriteOffsReportsQuery({ queryString: productsQueryString, item: 'products' })
  const { data: factoriesData, isLoading: factoriesLoading, isFetching: factoriesFetching, isError: factoriesError } = api.useGetWriteOffsReportsQuery({ queryString: factoriesQueryString, item: 'product-factories' })

  useEffect(() => {
    setProductsQueryString(productsQueryStringCollection)
  }, [productsPage, productsSubmittedSearch])

  useEffect(() => {
    setFactoriesQueryString(factoriesQueryStringCollection)
  }, [factoriesPage, factoriesSubmittedSearch])

  return (
    <>
      { isLoading && productsLoading && factoriesLoading ? (
        <SectionTableSkeleton />
      ) : (
        <section className='w-full flex flex-col gap-8'>
          <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 text-sm'>
            <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Общее количество списанных товаров: <span
              className='font-bold'>{formatter.format(data?.total_product_count)} шт</span></p>
            <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Общая себестоимость списанных
              товаров: <span className='font-bold'>{formatter.format(data?.total_self_price_sum)} сум</span></p>
            <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Общее количество списанных букетов: <span
              className='font-bold'>{formatter.format(data?.total_product_factory_count)} шт</span></p>
            <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Общая себестоимость списанных
              букетов: <span
                className='font-bold'>{formatter.format(data?.total_product_factory_self_price_sum)} сум</span></p>
          </div>

          <TableDownload
            apiUrl={`api/reports/write-offs-report/export-excel`}
            params={{
              'start_date': periodFromFormatted !== null ? periodFromFormatted : '',
              'end_date': periodToFormatted !== null ? periodToFormatted : '',
              'industry': industry !== null && industry !== 'null' ? industry : '',
              'category': productsCategory !== null && productsCategory !== 'null' ? productsCategory : '',
              'factory_category': factoriesCategory !== null && factoriesCategory !== 'null' ? factoriesCategory : '',
            }}
          />

          <div className='w-full flex flex-col gap-16'>
            <div className='w-full flex flex-col gap-8'>
              <FiltersBlock
                periodFrom={periodFrom}
                periodTo={periodTo}
                setPeriodFrom={setPeriodFrom}
                setPeriodTo={setPeriodTo}
                setProductsCategory={setProductsCategory}
                setFactoriesCategory={setFactoriesCategory}
                setIndustry={setIndustry}
                refetchData={() => {
                  setSummaryQueryString(summaryQueryStringCollection)
                  setProductsQueryString(productsQueryStringCollection)
                  setFactoriesQueryString(factoriesQueryStringCollection)
                }}
                productsCategory={productsCategory}
                factoriesCategory={factoriesCategory}
                industry={industry}
                pathName={'writeOffReports'}
                hasIndustry
                hasProductsCategory
                hasFactoriesCategory
              />

              <SectionsTop
                title='Списанные товары'
                placeholder='Поиск списанных товаров'
                inputValue={productsSearchValue}
                onChange={productsHandleSearch}
                onClick={productsSubmitSearch}
              />

              <div className='w-full h-full relative flex flex-col gap-3'>
                { !productsFetching ? (
                  <WriteOffReportsTable data={productsData?.results} />
                ) : (
                  <SectionTableSkeleton />
                ) }

                <PaginationComponent
                  data={!productsError && productsData}
                  currentPage={productsPage}
                  totalPages={productsTotalPages}
                  setCurrentPage={productsSetCurrentPage}
                  setTotalPages={productsSetTotalPages}
                  refetchData={() => setProductsQueryString(productsQueryStringCollection)}
                />
              </div>
            </div>

            <div className='w-full flex flex-col gap-8'>
              <SectionsTop
                title='Списанные букеты'
                placeholder='Поиск списанных букетов'
                inputValue={factoriesSearchValue}
                onChange={factoriesHandleSearch}
                onClick={factoriesSubmitSearch}
              />

              <div className='w-full h-full relative flex flex-col gap-3'>
                { !factoriesFetching ? (
                  <WriteOffReportsTable data={factoriesData?.results} isBouquet />
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
          </div>
        </section>
      )}
    </>
  )
}

export default WriteOffReportsSection