import TableItem from '@/components/tables/TableItem.tsx'
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table.tsx'
import formatDate from '@/helpers/formatDate.ts'
import {TablesProps} from '@/typing/interfaces.ts'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import {warehouseTHData} from '@/data/tablesHeaderData.ts'
import WriteOffDialog from '@/components/others/WriteOffDialog.tsx'
import {Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger} from '@/components/ui/dialog.tsx'
import {Button} from '@/components/ui/button.tsx'
import {Eye} from 'lucide-react'
import {useState} from 'react'
import {Skeleton} from '@/components/ui/skeleton.tsx'
import {api} from "@/services/api.ts"

const WarehouseTable = ({ data }: TablesProps) => {
  const { formatter } = useNumberFormatter()
  const [itemID, setItemID] = useState<string>('')
  const { data: historyData, isLoading: historyLoading } = api.useGetIncomeHistoryQuery(itemID)

  return (
    <TableItem data={data} headerData={warehouseTHData} notFoundText='Товары из склада не найдены!'>
      {data && Array.isArray(data) && data.map((item, index) => (
        <TableRow key={item.id}>
          <TableCell>{++index}</TableCell>
          <TableCell>{item.product?.name}</TableCell>
          <TableCell>{formatter.format(item.count)}</TableCell>
          <TableCell>{formatter.format(item.self_price)} сум</TableCell>
          <TableCell>{formatter.format(item.sale_price)} сум</TableCell>
          <TableCell>{formatDate(item.created_at)}</TableCell>
          <TableCell className='flex items-center gap-2'>
            <Dialog>
              <DialogTrigger>
                <Button size='icon' onClick={() => setItemID(item.product?.id)}>
                  <Eye className='w-4 h-4' />
                </Button>
              </DialogTrigger>

              <DialogContent className='min-w-[60%] h-[650px]'>
                <DialogHeader>
                  <DialogTitle>История прихода "{item.product?.name}"</DialogTitle>
                </DialogHeader>

                <Table className='w-full'>
                  <TableHeader>
                    <TableRow>
                      <TableHead>№</TableHead>
                      <TableHead>Количество</TableHead>
                      <TableHead>Цена</TableHead>
                      <TableHead>Продажная цена</TableHead>
                      <TableHead>Итого</TableHead>
                      <TableHead>Дата</TableHead>
                    </TableRow>
                  </TableHeader>

                  <TableBody>
                    { !historyLoading && historyData && historyData.income_items && Array.isArray(historyData.income_items) ? historyData.income_items.map((item: any, index: any) => (
                      <TableRow key={item.id}>
                        <TableCell>{++index}</TableCell>
                        <TableCell>{formatter.format(item.count)}</TableCell>
                        <TableCell>{formatter.format(item.price)}</TableCell>
                        <TableCell>{formatter.format(item.sale_price)} сум</TableCell>
                        <TableCell>{formatter.format(item.total)}</TableCell>
                        <TableCell>{formatDate(item.created_at)}</TableCell>
                      </TableRow>
                    )) : (
                      <div className='w-full flex flex-col gap-4'>
                        <Skeleton className='w-full h-10' />
                        <Skeleton className='w-full h-10' />
                        <Skeleton className='w-full h-10' />
                        <Skeleton className='w-full h-10' />
                      </div>
                    ) }
                  </TableBody>

                  { historyData && Array.isArray(historyData) && historyData.length === 0 && <p className='w-full mt-2 p-2 text-lg font-medium'>Возвращённых товаров нет</p> }
                </Table>
              </DialogContent>
            </Dialog>

            <WriteOffDialog warehouseProduct={item.id} />
          </TableCell>
        </TableRow>
      ))}
    </TableItem>
  )
}

export default WarehouseTable