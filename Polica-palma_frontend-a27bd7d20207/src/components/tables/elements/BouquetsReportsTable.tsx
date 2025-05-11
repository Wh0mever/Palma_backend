import {TablesProps} from '@/typing/interfaces.ts'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import TableItem from '@/components/tables/TableItem.tsx'
import {bouquetsReportsTHData} from '@/data/tablesHeaderData.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import translatedData from '@/data/translatedData.ts'
import formatDate from '@/helpers/formatDate.ts'
import {Link} from "react-router-dom"

const BouquetsReportsTable = ({ data }: TablesProps) => {
  const { formatter } = useNumberFormatter()

  return (
    <>
      <TableItem data={data} headerData={bouquetsReportsTHData} notFoundText='Букеты не найдены!'>
        {data && Array.isArray(data) && data.map((item, index) => (
          <TableRow key={item.id}>
            <TableCell>{++index}</TableCell>
            <TableCell>
              <Link to={`/dashboard/factories/bouquets/edit/${item.id}`} className='hover:underline'>
                {item.name}
              </Link>
            </TableCell>
            <TableCell>{item.category?.name}</TableCell>
            <TableCell>{translatedData(item.sales_type)}</TableCell>
            <TableCell>{formatter.format(item.self_price)} сум</TableCell>
            <TableCell>{formatter.format(item.price)} сум</TableCell>
            <TableCell>{item.florist?.first_name || item.florist?.username}</TableCell>
            <TableCell>{translatedData(item.status)}</TableCell>
            <TableCell>{item.product_code}</TableCell>
            <TableCell>{item.finished_at ? formatDate(item.finished_at) : '-'}</TableCell>
          </TableRow>
        ))}
      </TableItem>
    </>
  )
}

export default BouquetsReportsTable