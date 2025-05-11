/* eslint-disable @typescript-eslint/no-explicit-any */
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  BarElement,
  ArcElement,
} from 'chart.js'
import DashboardLayout from '@/components/elements/DashboardLayout.tsx'
import getUserData from "@/helpers/getUserData.ts"
import OneChartWrapper from "@/components/others/OneChartWrapper.tsx"
import useFilters from "@/hooks/useFilters.ts"
import useQueryString from "@/hooks/useQueryString.ts"
import FiltersBlock from "@/components/others/FiltersBlock.tsx"
import { Line } from "react-chartjs-2"
import {api} from "@/services/api.ts"
import {useState} from "react"
import {Button} from "@/components/ui/button.tsx"
import {AreaChart} from "lucide-react"
import AllChartsSection from "@/components/sections/AllChartsSection.tsx"

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  BarElement,
  ArcElement,
)

const responsiveOptions = {
  responsive: true
}

const DashboardPage = () => {
  const chartsFilterState = JSON.parse(localStorage.getItem("charts") || JSON.stringify({
    "floristsPeriodTo": "",
    "floristsPeriodFrom": "",
    "floristsPeriodFromFormatted": "",
    "floristsPeriodToFormatted": "",
    "floristsIndicator": "",
    "salesmanPeriodTo": "",
    "salesmanPeriodFrom": "",
    "salesmanPeriodFromFormatted": "",
    "salesmanPeriodToFormatted": "",
    "salesmanIndicator": "",
  }))

  const { userType } = getUserData()
  const [showCharts, setShowCharts] = useState(false)
  const { periodTo: floristsPeriodTo, periodFrom: floristsPeriodFrom, periodFromFormatted: floristsPeriodFromFormatted, periodToFormatted: floristsPeriodToFormatted, setPeriodFrom: floristsSetPeriodFrom, setPeriodTo: floristsSetPeriodTo, indicator: floristsIndicator, setIndicator: floristsSetIndicator } = useFilters(chartsFilterState)
  const { periodTo: salesmanPeriodTo, periodFrom: salesmanPeriodFrom, periodFromFormatted: salesmanPeriodFromFormatted, periodToFormatted: salesmanPeriodToFormatted, setPeriodFrom: salesmanSetPeriodFrom, setPeriodTo: salesmanSetPeriodTo, indicator: salesmanIndicator, setIndicator: salesmanSetIndicator } = useFilters(chartsFilterState)

  const floristsQueryParams: any = {
    'start_date': floristsPeriodFromFormatted !== null ? floristsPeriodFromFormatted : '',
    'end_date': floristsPeriodToFormatted !== null ? floristsPeriodToFormatted : '',
    'indicator': floristsIndicator !== null && floristsIndicator !== 'null' ? floristsIndicator : ''
  }

  const salesmanQueryParams: any = {
    'start_date': salesmanPeriodFromFormatted !== null ? salesmanPeriodFromFormatted : '',
    'end_date': salesmanPeriodToFormatted !== null ? salesmanPeriodToFormatted : '',
    'indicator': salesmanIndicator !== null && salesmanIndicator !== 'null' ? salesmanIndicator : ''
  }

  const { queryString: floristsQueryStringCollection } = useQueryString(floristsQueryParams)
  const { queryString: salesmanQueryStringCollection } = useQueryString(salesmanQueryParams)

  const [floristsQueryString, setFloristsQueryString] = useState('')
  const [salesmanQueryString, setSalesmanQueryString] = useState('')

  const { data: floristsData, isLoading: floristsLoading } = api.useGetAnalyticsQuery({ queryString: floristsQueryString, item: 'florists' })
  const { data: salesmanData, isLoading: salesmanLoading } = api.useGetAnalyticsQuery({ queryString: salesmanQueryString, item: 'salesmen' })

  const handleShowCharts = () => setShowCharts((prev) => !prev)

  return (
    <>
      <DashboardLayout>
        <>
          { userType === 'ADMIN' && (
            <section className="w-full flex flex-col gap-20">
              <div className='w-full grid grid-cols-1 xl:grid-cols-2 items-center gap-16'>
                <OneChartWrapper title='Флористы'>
                  <FiltersBlock
                    periodFrom={floristsPeriodFrom}
                    periodTo={floristsPeriodTo}
                    setPeriodFrom={floristsSetPeriodFrom}
                    setPeriodTo={floristsSetPeriodTo}
                    setIndicator={floristsSetIndicator}
                    indicatorApiUrl={`api/analytics/florists/options`}
                    refetchData={() => setFloristsQueryString(floristsQueryStringCollection)}
                    indicatorValue={floristsIndicator}
                    pathName={'charts'}
                    hasIndicator
                  />
                  { !floristsLoading ? (
                    <Line data={floristsData} options={responsiveOptions}/>
                  ) : (
                    <p>Загрузка...</p>
                  ) }
                </OneChartWrapper>

                <OneChartWrapper title='Продавцы'>
                  <FiltersBlock
                    periodFrom={salesmanPeriodFrom}
                    periodTo={salesmanPeriodTo}
                    setPeriodFrom={salesmanSetPeriodFrom}
                    setPeriodTo={salesmanSetPeriodTo}
                    setIndicator={salesmanSetIndicator}
                    indicatorApiUrl={`api/analytics/salesmen/options`}
                    refetchData={() => setSalesmanQueryString(salesmanQueryStringCollection)}
                    indicatorValue={salesmanIndicator}
                    pathName={'charts'}
                    hasIndicator
                  />
                  { !salesmanLoading ? (
                    <Line data={salesmanData} options={responsiveOptions}/>
                  ) : (
                    <p>Загрузка...</p>
                  ) }
                </OneChartWrapper>
              </div>

              { showCharts && (
                <AllChartsSection />
              ) }

              <div className="pb-3 flex justify-center">
                <Button className="w-max" onClick={handleShowCharts}>
                  <AreaChart className="mr-2 w-4 h-4" />
                  { showCharts ? 'Скрыть графики' : 'Показать все графики' }
                </Button>
              </div>
            </section>
          )}
        </>
      </DashboardLayout>
    </>
  )
}

export default DashboardPage