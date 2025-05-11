import SectionsTop from '@/components/others/SectionsTop.tsx'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import SectionTableSkeleton from '@/components/skeletons/SectionTableSkeleton.tsx'
import ReturnsReportsProductsTable from '@/components/tables/elements/ReturnsReportsProductsTable.tsx'
import ReturnsReportsBouquetsTable from '@/components/tables/elements/ReturnsReportsBouquetsTable.tsx'
import usePagination from '@/hooks/usePagination.ts'
import PaginationComponent from '@/components/others/PaginationComponent.tsx'
import useFilters from '@/hooks/useFilters.ts'
import FiltersBlock from '@/components/others/FiltersBlock.tsx'
import TableDownload from '@/components/others/TableDownload.tsx'
import useServerSearch from '@/hooks/useServerSearch.ts'
import {useEffect, useState} from "react"
import useQueryString from '@/hooks/useQueryString.ts'
import {api} from "@/services/api.ts"

const ReturnsReportsSection = () => {
  const returnsReportsFilterState = JSON.parse(localStorage.getItem("returnsReports") || JSON.stringify({
    "productsPage": "",
    "factoryPage": "",
    "productsSubmittedSearch": "",
    "factorySubmittedSearch": "",
    "periodFromFormatted": "",
    "periodToFormatted": "",
    "periodFrom": "",
    "periodTo": "",
    "productsCategory": "",
    "factoriesCategory": "",
    "industry": "",
  }))

  const { formatter } = useNumberFormatter()
  const { periodTo, periodFrom, periodFromFormatted, periodToFormatted, setPeriodFrom, setPeriodTo, productsCategory, factoriesCategory, setProductsCategory, setFactoriesCategory, industry, setIndustry } = useFilters(returnsReportsFilterState)
  const { currentPage: productsPage, setCurrentPage: productsSetCurrentPage, totalPages: productsTotalPages, setTotalPages: productsSetTotalPages } = usePagination(returnsReportsFilterState)
  const { currentPage: factoryPage, setCurrentPage: factorySetCurrentPage, totalPages: factoryTotalPages, setTotalPages: factorySetTotalPages } = usePagination(returnsReportsFilterState)
  const { searchValue: productsSearchValue, handleSearch: productsHandleSearch, submittedSearch: productsSubmittedSearch, submitSearch: productsSubmitSearch } = useServerSearch(productsSetCurrentPage)
  const { searchValue: factorySearchValue, handleSearch: factoryHandleSearch, submittedSearch: factorySubmittedSearch, submitSearch: factorySubmitSearch } = useServerSearch(factorySetCurrentPage)

  const summaryQueryParams: any = {
    'start_date': periodFromFormatted !== null ? periodFromFormatted : '',
    'end_date': periodToFormatted !== null ? periodToFormatted : '',
    'category': productsCategory !== null && productsCategory !== 'null' ? productsCategory : '',
    'factory_category': factoriesCategory !== null && factoriesCategory !== 'null' ? factoriesCategory : '',
    'industry': industry !== null && industry !== 'null' ? industry : ''
  }

  const productsQueryParams: any = {
    'page': productsPage,
    'search': productsSubmittedSearch,
    'start_date': periodFromFormatted !== null ? periodFromFormatted : '',
    'end_date': periodToFormatted !== null ? periodToFormatted : '',
    'category': productsCategory !== null && productsCategory !== 'null' ? productsCategory : '',
    'industry': industry !== null && industry !== 'null' ? industry : '',
  }

  const factoriesQueryParams: any = {
    'page': factoryPage,
    'search': factorySubmittedSearch,
    'start_date': periodFromFormatted !== null ? periodFromFormatted : '',
    'end_date': periodToFormatted !== null ? periodToFormatted : '',
    'factory_category': factoriesCategory !== null && factoriesCategory !== 'null' ? factoriesCategory : ''
  }

  useEffect(() => {
    localStorage.setItem("returnsReports", JSON.stringify({
      "productsPage": productsPage,
      "factoryPage": factoryPage,
      "productsSubmittedSearch": productsSubmittedSearch,
      "factorySubmittedSearch": factorySubmittedSearch,
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
    factoryPage,
    productsSubmittedSearch,
    factorySubmittedSearch,
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

  const { data, isLoading } = api.useGetReturnsReportsQuery({ queryString: summaryQueryString, item: 'summary' })
  const { data: productsData, isLoading: productsLoading, isFetching: productsFetching, isError: productsError } = api.useGetReturnsReportsQuery({ queryString: productsQueryString, item: 'product-returns' })
  const { data: factoriesData, isLoading: factoriesLoading, isFetching: factoriesFetching, isError: factoriesError } = api.useGetReturnsReportsQuery({ queryString: factoriesQueryString, item: 'factory-returns' })

  useEffect(() => {
    setProductsQueryString(productsQueryStringCollection)
  }, [productsPage, productsSubmittedSearch])

  useEffect(() => {
    setFactoriesQueryString(factoriesQueryStringCollection)
  }, [factoryPage, factorySubmittedSearch])

  return (
    <>
      { isLoading && productsLoading && factoriesLoading ? (
        <SectionTableSkeleton />
      ) : (
        <section className="w-full flex flex-col gap-8">
          <h1 className="text-3xl font-bold">Отчеты по возвратам</h1>

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3 text-sm">
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общее количество возвращенных товаров: <span className="font-bold">{formatter.format(data?.total_product_returns)} шт</span></p>
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общая сумма возвращенных товаров: <span className="font-bold">{formatter.format(data?.total_product_returns_price)} сум</span></p>
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общая себестоимость возвращенных товаров: <span className="font-bold">{formatter.format(data?.total_product_returns_self_price)} сум</span></p>
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общее количество возвращенных букетов: <span className="font-bold">{formatter.format(data?.total_product_factory_returns)} шт</span></p>
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общая сумма возвращенных букетов: <span className="font-bold">{formatter.format(data?.total_product_factory_returns_price)} сум</span></p>
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общая себестоимость возвращенных букетов: <span className="font-bold">{formatter.format(data?.total_product_factory_returns_self_price)} сум</span></p>
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общее количество возврата: <span className="font-bold">{formatter.format(data?.total_returns)} шт</span></p>
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общая сумма: <span className="font-bold">{formatter.format(data?.total_price)} сум</span></p>
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общее себестоимость: <span className="font-bold">{formatter.format(data?.total_self_price)} сум</span></p>
          </div>

          <TableDownload
            apiUrl={`api/reports/product-returns-report/excel-report`}
            params={{
              "start_date": periodFromFormatted !== null ? periodFromFormatted : "",
              "end_date": periodToFormatted !== null ? periodToFormatted : "",
              "industry": industry !== null && industry !== "null" ? industry : "",
              "category": productsCategory !== null && productsCategory !== "null" ? productsCategory : "",
              "factory_category": factoriesCategory !== null && factoriesCategory !== "null" ? factoriesCategory : "",
            }}
          />

          <div className="flex flex-col gap-16">
            <div className="flex flex-col gap-8">
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
                pathName={'returnsReports'}
                hasIndustry
                hasProductsCategory
                hasFactoriesCategory
              />

              <SectionsTop
                title="Возвращенные товары"
                placeholder="Поиск возвращенных товаров"
                inputValue={productsSearchValue}
                onChange={productsHandleSearch}
                onClick={productsSubmitSearch}
              />

              <div className="w-full h-full relative flex flex-col gap-3">
                { !productsFetching ? (
                  <ReturnsReportsProductsTable data={productsData?.results} />
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

            <div className="flex flex-col gap-8">
              <SectionsTop
                title="Возвращенные букеты"
                placeholder="Поиск возвращенных букетов"
                inputValue={factorySearchValue}
                onChange={factoryHandleSearch}
                onClick={factorySubmitSearch}
              />

              <div className="w-full h-full relative flex flex-col gap-3">
                { !factoriesFetching ? (
                  <ReturnsReportsBouquetsTable data={factoriesData?.results} />
                ) : (
                  <SectionTableSkeleton />
                ) }

                <PaginationComponent
                  data={!factoriesError && factoriesData}
                  currentPage={factoryPage}
                  totalPages={factoryTotalPages}
                  setCurrentPage={factorySetCurrentPage}
                  setTotalPages={factorySetTotalPages}
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

export default ReturnsReportsSection