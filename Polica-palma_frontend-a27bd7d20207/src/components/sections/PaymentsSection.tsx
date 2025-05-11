import SectionsTop from '@/components/others/SectionsTop.tsx'
import PaymentsTable from '@/components/tables/elements/PaymentsTable.tsx'
import SectionTableSkeleton from '@/components/skeletons/SectionTableSkeleton.tsx'
import useFilters from '@/hooks/useFilters.ts'
import FiltersBlock from '@/components/others/FiltersBlock.tsx'
import PaginationComponent from '@/components/others/PaginationComponent.tsx'
import usePagination from '@/hooks/usePagination.ts'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import useServerSearch from '@/hooks/useServerSearch.ts'
import {useEffect, useState} from "react"
import useQueryString from '@/hooks/useQueryString.ts'
import {api} from "@/services/api.ts"

const PaymentsSection = () => {
  const paymentsFilterState = JSON.parse(localStorage.getItem("payments") || JSON.stringify({
    "currentPage": "",
    "submittedSearch": "",
    "periodFromFormatted": "",
    "periodToFormatted": "",
    "periodFrom": "",
    "periodTo": "",
    "paymentType": "",
    "paymentModelType": "",
    "paymentMethod": "",
    "outlay": "",
    "created": "",
    "worker": "",
    "isDebt": "",
  }))

  const { formatter } = useNumberFormatter()
  const { currentPage, setCurrentPage, totalPages, setTotalPages } = usePagination(paymentsFilterState)
  const { periodFrom, periodTo, setPeriodFrom, setPeriodTo, periodFromFormatted, periodToFormatted, paymentType, setPaymentType, paymentModelType, setPaymentModelType, paymentMethod, setPaymentMethod, outlay, setOutlay, created, setCreated, worker, setWorker, isDebt, setIsDebt } = useFilters(paymentsFilterState)
  const { searchValue, handleSearch, submitSearch, submittedSearch } = useServerSearch(setCurrentPage)

  const queryParams: any = {
    'page': currentPage,
    'search': submittedSearch,
    'start_date': periodFromFormatted !== null ? periodFromFormatted : '',
    'end_date': periodToFormatted !== null ? periodToFormatted : '',
    'outlay': outlay !== null ? outlay : '',
    'created_user': created !== null ? created : '',
    'worker': worker !== null ? worker : '',
    'payment_method': paymentMethod !== null && paymentMethod !== 'null' ? paymentMethod : '',
    'payment_type': paymentType !== null && paymentType !== 'null' ? paymentType : '',
    'payment_model_type': paymentModelType !== null && paymentModelType !== 'null' ? paymentModelType : '',
    'is_debt': isDebt !== null && isDebt !== 'null' ? isDebt : '',
  }

  useEffect(() => {
    localStorage.setItem("payments", JSON.stringify({
      "currentPage": currentPage,
      "submittedSearch": submittedSearch,
      "periodFromFormatted": periodFromFormatted,
      "periodToFormatted": periodToFormatted,
      "periodFrom": periodFrom,
      "periodTo": periodTo,
      "paymentType": paymentType,
      "paymentModelType": paymentModelType,
      "paymentMethod": paymentMethod,
      "outlay": outlay,
      "created": created,
      "worker": worker,
      "isDebt": isDebt,
    }))
  }, [
    currentPage,
    submittedSearch,
    periodFromFormatted,
    periodToFormatted,
    periodFrom,
    periodTo,
    paymentType,
    paymentModelType,
    paymentMethod,
    outlay,
    created,
    worker,
    isDebt
  ])

  const { queryString: queryStringCollection } = useQueryString(queryParams)
  const [queryString, setQueryString] = useState('')
  const { data, isLoading, isFetching, isError } = api.useGetPaymentsWithSummaryQuery(queryString)

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
            title='Платежи'
            placeholder='Поиск платежей'
            inputValue={searchValue}
            onChange={handleSearch}
            onClick={submitSearch}
          />

          <div className='grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3'>
            <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Общая сумма дохода: <span
              className='font-bold'>{formatter.format(data.results?.total_income)} сум</span></p>
            <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Общая сумма расхода: <span
              className='font-bold'>{formatter.format(data.results?.total_outcome)} сум</span></p>
            <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Общая сумма прибыли: <span
              className='font-bold'>{formatter.format(data.results?.total_profit)} сум</span></p>
            <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Общее количество платежей: <span
              className='font-bold'>{formatter.format(data.results?.total_count)} шт</span></p>
          </div>

          <div className='w-full h-full relative flex flex-col gap-3'>
            <FiltersBlock
              periodFrom={periodFrom}
              periodTo={periodTo}
              setPeriodFrom={setPeriodFrom}
              setPeriodTo={setPeriodTo}
              setPaymentType={setPaymentType}
              setPaymentMethod={setPaymentMethod}
              setPaymentModelType={setPaymentModelType}
              setOutlay={setOutlay}
              setCreated={setCreated}
              setWorker={setWorker}
              setIsDebt={setIsDebt}
              createdApiUrl={`api/users/payment-creators`}
              refetchData={() => setQueryString(queryStringCollection)}
              paymentType={paymentType}
              paymentModelType={paymentModelType}
              paymentMethod={paymentMethod}
              outlay={outlay}
              created={created}
              worker={worker}
              isDebt={isDebt}
              pathName={'payments'}
              hasPaymentType
              hasPaymentMethod
              hasPaymentModelType
              hasOutlay
              hasCreated
              hasWorker
              hasIsDebt
            />

            { !isFetching ? (
              <PaymentsTable data={data?.results?.payments} />
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

export default PaymentsSection