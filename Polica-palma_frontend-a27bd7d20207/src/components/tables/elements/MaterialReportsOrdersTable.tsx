import {TablesProps} from '@/typing/interfaces.ts'
import TableItem from '@/components/tables/TableItem.tsx'
import {materialReportsOrdersTHData} from '@/data/tablesHeaderData.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import formatDate from '@/helpers/formatDate.ts'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'

const MaterialReportsOrdersTable = ({ data }: TablesProps) => {
  const { formatter } = useNumberFormatter()

  return (
    <>
      <TableItem data={data} headerData={materialReportsOrdersTHData} notFoundText='Продажи не найдены!'>
        {data && Array.isArray(data) && data.map((item, index) => (
          <TableRow key={item.id}>
            <TableCell>{++index}</TableCell>
            <TableCell>{item.order_name}</TableCell>
            <TableCell>{formatter.format(item.product_count)} шт</TableCell>
            <TableCell>{formatter.format(item.total_product_sum)} сум</TableCell>
            <TableCell>{formatter.format(item.total_product_discount)} сум</TableCell>
            <TableCell>{item.client?.full_name}</TableCell>
            <TableCell>{item.salesman?.first_name || item.salesman?.username}</TableCell>
            <TableCell>{item.created_user?.first_name || item.created_user?.username}</TableCell>
            <TableCell>{formatDate(item.created_at)}</TableCell>
          </TableRow>
        ))}
      </TableItem>
    </>
  )
}

export default MaterialReportsOrdersTable