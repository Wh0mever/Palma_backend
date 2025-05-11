/* eslint-disable @typescript-eslint/no-explicit-any */
import SectionsTop from "@/components/others/SectionsTop.tsx"
import useAxiosPost from "@/hooks/useAxiosPost.ts"
import {z} from "zod"
import AddDialog from "@/components/others/AddDialog.tsx"
import AddForm from "@/components/others/AddForm.tsx"
import IncomesTable from "@/components/tables/elements/IncomesTable.tsx"
import IncomesFormFields from "@/components/forms/IncomesFormFields.tsx"
import {Button} from "@/components/ui/button.tsx"
import SectionTableSkeleton from "@/components/skeletons/SectionTableSkeleton.tsx"
import useFilters from "@/hooks/useFilters.ts"
import usePagination from "@/hooks/usePagination.ts"
import PaginationComponent from "@/components/others/PaginationComponent.tsx"
import FiltersBlock from "@/components/others/FiltersBlock.tsx"
import {useEffect, useState} from "react"
import useServerSearch from "@/hooks/useServerSearch.ts"
import useQueryString from "@/hooks/useQueryString.ts"
import useNumberFormatter from "@/hooks/useNumberFormatter.ts"
import {api} from "@/services/api.ts"

const IncomesSection = () => {
  const incomeFilterState = JSON.parse(localStorage.getItem("income") || JSON.stringify({
    "currentPage": "",
    "submittedSearch": "",
    "periodFromFormatted": "",
    "periodToFormatted": "",
    "periodFrom": "",
    "periodTo": "",
    "status": "",
    "provider": "",
  }))

  const {formatter} = useNumberFormatter()
  const {currentPage, setCurrentPage, totalPages, setTotalPages} = usePagination(incomeFilterState)
  const {periodTo, periodFrom, periodFromFormatted, periodToFormatted, setPeriodFrom, setPeriodTo, status, setStatus, provider, setProvider} = useFilters(incomeFilterState)
  const {searchValue, handleSearch, submitSearch, submittedSearch} = useServerSearch(setCurrentPage)

  const queryParams: any = {
    "page": currentPage,
    "search": submittedSearch,
    "start_date": periodFromFormatted !== null ? periodFromFormatted : "",
    "end_date": periodToFormatted !== null ? periodToFormatted : "",
    "status": status !== null && status !== "null" ? status : "",
    "provider": provider !== null && provider !== "null" ? provider : "",
  }

  useEffect(() => {
    localStorage.setItem("income", JSON.stringify({
      "currentPage": currentPage,
      "submittedSearch": submittedSearch,
      "periodFromFormatted": periodFromFormatted,
      "periodToFormatted": periodToFormatted,
      "periodFrom": periodFrom,
      "periodTo": periodTo,
      "status": status,
      "provider": provider,
    }))
  }, [
    currentPage,
    submittedSearch,
    periodFromFormatted,
    periodToFormatted,
    status,
    provider
  ])

  const {queryString: queryStringCollection} = useQueryString(queryParams)
  const [queryString, setQueryString] = useState("")
  const {data, isLoading, isFetching, isError} = api.useGetIncomesQuery({params: queryString})
  const {data: summaryData, isLoading: summaryLoading} = api.useGetIncomesSummaryQuery(queryString)

  const {success, form, onSubmit, pending} = useAxiosPost(
    {
      provider: z.string({required_error: "Пожалуйста, выберите поставщика"}),
      comment: z.string().optional(),
    },
    {},
    "api/incomes/",
    ["Incomes"]
  )

  useEffect(() => {
    setQueryString(queryStringCollection)
  }, [currentPage, submittedSearch])

  return (
    <>
      {isLoading && summaryLoading ? (
        <SectionTableSkeleton/>
      ) : (
        <section className="w-full flex flex-col gap-8">
          <SectionsTop
            title="Закуп"
            placeholder="Поиск закупа"
            inputValue={searchValue}
            onChange={handleSearch}
            onClick={submitSearch}
          />

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-3">
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общая сумма: <span
              className="font-bold">{formatter.format(summaryData?.total_sum)} сум</span></p>
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общее количество закупов: <span className="font-bold">{formatter.format(summaryData?.total_count)} шт</span></p>
          </div>

          <div className="flex items-center justify-center sm:justify-end">
            {!success ? (
              <AddDialog btnText="Добавить закуп" dialogTitle="Добавить закуп" dialogDesc="Заполните все поля чтобы добавить закуп">
                <AddForm
                  form={form}
                  onSubmit={onSubmit}
                  success={success}
                  successDesc="Новый закуп успешно добавлен"
                >
                  <IncomesFormFields form={form}/>
                  <Button className="mt-5" disabled={pending}>Добавить закуп</Button>
                </AddForm>
              </AddDialog>
            ) : null}
          </div>

          <div className="w-full h-full relative flex flex-col gap-3">
            <FiltersBlock
              periodFrom={periodFrom}
              periodTo={periodTo}
              setPeriodFrom={setPeriodFrom}
              setPeriodTo={setPeriodTo}
              setStatus={setStatus}
              setProvider={setProvider}
              status={status}
              provider={provider}
              refetchData={() => setQueryString(queryStringCollection)}
              statusApiUrl={`api/incomes/statuses/`}
              pathName={"income"}
              hasStatus
              hasProvider
            />

            {!isFetching ? (
              <IncomesTable data={data?.results}/>
            ) : (
              <SectionTableSkeleton/>
            )}

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

export default IncomesSection