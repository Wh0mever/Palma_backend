import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import TableItem from '@/components/tables/TableItem.tsx'
import {TablesProps} from '@/typing/interfaces.ts'
import {writeOffReportsTHData} from '@/data/tablesHeaderData.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import {Link} from 'react-router-dom'
import {Button} from '@/components/ui/button.tsx'
import {Eye} from 'lucide-react'
import formatDate from "@/helpers/formatDate.ts"

interface WriteOffReportsTableProps extends TablesProps {
  isBouquet?: boolean
}

const WriteOffReportsTable = ({ data, isBouquet }: WriteOffReportsTableProps) => {
  const { formatter } = useNumberFormatter()

  return (
    <>
      <TableItem data={data} headerData={writeOffReportsTHData} notFoundText='Товары не найдены!'>
        {data && Array.isArray(data) && data.map((item, index) => (
          <TableRow key={item.id}>
            <TableCell>{++index}</TableCell>
            <TableCell>{item.name}</TableCell>
            <TableCell>{item.category.name}</TableCell>
            <TableCell>{formatter.format(item.self_price_sum)} сум</TableCell>
            <TableCell>{formatter.format(item.product_count)} шт</TableCell>
            <TableCell>{item.code}</TableCell>
            <TableCell>{item.written_off_at ? formatDate(item.written_off_at) : '-'}</TableCell>
            <TableCell>
              <Link to={isBouquet ? `/dashboard/factories/bouquets/edit/${item.id}/` : `/dashboard/reports/write-offs/${item.id}/`}>
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

export default WriteOffReportsTable