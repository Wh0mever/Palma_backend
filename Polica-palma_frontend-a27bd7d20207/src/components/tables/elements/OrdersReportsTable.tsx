import {TablesProps} from '@/typing/interfaces.ts'
import TableItem from '@/components/tables/TableItem.tsx'
import {ordersReportsTHData} from '@/data/tablesHeaderData.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import translatedData from '@/data/translatedData.ts'
import {Link} from 'react-router-dom'
import {Button} from '@/components/ui/button.tsx'
import {Eye} from 'lucide-react'
import formatDate from '@/helpers/formatDate.ts'

const OrdersReportsTable = ({ data }: TablesProps) => {
  const { formatter } = useNumberFormatter()

  return (
    <>
      <TableItem data={data} headerData={ordersReportsTHData} notFoundText='Продажи не найдены!'>
        {data && Array.isArray(data) && data.map((item, index) => (
          <TableRow key={item.id}>
            <TableCell>{++index}</TableCell>
            <TableCell>Продажа #{item.id}</TableCell>
            <TableCell>{item.salesman?.first_name || item.salesman?.username || '-'}</TableCell>
            <TableCell>{item.created_user?.first_name || item.created_user?.username || '-'}</TableCell>
            <TableCell>{formatter.format(item.total)} сум</TableCell>
            <TableCell>{formatter.format(item.total_with_discount)} сум</TableCell>
            <TableCell>{formatter.format(item.total_self_price)} сум</TableCell>
            <TableCell>{formatter.format(item.total_discount)} сум</TableCell>
            <TableCell>{formatter.format(item.total_charge)} сум</TableCell>
            <TableCell>{formatter.format(item.total_profit)} сум</TableCell>
            <TableCell>{formatter.format(item.amount_paid)} сум</TableCell>
            <TableCell>{formatter.format(item.debt)} сум</TableCell>
            <TableCell>{translatedData(item.status)}</TableCell>
            <TableCell>{formatDate(item.created_at)}</TableCell>
            <TableCell>
              <Link to={`/dashboard/order/orders/edit/${item.id}/`}>
                <Button size='icon'>
                  <Eye className='w-4 h-4' />
                </Button>
              </Link>
            </TableCell>
          </TableRow>
        ))}
      </TableItem>
    </>
  )
}

export default OrdersReportsTable