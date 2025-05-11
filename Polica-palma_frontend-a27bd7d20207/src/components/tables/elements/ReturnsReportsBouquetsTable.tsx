import {TablesProps} from '@/typing/interfaces.ts'
import {bouquetsReturnsReportsTHData} from '@/data/tablesHeaderData.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import formatDate from '@/helpers/formatDate.ts'
import TableItem from '@/components/tables/TableItem.tsx'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'

const ReturnsReportsBouquetsTable = ({ data }: TablesProps) => {
  const { formatter } = useNumberFormatter()

  return (
    <>
      <TableItem data={data} headerData={bouquetsReturnsReportsTHData} notFoundText='Возвращенные букеты не найдены!'>
        {data && Array.isArray(data) && data.map((item, index) => (
          <TableRow key={item.id}>
            <TableCell>{++index}</TableCell>
            <TableCell>{item.order_name}</TableCell>
            <TableCell>{item.product_factory?.name}</TableCell>
            <TableCell>{formatter.format(item.count)} шт</TableCell>
            <TableCell>{formatter.format(item.price)} сум</TableCell>
            <TableCell>{formatter.format(item.total)} сум</TableCell>
            <TableCell>{formatter.format(item.total_self_price)} сум</TableCell>
            <TableCell>{formatDate(item.returned_at)}</TableCell>
          </TableRow>
        ))}
      </TableItem>
    </>
  )
}

export default ReturnsReportsBouquetsTable