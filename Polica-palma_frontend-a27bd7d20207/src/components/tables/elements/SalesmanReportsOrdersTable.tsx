import {salesmanReportsOrdersTHData} from '@/data/tablesHeaderData.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import formatDate from '@/helpers/formatDate.ts'
import TableItem from '@/components/tables/TableItem.tsx'
import {TablesProps} from '@/typing/interfaces.ts'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import {Link} from "react-router-dom"

const SalesmanReportsOrdersTable = ({ data }: TablesProps) => {
  const { formatter } = useNumberFormatter()

  return (
    <>
      <TableItem data={data} headerData={salesmanReportsOrdersTHData} notFoundText='Продажи не найдены!'>
        {data && Array.isArray(data) && data.map((item, index) => (
          <TableRow key={item.id}>
            <TableCell>{++index}</TableCell>
            <TableCell>
              <Link to={`/dashboard/order/orders/edit/${item.id}`} className='hover:underline'>
                {item.order_name}
              </Link>
            </TableCell>
            <TableCell>{formatter.format(item.total_with_discount)} сум</TableCell>
            <TableCell>{formatDate(item.created_at)}</TableCell>
          </TableRow>
        ))}
      </TableItem>
    </>
  )
}

export default SalesmanReportsOrdersTable