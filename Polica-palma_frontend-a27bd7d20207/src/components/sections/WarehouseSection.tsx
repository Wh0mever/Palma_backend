import SectionsTop from '@/components/others/SectionsTop.tsx'
import WarehouseTable from '@/components/tables/elements/WarehouseTable.tsx'
import SectionTableSkeleton from '@/components/skeletons/SectionTableSkeleton.tsx'
import usePagination from '@/hooks/usePagination.ts'
import useFilters from '@/hooks/useFilters.ts'
import FiltersBlock from '@/components/others/FiltersBlock.tsx'
import PaginationComponent from '@/components/others/PaginationComponent.tsx'
import useServerSearch from '@/hooks/useServerSearch.ts'
import {useEffect, useState} from "react"
import useQueryString from '@/hooks/useQueryString.ts'
import TableDownload from '@/components/others/TableDownload.tsx'
import {api} from "@/services/api.ts"
import useNumberFormatter from "@/hooks/useNumberFormatter.ts"
import {Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger} from "@/components/ui/dialog.tsx"
import {Button} from "@/components/ui/button.tsx"
import {Download} from "lucide-react"
import {Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue} from "@/components/ui/select.tsx"

const WarehouseSection = () => {
  const warehouseFilterState = JSON.parse(localStorage.getItem("warehouse") || JSON.stringify({
    "currentPage": "",
    "submittedSearch": "",
    "industry": "",
    "productsCategory": "",
  }))

  const { formatter } = useNumberFormatter()
  const { currentPage, setCurrentPage, totalPages, setTotalPages } = usePagination(warehouseFilterState)
  const { industry, setIndustry, productsCategory, setProductsCategory } = useFilters(warehouseFilterState)
  const { searchValue, handleSearch, submitSearch, submittedSearch } = useServerSearch(setCurrentPage)

  const queryParams: any = {
    'page': currentPage,
    'search': submittedSearch,
    'industry': industry !== null && industry !== 'null' ? industry : '',
    'category': productsCategory !== null && productsCategory !== 'null' ? productsCategory : ''
  }

  useEffect(() => {
    localStorage.setItem("warehouse", JSON.stringify({
      "currentPage": currentPage,
      "submittedSearch": submittedSearch,
      "industry": industry,
      "productsCategory": productsCategory,
    }))
  }, [
    currentPage,
    submittedSearch,
    industry,
    productsCategory
  ])

  const [industryID, setIndustryID] = useState(undefined);
  const { queryString: queryStringCollection } = useQueryString(queryParams)
  const [queryString, setQueryString] = useState('')
  const { data: summaryData } = api.useGetWarehouseSummaryQuery(queryString)
  const { data, isLoading, isFetching, isError } = api.useGetWarehouseQuery(queryString)
  const { data: industriesData, isLoading: industriesLoading } = api.useGetIndustriesQuery('')

  const sortedData = data && data.results && Array.isArray(data.results) && data.results?.slice().sort((a: any, b: never) => {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-expect-error
    return new Date(b.created_at) - new Date(a.created_at)
  })

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
            title='Склад'
            placeholder='Поиск товара'
            inputValue={searchValue}
            onChange={handleSearch}
            onClick={submitSearch}
          />

          <div className='grid grid-cols-1 gap-3'>
            <p className='px-4 py-2 bg-neutral-100/70 rounded-lg font-medium'>Общая себестоимость: <span
              className='font-bold'>{formatter.format(summaryData?.total_self_price_sum)} сум</span></p>
          </div>

          <div className='w-max flex items-center self-end gap-3'>
            <Dialog>
              <DialogTrigger>
                <Button>
                  <Download className='w-4 h-4 mr-2'/>
                  Инвентаризация
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Скачать отчет по инвентаризации</DialogTitle>
                </DialogHeader>

                <div className='w-full flex flex-col gap-6'>
                  <Select defaultValue={industryID} onValueChange={(e: any) => setIndustryID(e)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Выберите магазин" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectGroup>
                        { !industriesLoading && Array.isArray(industriesData) && industriesData?.map((item) => (
                          <SelectItem value={item.id}>{item.name}</SelectItem>
                        )) }
                      </SelectGroup>
                    </SelectContent>
                  </Select>

                  { industryID && (
                    <TableDownload
                      haventUserID
                      text='Экспорт в Excel'
                      apiUrl={`core/products-export/${industryID}`}
                    />
                  ) }
                </div>
              </DialogContent>
            </Dialog>

            <TableDownload
              apiUrl={`api/warehouse/export-excel`}
              params={queryString}
              text='Экспорт в Excel'
            />
          </div>

          <div className='w-full h-full relative flex flex-col gap-3'>
            <FiltersBlock
              setIndustry={setIndustry}
              setProductsCategory={setProductsCategory}
              refetchData={() => setQueryString(queryStringCollection)}
              industry={industry}
              productsCategory={productsCategory}
              pathName={'warehouse'}
              hasIndustry
              hasProductsCategory
              haventPeriods
            />

            {!isFetching ? (
              <WarehouseTable data={sortedData}/>
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

export default WarehouseSection