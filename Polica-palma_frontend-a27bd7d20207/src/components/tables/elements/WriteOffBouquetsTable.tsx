import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import TableItem from '@/components/tables/TableItem.tsx'
import {bouquetsTHData} from '@/data/tablesHeaderData.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import translatedData from '@/data/translatedData.ts'
import formatDate from '@/helpers/formatDate.ts'
import {TablesProps} from '@/typing/interfaces.ts'

const WriteOffBouquetsTable = ({ data }: TablesProps) => {
  const { formatter } = useNumberFormatter()

  return (
    <TableItem data={data} headerData={bouquetsTHData} notFoundText='Списанные букеты не найдены!'>
      {data && Array.isArray(data) && data.map((item, index) => (
        <TableRow key={item.id}>
          <TableCell>{++index}</TableCell>
          <TableCell>{item.name}</TableCell>
          <TableCell>{item.category?.name}</TableCell>
          <TableCell>{item.florist?.first_name || item.florist?.username}</TableCell>
          <TableCell>{formatter.format(item.self_price)}</TableCell>
          <TableCell>{formatter.format(item.price)}</TableCell>
          <TableCell>{translatedData(item.status)}</TableCell>
          <TableCell>{translatedData(item.sales_type)}</TableCell>
          <TableCell>{item.product_code}</TableCell>
          <TableCell>{formatDate(item.created_at) || '-'}</TableCell>
          <TableCell>{item.finished_at !== null ? formatDate(item.finished_at) : '-'}</TableCell>
          <TableCell>{formatDate(item.written_off_at)}</TableCell>
        </TableRow>
      ))}
    </TableItem>
  )
}

export default WriteOffBouquetsTable