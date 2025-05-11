import TableItem from '@/components/tables/TableItem.tsx'
import {TablesProps} from '@/typing/interfaces.ts'
import {floristReportsTHData} from '@/data/tablesHeaderData.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import translatedData from '@/data/translatedData.ts'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import {Link} from 'react-router-dom'
import {Button} from '@/components/ui/button.tsx'
import {Eye} from 'lucide-react'

const FloristReportsTable = ({ data }: TablesProps) => {
  const { formatter } = useNumberFormatter()

  return (
    <>
      <TableItem data={data} headerData={floristReportsTHData} notFoundText='Флористы не найдены!'>
        {data && Array.isArray(data) && data.map((item, index) => (
          <TableRow key={item.id}>
            <TableCell>{++index}</TableCell>
            <TableCell>{item.name}</TableCell>
            <TableCell>{translatedData(item.type)}</TableCell>
            <TableCell>{formatter.format(item.total_product_count)} шт</TableCell>
            <TableCell>{formatter.format(item.finished_product_count)} шт</TableCell>
            <TableCell>{formatter.format(item.sold_product_count)} шт</TableCell>
            <TableCell>{formatter.format(item.written_off_product_count)} шт</TableCell>
            <TableCell>{formatter.format(item.income_sum)} сум</TableCell>
            <TableCell>{formatter.format(item.payment_sum)} сум</TableCell>
            <TableCell>
              <Link to={`/dashboard/reports/florists/${item.id}`}>
                <Button size='icon'>
                  <Eye className='w-4 h-4' />
                </Button>
              </Link>
            </TableCell>
          </TableRow>
        ))}
      </TableItem>
    </>
  )
}

export default FloristReportsTable