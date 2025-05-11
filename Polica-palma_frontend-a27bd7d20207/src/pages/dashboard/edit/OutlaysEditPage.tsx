import DashboardLayout from '@/components/elements/DashboardLayout.tsx'
import {useParams} from 'react-router-dom'
import EditSection from '@/components/sections/EditSection.tsx'
import useAxiosPut from '@/hooks/useAxiosPut.ts'
import InputFormField from '@/components/others/InputFormField.tsx'
import TextareaFormField from '@/components/others/TextareaFormField.tsx'
import {z} from 'zod'
import useValues from '@/hooks/useValues.ts'
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table.tsx'
import formatDate from '@/helpers/formatDate.ts'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import translatedData from '@/data/translatedData.ts'
import {Button} from '@/components/ui/button.tsx'
import {Trash2} from 'lucide-react'
import EditSectionSkeleton from '@/components/skeletons/EditSectionSkeleton.tsx'
import useDeleteItem from '@/hooks/useDeleteItem.ts'
import ReactSelectFormField from "@/components/others/ReactSelectFormField.tsx"
import usePagination from "@/hooks/usePagination.ts"
import PaginationComponent from "@/components/others/PaginationComponent.tsx"
import useQueryString from "@/hooks/useQueryString.ts"
import {api} from "@/services/api.ts"
import {useState} from "react"

const OutlaysEditPage = () => {
  const { id } = useParams()
  const { formatter } = useNumberFormatter()
  const { deleteItem, isDeleting } = useDeleteItem()
  const { currentPage, setCurrentPage, totalPages, setTotalPages } = usePagination()

  const queryParams: any = {
    'page': currentPage
  }

  const { queryString: queryStringCollection } = useQueryString(queryParams)
  const [queryString, setQueryString] = useState('')
  const { data, isLoading } = api.useGetOutlaysQuery({ id: id })
  const { data: outlaysPaymentsData, isLoading: outlaysPaymentsLoading } = api.useGetOutlaysPaymentsQuery({ id: id, queryString: queryString })
  const { data: industriesData, isLoading: industriesLoading } = api.useGetIndustriesQuery('')

  const { form, onSubmit, success } = useAxiosPut(
    {
      title: z.string().optional(),
      industry: z.string().optional(),
      outlay_type: z.string().optional(),
      comment: z.string().optional(),
    },
    {},
    `api/outlays`,
    id,
    ["Outlays"]
  )
  const { inputValues, handleInputChange } = useValues(
    {
      title: '',
      outlay_type: '',
      comment: ''
    },
    {
      title: data && data?.title || '',
      outlay_type: data && data?.outlay_type || '',
      comment: data && data?.comment
    },
    isLoading,
    data
  )

  return (
    <>
      <DashboardLayout>
        { !isLoading && !outlaysPaymentsLoading && data ? (
          <>
            <div className='w-full flex flex-col xl:flex-row gap-6'>
              <section className='w-full flex flex-col gap-6'>
                <EditSection form={form} onSubmit={onSubmit} success={success}>
                  <InputFormField
                    control={form.control}
                    type='text'
                    name='title'
                    label='Название'
                    _value={inputValues.title}
                    _onChange={(e: any) => handleInputChange('title', e.target.value)}
                  />
                  <ReactSelectFormField
                    idData={industriesData}
                    isLoading={industriesLoading}
                    control={form.control}
                    name='industry'
                    placeholder={data.industry?.name}
                    label='Магазин'
                  />
                  <TextareaFormField
                    control={form.control}
                    name='comment'
                    label='Комментарий'
                    _value={inputValues.comment}
                    _onChange={(e: any) => handleInputChange('comment', e.target.value)}
                  />
                  <p>Тип расхода: <span className='font-semibold'>{translatedData(data.outlay_type)}</span></p>
                </EditSection>
              </section>

              <section className='w-full h-full relative flex flex-col gap-6'>
                <Table className='w-full'>
                  <TableHeader className='z-30 sticky top-0 bg-white dark:bg-neutral-950'>
                    <TableRow>
                      <TableHead>№</TableHead>
                      { data.outlay_type === 'WORKERS' && <TableHead>Сотрудник</TableHead> }
                      <TableHead>Комментарий</TableHead>
                      <TableHead>Сумма</TableHead>
                      <TableHead>Метод оплаты</TableHead>
                      <TableHead>Доход / расход</TableHead>
                      <TableHead>Дата создания</TableHead>
                      <TableHead></TableHead>
                    </TableRow>
                  </TableHeader>

                  <TableBody>
                    { outlaysPaymentsData.results && Array.isArray(outlaysPaymentsData.results) && outlaysPaymentsData.results.map((item: any, index: any) => (
                      <TableRow key={item.id}>
                        <TableCell>{++index}</TableCell>
                        { data.outlay_type === 'WORKERS' && (
                          <TableCell>{item.worker?.first_name || item.worker?.username || '-'}</TableCell>
                        ) }
                        <TableCell>{item.comment || '-'}</TableCell>
                        <TableCell>{formatter.format(item.amount)}</TableCell>
                        <TableCell>{translatedData(item.payment_method?.name)}</TableCell>
                        <TableCell>{translatedData(item.payment_type)}</TableCell>
                        <TableCell>{formatDate(item.created_at)}</TableCell>
                        <TableCell>
                          <Button variant='destructive' size='icon' disabled={isDeleting} onClick={() => deleteItem(
                            `api/payments`,
                            item.id,
                            ["Outlays", "Payments", "Cashiers"]
                          )}>
                            <Trash2 className='w-4 h-4' />
                          </Button>
                        </TableCell>
                      </TableRow>
                    )) }
                  </TableBody>

                  { data.payments && Array.isArray(data.payments) && data.payments.length === 0 && <p className='mt-4 text-xl font-bold'>Платежей нет</p> }
                </Table>

                <PaginationComponent
                  data={outlaysPaymentsData}
                  currentPage={currentPage}
                  totalPages={totalPages}
                  setCurrentPage={setCurrentPage}
                  setTotalPages={setTotalPages}
                  refetchData={() => setQueryString(queryStringCollection)}
                />
              </section>
            </div>
          </>
        ) : (
          <EditSectionSkeleton />
        ) }
      </DashboardLayout>
    </>
  )
}

export default OutlaysEditPage