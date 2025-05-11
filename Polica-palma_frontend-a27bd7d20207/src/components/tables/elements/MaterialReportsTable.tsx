import {TablesProps} from '@/typing/interfaces.ts'
import TableItem from '@/components/tables/TableItem.tsx'
import {materialReportsTHData} from '@/data/tablesHeaderData.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import {Link} from 'react-router-dom'
import {Button} from '@/components/ui/button.tsx'
import {Eye} from 'lucide-react'

const MaterialReportsTable = ({ data }: TablesProps) => {
  const { formatter } = useNumberFormatter()

  return (
    <>
      <TableItem data={data} headerData={materialReportsTHData} notFoundText='Отчеты не найдены!'>
        {data && Array.isArray(data) && data.map((item, index) => (
          <TableRow key={item.id}>
            <TableCell>{++index}</TableCell>
            <TableCell>{item.name}</TableCell>
            <TableCell>{formatter.format(item.before_count)} шт</TableCell>
            <TableCell>{formatter.format(item.total_income_in_range)} шт</TableCell>
            <TableCell>{formatter.format(item.total_outcome_in_range)} шт</TableCell>
            <TableCell>{formatter.format(item.after_count)} шт</TableCell>
            <TableCell>{formatter.format(item.current_count)} шт</TableCell>
            <TableCell>
              <Link to={`/dashboard/reports/materials/${item.id}/`}>
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

export default MaterialReportsTable