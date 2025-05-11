import TableItem from '@/components/tables/TableItem.tsx'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import EditItem from '@/components/items/EditItem.tsx'
import DeleteDialog from '@/components/others/DeleteDialog.tsx'
import {TablesProps} from '@/typing/interfaces.ts'
import {categoriesTHData} from '@/data/tablesHeaderData.ts'

const CategoriesTable = ({ data }: TablesProps) => {
  return (
    <TableItem data={data} headerData={categoriesTHData} notFoundText='Категории не найдены!'>
      {data && Array.isArray(data) && data.map((item, index) => (
        <TableRow key={item.id}>
          <TableCell>{++index}</TableCell>
          <TableCell>{item.name}</TableCell>
          <TableCell>{item.industry?.name}</TableCell>
          <TableCell className='flex items-center gap-4'>
            <EditItem link={`/dashboard/product/categories/edit/${item.id}`} />
            <DeleteDialog
              desc
              id={item.id}
              url='api/categories'
              item={item.name}
              invalidatesTags={["Categories"]}
            />
          </TableCell>
        </TableRow>
      ))}
    </TableItem>
  )
}

export default CategoriesTable