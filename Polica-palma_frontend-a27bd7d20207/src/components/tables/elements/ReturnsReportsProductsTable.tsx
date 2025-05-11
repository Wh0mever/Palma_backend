import TableItem from '@/components/tables/TableItem.tsx'
import {TablesProps} from '@/typing/interfaces.ts'
import {productsReportsReturnsTHData} from '@/data/tablesHeaderData.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import formatDate from '@/helpers/formatDate.ts'

const ReturnsReportsProductsTable = ({ data }: TablesProps) => {
  const { formatter } = useNumberFormatter()

  return (
    <>
      <TableItem data={data} headerData={productsReportsReturnsTHData} notFoundText='Возвращенные товары не найдены!'>
        {data && Array.isArray(data) && data.map((item, index) => (
          <TableRow key={item.id}>
            <TableCell>{++index}</TableCell>
            <TableCell>{item.order_name}</TableCell>
            <TableCell>{item.product?.name}</TableCell>
            <TableCell>{formatter.format(item.count)} шт</TableCell>
            <TableCell>{formatter.format(item.price)} сум</TableCell>
            <TableCell>{formatter.format(item.total)} сум</TableCell>
            <TableCell>{formatter.format(item.total_self_price)} сум</TableCell>
            <TableCell>{formatDate(item.created_at)}</TableCell>
          </TableRow>
        ))}
      </TableItem>
    </>
  )
}

export default ReturnsReportsProductsTable