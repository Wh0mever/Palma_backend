import TableItem from '@/components/tables/TableItem.tsx'
import {TablesProps} from '@/typing/interfaces.ts'
import {floristsReportsEditTHData} from '@/data/tablesHeaderData.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import translatedData from '@/data/translatedData.ts'
import {Link} from "react-router-dom"

const FloristsReportsEditTable = ({ data }: TablesProps) => {
  const { formatter } = useNumberFormatter()

  return (
    <>
      <TableItem data={data} headerData={floristsReportsEditTHData} notFoundText='Букеты не найдены!'>
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
            <TableCell>{formatter.format(item.price)} сум</TableCell>
            <TableCell>{formatter.format(item.self_price)} сум</TableCell>
          </TableRow>
        ))}
      </TableItem>
    </>
  )
}

export default FloristsReportsEditTable