import {TablesProps} from '@/typing/interfaces.ts'
import TableItem from '@/components/tables/TableItem.tsx'
import {salesmanReportsTHData} from '@/data/tablesHeaderData.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import {Link} from 'react-router-dom'
import {Button} from '@/components/ui/button.tsx'
import {Eye} from 'lucide-react'

const SalesmanReportsTable = ({ data }: TablesProps) => {
  const { formatter } = useNumberFormatter()

  return (
    <>
      <TableItem data={data} headerData={salesmanReportsTHData} notFoundText='Продавцы не найдены!'>
        {data && Array.isArray(data) && data.map((item, index) => (
          <TableRow key={item.id}>
            <TableCell>{++index}</TableCell>
            <TableCell>{item.name}</TableCell>
            <TableCell>{item.industry?.name || '-'}</TableCell>
            <TableCell>{formatter.format(item.balance)} сум</TableCell>
            <TableCell>{formatter.format(item.orders_count)} шт</TableCell>
            <TableCell>{formatter.format(item.order_total_sum)} сум</TableCell>
            <TableCell>{formatter.format(item.income_sum)} сум</TableCell>
            <TableCell>{formatter.format(item.payment_sum)} сум</TableCell>
            <TableCell>
              <Link to={`/dashboard/reports/salesman/${item.id}/`} target='_blank'>
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

export default SalesmanReportsTable