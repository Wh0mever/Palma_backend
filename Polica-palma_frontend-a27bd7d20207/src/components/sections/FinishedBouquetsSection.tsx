import SectionsTop from '@/components/others/SectionsTop.tsx'
import FinishedBouquetsTable from '@/components/tables/elements/FinishedBouquetsTable.tsx'
import SectionTableSkeleton from '@/components/skeletons/SectionTableSkeleton.tsx'
import usePagination from '@/hooks/usePagination.ts'
import useFilters from '@/hooks/useFilters.ts'
import PaginationComponent from '@/components/others/PaginationComponent.tsx'
import FiltersBlock from '@/components/others/FiltersBlock.tsx'
import {useEffect, useState} from "react"
import useServerSearch from '@/hooks/useServerSearch.ts'
import useQueryString from '@/hooks/useQueryString.ts'
// import getUrl from "@/config.ts"
// import {Button} from "@/components/ui/button.tsx"
// import {List} from "lucide-react"
import TableDownload from "@/components/others/TableDownload.tsx"
import {api} from "@/services/api.ts"

const FinishedBouquetsSection = () => {
  const finishedBouquetsFilterState = JSON.parse(localStorage.getItem("finishedBouquets") || JSON.stringify({
    "currentPage": "",
    "submittedSearch": "",
    "periodFromFormatted": "",
    "periodToFormatted": "",
    "periodFrom": "",
    "periodTo": "",
    "factoriesCategory": "",
  }))

  const { currentPage, setCurrentPage, totalPages, setTotalPages } = usePagination(finishedBouquetsFilterState)
  const { periodFrom, periodTo, setPeriodFrom, setPeriodTo, periodFromFormatted, periodToFormatted, factoriesCategory, setFactoriesCategory } = useFilters(finishedBouquetsFilterState)
  const { searchValue, handleSearch, submittedSearch, submitSearch } = useServerSearch(setCurrentPage)

  const queryParams: any = {
    'page': currentPage,
    'search': submittedSearch,
    'start_date': periodFromFormatted !== null ? periodFromFormatted : '',
    'end_date': periodToFormatted !== null ? periodToFormatted : '',
    'category': factoriesCategory !== null ? factoriesCategory : '',
  }

  useEffect(() => {
    localStorage.setItem("finishedBouquets", JSON.stringify({
      "currentPage": currentPage,
      "submittedSearch": submittedSearch,
      "periodFromFormatted": periodFromFormatted,
      "periodToFormatted": periodToFormatted,
      "periodFrom": periodFrom,
      "periodTo": periodTo,
      "factoriesCategory": factoriesCategory
    }))
  }, [
    currentPage,
    submittedSearch,
    periodFromFormatted,
    periodToFormatted,
    periodFrom,
    periodTo,
    factoriesCategory
  ])

  const { queryString: queryStringCollection } = useQueryString(queryParams)
  const [queryString, setQueryString] = useState('')
  const { data, isLoading, isFetching, isError } = api.useGetFinishedFactoriesQuery(queryString)

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
            title='Собранные букеты'
            placeholder='Поиск собранных букетов'
            inputValue={searchValue}
            onChange={handleSearch}
            onClick={submitSearch}
          />

          <TableDownload
            apiUrl={`core/product-factories-export`}
            params={queryString}
          />

          {/*<a href={`${getUrl()}/core/product-factories-print/`} target='_blank' className='flex justify-end'>*/}
          {/*  <Button>*/}
          {/*    <List className='w-4 h-4 mr-2' /> Список собранных букетов*/}
          {/*  </Button>*/}
          {/*</a>*/}

          <div className='w-full h-full relative flex flex-col gap-3'>
            <FiltersBlock
              periodFrom={periodFrom}
              periodTo={periodTo}
              setPeriodFrom={setPeriodFrom}
              setPeriodTo={setPeriodTo}
              setFactoriesCategory={setFactoriesCategory}
              refetchData={() => setQueryString(queryStringCollection)}
              factoriesCategory={factoriesCategory}
              pathName={'finishedBouquets'}
              hasFactoriesCategory
            />

            { !isFetching ? (
              <FinishedBouquetsTable data={data.results} />
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

export default FinishedBouquetsSection