import {shiftsTHData} from '@/data/tablesHeaderData.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import TableItem from '@/components/tables/TableItem.tsx'
import {TablesProps} from '@/typing/interfaces.ts'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import formatDate from '@/helpers/formatDate.ts'

const ShiftsSectionTable = ({ data }: TablesProps) => {
  const { formatter } = useNumberFormatter()

  return (
    <TableItem data={data} headerData={shiftsTHData} notFoundText='Товары не найдены!'>
      {data && Array.isArray(data) && data.map((item, index) => (
        <TableRow key={item.id}>
          <TableCell>{++index}</TableCell>
          <TableCell>{formatDate(item.start_date)}</TableCell>
          <TableCell>{item.end_date !== null ? formatDate(item.end_date) : '-'}</TableCell>
          <TableCell>{item.started_user?.first_name || item.started_user?.username}</TableCell>
          <TableCell>{item.completed_user?.first_name || item.completed_user?.username || '-'}</TableCell>
          <TableCell>{formatter.format(item.cash_income_amount)} сум</TableCell>
          <TableCell>{formatter.format(item.cash_outcome_amount)} сум</TableCell>
          <TableCell>{formatter.format(item.total_profit_cash)} сум</TableCell>
          <TableCell>{formatter.format(item.overall_income_amount)} сум</TableCell>
          <TableCell>{formatter.format(item.overall_outcome_amount)} сум</TableCell>
          <TableCell>{formatter.format(item.total_profit)} сум</TableCell>
        </TableRow>
      ))}
    </TableItem>
  )
}

export default ShiftsSectionTable