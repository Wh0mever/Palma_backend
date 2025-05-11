import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import TableItem from '@/components/tables/TableItem.tsx'
import {TablesProps} from '@/typing/interfaces.ts'
import {salesmanReportsIncomesTHData} from '@/data/tablesHeaderData.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import translatedData from '@/data/translatedData.ts'
import formatDate from '@/helpers/formatDate.ts'
import {Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger} from '@/components/ui/dialog.tsx'
import {Button} from '@/components/ui/button.tsx'
import {Eye} from 'lucide-react'
import {Link} from 'react-router-dom'

const SalesmanReportsIncomesTable = ({ data }: TablesProps) => {
  const { formatter } = useNumberFormatter()

  return (
    <>
      <TableItem data={data} headerData={salesmanReportsIncomesTHData} notFoundText='Начисления не найдены!'>
        {data && Array.isArray(data) && data.map((item, index) => (
          <TableRow key={item.id}>
            <TableCell>{++index}</TableCell>
            <TableCell>{item.income_name}</TableCell>
            <TableCell>{item.order !== null ? <Link target='_blank' className='hover:underline' to={`/dashboard/order/orders/edit/${item.order}`}>Заказ #{item.order}</Link> : '-'}</TableCell>
            <TableCell>{item.product_factory !== null ? <Link target='_blank' className='hover:underline' to={`/dashboard/factories/bouquets/edit/${item.product_factory}`}>Букет #{item.product_factory}</Link> : '-'}</TableCell>
            <TableCell>{formatter.format(item.total)} сум</TableCell>
            <TableCell>{translatedData(item.income_type)}</TableCell>
            <TableCell>{translatedData(item.reason)}</TableCell>
            <TableCell>{formatDate(item.created_at)}</TableCell>
            <TableCell>
              <Dialog>
                <DialogTrigger>
                  <Button size='icon'>
                    <Eye className='w-4 h-4' />
                  </Button>
                </DialogTrigger>

                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Подробнее</DialogTitle>
                  </DialogHeader>

                  <p className='font-medium'>{item.comment}</p>
                </DialogContent>
              </Dialog>
            </TableCell>
          </TableRow>
        ))}
      </TableItem>
    </>
  )
}

export default SalesmanReportsIncomesTable