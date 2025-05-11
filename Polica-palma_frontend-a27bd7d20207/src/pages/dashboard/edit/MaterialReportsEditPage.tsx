import DashboardLayout from '@/components/elements/DashboardLayout.tsx'
import {useNavigate, useParams} from 'react-router-dom'
import {ChevronLeft} from 'lucide-react'
import {Button} from '@/components/ui/button.tsx'
import EditSectionSkeleton from '@/components/skeletons/EditSectionSkeleton.tsx'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import MaterialReportsIncomesTable from '@/components/tables/elements/MaterialReportsIncomesTable.tsx'
import MaterialReportsFactoriesTable from '@/components/tables/elements/MaterialReportsFactoriesTable.tsx'
import MaterialReportsFactoryReturnsTable from '@/components/tables/elements/MaterialReportsFactoryReturnsTable.tsx'
import MaterialReportsOrdersTable from '@/components/tables/elements/MaterialReportsOrdersTable.tsx'
import MaterialReportsProductReturnsTable from '@/components/tables/elements/MaterialReportsProductReturnsTable.tsx'
import MaterialReportsWriteOffTable from '@/components/tables/elements/MaterialReportsWriteOffTable.tsx'
import SectionsTop from '@/components/others/SectionsTop.tsx'
import usePagination from '@/hooks/usePagination.ts'
import PaginationComponent from '@/components/others/PaginationComponent.tsx'
import {materialReportsEditTHData} from '@/data/tablesHeaderData.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import TableItem from '@/components/tables/TableItem.tsx'
import useFilters from '@/hooks/useFilters.ts'
import FiltersBlock from '@/components/others/FiltersBlock.tsx'
import useServerSearch from '@/hooks/useServerSearch.ts'
import {useEffect, useState} from "react"
import useQueryString from '@/hooks/useQueryString.ts'
import {api} from "@/services/api.ts"
import SectionTableSkeleton from "@/components/skeletons/SectionTableSkeleton.tsx"

const MaterialReportsEditPage = () => {
  const materialReportsEditFilterState = JSON.parse(localStorage.getItem("materialReportsEdit") || JSON.stringify({
    "factoriesPage": "",
    "incomesPage": "",
    "factoryReturnsPage": "",
    "ordersPage": "",
    "productReturnsPage": "",
    "writeOffPage": "",
    "factoriesSubmittedSearch": "",
    "factoryReturnsSubmittedSearch": "",
    "incomesSubmittedSearch": "",
    "ordersSubmittedSearch": "",
    "productReturnsSubmittedSearch": "",
    "periodFromFormatted": "",
    "periodToFormatted": "",
    "periodFrom": "",
    "periodTo": "",
    "client": "",
    "salesman": "",
    "createdUser": "",
    "industry": ""
  }))

  const { id } = useParams()
  const navigate = useNavigate()
  const { formatter } = useNumberFormatter()
  const { periodTo, periodFrom, periodFromFormatted, periodToFormatted, setPeriodFrom, setPeriodTo, client, setClient, salesman, setSalesman, createdUser, setCreatedUser, industry, setIndustry } = useFilters(materialReportsEditFilterState)

  const { currentPage: factoriesPage, setCurrentPage: factoriesSetCurrentPage, totalPages: factoriesTotalPages, setTotalPages: factoriesSetTotalPages } = usePagination(materialReportsEditFilterState)
  const { currentPage: incomesPage, setCurrentPage: incomesSetCurrentPage, totalPages: incomesTotalPages, setTotalPages: incomesSetTotalPages } = usePagination(materialReportsEditFilterState)
  const { currentPage: factoryReturnsPage, setCurrentPage: factoryReturnsSetCurrentPage, totalPages: factoryReturnsTotalPages, setTotalPages: factoryReturnsSetTotalPages } = usePagination(materialReportsEditFilterState)
  const { currentPage: ordersPage, setCurrentPage: ordersSetCurrentPage, totalPages: ordersTotalPages, setTotalPages: ordersSetTotalPages } = usePagination(materialReportsEditFilterState)
  const { currentPage: productReturnsPage, setCurrentPage: productReturnsSetCurrentPage, totalPages: productReturnsTotalPages, setTotalPages: productReturnsSetTotalPages } = usePagination(materialReportsEditFilterState)
  const { currentPage: writeOffPage, setCurrentPage: writeOffSetCurrentPage, totalPages: writeOffTotalPages, setTotalPages: writeOffSetTotalPages } = usePagination(materialReportsEditFilterState)

  const { searchValue: factoriesSearchValue, handleSearch: factoriesHandleSearch, submittedSearch: factoriesSubmittedSearch, submitSearch: factoriesSubmitSearch } = useServerSearch(factoriesSetCurrentPage)
  const { searchValue: factoryReturnsSearchValue, handleSearch: factoryReturnsHandleSearch, submittedSearch: factoryReturnsSubmittedSearch, submitSearch: factoryReturnsSubmitSearch } = useServerSearch(factoryReturnsSetCurrentPage)
  const { searchValue: incomesSearchValue, handleSearch: incomesHandleSearch, submittedSearch: incomesSubmittedSearch, submitSearch: incomesSubmitSearch } = useServerSearch(incomesSetCurrentPage)
  const { searchValue: ordersSearchValue, handleSearch: ordersHandleSearch, submittedSearch: ordersSubmittedSearch, submitSearch: ordersSubmitSearch } = useServerSearch(ordersSetCurrentPage)
  const { searchValue: productReturnsSearchValue, handleSearch: productReturnsHandleSearch, submittedSearch: productReturnsSubmittedSearch, submitSearch: productReturnsSubmitSearch } = useServerSearch(productReturnsSetCurrentPage)

  const summaryQueryParams: any = {
    'start_date': periodFromFormatted !== null ? periodFromFormatted : '',
    'end_date': periodToFormatted !== null ? periodToFormatted : '',
    'client': client !== null && client !== 'null' ? client : '',
    'salesman': salesman !== null && salesman !== 'null' ? salesman : '',
    'created_user': createdUser !== null && createdUser !== 'null' ? createdUser : '',
    'industry': industry !== null && industry !== 'null' ? industry : ''
  }

  const factoriesQueryParams: any = {
    'page': factoriesPage,
    'search': factoriesSubmittedSearch,
    'start_date': periodFromFormatted !== null ? periodFromFormatted : '',
    'end_date': periodToFormatted !== null ? periodToFormatted : ''
  }

  const factoriesReturnsQueryParams: any = {
    'page': factoriesPage,
    'search': factoryReturnsSubmittedSearch,
    'start_date': periodFromFormatted !== null ? periodFromFormatted : '',
    'end_date': periodToFormatted !== null ? periodToFormatted : ''
  }

  const incomesQueryParams: any = {
    'page': factoriesPage,
    'search': incomesSubmittedSearch,
    'start_date': periodFromFormatted !== null ? periodFromFormatted : '',
    'end_date': periodToFormatted !== null ? periodToFormatted : ''
  }

  const ordersQueryParams: any = {
    'page': factoriesPage,
    'search': ordersSubmittedSearch,
    'start_date': periodFromFormatted !== null ? periodFromFormatted : '',
    'end_date': periodToFormatted !== null ? periodToFormatted : '',
    'client': client !== null && client !== 'null' ? client : '',
    'salesman': salesman !== null && salesman !== 'null' ? salesman : '',
    'created_user': createdUser !== null && createdUser !== 'null' ? createdUser : '',
    'industry': industry !== null && industry !== 'null' ? industry : ''
  }

  const productReturnsQueryParams: any = {
    'page': factoriesPage,
    'search': productReturnsSubmittedSearch,
    'start_date': periodFromFormatted !== null ? periodFromFormatted : '',
    'end_date': periodToFormatted !== null ? periodToFormatted : ''
  }

  const writeOffsQueryParams: any = {
    'page': writeOffPage,
    'start_date': periodFromFormatted !== null ? periodFromFormatted : '',
    'end_date': periodToFormatted !== null ? periodToFormatted : ''
  }

  useEffect(() => {
    localStorage.setItem("materialReportsEdit", JSON.stringify({
      "factoriesPage": factoriesPage,
      "incomesPage": incomesPage,
      "factoryReturnsPage": factoryReturnsPage,
      "ordersPage": ordersPage,
      "productReturnsPage": productReturnsPage,
      "writeOffPage": writeOffPage,
      "factoriesSubmittedSearch": factoriesSubmittedSearch,
      "factoryReturnsSubmittedSearch": factoryReturnsSubmittedSearch,
      "incomesSubmittedSearch": incomesSubmittedSearch,
      "ordersSubmittedSearch": ordersSubmittedSearch,
      "productReturnsSubmittedSearch": productReturnsSubmittedSearch,
      "periodFromFormatted": periodFromFormatted,
      "periodToFormatted": periodToFormatted,
      "periodFrom": periodFrom,
      "periodTo": periodTo,
      "client": client,
      "salesman": salesman,
      "createdUser": createdUser,
      "industry": industry
    }))
  }, [
    factoriesPage,
    incomesPage,
    factoryReturnsPage,
    ordersPage,
    productReturnsPage,
    writeOffPage,
    factoriesSubmittedSearch,
    factoryReturnsSubmittedSearch,
    incomesSubmittedSearch,
    ordersSubmittedSearch,
    productReturnsSubmittedSearch,
    periodFromFormatted,
    periodToFormatted,
    periodFrom,
    periodTo,
    client,
    salesman,
    createdUser,
    industry
  ])

  const { queryString: summaryQueryStringCollection } = useQueryString(summaryQueryParams)
  const { queryString: factoriesQueryStringCollection } = useQueryString(factoriesQueryParams)
  const { queryString: factoriesReturnsQueryStringCollection } = useQueryString(factoriesReturnsQueryParams)
  const { queryString: incomesQueryStringCollection } = useQueryString(incomesQueryParams)
  const { queryString: ordersQueryStringCollection } = useQueryString(ordersQueryParams)
  const { queryString: productReturnsQueryStringCollection } = useQueryString(productReturnsQueryParams)
  const { queryString: writeOffsQueryStringCollection } = useQueryString(writeOffsQueryParams)

  const [summaryQueryString, setSummaryQueryString] = useState('')
  const [factoriesQueryString, setFactoriesQueryString] = useState('')
  const [factoriesReturnsQueryString, setFactoriesReturnsQueryString] = useState('')
  const [incomesQueryString, setIncomesQueryString] = useState('')
  const [ordersQueryString, setOrdersQueryString] = useState('')
  const [productReturnsQueryString, setProductReturnsQueryString] = useState('')
  const [writeOffsQueryString, setWriteOffsQueryString] = useState('')

  const { data, isLoading } = api.useGetMaterialReportsIdQuery({ id: id, queryString: summaryQueryString })
  const { data: factoriesData, isLoading: factoriesLoading, isFetching: factoriesFetching, isError: factoriesError } = api.useGetMaterialReportsQuery({ id: id, queryString: factoriesQueryString, item: 'factories' })
  const { data: factoriesReturnsData, isLoading: factoriesReturnsLoading, isFetching: factoriesReturnsFetching, isError: factoriesReturnsError } = api.useGetMaterialReportsQuery({ id: id, queryString: factoriesReturnsQueryString, item: 'factory-item-returns' })
  const { data: incomesData, isLoading: incomesLoading, isFetching: incomesFetching, isError: incomesError } = api.useGetMaterialReportsQuery({ id: id, queryString: incomesQueryString, item: 'incomes' })
  const { data: ordersData, isLoading: ordersLoading, isFetching: ordersFetching, isError: ordersError } = api.useGetMaterialReportsQuery({ id: id, queryString: ordersQueryString, item: 'orders' })
  const { data: productReturnsData, isLoading: productReturnsLoading, isFetching: productReturnsFetching, isError: productReturnsError } = api.useGetMaterialReportsQuery({ id: id, queryString: productReturnsQueryString, item: 'product-returns' })
  const { data: writeOffData, isLoading: writeOffLoading, isFetching: writeOffFetching, isError: writeOffError } = api.useGetMaterialReportsQuery({ id: id, queryString: writeOffsQueryString, item: 'write-offs' })

  useEffect(() => {
    setFactoriesQueryString(factoriesQueryStringCollection)
  }, [factoriesPage, factoriesSubmittedSearch])

  useEffect(() => {
    setFactoriesReturnsQueryString(factoriesReturnsQueryStringCollection)
  }, [factoryReturnsPage, factoryReturnsSubmittedSearch])

  useEffect(() => {
    setIncomesQueryString(incomesQueryStringCollection)
  }, [incomesPage, incomesSubmittedSearch])

  useEffect(() => {
    setOrdersQueryString(ordersQueryStringCollection)
  }, [ordersPage, ordersSubmittedSearch])

  useEffect(() => {
    setProductReturnsQueryString(productReturnsQueryStringCollection)
  }, [productReturnsPage, productReturnsSubmittedSearch])

  return (
    <>
      <DashboardLayout>
        { !isLoading && !factoriesLoading && !factoriesReturnsLoading && !incomesLoading && !ordersLoading && !productReturnsLoading && !writeOffLoading ? (
          <section className='w-full flex flex-col gap-8'>
            <Button className='w-48' variant='outline' onClick={() => navigate(-1)}>
              <ChevronLeft className='w-4 h-4 mr-2'/> Вернуться назад
            </Button>

            <h3 className="text-2xl font-semibold">Название товара: <span className="font-extrabold">{data?.name}</span></h3>

            <div>
              <TableItem data={data} headerData={materialReportsEditTHData} notFoundText='Отчеты не найдены!'>
                {data && (
                  <TableRow key={data?.id}>
                    <TableCell>{formatter.format(data?.before_count)} шт</TableCell>
                    <TableCell>{formatter.format(data?.total_income_in_range)} шт</TableCell>
                    <TableCell>{formatter.format(data?.total_outcome_in_range)} шт</TableCell>
                    <TableCell>{formatter.format(data?.after_count)} шт</TableCell>
                    <TableCell>{formatter.format(data?.current_count)} шт</TableCell>
                    <TableCell>{formatter.format(data?.total_sales_in_range)} cум</TableCell>
                    <TableCell>{formatter.format(data?.total_self_price_in_range)} cум</TableCell>
                    <TableCell>{formatter.format(data?.total_sales_count)} шт</TableCell>
                  </TableRow>
                )}
              </TableItem>
            </div>

            <div className='mt-12 flex flex-col gap-16'>
              <div className='flex flex-col gap-8'>
                <FiltersBlock
                  periodFrom={periodFrom}
                  periodTo={periodTo}
                  setPeriodFrom={setPeriodFrom}
                  setPeriodTo={setPeriodTo}
                  setClients={setClient}
                  setSalesman={setSalesman}
                  setCreatedUser={setCreatedUser}
                  setIndustry={setIndustry}
                  refetchData={() => {
                    setSummaryQueryString(summaryQueryStringCollection)
                    setWriteOffsQueryString(writeOffsQueryStringCollection)
                    setFactoriesQueryString(factoriesQueryStringCollection)
                    setFactoriesReturnsQueryString(factoriesReturnsQueryStringCollection)
                    setIncomesQueryString(incomesQueryStringCollection)
                    setOrdersQueryString(ordersQueryStringCollection)
                    setProductReturnsQueryString(productReturnsQueryStringCollection)
                  }}
                  pathName={'materialReportsEdit'}
                  hasClients
                  hasSalesman
                  hasCreatedUser
                  hasIndustry
                />

                <SectionsTop
                  title='Букеты'
                  placeholder='Поиск букетов'
                  inputValue={factoriesSearchValue}
                  onChange={factoriesHandleSearch}
                  onClick={factoriesSubmitSearch}
                />

                <div className='w-full h-full relative flex flex-col gap-3'>
                  { !factoriesFetching ? (
                    <MaterialReportsFactoriesTable data={factoriesData?.results} />
                  ) : (
                    <SectionTableSkeleton />
                  ) }

                  <PaginationComponent
                    data={!factoriesError && factoriesData}
                    currentPage={factoriesPage}
                    totalPages={factoriesTotalPages}
                    setCurrentPage={factoriesSetCurrentPage}
                    setTotalPages={factoriesSetTotalPages}
                    refetchData={() => setFactoriesQueryString(factoriesQueryStringCollection)}
                  />
                </div>
              </div>

              <div className='flex flex-col gap-8'>
                <SectionsTop
                  title='Возвращенные букеты'
                  placeholder='Поиск возвращенных букетов'
                  inputValue={factoryReturnsSearchValue}
                  onChange={factoryReturnsHandleSearch}
                  onClick={factoryReturnsSubmitSearch}
                />

                <div className='w-full h-full relative flex flex-col gap-3'>
                  { !factoriesReturnsFetching ? (
                    <MaterialReportsFactoryReturnsTable data={factoriesReturnsData?.results} />
                  ) : (
                    <SectionTableSkeleton />
                  ) }

                  <PaginationComponent
                    data={!factoriesReturnsError && factoriesReturnsData}
                    currentPage={factoryReturnsPage}
                    totalPages={factoryReturnsTotalPages}
                    setCurrentPage={factoryReturnsSetCurrentPage}
                    setTotalPages={factoryReturnsSetTotalPages}
                    refetchData={() => setFactoriesReturnsQueryString(factoriesReturnsQueryStringCollection)}
                  />
                </div>
              </div>

              <div className='flex flex-col gap-8'>
                <SectionsTop
                  title='Приходы'
                  placeholder='Поиск приходов'
                  inputValue={incomesSearchValue}
                  onChange={incomesHandleSearch}
                  onClick={incomesSubmitSearch}
                />

                <div className='w-full h-full relative flex flex-col gap-3'>
                  { !incomesFetching ? (
                    <MaterialReportsIncomesTable data={incomesData?.results} />
                  ) : (
                    <SectionTableSkeleton />
                  ) }

                  <PaginationComponent
                    data={!incomesError && incomesData}
                    currentPage={incomesPage}
                    totalPages={incomesTotalPages}
                    setCurrentPage={incomesSetCurrentPage}
                    setTotalPages={incomesSetTotalPages}
                    refetchData={() => setIncomesQueryString(incomesQueryStringCollection)}
                  />
                </div>
              </div>

              <div className='flex flex-col gap-8'>
                <SectionsTop
                  title='Продажи'
                  placeholder='Поиск продаж'
                  inputValue={ordersSearchValue}
                  onChange={ordersHandleSearch}
                  onClick={ordersSubmitSearch}
                />

                <div className='w-full h-full relative flex flex-col gap-3'>
                  { !ordersFetching ? (
                    <MaterialReportsOrdersTable data={ordersData?.results} />
                  ) : (
                    <SectionTableSkeleton />
                  ) }

                  <PaginationComponent
                    data={!ordersError && ordersData}
                    currentPage={ordersPage}
                    totalPages={ordersTotalPages}
                    setCurrentPage={ordersSetCurrentPage}
                    setTotalPages={ordersSetTotalPages}
                    refetchData={() => setOrdersQueryString(ordersQueryStringCollection)}
                  />
                </div>
              </div>

              <div className='flex flex-col gap-8'>
                <SectionsTop
                  title='Возвраты'
                  placeholder='Поиск возвратов'
                  inputValue={productReturnsSearchValue}
                  onChange={productReturnsHandleSearch}
                  onClick={productReturnsSubmitSearch}
                />

                <div className='w-full h-full relative flex flex-col gap-3'>
                  { !productReturnsFetching ? (
                    <MaterialReportsProductReturnsTable data={productReturnsData?.results} />
                  ) : (
                    <SectionTableSkeleton />
                  ) }

                  <PaginationComponent
                    data={!productReturnsError && productReturnsData}
                    currentPage={productReturnsPage}
                    totalPages={productReturnsTotalPages}
                    setCurrentPage={productReturnsSetCurrentPage}
                    setTotalPages={productReturnsSetTotalPages}
                    refetchData={() => setProductReturnsQueryString(productReturnsQueryStringCollection)}
                  />
                </div>
              </div>

              <div className="flex flex-col gap-8">
                <h1 className="text-3xl font-bold">Списания</h1>

                <div className="w-full h-full relative flex flex-col gap-3">
                  { !writeOffFetching ? (
                    <MaterialReportsWriteOffTable data={writeOffData?.results} />
                  ) : (
                    <SectionTableSkeleton />
                  ) }

                  <PaginationComponent
                    data={!writeOffError && writeOffData}
                    currentPage={writeOffPage}
                    totalPages={writeOffTotalPages}
                    setCurrentPage={writeOffSetCurrentPage}
                    setTotalPages={writeOffSetTotalPages}
                    refetchData={() => setWriteOffsQueryString(writeOffsQueryStringCollection)}
                  />
                </div>
              </div>
            </div>
          </section>
        ) : (
          <EditSectionSkeleton/>
        )}
      </DashboardLayout>
    </>
  )
}

export default MaterialReportsEditPage