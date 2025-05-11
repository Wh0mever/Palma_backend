import SectionsTop from '@/components/others/SectionsTop.tsx'
import WriteOffBouquetsTable from '@/components/tables/elements/WriteOffBouquetsTable.tsx'
import SectionTableSkeleton from '@/components/skeletons/SectionTableSkeleton.tsx'
import usePagination from '@/hooks/usePagination.ts'
import useFilters from '@/hooks/useFilters.ts'
import FiltersBlock from '@/components/others/FiltersBlock.tsx'
import PaginationComponent from '@/components/others/PaginationComponent.tsx'
import useServerSearch from '@/hooks/useServerSearch.ts'
import {useEffect, useState} from "react"
import useQueryString from '@/hooks/useQueryString.ts'
import {api} from "@/services/api.ts"
import useNumberFormatter from "@/hooks/useNumberFormatter.ts"
import {Skeleton} from "@/components/ui/skeleton.tsx"

const WriteOffBouquetsSection = () => {
  const writeOffBouquetsFilterState = JSON.parse(localStorage.getItem("writeOffBouquets") || JSON.stringify({
    "currentPage": "",
    "submittedSearch": "",
    "periodFromFormatted": "",
    "periodToFormatted": "",
    "periodFrom": "",
    "periodTo": "",
    "florist": "",
    "factoriesCategory": "",
  }))

  const { formatter } = useNumberFormatter()
  const { currentPage, setCurrentPage, totalPages, setTotalPages } = usePagination(writeOffBouquetsFilterState)
  const { fromTime, toTime, setToTime, setFromTime, periodFromTime, setPeriodFromTime, periodToTime, setPeriodToTime, periodFromTimeFormatted, periodToTimeFormatted, florist, setFlorist, factoriesCategory, setFactoriesCategory } = useFilters(writeOffBouquetsFilterState)
  const { searchValue, handleSearch, submittedSearch, submitSearch } = useServerSearch(setCurrentPage)

  const queryParams: any = {
    'page': currentPage,
    'search': submittedSearch,
    "start_date": periodFromTimeFormatted !== null ? periodFromTimeFormatted : "",
    "end_date": periodToTimeFormatted !== null ? periodToTimeFormatted : "",
    "florist": florist !== null ? florist : "",
    "category": factoriesCategory !== null ? factoriesCategory : "",
  }

  useEffect(() => {
    localStorage.setItem("writeOffBouquets", JSON.stringify({
      "currentPage": currentPage,
      "submittedSearch": submittedSearch,
      "periodFromTimeFormatted": periodFromTimeFormatted,
      "periodToTimeFormatted": periodToTimeFormatted,
      "periodFromTime": periodFromTime,
      "periodToTime": periodToTime,
      "florist": florist,
      "factoriesCategory": factoriesCategory,
    }))
  }, [
    currentPage,
    submittedSearch,
    periodFromTimeFormatted,
    periodToTimeFormatted,
    periodFromTime,
    periodToTime,
    florist,
    factoriesCategory,
  ])

  const { queryString: queryStringCollection } = useQueryString(queryParams)
  const [queryString, setQueryString] = useState('')
  const { data, isLoading, isFetching, isError } = api.useGetWrittenOffFactoriesQuery(queryString)
  const { data: summaryData, isLoading: summaryLoading, isFetching: summaryFetching } = api.useGetWrittenOffFactoriesSummaryQuery(queryString)

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
            title='Списанные букеты'
            placeholder='Поиск списанных букетов'
            inputValue={searchValue}
            onChange={handleSearch}
            onClick={submitSearch}
          />

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
              setFlorist={setFlorist}
              setFactoriesCategory={setFactoriesCategory}
              refetchData={() => setQueryString(queryStringCollection)}
              pathName={'writeOffBouquets'}
              haventPeriods
              hasTimePeriods
              hasFlorist
              hasFactoriesCategory
            />

            { summaryLoading || summaryFetching ? (
              <Skeleton className='w-full h-8' />
            ) : (
              <div className="w-full my-3 flex items-center justify-between gap-3">
                <div className="w-full p-3 text-sm font-semibold rounded-xl bg-neutral-100">
                  Общая себестоимость: {formatter.format(summaryData?.total_self_price)} сум
                </div>
                <div className="w-full p-3 text-sm font-semibold rounded-xl bg-neutral-100">
                  Общее количество: {formatter.format(summaryData?.total_count)} шт
                </div>
              </div>
            )}

            {!isFetching ? (
              <WriteOffBouquetsTable data={data.results}/>
            ) : (
              <SectionTableSkeleton/>
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

export default WriteOffBouquetsSection