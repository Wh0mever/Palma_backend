import DashboardLayout from '@/components/elements/DashboardLayout.tsx'
import {useNavigate, useParams} from 'react-router-dom'
import {Button} from '@/components/ui/button.tsx'
import {ChevronLeft} from 'lucide-react'
import EditSectionSkeleton from '@/components/skeletons/EditSectionSkeleton.tsx'
import formatPhoneNumber from '@/helpers/formatPhoneNumber.ts'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import ClientsReportsEditTable from '@/components/tables/elements/ClientsReportsEditTable.tsx'
import SectionsTop from '@/components/others/SectionsTop.tsx'
import usePagination from '@/hooks/usePagination.ts'
import PaginationComponent from '@/components/others/PaginationComponent.tsx'
import useFilters from '@/hooks/useFilters.ts'
import FiltersBlock from '@/components/others/FiltersBlock.tsx'
import useServerSearch from '@/hooks/useServerSearch.ts'
import {useEffect, useState} from "react"
import useQueryString from '@/hooks/useQueryString.ts'
import {api} from "@/services/api.ts"
import SectionTableSkeleton from "@/components/skeletons/SectionTableSkeleton.tsx"

const ClientsReportsEditPage = () => {
  const clientsReportsEditFilterState = JSON.parse(localStorage.getItem("clientsReportsEdit") || JSON.stringify({
    "currentPage": "",
    "submittedSearch": "",
    "periodFromFormatted": "",
    "periodToFormatted": "",
    "periodFrom": "",
    "periodTo": "",
    "industry": "",
  }))

  const { id } = useParams()
  const navigate = useNavigate()
  const { formatter } = useNumberFormatter()
  const { periodTo, periodFrom, periodFromFormatted, periodToFormatted, setPeriodFrom, setPeriodTo, industry, setIndustry } = useFilters(clientsReportsEditFilterState)
  const { currentPage, setCurrentPage, totalPages, setTotalPages } = usePagination(clientsReportsEditFilterState)
  const { searchValue, handleSearch, submittedSearch, submitSearch } = useServerSearch(setCurrentPage)

  const queryParams: any = {
    'start_date': periodFromFormatted !== null ? periodFromFormatted : '',
    'end_date': periodToFormatted !== null ? periodToFormatted : '',
    'industry': industry !== null && industry !== 'null' ? industry : ''
  }

  const ordersQueryParams: any = {
    'page': currentPage,
    'search': submittedSearch,
    'start_date': periodFromFormatted !== null ? periodFromFormatted : '',
    'end_date': periodToFormatted !== null ? periodToFormatted : '',
    'industry': industry !== null && industry !== 'null' ? industry : ''
  }

  useEffect(() => {
    localStorage.setItem("clientsReportsEdit", JSON.stringify({
      "currentPage": currentPage,
      "submittedSearch": submittedSearch,
      "periodFromFormatted": periodFromFormatted,
      "periodToFormatted": periodToFormatted,
      "periodFrom": periodFrom,
      "periodTo": periodTo,
      "industry": industry,
    }))
  }, [
    currentPage,
    submittedSearch,
    periodFromFormatted,
    periodToFormatted,
    periodFrom,
    periodTo,
    industry
  ])

  const { queryString: queryStringCollection } = useQueryString(queryParams)
  const { queryString: ordersQueryStringCollection } = useQueryString(ordersQueryParams)

  const [queryString, setQueryString] = useState('')
  const [ordersQueryString, setOrdersQueryString] = useState('')

  const { data, isLoading } = api.useGetClientsReportsQuery({ queryString: queryString, id: id })
  const { data: clientsOrdersData, isLoading: clientsOrdersLoading, isFetching: clientsOrdersFetching, isError: clientsOrdersError } = api.useGetClientsReportsOrdersQuery({ queryString: ordersQueryString, id: id })

  useEffect(() => {
    setQueryString(queryStringCollection)
    setOrdersQueryString(ordersQueryStringCollection)
  }, [currentPage, submittedSearch])

  return (
    <>
      <DashboardLayout>
        { !isLoading && !clientsOrdersLoading && data ? (
          <section className='w-full flex flex-col gap-8'>
            <Button className='w-48' variant='outline' onClick={() => navigate(-1)}>
              <ChevronLeft className='w-4 h-4 mr-2' /> Вернуться назад
            </Button>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3 text-sm">
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Имя клиента: <span
                className="font-bold">{data?.full_name}</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Номер телефона: <span
                className="font-bold">{data?.phone_number !== null && data?.phone_number !== undefined ? formatPhoneNumber(data?.phone_number) : '-'}</span>
              </p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Количество покупок: <span
                className="font-bold">{formatter.format(data?.orders_count)}</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Сумма покупок: <span
                className="font-bold">{formatter.format(data?.orders_sum)} сум</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Долг: <span
                className="font-bold">{formatter.format(data?.debt)} сум</span></p>
              <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общая сумма скидки: <span
                className="font-bold">{formatter.format(data?.total_discount_sum)} сум</span></p>
            </div>

            <SectionsTop
              title="Покупки"
              placeholder="Поиск покупок"
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
                refetchData={() => {
                  setQueryString(queryStringCollection)
                  setOrdersQueryString(ordersQueryStringCollection)
                }}
                industry={industry}
                pathName={'clientsReportsEdit'}
                hasIndustry
              />

              { !clientsOrdersFetching ? (
                <ClientsReportsEditTable data={clientsOrdersData?.results} />
              ) : (
                <SectionTableSkeleton />
              ) }

              <PaginationComponent
                data={!clientsOrdersError && clientsOrdersData}
                currentPage={currentPage}
                totalPages={totalPages}
                setCurrentPage={setCurrentPage}
                setTotalPages={setTotalPages}
                refetchData={() => setOrdersQueryString(ordersQueryStringCollection)}
              />
            </div>
          </section>
        ) : (
          <EditSectionSkeleton />
        ) }
      </DashboardLayout>
    </>
  )
}

export default ClientsReportsEditPage