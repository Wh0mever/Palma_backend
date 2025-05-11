import TableChartWrapper from "@/components/others/TableChartWrapper.tsx"
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from "@/components/ui/table.tsx"
import useNumberFormatter from "@/hooks/useNumberFormatter.ts"
import {ArcElement, BarElement, CategoryScale, Chart as ChartJS, Legend, LinearScale, LineElement, PointElement, Title, Tooltip} from "chart.js"
import useFilters from "@/hooks/useFilters.ts"
import useQueryString from "@/hooks/useQueryString.ts"
import {api} from "@/services/api.ts"
import {useState} from "react"
import OneChartWrapper from "@/components/others/OneChartWrapper.tsx"
import FiltersBlock from "@/components/others/FiltersBlock.tsx"
import {Bar, Line, Pie} from "react-chartjs-2"
import ClientsChartsSection from "@/components/sections/ClientsChartsSection.tsx"

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

const barOptions = {
  responsive: true,
  indexAxis: 'y' as const,
  elements: {
    bar: {
      borderWidth: 3,
    },
  },
}

const AllChartsSection = () => {
  const chartsFilterState = JSON.parse(localStorage.getItem("charts") || JSON.stringify({
    "profitPeriodTo": "",
    "profitPeriodFrom": "",
    "profitPeriodFromFormatted": "",
    "profitPeriodToFormatted": "",
    "profitByIndustryPeriodTo": "",
    "profitByIndustryPeriodFrom": "",
    "profitByIndustryPeriodFromFormatted": "",
    "profitByIndustryPeriodToFormatted": "",
    "profitByIndustryIndustry": "",
    "productsPeriodTo": "",
    "productsPeriodFrom": "",
    "productsPeriodFromFormatted": "",
    "productsPeriodToFormatted": "",
    "productsIndicator": "",
    "cashierPeriodTo": "",
    "cashierPeriodFrom": "",
    "cashierPeriodFromFormatted": "",
    "cashierPeriodToFormatted": "",
    "productFactorySellsPeriodTo": "",
    "productFactorySellsPeriodFrom": "",
    "productFactorySellsPeriodFromFormatted": "",
    "productFactorySellsPeriodToFormatted": "",
    "industryPeriodTo": "",
    "industryPeriodFrom": "",
    "industryPeriodFromFormatted": "",
    "industryPeriodToFormatted": "",
    "outlaysPeriodTo": "",
    "outlaysPeriodFrom": "",
    "outlaysPeriodFromFormatted": "",
    "outlaysPeriodToFormatted": "",
    "outlaysIndicator": "",
    "turnoverPeriodTo": "",
    "turnoverPeriodFrom": "",
    "turnoverPeriodFromFormatted": "",
    "turnoverPeriodToFormatted": "",
    "writeOffsPeriodTo": "",
    "writeOffsPeriodFrom": "",
    "writeOffsPeriodFromFormatted": "",
    "writeOffsPeriodToFormatted": "",
  }))

  const { formatter } = useNumberFormatter()

  const { periodTo: profitPeriodTo, periodFrom: profitPeriodFrom, periodFromFormatted: profitPeriodFromFormatted, periodToFormatted: profitPeriodToFormatted, setPeriodFrom: profitSetPeriodFrom, setPeriodTo: profitSetPeriodTo } = useFilters(chartsFilterState)
  const { periodTo: profitByIndustryPeriodTo, periodFrom: profitByIndustryPeriodFrom, periodFromFormatted: profitByIndustryPeriodFromFormatted, periodToFormatted: profitByIndustryPeriodToFormatted, setPeriodFrom: profitByIndustrySetPeriodFrom, setPeriodTo: profitByIndustrySetPeriodTo, industry: profitByIndustryIndustry, setIndustry: profitByIndustrySetIndustry } = useFilters(chartsFilterState)
  const { periodTo: productsPeriodTo, periodFrom: productsPeriodFrom, periodFromFormatted: productsPeriodFromFormatted, periodToFormatted: productsPeriodToFormatted, setPeriodFrom: productsSetPeriodFrom, setPeriodTo: productsSetPeriodTo, indicator: productsIndicator, setIndicator: productsSetIndicator } = useFilters(chartsFilterState)
  const { periodTo: cashierPeriodTo, periodFrom: cashierPeriodFrom, periodFromFormatted: cashierPeriodFromFormatted, periodToFormatted: cashierPeriodToFormatted, setPeriodFrom: cashierSetPeriodFrom, setPeriodTo: cashierSetPeriodTo } = useFilters(chartsFilterState)
  const { periodTo: productFactorySellsPeriodTo, periodFrom: productFactorySellsPeriodFrom, periodFromFormatted: productFactorySellsPeriodFromFormatted, periodToFormatted: productFactorySellsPeriodToFormatted, setPeriodFrom: productFactorySellsSetPeriodFrom, setPeriodTo: productFactorySellsSetPeriodTo } = useFilters(chartsFilterState)
  const { periodTo: industryPeriodTo, periodFrom: industryPeriodFrom, periodFromFormatted: industryPeriodFromFormatted, periodToFormatted: industryPeriodToFormatted, setPeriodFrom: industrySetPeriodFrom, setPeriodTo: industrySetPeriodTo } = useFilters(chartsFilterState)
  const { periodTo: outlaysPeriodTo, periodFrom: outlaysPeriodFrom, periodFromFormatted: outlaysPeriodFromFormatted, periodToFormatted: outlaysPeriodToFormatted, setPeriodFrom: outlaysSetPeriodFrom, setPeriodTo: outlaysSetPeriodTo, indicator: outlaysIndicator, setIndicator: outlaysSetIndicator } = useFilters(chartsFilterState)
  const { periodTo: turnoverPeriodTo, periodFrom: turnoverPeriodFrom, periodFromFormatted: turnoverPeriodFromFormatted, periodToFormatted: turnoverPeriodToFormatted, setPeriodFrom: turnoverSetPeriodFrom, setPeriodTo: turnoverSetPeriodTo } = useFilters(chartsFilterState)
  const { periodTo: writeOffsPeriodTo, periodFrom: writeOffsPeriodFrom, periodFromFormatted: writeOffsPeriodFromFormatted, periodToFormatted: writeOffsPeriodToFormatted, setPeriodFrom: writeOffsSetPeriodFrom, setPeriodTo: writeOffsSetPeriodTo } = useFilters(chartsFilterState)

  const profitQueryParams: any = {
    'start_date': profitPeriodFromFormatted !== null ? profitPeriodFromFormatted : '',
    'end_date': profitPeriodToFormatted !== null ? profitPeriodToFormatted : '',
  }

  const profitByIndustryQueryParams: any = {
    'start_date': profitByIndustryPeriodFromFormatted !== null ? profitByIndustryPeriodFromFormatted : '',
    'end_date': profitByIndustryPeriodToFormatted !== null ? profitByIndustryPeriodToFormatted : '',
    'industry': profitByIndustryIndustry !== null && profitByIndustryIndustry !== 'null' ? profitByIndustryIndustry : ''
  }

  const productsQueryParams: any = {
    'start_date': productsPeriodFromFormatted !== null ? productsPeriodFromFormatted : '',
    'end_date': productsPeriodToFormatted !== null ? productsPeriodToFormatted : '',
    'indicator': productsIndicator !== null && productsIndicator !== 'null' ? productsIndicator : ''
  }

  const cashierQueryParams: any = {
    'start_date': cashierPeriodFromFormatted !== null ? cashierPeriodFromFormatted : '',
    'end_date': cashierPeriodToFormatted !== null ? cashierPeriodToFormatted : '',
  }

  const productFactorySellsQueryParams: any = {
    'start_date': productFactorySellsPeriodFromFormatted !== null ? productFactorySellsPeriodFromFormatted : '',
    'end_date': productFactorySellsPeriodToFormatted !== null ? productFactorySellsPeriodToFormatted : '',
  }

  const industryQueryParams: any = {
    'start_date': industryPeriodFromFormatted !== null ? industryPeriodFromFormatted : '',
    'end_date': industryPeriodToFormatted !== null ? industryPeriodToFormatted : '',
  }

  const outlaysQueryParams: any = {
    'start_date': outlaysPeriodFromFormatted !== null ? outlaysPeriodFromFormatted : '',
    'end_date': outlaysPeriodToFormatted !== null ? outlaysPeriodToFormatted : '',
    'indicator': outlaysIndicator !== null && outlaysIndicator !== 'null' ? outlaysIndicator : ''
  }

  const turnoverQueryParams: any = {
    'start_date': turnoverPeriodFromFormatted !== null ? turnoverPeriodFromFormatted : '',
    'end_date': turnoverPeriodToFormatted !== null ? turnoverPeriodToFormatted : '',
  }

  const writeOffsQueryParams: any = {
    'start_date': writeOffsPeriodFromFormatted !== null ? writeOffsPeriodFromFormatted : '',
    'end_date': writeOffsPeriodToFormatted !== null ? writeOffsPeriodToFormatted : '',
  }

  const { queryString: profitQueryStringCollection } = useQueryString(profitQueryParams)
  const { queryString: profitByIndustryQueryStringCollection } = useQueryString(profitByIndustryQueryParams)
  const { queryString: productsQueryStringCollection } = useQueryString(productsQueryParams)
  const { queryString: cashierQueryStringCollection } = useQueryString(cashierQueryParams)
  const { queryString: productFactorySellsQueryStringCollection } = useQueryString(productFactorySellsQueryParams)
  const { queryString: industryQueryStringCollection } = useQueryString(industryQueryParams)
  const { queryString: outlaysQueryStringCollection } = useQueryString(outlaysQueryParams)
  const { queryString: turnoverQueryStringCollection } = useQueryString(turnoverQueryParams)
  const { queryString: writeOffsQueryStringCollection } = useQueryString(writeOffsQueryParams)

  const [profitQueryString, setProfitQueryString] = useState('')
  const [profitByIndustryQueryString, setProfitByIndustryQueryString] = useState('')
  const [productsQueryString, setProductsQueryString] = useState('')
  const [cashierQueryString, setCashierQueryString] = useState('')
  const [productFactorySellsQueryString, setProductFactorySellsQueryString] = useState('')
  const [industryQueryString, setIndustryQueryString] = useState('')
  const [outlaysQueryString, setOutlaysQueryString] = useState('')
  const [turnoverQueryString, setTurnoverQueryString] = useState('')
  const [writeOffsQueryString, setWriteOffsQueryString] = useState('')

  const { data: profitData, isLoading: profitLoading } = api.useGetAnalyticsQuery({ queryString: profitQueryString, item: 'profit' })
  const { data: profitByIndustryData, isLoading: profitByIndustryLoading } = api.useGetAnalyticsQuery({ queryString: profitByIndustryQueryString, item: 'profit-by-industry' })
  const { data: productsData, isLoading: productsLoading } = api.useGetAnalyticsQuery({ queryString: productsQueryString, item: 'products' })
  const { data: cashierData, isLoading: cashierLoading } = api.useGetAnalyticsQuery({ queryString: cashierQueryString, item: 'cashier' })
  const { data: productFactorySellsData, isLoading: productFactorySellsLoading } = api.useGetAnalyticsQuery({ queryString: productFactorySellsQueryString, item: 'products-factory-sells/chart' })
  const { data: productFactorySellsTableData, isLoading: productFactorySellsTableLoading } = api.useGetAnalyticsQuery({ queryString: productFactorySellsQueryString, item: 'products-factory-sells/table' })
  const { data: industryData, isLoading: industryLoading } = api.useGetAnalyticsQuery({ queryString: industryQueryString, item: 'industry-pie-chart/chart' })
  const { data: industryTableData, isLoading: industryTableLoading } = api.useGetAnalyticsQuery({ queryString: industryQueryString, item: 'industry-pie-chart/table' })
  const { data: outlaysData, isLoading: outlaysLoading } = api.useGetAnalyticsQuery({ queryString: outlaysQueryString, item: 'outlays/chart' })
  const { data: outlaysTableData, isLoading: outlaysTableLoading } = api.useGetAnalyticsQuery({ queryString: outlaysQueryString, item: 'outlays/table' })
  const { data: turnoverData, isLoading: turnoverLoading } = api.useGetAnalyticsQuery({ queryString: turnoverQueryString, item: 'turnover-pie-chart/chart' })
  const { data: turnoverTableData, isLoading: turnoverTableLoading } = api.useGetAnalyticsQuery({ queryString: turnoverQueryString, item: 'turnover-pie-chart/table' })
  const { data: writeOffsData, isLoading: writeOffsLoading } = api.useGetAnalyticsQuery({ queryString: writeOffsQueryString, item: 'write-offs/chart' })
  const { data: writeOffsTableData, isLoading: writeOffsTableLoading } = api.useGetAnalyticsQuery({ queryString: writeOffsQueryString, item: 'write-offs/tables' })

  if (profitLoading || profitByIndustryLoading || productsLoading || cashierLoading || productFactorySellsLoading || productFactorySellsTableLoading || industryLoading || outlaysLoading || outlaysTableLoading || turnoverLoading || turnoverTableLoading || writeOffsLoading || writeOffsTableLoading) {
    return <h3>Идет загрузка, подождите...</h3>
  }

  return (
    <>
      <div className='w-full grid grid-cols-1 xl:grid-cols-2 items-center gap-16'>
        <OneChartWrapper title='Прибыль'>
          <FiltersBlock
            periodFrom={profitPeriodFrom}
            periodTo={profitPeriodTo}
            setPeriodFrom={profitSetPeriodFrom}
            setPeriodTo={profitSetPeriodTo}
            refetchData={() => setProfitQueryString(profitQueryStringCollection)}
            pathName={'charts'}
          />
          { !profitLoading ? (
            <Line data={profitData} options={responsiveOptions}/>
          ) : (
            <p>Загрузка...</p>
          ) }
        </OneChartWrapper>

        <OneChartWrapper title='Прибыль по магазинам'>
          <FiltersBlock
            periodFrom={profitByIndustryPeriodFrom}
            periodTo={profitByIndustryPeriodTo}
            setPeriodFrom={profitByIndustrySetPeriodFrom}
            setPeriodTo={profitByIndustrySetPeriodTo}
            setIndustry={profitByIndustrySetIndustry}
            refetchData={() => setProfitByIndustryQueryString(profitByIndustryQueryStringCollection)}
            industry={profitByIndustryIndustry}
            pathName={'charts'}
            hasIndustry
            industryNotMulti
          />
          { !profitByIndustryLoading ? (
            <Line data={profitByIndustryData} options={responsiveOptions}/>
          ) : (
            <p>Загрузка...</p>
          )}
        </OneChartWrapper>

        <OneChartWrapper title='Товары'>
          <FiltersBlock
            periodFrom={productsPeriodFrom}
            periodTo={productsPeriodTo}
            setPeriodFrom={productsSetPeriodFrom}
            setPeriodTo={productsSetPeriodTo}
            setIndicator={productsSetIndicator}
            indicatorApiUrl={`api/analytics/products/options`}
            refetchData={() => setProductsQueryString(productsQueryStringCollection)}
            indicatorValue={productsIndicator}
            pathName={'charts'}
            hasIndicator
          />
          { !productsLoading ? (
            <Line data={productsData} options={responsiveOptions}/>
          ) : (
            <p>Загрузка...</p>
          ) }
        </OneChartWrapper>

        <OneChartWrapper title='Касса'>
          <FiltersBlock
            periodFrom={cashierPeriodFrom}
            periodTo={cashierPeriodTo}
            setPeriodFrom={cashierSetPeriodFrom}
            setPeriodTo={cashierSetPeriodTo}
            refetchData={() => setCashierQueryString(cashierQueryStringCollection)}
            pathName={'charts'}
          />
          { !cashierLoading ? (
            <Line data={cashierData} options={responsiveOptions}/>
          ) : (
            <p>Загрузка...</p>
          ) }
        </OneChartWrapper>
      </div>

      <div className="w-full flex flex-col gap-24">
        <TableChartWrapper>
          <OneChartWrapper title='Продажи букетов'>
            <FiltersBlock
              periodFrom={productFactorySellsPeriodFrom}
              periodTo={productFactorySellsPeriodTo}
              setPeriodFrom={productFactorySellsSetPeriodFrom}
              setPeriodTo={productFactorySellsSetPeriodTo}
              refetchData={() => setProductFactorySellsQueryString(productFactorySellsQueryStringCollection)}
              pathName={'charts'}
            />
            {!productFactorySellsLoading && productFactorySellsData.labels && Array.isArray(productFactorySellsData.labels) && productFactorySellsData.labels?.length !== 0 ? (
              <Bar data={productFactorySellsData} options={barOptions}/>
            ) : (
              <p className='pt-10 pb-10 text-xl text-center font-medium text-neutral-400'>Данные не найдены</p>
            )}
          </OneChartWrapper>

          <Table className='w-full'>
            <TableHeader>
              <TableRow>
                <TableHead>№</TableHead>
                <TableHead>Название</TableHead>
                <TableHead colSpan={2}>Себестоимость (сумма / процент)</TableHead>
                <TableHead colSpan={2}>Начисления сотруднику (сумма / процент)</TableHead>
                <TableHead colSpan={2}>Прибыль (сумма / процент)</TableHead>
              </TableRow>
            </TableHeader>

            <TableBody>
              {!productFactorySellsTableLoading && productFactorySellsTableData && Array.isArray(productFactorySellsTableData) ? productFactorySellsTableData.map((item, index) => (
                <TableRow key={index}>
                  <TableCell>{index + 1}</TableCell>
                  <TableCell>{item.name}</TableCell>
                  <TableCell>{formatter.format(item.self_price?.amount)} сум</TableCell>
                  <TableCell>{formatter.format(item.self_price?.percentage)}%</TableCell>
                  <TableCell>{formatter.format(item.worker_income?.amount)} сум</TableCell>
                  <TableCell>{formatter.format(item.worker_income?.percentage)}%</TableCell>
                  <TableCell>{formatter.format(item.profit?.amount)} сум</TableCell>
                  <TableCell>{formatter.format(item.profit?.percentage)}%</TableCell>
                </TableRow>
              )) : (
                <p>Загрузка...</p>
              )}
            </TableBody>
          </Table>
        </TableChartWrapper>

        <ClientsChartsSection />

        <TableChartWrapper>
          <OneChartWrapper title='Магазины'>
            <FiltersBlock
              periodFrom={industryPeriodFrom}
              periodTo={industryPeriodTo}
              setPeriodFrom={industrySetPeriodFrom}
              setPeriodTo={industrySetPeriodTo}
              refetchData={() => setIndustryQueryString(industryQueryStringCollection)}
              pathName={'charts'}
            />
            {!industryLoading && industryData.labels && Array.isArray(industryData.labels) && industryData.labels?.length !== 0 ? (
              <Pie data={industryData} options={responsiveOptions}/>
            ) : (
              <p className='pt-10 pb-10 text-xl text-center font-medium text-neutral-400'>Данные не найдены</p>
            )}
          </OneChartWrapper>

          <Table className='w-full'>
            <TableHeader>
              <TableRow>
                <TableHead>№</TableHead>
                <TableHead>Название</TableHead>
                <TableHead>Сумма оборота</TableHead>
                <TableHead>Процент</TableHead>
              </TableRow>
            </TableHeader>

            <TableBody>
              {!industryTableLoading && industryTableData && Array.isArray(industryTableData) ? industryTableData.map((item, index) => (
                <TableRow key={index}>
                  <TableCell>{index + 1}</TableCell>
                  <TableCell>{item.name}</TableCell>
                  <TableCell>{formatter.format(item.total_turnover_sum)} сум</TableCell>
                  <TableCell>{formatter.format(item.share_percentage)}%</TableCell>
                </TableRow>
              )) : (
                <p>Загрузка...</p>
              )}
            </TableBody>
          </Table>
        </TableChartWrapper>

        <TableChartWrapper>
          <OneChartWrapper title='Причины расхода'>
            <FiltersBlock
              periodFrom={outlaysPeriodFrom}
              periodTo={outlaysPeriodTo}
              setPeriodFrom={outlaysSetPeriodFrom}
              setPeriodTo={outlaysSetPeriodTo}
              setIndicator={outlaysSetIndicator}
              indicatorApiUrl={`api/analytics/outlays/options/`}
              refetchData={() => setOutlaysQueryString(outlaysQueryStringCollection)}
              indicatorValue={outlaysIndicator}
              pathName={'charts'}
              hasIndicator
            />
            {!outlaysLoading && outlaysData.labels && Array.isArray(outlaysData.labels) && outlaysData.labels?.length !== 0 ? (
              <Pie data={outlaysData} options={responsiveOptions}/>
            ) : (
              <p className='pt-10 pb-10 text-xl text-center font-medium text-neutral-400'>Данные не найдены</p>
            )}
          </OneChartWrapper>

          <div className='w-full flex flex-col gap-4'>
            <h4 className='text-xl font-semibold'>Общая сумма платежей: {formatter.format(outlaysTableData?.total_payments_amount)} сум</h4>

            <Table className='w-full'>
              <TableHeader>
                <TableRow>
                  <TableHead>№</TableHead>
                  <TableHead>Название</TableHead>
                  <TableHead>Сумма платежей</TableHead>
                  <TableHead>Процент</TableHead>
                </TableRow>
              </TableHeader>

              <TableBody>
                {!outlaysTableLoading && outlaysTableData.outlays && Array.isArray(outlaysTableData.outlays) ? outlaysTableData.outlays.map((item: any, index: any) => (
                  <TableRow key={index}>
                    <TableCell>{index + 1}</TableCell>
                    <TableCell>{item.title}</TableCell>
                    <TableCell>{formatter.format(item.payments_amount)} сум</TableCell>
                    <TableCell>{formatter.format(item.payments_percentage)}%</TableCell>
                  </TableRow>
                )) : (
                  <p>Загрузка...</p>
                )}
              </TableBody>
            </Table>
          </div>
        </TableChartWrapper>

        <TableChartWrapper>
          <OneChartWrapper title='Оборот'>
            <FiltersBlock
              periodFrom={turnoverPeriodFrom}
              periodTo={turnoverPeriodTo}
              setPeriodFrom={turnoverSetPeriodFrom}
              setPeriodTo={turnoverSetPeriodTo}
              refetchData={() => setTurnoverQueryString(turnoverQueryStringCollection)}
              pathName={'charts'}
            />
            {!turnoverLoading && turnoverData.labels && Array.isArray(turnoverData.labels) && turnoverData.labels?.length !== 0 ? (
              <Pie data={turnoverData} options={responsiveOptions}/>
            ) : (
              <p className='pt-10 pb-10 text-xl text-center font-medium text-neutral-400'>Данные не найдены</p>
            )}
          </OneChartWrapper>

          <Table className='w-full'>
            <TableHeader>
              <TableRow>
                <TableHead>№</TableHead>
                <TableHead>Название</TableHead>
                <TableHead>Общая сумма</TableHead>
                <TableHead>Процент</TableHead>
              </TableRow>
            </TableHeader>

            <TableBody>
              {!turnoverTableLoading && turnoverTableData && Array.isArray(turnoverTableData) ? turnoverTableData.map((item, index) => (
                <TableRow key={index}>
                  <TableCell>{index + 1}</TableCell>
                  <TableCell>{item.label}</TableCell>
                  <TableCell>{formatter.format(item.total_sum)} сум</TableCell>
                  <TableCell>{formatter.format(item.percentage)}%</TableCell>
                </TableRow>
              )) : (
                <p>Загрузка...</p>
              )}
            </TableBody>
          </Table>
        </TableChartWrapper>

        <TableChartWrapper>
          <OneChartWrapper title='Списания'>
            <FiltersBlock
              periodFrom={writeOffsPeriodFrom}
              periodTo={writeOffsPeriodTo}
              setPeriodFrom={writeOffsSetPeriodFrom}
              setPeriodTo={writeOffsSetPeriodTo}
              refetchData={() => setWriteOffsQueryString(writeOffsQueryStringCollection)}
              pathName={'charts'}
            />
            {!writeOffsLoading && writeOffsData.labels && Array.isArray(writeOffsData.labels) && writeOffsData.labels?.length !== 0 ? (
              <Pie data={writeOffsData} options={responsiveOptions}/>
            ) : (
              <p className='pt-10 pb-10 text-xl text-center font-medium text-neutral-400'>Данные не найдены</p>
            )}
          </OneChartWrapper>

          <div className='w-full flex flex-col gap-10'>
            <Table className='w-full'>
              <TableHeader>
                <TableRow>
                  <TableHead>№</TableHead>
                  <TableHead>Название</TableHead>
                  <TableHead>Общая сумма себестоимости</TableHead>
                  <TableHead>Процент себестоимости</TableHead>
                </TableRow>
              </TableHeader>

              <TableBody>
                {!writeOffsTableLoading && writeOffsTableData && writeOffsTableData.main_table && Array.isArray(writeOffsTableData.main_table) ? writeOffsTableData.main_table.map((item: any, index: any) => (
                  <TableRow key={index}>
                    <TableCell>{index + 1}</TableCell>
                    <TableCell>{item.title}</TableCell>
                    <TableCell>{formatter.format(item.self_price_sum)} сум</TableCell>
                    <TableCell>{formatter.format(item.self_price_percentage)}%</TableCell>
                  </TableRow>
                )) : (
                  <p>Загрузка...</p>
                )}
              </TableBody>
            </Table>

            <Table className='w-full'>
              <TableHeader>
                <TableRow>
                  <TableHead>№</TableHead>
                  <TableHead>Название</TableHead>
                  <TableHead>Количество списаний</TableHead>
                </TableRow>
              </TableHeader>

              <TableBody>
                {!writeOffsTableLoading && writeOffsTableData && writeOffsTableData.count_table && Array.isArray(writeOffsTableData.count_table) ? writeOffsTableData.count_table.map((item: any, index: any) => (
                  <TableRow key={index}>
                    <TableCell>{index + 1}</TableCell>
                    <TableCell>{item.title}</TableCell>
                    <TableCell>{formatter.format(item.write_off_count)} шт</TableCell>
                  </TableRow>
                )) : (
                  <p>Загрузка...</p>
                )}
              </TableBody>
            </Table>

            <Table className='w-full'>
              <TableHeader>
                <TableRow>
                  <TableHead>№</TableHead>
                  <TableHead>Название</TableHead>
                  <TableHead>Сумма</TableHead>
                </TableRow>
              </TableHeader>

              <TableBody>
                {!writeOffsTableLoading && writeOffsTableData && writeOffsTableData.sum_table && Array.isArray(writeOffsTableData.sum_table) ? writeOffsTableData.sum_table.map((item: any, index: any) => (
                  <TableRow key={index}>
                    <TableCell>{index + 1}</TableCell>
                    <TableCell>{item.title}</TableCell>
                    <TableCell>{formatter.format(item.write_off_count)} сум</TableCell>
                  </TableRow>
                )) : (
                  <p>Загрузка...</p>
                )}
              </TableBody>
            </Table>
          </div>
        </TableChartWrapper>
      </div>
    </>
  )
}

export default AllChartsSection