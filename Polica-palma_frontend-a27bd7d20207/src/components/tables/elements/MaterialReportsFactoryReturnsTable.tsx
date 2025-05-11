import TableItem from '@/components/tables/TableItem.tsx'
import {TablesProps} from '@/typing/interfaces.ts'
import {materialReportsFactoryReturnsTHData} from '@/data/tablesHeaderData.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import formatDate from '@/helpers/formatDate.ts'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'

const MaterialReportsFactoryReturnsTable = ({ data }: TablesProps) => {
  const { formatter } = useNumberFormatter()

  return (
    <>
      <TableItem data={data} headerData={materialReportsFactoryReturnsTHData} notFoundText='Возвращенные букеты не найдены!'>
        {data && Array.isArray(data) && data.map((item, index) => (
          <TableRow key={item.id}>
            <TableCell>{++index}</TableCell>
            <TableCell>{item.product_name}</TableCell>
            <TableCell>{formatter.format(item.count)} шт</TableCell>
            <TableCell>{formatDate(item.created_at)}</TableCell>
          </TableRow>
        ))}
      </TableItem>
    </>
  )
}

export default MaterialReportsFactoryReturnsTable