import TableItem from '@/components/tables/TableItem.tsx'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import EditItem from '@/components/items/EditItem.tsx'
import DeleteDialog from '@/components/others/DeleteDialog.tsx'
import {TablesProps} from '@/typing/interfaces.ts'
import {industriesTHData} from '@/data/tablesHeaderData.ts'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'

const IndustriesTable = ({ data }: TablesProps) => {
  const { formatter } = useNumberFormatter()

  return (
    <TableItem data={data} headerData={industriesTHData} notFoundText='Магазины не найдены!'>
      {data && Array.isArray(data) && data.map((item, index) => (
        <TableRow key={item.id}>
          <TableCell>{++index}</TableCell>
          <TableCell>{item.name}</TableCell>
          <TableCell>{formatter.format(item.sale_compensation_percent)}%</TableCell>
          <TableCell className='flex items-center gap-4'>
            <EditItem link={`/dashboard/product/industries/edit/${item.id}`} />
            <DeleteDialog
              desc
              item={item.name}
              id={item.id}
              url='api/industries'
              invalidatesTags={["Industries"]}
            />
          </TableCell>
        </TableRow>
      ))}
    </TableItem>
  )
}

export default IndustriesTable