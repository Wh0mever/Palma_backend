import useNumberFormatter from "@/hooks/useNumberFormatter.ts"
import usePagination from "@/hooks/usePagination.ts"
import useFilters from "@/hooks/useFilters.ts"
import SectionTableSkeleton from "@/components/skeletons/SectionTableSkeleton.tsx"
import FiltersBlock from "@/components/others/FiltersBlock.tsx"
import PaginationComponent from "@/components/others/PaginationComponent.tsx"
import ShiftsSectionTable from "@/components/tables/elements/ShiftsSectionTable.tsx"
import {Button} from "@/components/ui/button.tsx"
import {CalendarClock, CalendarOff} from "lucide-react"
import ErrorItem from "@/components/items/ErrorItem.tsx"
import useQueryString from "@/hooks/useQueryString.ts"
import {api} from "@/services/api.ts"

const ShiftsSection = () => {
  const {formatter} = useNumberFormatter()
  const {currentPage, setCurrentPage, totalPages, setTotalPages} = usePagination()
  const {periodFrom, periodTo, setPeriodFrom, setPeriodTo, periodFromFormatted, periodToFormatted, created, setCreated} = useFilters(undefined)

  const queryParams: any = {
    "page": currentPage,
    "start_date": periodFromFormatted !== null ? periodFromFormatted : "",
    "end_date": periodToFormatted !== null ? periodToFormatted : "",
    "created_user": created !== null ? created : "",
  }

  const {queryString} = useQueryString(queryParams)
  const {data, isLoading} = api.useGetShiftReportQuery(queryString)
  const [createShift, {isLoading: openPending, isError: openError, error: openErrorText}] = api.useCreateShiftMutation<any>()
  const [closeShift, {isLoading: closePending, isError: closeError, error: closeErrorText}] = api.useCloseShiftMutation<any>()

  return (
    <>
      {isLoading && !data ? (
        <SectionTableSkeleton/>
      ) : (
        <section className="w-full flex flex-col gap-8">
          <h1 className="text-3xl font-bold">Смена кассы</h1>

          {openError && (
            <ErrorItem title="Ошибка" desc={openErrorText.data?.error}/>
          )}

          {closeError && (
            <ErrorItem title="Ошибка" desc={closeErrorText.data?.error}/>
          )}

          <div className="flex items-center gap-2 justify-end">
            <Button disabled={openPending} onClick={() => createShift({})}>
              <CalendarClock className="w-4 h-4 mr-2"/> Открыть смену
            </Button>

            <Button variant="destructive" disabled={closePending} onClick={() => closeShift({})}>
              <CalendarOff className="w-4 h-4 mr-2"/> Закрыть смену
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общая сумма дохода: <span
              className="font-bold">{formatter.format(data.results?.total_income_sum)} сум</span></p>
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общая сумма расхода: <span
              className="font-bold">{formatter.format(data.results?.total_outcome_sum)} сум</span></p>
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общая сумма прибыли: <span
              className="font-bold">{formatter.format(data.results?.total_profit_sum)} сум</span></p>
          </div>

          <div className="w-full h-full relative flex flex-col gap-3">
            <FiltersBlock
              periodFrom={periodFrom}
              periodTo={periodTo}
              setPeriodFrom={setPeriodFrom}
              setPeriodTo={setPeriodTo}
              setCreated={setCreated}
              createdApiUrl={`api/users/payment-creators`}
              hasCreated
            />
            <ShiftsSectionTable data={data.results?.shifts}/>
            <PaginationComponent
              data={data}
              currentPage={currentPage}
              totalPages={totalPages}
              setCurrentPage={setCurrentPage}
              setTotalPages={setTotalPages}
            />
          </div>
        </section>
      )}
    </>
  )
}

export default ShiftsSection