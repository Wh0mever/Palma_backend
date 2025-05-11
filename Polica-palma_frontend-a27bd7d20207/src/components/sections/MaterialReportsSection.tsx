import SectionsTop from '@/components/others/SectionsTop.tsx'
import SectionTableSkeleton from '@/components/skeletons/SectionTableSkeleton.tsx'
import MaterialReportsTable from '@/components/tables/elements/MaterialReportsTable.tsx'
import usePagination from '@/hooks/usePagination.ts'
import PaginationComponent from '@/components/others/PaginationComponent.tsx'
import useFilters from '@/hooks/useFilters.ts'
import FiltersBlock from '@/components/others/FiltersBlock.tsx'
import TableDownload from '@/components/others/TableDownload.tsx'
import useServerSearch from '@/hooks/useServerSearch.ts'
import {useEffect, useState} from "react"
import useQueryString from '@/hooks/useQueryString.ts'
import {api} from "@/services/api.ts"

const MaterialReportsSection = () => {
  const materialReportsFilterState = JSON.parse(localStorage.getItem("materialReports") || JSON.stringify({
    "currentPage": "",
    "submittedSearch": "",
    "periodFromFormatted": "",
    "periodToFormatted": "",
    "periodFrom": "",
    "periodTo": "",
    "industry": "",
    "productsCategory": "",
  }))

  const { periodTo, periodFrom, periodFromFormatted, periodToFormatted, setPeriodFrom, setPeriodTo, industry, setIndustry, productsCategory, setProductsCategory } = useFilters(materialReportsFilterState)
  const { currentPage, setCurrentPage, totalPages, setTotalPages } = usePagination(materialReportsFilterState)
  const { searchValue, handleSearch, submittedSearch, submitSearch } = useServerSearch(setCurrentPage)

  const queryParams: any = {
    'page': currentPage,
    'search': submittedSearch,
    'start_date': periodFromFormatted !== null ? periodFromFormatted : '',
    'end_date': periodToFormatted !== null ? periodToFormatted : '',
    'industry': industry !== null && industry !== 'null' ? industry : '',
    'category': productsCategory !== null && productsCategory !== 'null' ? productsCategory : '',
  }

  useEffect(() => {
    localStorage.setItem("materialReports", JSON.stringify({
      "currentPage": currentPage,
      "submittedSearch": submittedSearch,
      "periodFromFormatted": periodFromFormatted,
      "periodToFormatted": periodToFormatted,
      "periodFrom": periodFrom,
      "periodTo": periodTo,
      "industry": industry,
      "productsCategory": productsCategory,
    }))
  }, [
    currentPage,
    submittedSearch,
    periodFromFormatted,
    periodToFormatted,
    periodFrom,
    periodTo,
    industry,
    productsCategory
  ])

  const { queryString: queryStringCollection } = useQueryString(queryParams)
  const [queryString, setQueryString] = useState('')
  const { data, isLoading, isFetching, isError } = api.useGetMaterialReportsQuery({ queryString: queryString })

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
            title='Материальный отчет'
            placeholder='Поиск отчетов'
            inputValue={searchValue}
            onChange={handleSearch}
            onClick={submitSearch}
          />

          <TableDownload
            apiUrl={`api/reports/material-report/excel-export`}
            params={queryString}
          />

          <div className='w-full h-full relative flex flex-col gap-3'>
            <FiltersBlock
              periodFrom={periodFrom}
              periodTo={periodTo}
              setPeriodFrom={setPeriodFrom}
              setPeriodTo={setPeriodTo}
              setIndustry={setIndustry}
              setProductsCategory={setProductsCategory}
              refetchData={() => setQueryString(queryStringCollection)}
              industry={industry}
              productsCategory={productsCategory}
              pathName={'materialReports'}
              hasIndustry
              hasProductsCategory
            />

            { !isFetching ? (
              <MaterialReportsTable data={data?.results?.products} />
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

export default MaterialReportsSection