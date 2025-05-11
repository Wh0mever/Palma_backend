import {TablesProps} from '@/typing/interfaces.ts'
import TableItem from '@/components/tables/TableItem.tsx'
import {writeOffReportsEditTHData} from '@/data/tablesHeaderData.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import formatDate from '@/helpers/formatDate.ts'

const WriteOffReportsEditTable = ({ data }: TablesProps) => {
  const { formatter } = useNumberFormatter()

  return (
    <>
      <TableItem data={data} headerData={writeOffReportsEditTHData} notFoundText='Списания не найдены!'>
        {data && Array.isArray(data) && data.map((item, index) => (
          <TableRow key={item.id}>
            <TableCell>{++index}</TableCell>
            <TableCell>{item.comment}</TableCell>
            <TableCell>{formatter.format(item.count)} шт</TableCell>
            <TableCell>{formatter.format(item.self_price)} сум</TableCell>
            <TableCell>{formatDate(item.created_at)}</TableCell>
          </TableRow>
        ))}
      </TableItem>
    </>
  )
}

export default WriteOffReportsEditTable