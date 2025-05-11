import {bouquetsTHData} from '@/data/tablesHeaderData.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import translatedData from '@/data/translatedData.ts'
import formatDate from '@/helpers/formatDate.ts'
import TableItem from '@/components/tables/TableItem.tsx'
import {TablesProps} from '@/typing/interfaces.ts'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import getUrl from '@/config.ts'
import {Button} from '@/components/ui/button.tsx'
import {ScanLine} from 'lucide-react'

const FinishedBouquetsTable = ({ data }: TablesProps) => {
  const { formatter } = useNumberFormatter()

  return (
    <TableItem data={data} headerData={bouquetsTHData} notFoundText='Собранные букеты не найдены!'>
      {data && Array.isArray(data) && data.map((item, index) => (
        <TableRow key={item.id}>
          <TableCell>{++index}</TableCell>
          <TableCell>{item.name}</TableCell>
          <TableCell>{item.category?.name}</TableCell>
          <TableCell>{formatter.format(item.self_price)}</TableCell>
          <TableCell>{formatter.format(item.price)}</TableCell>
          <TableCell>{translatedData(item.status)}</TableCell>
          <TableCell>{translatedData(item.sales_type)}</TableCell>
          <TableCell>{item.product_code}</TableCell>
          <TableCell>{formatDate(item.created_at) || '-'}</TableCell>
          <TableCell>{item.finished_at !== null ? formatDate(item.finished_at) : '-'}</TableCell>
          <TableCell>
            <a href={`${getUrl()}/core/print-receipt/factory/${item.id}/`} target='_blank'>
              <Button size='icon'>
                <ScanLine className='w-4 h-4'/>
              </Button>
            </a>
          </TableCell>
        </TableRow>
      ))}
    </TableItem>
  )
}

export default FinishedBouquetsTable