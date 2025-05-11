import SectionsTop from '@/components/others/SectionsTop.tsx'
import WriteOffTable from '@/components/tables/elements/WriteOffTable.tsx'
import SectionTableSkeleton from '@/components/skeletons/SectionTableSkeleton.tsx'
import usePagination from '@/hooks/usePagination.ts'
import useFilters from '@/hooks/useFilters.ts'
import FiltersBlock from '@/components/others/FiltersBlock.tsx'
import PaginationComponent from '@/components/others/PaginationComponent.tsx'
import useServerSearch from '@/hooks/useServerSearch.ts'
import {useEffect, useState} from "react"
import useQueryString from '@/hooks/useQueryString.ts'
import {api} from "@/services/api.ts"

const WriteOffSection = () => {
  const writeOffFilterState = JSON.parse(localStorage.getItem("writeOff") || JSON.stringify({
    "currentPage": "",
    "submittedSearch": "",
    "periodFromFormatted": "",
    "periodToFormatted": "",
    "periodFrom": "",
    "periodTo": "",
    "industry": "",
    "productsCategory": "",
  }))

  const { currentPage, setCurrentPage, totalPages, setTotalPages } = usePagination(writeOffFilterState)
  const { periodFrom, periodTo, setPeriodFrom, setPeriodTo, periodFromFormatted, periodToFormatted, industry, setIndustry, productsCategory, setProductsCategory } = useFilters(writeOffFilterState)
  const { searchValue, handleSearch, submittedSearch, submitSearch } = useServerSearch(setCurrentPage)

  const queryParams: any = {
    'page': currentPage,
    'search': submittedSearch,
    'start_date': periodFromFormatted !== null ? periodFromFormatted : '',
    'end_date': periodToFormatted !== null ? periodToFormatted : '',
    'industry': industry !== null && industry !== 'null' ? industry : '',
    'category': productsCategory !== null && productsCategory !== 'null' ? productsCategory : ''
  }

  useEffect(() => {
    localStorage.setItem("writeOff", JSON.stringify({
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
  const { data, isLoading, isFetching, isError } = api.useGetWriteOffsQuery(queryString)

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
            title='Списанные товары'
            placeholder='Поиск списанных товаров'
            inputValue={searchValue}
            onChange={handleSearch}
            onClick={submitSearch}
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
              pathName={'writeOff'}
              hasIndustry
              hasProductsCategory
            />

            { !isFetching ? (
              <WriteOffTable data={data && data?.results} />
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

export default WriteOffSection