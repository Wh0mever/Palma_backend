import {TablesProps} from '@/typing/interfaces.ts'
import {orderItemsReportsTHData} from '@/data/tablesHeaderData.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import {Link} from 'react-router-dom'
import {Button} from '@/components/ui/button.tsx'
import {Eye} from 'lucide-react'
import TableItem from '@/components/tables/TableItem.tsx'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'

interface OrderItemsReportsTableProps extends TablesProps {
  hasntEye?: boolean
  isBouquet?: boolean
}

const OrderItemsReportsTable = ({ data, hasntEye, isBouquet }: OrderItemsReportsTableProps) => {
  const { formatter } = useNumberFormatter()

  return (
    <>
      <TableItem data={data} headerData={orderItemsReportsTHData} notFoundText='Товары не найдены!'>
        {data && Array.isArray(data) && data.map((item, index) => (
          <TableRow key={item.id}>
            <TableCell>{++index}</TableCell>
            { !isBouquet ? (
              <TableCell>{item.product_name}</TableCell>
            ) : (
              <TableCell>
                <Link to={`/dashboard/factories/bouquets/edit/${item.product?.id}`} className='hover:underline'>
                  {item.product_name}
                </Link>
              </TableCell>
            ) }
            <TableCell>
              <Link to={`/dashboard/order/orders/edit/${item.order?.id}`} className='hover:underline'>
                Заказ #{item.order?.id}
              </Link>
            </TableCell>
            <TableCell>{item.salesman_name}</TableCell>
            <TableCell>{item.created_user || '-'}</TableCell>
            <TableCell>{item.client_name}</TableCell>
            <TableCell>{item.industry}</TableCell>
            <TableCell>{formatter.format(item.price)} сум</TableCell>
            <TableCell>{formatter.format(item.count)} шт</TableCell>
            <TableCell>{formatter.format(item.returned_count)} шт</TableCell>
            <TableCell>{formatter.format(item.total_discount)} сум</TableCell>
            <TableCell>{formatter.format(item.total_charge)} сум</TableCell>
            <TableCell>{formatter.format(item.total_self_price)} сум</TableCell>
            <TableCell>{formatter.format(item.total_profit)} сум</TableCell>
            <TableCell>{formatter.format(item.total)} сум</TableCell>
            { !hasntEye && (
              <TableCell>
                <Link to={`/dashboard/reports/materials/${item.product?.id}/`}>
                  <Button size='icon'>
                    <Eye className='w-4 h-4' />
                  </Button>
                </Link>
              </TableCell>
            ) }
          </TableRow>
        ))}
      </TableItem>
    </>
  )
}

export default OrderItemsReportsTable