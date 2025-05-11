import TableItem from '@/components/tables/TableItem.tsx'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import formatDate from '@/helpers/formatDate.ts'
import translateFunc from '@/data/translatedData.ts'
import EditItem from '@/components/items/EditItem.tsx'
import DeleteDialog from '@/components/others/DeleteDialog.tsx'
import {TablesProps} from '@/typing/interfaces.ts'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import {ordersTHData} from '@/data/tablesHeaderData.ts'
import getUserData from '@/helpers/getUserData.ts'

const OrdersTable = ({ data }: TablesProps) => {
  const { userType } = getUserData()
  const { formatter } = useNumberFormatter()

  return (
    <TableItem data={data} headerData={ordersTHData} notFoundText='Продажи не найдены!'>
      {data && Array.isArray(data) && data.map((item, index) => (
        <TableRow key={item.id}>
          <TableCell>{++index}</TableCell>
          <TableCell>Заказ #{item.id}</TableCell>
          <TableCell>{item.client?.full_name}</TableCell>
          <TableCell>{item.salesman?.first_name || item.salesman?.username || '-'}</TableCell>
          <TableCell>{formatDate(item.created_at)}</TableCell>
          <TableCell>{translateFunc(item.status)}</TableCell>
          <TableCell>{item.department?.name}</TableCell>
          <TableCell>{formatter.format(item.total)} сум</TableCell>
          <TableCell>{formatter.format(item.debt)} сум</TableCell>
          <TableCell>{item.comment || '-'}</TableCell>
          <TableCell>{item.created_user?.first_name || item.created_user?.username}</TableCell>
          <TableCell className='flex items-center gap-4'>
            <EditItem link={`/dashboard/order/orders/edit/${item.id}`} isEye />

            { userType !== 'MANAGER' && userType !== 'SALESMAN' && userType !== 'CASHIER' && (
              <DeleteDialog
                desc
                id={item.id}
                url='api/orders'
                item={`Заказ #${item.id}`}
                invalidatesTags={["Orders"]}
              />
            ) }
          </TableCell>
        </TableRow>
      ))}
    </TableItem>
  )
}

export default OrdersTable