import SectionsTop from '@/components/others/SectionsTop.tsx'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import SectionTableSkeleton from '@/components/skeletons/SectionTableSkeleton.tsx'
import ClientsReportsTable from '@/components/tables/elements/ClientsReportsTable.tsx'
import usePagination from '@/hooks/usePagination.ts'
import PaginationComponent from '@/components/others/PaginationComponent.tsx'
import useFilters from '@/hooks/useFilters.ts'
import FiltersBlock from '@/components/others/FiltersBlock.tsx'
import TableDownload from '@/components/others/TableDownload.tsx'
import useServerSearch from '@/hooks/useServerSearch.ts'
import {useEffect, useState} from "react"
import useQueryString from '@/hooks/useQueryString.ts'
import {api} from "@/services/api.ts"

const ClientsReportsSection = () => {
  const clientsReportsFilterState = JSON.parse(localStorage.getItem("clientsReports") || JSON.stringify({
    "currentPage": "",
    "submittedSearch": "",
    "periodFromFormatted": "",
    "periodToFormatted": "",
    "periodFrom": "",
    "periodTo": "",
    "hasDebt": "",
  }))

  const { formatter } = useNumberFormatter()
  const { periodTo, periodFrom, periodFromFormatted, periodToFormatted, setPeriodFrom, setPeriodTo, hasDebt, setHasDebt } = useFilters(clientsReportsFilterState)
  const { currentPage, setCurrentPage, totalPages, setTotalPages } = usePagination(clientsReportsFilterState)
  const { searchValue, handleSearch, submitSearch, submittedSearch } = useServerSearch(setCurrentPage)

  const queryParams: any = {
    'page': currentPage,
    'search': submittedSearch,
    'start_date': periodFromFormatted !== null ? periodFromFormatted : '',
    'end_date': periodToFormatted !== null ? periodToFormatted : '',
    'has_debt': hasDebt !== null ? hasDebt : '',
  }

  useEffect(() => {
    localStorage.setItem("clientsReports", JSON.stringify({
      "currentPage": currentPage,
      "submittedSearch": submittedSearch,
      "periodFromFormatted": periodFromFormatted,
      "periodToFormatted": periodToFormatted,
      "periodFrom": periodFrom,
      "periodTo": periodTo,
      "hasDebt": hasDebt,
    }))
  }, [
    currentPage,
    submittedSearch,
    periodFromFormatted,
    periodToFormatted,
    periodFrom,
    periodTo,
    hasDebt
  ])

  const { queryString: queryStringCollection } = useQueryString(queryParams)
  const [queryString, setQueryString] = useState('')
  const { data, isLoading, isFetching, isError } = api.useGetClientsReportsQuery({ queryString: queryString })

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
            title='Отчеты по клиентам'
            placeholder='Поиск клиентов'
            inputValue={searchValue}
            onChange={handleSearch}
            onClick={submitSearch}
          />

          <div className='flex items-center justify-between gap-5 max-[960px]:grid max-[960px]:grid-cols-2 max-[960px]:gap-2 max-[690px]:grid-cols-1'>
            <p className='px-4 py-2 bg-neutral-100/70 rounded-lg text-lg font-medium max-[1440px]:text-base'>Общая сумма: <span className='font-bold'>{formatter.format(data.results?.total_orders_sum)} сум</span></p>
            <p className='px-4 py-2 bg-neutral-100/70 rounded-lg text-lg font-medium max-[1440px]:text-base'>Общее количество покупок: <span className='font-bold'>{formatter.format(data.results?.total_orders_count)}</span></p>
            <p className='px-4 py-2 bg-neutral-100/70 rounded-lg text-lg font-medium max-[1440px]:text-base'>Общий долг: <span className='font-bold'>{formatter.format(data.results?.total_debt)} сум</span></p>
          </div>

          <TableDownload
            apiUrl={`api/reports/clients-report/export-excel`}
            params={queryString}
          />

          <div className='w-full h-full relative flex flex-col gap-3'>
            <FiltersBlock
              periodFrom={periodFrom}
              periodTo={periodTo}
              setPeriodFrom={setPeriodFrom}
              setPeriodTo={setPeriodTo}
              refetchData={() => setQueryString(queryStringCollection)}
              setHasDebt={setHasDebt}
              hasDebtValue={hasDebt}
              pathName={'clientsReports'}
              hasDebt
            />

            { !isFetching ? (
              <ClientsReportsTable data={data.results?.clients} />
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

export default ClientsReportsSection