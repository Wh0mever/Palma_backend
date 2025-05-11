import useFilters from "@/hooks/useFilters.ts"
import {useEffect, useState} from "react"
import useQueryString from "@/hooks/useQueryString.ts"
import {api} from "@/services/api.ts"
import SectionTableSkeleton from "@/components/skeletons/SectionTableSkeleton.tsx"
import useNumberFormatter from "@/hooks/useNumberFormatter.ts"
import FiltersBlock from "@/components/others/FiltersBlock.tsx"

const OverallReportsSection = () => {
  const overallReportsFilterState = JSON.parse(localStorage.getItem("overallReports") || JSON.stringify({
    "periodFromTimeFormatted": "",
    "periodToTimeFormatted": "",
    "periodFromTime": "",
    "periodToTime": "",
    "industry": "",
    "client": "",
  }))

  const { formatter } = useNumberFormatter()
  const { fromTime, toTime, setToTime, setFromTime, periodFromTime, setPeriodFromTime, periodToTime, setPeriodToTime, periodFromTimeFormatted, periodToTimeFormatted, industry, setIndustry, client, setClient } = useFilters(overallReportsFilterState)

  const queryParams: any = {
    'start_date': periodFromTimeFormatted !== null ? periodFromTimeFormatted : '',
    'end_date': periodToTimeFormatted !== null ? periodToTimeFormatted : '',
    'industry': industry !== null && industry !== 'null' ? industry : '',
    'client': client !== null && client !== 'null' ? client : '',
  }

  useEffect(() => {
    localStorage.setItem("overallReports", JSON.stringify({
      "periodFromTimeFormatted": periodFromTimeFormatted,
      "periodToTimeFormatted": periodToTimeFormatted,
      "periodFromTime": periodFromTime,
      "periodToTime": periodToTime,
      "industry": industry,
      "client": client,
    }))
  }, [
    periodFromTimeFormatted,
    periodToTimeFormatted,
    periodFromTime,
    periodToTime,
    industry,
    client
  ])

  const { queryString: queryStringCollection } = useQueryString(queryParams)
  const [queryString, setQueryString] = useState('')
  const { data, isLoading } = api.useGetOverallReportQuery(queryString)

  return (
    <>
      { isLoading ? (
        <SectionTableSkeleton />
      ) : (
        <section className="w-full flex flex-col gap-8">
          <h1 className="text-3xl font-bold">Общий отчет</h1>

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3 text-sm">
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общая сумма продаж: <span className="font-bold">{formatter.format(data?.total_sale_sum)} сум</span></p>
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общая сумма себестоимости: <span className="font-bold">{formatter.format(data?.total_self_price_sum)} сум</span></p>
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общая сумма расхода: <span className="font-bold">{formatter.format(data?.outlay_total_sum)} сум</span></p>
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общая сумма прибыли: <span className="font-bold">{formatter.format(data?.total_profit_sum)} сум</span></p>
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общая сумма долга: <span className="font-bold">{formatter.format(data?.total_debt_sum)} сум</span></p>
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общая сумма списаний: <span className="font-bold">{formatter.format(data?.total_write_off_sum)} сум</span></p>
            <p className="px-4 py-2 bg-neutral-100/70 rounded-lg font-medium">Общая сумма начислений сотрудникам: <span className="font-bold">{formatter.format(data?.worker_incomes_sum)} сум</span></p>
          </div>

          <FiltersBlock
            fromTime={fromTime}
            toTime={toTime}
            periodFromTime={periodFromTime}
            periodToTime={periodToTime}
            setFromTime={setFromTime}
            setToTime={setToTime}
            setPeriodFromTime={setPeriodFromTime}
            setPeriodToTime={setPeriodToTime}
            setIndustry={setIndustry}
            setClients={setClient}
            refetchData={() => setQueryString(queryStringCollection)}
            industry={industry}
            client={client}
            pathName={'overallReports'}
            hasIndustry
            hasClients
            haventPeriods
            hasTimePeriods
          />
        </section>
      )}
    </>
  )
}

export default OverallReportsSection