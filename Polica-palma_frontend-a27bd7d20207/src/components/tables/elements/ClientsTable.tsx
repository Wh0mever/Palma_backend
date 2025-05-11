import TableItem from '@/components/tables/TableItem.tsx'
import {TablesProps} from '@/typing/interfaces.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import EditItem from '@/components/items/EditItem.tsx'
import DeleteDialog from '@/components/others/DeleteDialog.tsx'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import {clientsTHData} from '@/data/tablesHeaderData.ts'
import formatPhoneNumber from '@/helpers/formatPhoneNumber.ts'

const ClientsTable = ({ data }: TablesProps) => {
  const { formatter } = useNumberFormatter()

  return (
    <TableItem data={data} headerData={clientsTHData} notFoundText='Клиенты не найдены!'>
      {data && Array.isArray(data) && data.map((item, index) => (
        <TableRow key={item.id}>
          <TableCell>{++index}</TableCell>
          <TableCell>{item.full_name}</TableCell>
          <TableCell>{item.phone_number ? formatPhoneNumber(item.phone_number) : '-'}</TableCell>
          <TableCell>{formatter.format(item.debt)} сум</TableCell>
          <TableCell>{formatter.format(item.discount_percent)}%</TableCell>
          <TableCell>{formatter.format(item?.total_orders_sum)} сум</TableCell>
          <TableCell>{Number(item?.orders_count)}</TableCell>
          <TableCell>{item.comment || '-'}</TableCell>
          <TableCell className='flex items-center gap-4'>
            <EditItem link={`/dashboard/order/clients/edit/${item.id}`} />
            <DeleteDialog
              desc
              id={item.id}
              url='api/clients'
              item={item.full_name}
              invalidatesTags={["Clients"]}
            />
          </TableCell>
        </TableRow>
      ))}
    </TableItem>
  )
}

export default ClientsTable