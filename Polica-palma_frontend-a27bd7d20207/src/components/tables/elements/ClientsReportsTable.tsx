import {TablesProps} from '@/typing/interfaces.ts'
import TableItem from '@/components/tables/TableItem.tsx'
import {clientsReportsTHData} from '@/data/tablesHeaderData.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import {Button} from '@/components/ui/button.tsx'
import {Eye} from 'lucide-react'
import {Link} from 'react-router-dom'
import formatPhoneNumber from '@/helpers/formatPhoneNumber.ts'

const ClientsReportsTable = ({ data }: TablesProps) => {
  const { formatter } = useNumberFormatter()

  return (
    <>
      <TableItem data={data} headerData={clientsReportsTHData} notFoundText='Клиенты не найдены!'>
        {data && Array.isArray(data) && data.map((item, index) => (
          <TableRow key={item.id}>
            <TableCell>{++index}</TableCell>
            <TableCell>{item.full_name}</TableCell>
            <TableCell>{formatPhoneNumber(item.phone_number || '-')}</TableCell>
            <TableCell>{formatter.format(item.orders_count)}</TableCell>
            <TableCell>{formatter.format(item.orders_sum)} сум</TableCell>
            <TableCell>{formatter.format(item.total_discount_sum)} сум</TableCell>
            <TableCell>{formatter.format(item.debt)} сум</TableCell>
            <TableCell>
              <Link to={`/dashboard/reports/clients/${item.id}`}>
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

export default ClientsReportsTable