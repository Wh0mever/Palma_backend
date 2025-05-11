import {TablesProps} from '@/typing/interfaces.ts'
import TableItem from '@/components/tables/TableItem.tsx'
import {clientsReportsEditTHData} from '@/data/tablesHeaderData.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import formatDate from '@/helpers/formatDate.ts'
import {Link} from 'react-router-dom'
import {Button} from '@/components/ui/button.tsx'
import {Eye} from 'lucide-react'

const ClientsReportsEditTable = ({ data }: TablesProps) => {
  const { formatter } = useNumberFormatter()

  return (
    <>
      <TableItem data={data} headerData={clientsReportsEditTHData} notFoundText='Продажи не найдены!'>
        {data && Array.isArray(data) && data.map((item, index) => (
          <TableRow key={item.id}>
            <TableCell>{++index}</TableCell>
            <TableCell>{item.name}</TableCell>
            <TableCell>{formatter.format(item.total_with_discount)} сум</TableCell>
            <TableCell>{formatter.format(item.debt)} сум</TableCell>
            <TableCell>{formatter.format(item.total_discount)} сум</TableCell>
            <TableCell>{formatDate(item.created_at)}</TableCell>
            <TableCell>
              <Link to={`/dashboard/order/orders/edit/${item.id}`}>
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

export default ClientsReportsEditTable