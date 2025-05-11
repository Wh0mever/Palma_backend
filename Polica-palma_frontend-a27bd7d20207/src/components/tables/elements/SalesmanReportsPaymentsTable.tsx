import {TablesProps} from '@/typing/interfaces.ts'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import {salesmanReportsPaymentsTHData} from '@/data/tablesHeaderData.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import translatedData from '@/data/translatedData.ts'
import formatDate from '@/helpers/formatDate.ts'
import TableItem from '@/components/tables/TableItem.tsx'

const SalesmanReportsPaymentsTable = ({ data }: TablesProps) => {
  const { formatter } = useNumberFormatter()

  return (
    <>
      <TableItem data={data} headerData={salesmanReportsPaymentsTHData} notFoundText='Платежи не найдены!'>
        {data && Array.isArray(data) && data.map((item, index) => (
          <TableRow key={item.id}>
            <TableCell>{++index}</TableCell>
            <TableCell>{item.payment_name}</TableCell>
            <TableCell>{formatter.format(item.amount)} сум</TableCell>
            <TableCell>{translatedData(item.payment_type)}</TableCell>
            <TableCell>{translatedData(item.payment_model_type)}</TableCell>
            <TableCell>{formatDate(item.created_at)}</TableCell>
          </TableRow>
        ))}
      </TableItem>
    </>
  )
}

export default SalesmanReportsPaymentsTable