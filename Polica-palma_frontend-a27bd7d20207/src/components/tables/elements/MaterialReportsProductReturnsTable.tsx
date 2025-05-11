import {TablesProps} from '@/typing/interfaces.ts'
import TableItem from '@/components/tables/TableItem.tsx'
import {materialReportsProductReturnsTHData} from '@/data/tablesHeaderData.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import formatDate from '@/helpers/formatDate.ts'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'

const MaterialReportsProductReturnsTable = ({ data }: TablesProps) => {
  const { formatter } = useNumberFormatter()

  return (
    <>
      <TableItem data={data} headerData={materialReportsProductReturnsTHData} notFoundText='Возвращенные товары не найдены!'>
        {data && Array.isArray(data) && data.map((item, index) => (
          <TableRow key={item.id}>
            <TableCell>{++index}</TableCell>
            <TableCell>{item.order_name}</TableCell>
            <TableCell>{formatter.format(item.count)} шт</TableCell>
            <TableCell>{formatDate(item.created_at)}</TableCell>
          </TableRow>
        ))}
      </TableItem>
    </>
  )
}

export default MaterialReportsProductReturnsTable