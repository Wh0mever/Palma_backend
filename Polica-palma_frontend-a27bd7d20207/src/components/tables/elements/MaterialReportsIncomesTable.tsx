import {TablesProps} from '@/typing/interfaces.ts'
import TableItem from '@/components/tables/TableItem.tsx'
import {materialReportsIncomesTHData} from '@/data/tablesHeaderData.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import formatDate from '@/helpers/formatDate.ts'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'

const MaterialReportsIncomesTable = ({ data }: TablesProps) => {
  const { formatter } = useNumberFormatter()

  return (
    <>
      <TableItem data={data} headerData={materialReportsIncomesTHData} notFoundText='Приходы не найдены!'>
        {data && Array.isArray(data) && data.map((item, index) => (
          <TableRow key={item.id}>
            <TableCell>{++index}</TableCell>
            <TableCell>{item.provider?.full_name}</TableCell>
            <TableCell>{formatter.format(item.product_count)} шт</TableCell>
            <TableCell>{formatDate(item.created_at)}</TableCell>
          </TableRow>
        ))}
      </TableItem>
    </>
  )
}

export default MaterialReportsIncomesTable